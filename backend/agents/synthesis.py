from storage import storage
from models import GraphData


def build_cytoscape_graph(graph_data: GraphData) -> dict:
    elements = []

    for paper in graph_data.nodes:
        elements.append({
            "data": {
                "id": paper.id,
                "label": paper.title[:50] + "..." if len(paper.title) > 50 else paper.title,
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "abstract": paper.summary[:200] + "..." if paper.summary and len(paper.summary) > 200 else paper.summary,
                "key_concepts": paper.key_concepts,
                "arxiv_url": paper.arxiv_url,
                "pdf_url": paper.pdf_url,
            }
        })

    for edge in graph_data.edges:
        elements.append({
            "data": {
                "id": edge.id,
                "source": edge.source_id,
                "target": edge.target_id,
            }
        })

    return {"elements": elements}


def build_response_message(state: dict) -> str:
    parts = []

    if state.get("response"):
        parts.append(state["response"])
    if state.get("citation_message"):
        parts.append(state["citation_message"])
    if state.get("error"):
        parts.append(f"Note: {state['error']}")

    return " ".join(parts) if parts else "I'm here to help with your research papers."


def synthesis_agent(state: dict) -> dict:
    graph_data = storage.get_graph_data()

    return {
        **state,
        "graph_data": build_cytoscape_graph(graph_data),
        "final_response": build_response_message(state),
    }
