from tavily import TavilyClient
from agents.base import invoke_bedrock
from agents.prompts import ANSWER_PROMPT
from config import TAVILY_API_KEY
from storage import storage

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def build_papers_context(papers: list) -> str:
    if not papers:
        return "No papers in collection yet."

    context_parts = []
    for paper in papers:
        context_parts.append(
            f"- {paper.title} ({paper.year})\n"
            f"  arXiv ID: {paper.id}\n"
            f"  Authors: {', '.join(paper.authors[:3])}\n"
            f"  Key concepts: {', '.join(paper.key_concepts)}\n"
            f"  Abstract: {paper.summary[:300]}..."
        )
    return "\n\n".join(context_parts)


def build_edges_context(edges: list, papers: list) -> str:
    if not edges:
        return "No connections found yet."

    paper_map = {p.id: p.title for p in papers}
    context_parts = []
    for edge in edges:
        source_title = paper_map.get(edge.source_id, edge.source_id)
        target_title = paper_map.get(edge.target_id, edge.target_id)
        context_parts.append(
            f"- {source_title[:50]} -> {target_title[:50]} ({edge.edge_type})"
        )
    return "\n".join(context_parts)


def search_for_answer(question: str, papers: list) -> dict:

    paper_concepts = []
    for paper in papers[:3]:  # Limit to 3 papers for query
        paper_concepts.extend(paper.key_concepts[:2])

    query = f"{question} {' '.join(paper_concepts[:5])}"

    try:
        result = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=5,
        )
        return result
    except Exception as e:
        print(f"Tavily search error: {e}")
        return {"results": []}


def answer_agent(state: dict) -> dict:
    question = state.get("user_message", "")
    papers = storage.get_all_papers()
    edges = storage.get_edges()

    search_results = search_for_answer(question, papers)

    results_text = "\n".join([
        f"- {r.get('title', 'No title')}: {r.get('content', 'No content')[:300]}..."
        for r in search_results.get("results", [])[:5]
    ]) or "No relevant search results found."

    papers_context = build_papers_context(papers)
    edges_context = build_edges_context(edges, papers)

    answer = invoke_bedrock(
        ANSWER_PROMPT.format(
            papers_context=papers_context,
            edges_context=edges_context,
            question=question,
            search_results=results_text
        ),
        max_tokens=500,
        temperature=0.7
    )

    return {
        **state,
        "response": answer
    }
