from itertools import combinations
from models import Paper, Edge
from storage import storage
import uuid


def has_shared_concepts(paper_a: Paper, paper_b: Paper) -> bool:
    concepts_a = {c.lower() for c in paper_a.key_concepts}
    concepts_b = {c.lower() for c in paper_b.key_concepts}
    return bool(concepts_a & concepts_b)


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
    new_edges = []

    # Determine which paper pairs to check
    if papers_added:
        pairs = [(p, other) for p in papers_added for other in all_papers if p.id != other.id]
    elif state.get("intent") == "find_connections":
        pairs = list(combinations(all_papers, 2))
    else:
        pairs = []

    for paper_a, paper_b in pairs:
        if (paper_a.id, paper_b.id) in existing_edges or (paper_b.id, paper_a.id) in existing_edges:
            continue

        if has_shared_concepts(paper_a, paper_b):
            edge = Edge(id=str(uuid.uuid4()), source_id=paper_a.id, target_id=paper_b.id)
            new_edges.append(edge)
            storage.add_edge(edge)
            existing_edges.add((paper_a.id, paper_b.id))

    msg = f"Found {len(new_edges)} connections based on shared concepts." if new_edges else "No shared concepts found between papers."
    return {**state, "connection_edges": new_edges, "connection_message": msg}
