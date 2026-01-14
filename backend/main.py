import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import Paper, ChatRequest, ChatResponse, AddPaperRequest, GraphData, SelectPaperRequest, Edge, PaperCandidate
from storage import storage
from graph import run_pipeline
from agents.utils import extract_arxiv_id, search_arxiv_by_name
from agents.ingest import fetch_paper_from_arxiv
from agents.synthesis import build_cytoscape_graph

app = FastAPI(title="Research Paper Connection Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Research Paper Connection Agent API"}


@app.post("/papers", response_model=Paper)
async def add_paper(request: AddPaperRequest):
    arxiv_id = extract_arxiv_id(request.arxiv_id)
    existing = storage.get_paper(arxiv_id)
    if existing:
        return existing
    paper = fetch_paper_from_arxiv(arxiv_id)
    storage.add_paper(paper)
    return paper


@app.get("/papers", response_model=List[Paper])
async def get_papers():
    return storage.get_all_papers()


@app.get("/papers/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str):
    paper = storage.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@app.post("/papers/select", response_model=ChatResponse)
async def select_paper(request: SelectPaperRequest):
    papers_added = []
    citation_edges = []
    error_message = None

    arxiv_id = extract_arxiv_id(request.arxiv_id)

    if arxiv_id:
        existing = storage.get_paper(arxiv_id)
        if existing:
            papers_added = [existing.id]
        else:
            try:
                paper = fetch_paper_from_arxiv(arxiv_id)
                storage.add_paper(paper)
                papers_added = [paper.id]
            except Exception as e:
                error_message = f"Could not fetch paper: {str(e)}"
    else:
        try:
            results = search_arxiv_by_name(f'ti:"{request.arxiv_id}"', max_results=5)
            if not results:
                results = search_arxiv_by_name(request.arxiv_id, max_results=5)

            if results:
                candidates = [
                    PaperCandidate(
                        arxiv_id=r.get_short_id(),
                        title=r.title,
                        authors=[a.name for a in r.authors[:3]],
                        year=r.published.year,
                        source_paper_id=request.source_paper_id
                    )
                    for r in results
                ]
                return ChatResponse(
                    message=f"Found {len(candidates)} papers. Select the correct one:",
                    graph_updated=False,
                    papers_added=[],
                    paper_candidates=candidates
                )
            else:
                error_message = f"No papers found matching '{request.arxiv_id}'"
        except Exception as e:
            error_message = f"Search failed: {str(e)}"

    citation_created = False
    if request.source_paper_id and papers_added:
        added_paper_id = papers_added[0]
        existing_edges = storage.get_edges()
        edge_exists = any(
            (e.source_id == request.source_paper_id and e.target_id == added_paper_id) or
            (e.source_id == added_paper_id and e.target_id == request.source_paper_id)
            for e in existing_edges
        )

        if not edge_exists:
            source_paper = storage.get_paper(request.source_paper_id)
            source_title = source_paper.title if source_paper else request.source_paper_id
            citation_edge = Edge(
                id=str(uuid.uuid4()),
                source_id=request.source_paper_id,
                target_id=added_paper_id,
                edge_type="citation",
                evidence=f"Cited in references of '{source_title}'"
            )
            storage.add_edge(citation_edge)
            citation_edges.append(citation_edge)
            citation_created = True

    graph_updated = bool(papers_added) or bool(citation_edges)

    if error_message:
        base_message = error_message
    elif papers_added:
        added_paper = storage.get_paper(papers_added[0])
        base_message = f"Added: {added_paper.title}" if added_paper else "Paper added."
        if citation_created:
            base_message += " (linked as citation)"
    else:
        base_message = "No paper was added."

    response = ChatResponse(
        message=base_message,
        graph_updated=graph_updated,
        papers_added=papers_added
    )

    storage.add_chat_message("assistant", response.message)
    return response


@app.get("/graph", response_model=GraphData)
async def get_graph():
    return storage.get_graph_data()


@app.get("/graph/cytoscape")
async def get_cytoscape_graph():
    graph_data = storage.get_graph_data()
    return build_cytoscape_graph(graph_data)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    storage.add_chat_message("user", request.message)

    try:
        result = run_pipeline(request.message)
        message = result.get("final_response", "I processed your request.")
        papers_added = [p.id for p in result.get("papers_added", [])]
        graph_updated = bool(papers_added) or bool(result.get("citation_edges", []))
        paper_candidates = result.get("paper_candidates", [])

        response = ChatResponse(
            message=message,
            graph_updated=graph_updated,
            papers_added=papers_added,
            paper_candidates=paper_candidates
        )
    except Exception as e:
        response = ChatResponse(
            message=f"Error processing request: {str(e)}",
            graph_updated=False,
            papers_added=[]
        )

    storage.add_chat_message("assistant", response.message)
    return response


@app.get("/chat/history")
async def get_chat_history():
    return storage.get_chat_history()


@app.delete("/chat/history")
async def clear_chat_history():
    storage.clear_chat_history()
    return {"message": "Chat history cleared"}


@app.get("/papers/{paper_id}/related")
async def get_related_papers(paper_id: str):
    paper = storage.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    all_papers = storage.get_all_papers()
    existing_edges = storage.get_edges()

    connected_ids = set()
    for edge in existing_edges:
        if edge.source_id == paper_id:
            connected_ids.add(edge.target_id)
        elif edge.target_id == paper_id:
            connected_ids.add(edge.source_id)

    return [p for p in all_papers if p.id != paper_id and p.id not in connected_ids]


@app.post("/edges/batch")
async def create_batch_edges(request: dict):
    source_id = request.get("source_id")
    target_ids = request.get("target_ids", [])
    edge_type = request.get("edge_type", "manual")

    if not source_id or not target_ids:
        raise HTTPException(status_code=400, detail="source_id and target_ids required")

    source_paper = storage.get_paper(source_id)
    if not source_paper:
        raise HTTPException(status_code=404, detail="Source paper not found")

    edges_created = []
    for target_id in target_ids:
        target_paper = storage.get_paper(target_id)
        if not target_paper:
            continue

        edge = Edge(
            id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            evidence="Connected by user"
        )
        storage.add_edge(edge)
        edges_created.append(edge)

    return {"edges_created": len(edges_created)}


@app.delete("/papers/{paper_id}")
async def delete_paper(paper_id: str):
    paper = storage.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    storage.delete_paper(paper_id)
    return {"message": f"Paper '{paper.title}' deleted"}


@app.delete("/edges/{edge_id}")
async def delete_edge(edge_id: str):
    storage.delete_edge(edge_id)
    return {"message": "Edge deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
