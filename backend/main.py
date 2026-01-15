import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import Paper, ChatRequest, ChatResponse, AddPaperRequest, GraphData, SelectPaperRequest, Edge
from storage import storage
from graph import run_pipeline
from agents.utils import extract_arxiv_id
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
    """Add a paper by arXiv ID and optionally link it to a source paper."""
    papers_added = []
    error_message = None

    arxiv_id = extract_arxiv_id(request.arxiv_id)

    if not arxiv_id:
        error_message = f"Invalid arXiv ID: {request.arxiv_id}"
    else:
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

    # Create edge linking source paper to added paper
    edge_created = False
    if request.source_paper_id and papers_added:
        added_paper_id = papers_added[0]
        existing_edges = storage.get_edges()
        edge_exists = any(
            (e.source_id == request.source_paper_id and e.target_id == added_paper_id) or
            (e.source_id == added_paper_id and e.target_id == request.source_paper_id)
            for e in existing_edges
        )

        if not edge_exists:
            edge = Edge(
                id=str(uuid.uuid4()),
                source_id=request.source_paper_id,
                target_id=added_paper_id
            )
            storage.add_edge(edge)
            edge_created = True

    graph_updated = bool(papers_added) or edge_created

    if error_message:
        message = error_message
    elif papers_added:
        added_paper = storage.get_paper(papers_added[0])
        message = f"Added: {added_paper.title}" if added_paper else "Paper added."
        if edge_created:
            message += " (linked)"
    else:
        message = "No paper was added."

    response = ChatResponse(
        message=message,
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
        graph_updated = bool(papers_added) or bool(result.get("connection_edges", []))
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
