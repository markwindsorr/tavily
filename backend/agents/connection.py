from typing import List, Set, Tuple
from models import Paper, Edge
from storage import storage
import uuid


def find_concept_connections(
    paper: Paper,
    all_papers: List[Paper],
    existing_edges: Set[Tuple[str, str]]
) -> List[Edge]:
    edges = []

    for other in all_papers:
        if other.id == paper.id:
            continue

        if (paper.id, other.id) in existing_edges or (other.id, paper.id) in existing_edges:
            continue

        paper_concepts = set(c.lower() for c in paper.key_concepts)
        other_concepts = set(c.lower() for c in other.key_concepts)
        shared = paper_concepts & other_concepts

        if shared:
            edge = Edge(
                id=str(uuid.uuid4()),
                source_id=paper.id,
                target_id=other.id
            )
            edges.append(edge)
            storage.add_edge(edge)
            existing_edges.add((paper.id, other.id))

    return edges


def connection_agent(state: dict) -> dict:
    papers_added = state.get("papers_added", [])
    all_papers = storage.get_all_papers()

    if len(all_papers) < 2:
        return {
            **state,
            "connection_edges": [],
            "connection_message": "Need at least 2 papers to find connections."
        }

    existing_edges = {(e.source_id, e.target_id) for e in storage.get_edges()}
    all_edges = []

    for paper in papers_added:
        edges = find_concept_connections(paper, all_papers, existing_edges)
        all_edges.extend(edges)

    if not papers_added and state.get("intent") == "find_connections":
        for i, paper_a in enumerate(all_papers):
            for paper_b in all_papers[i + 1:]:
                edges = find_concept_connections(paper_a, [paper_b], existing_edges)
                all_edges.extend(edges)

    return {
        **state,
        "connection_edges": all_edges,
        "connection_message": f"Found {len(all_edges)} connections based on shared concepts." if all_edges else "No shared concepts found between papers."
    }
