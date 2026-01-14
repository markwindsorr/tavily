from typing import List
from tavily import TavilyClient
from agents.base import invoke_bedrock
from agents.utils import extract_arxiv_id
from agents.prompts import PAPER_TITLE_EXTRACTION_PROMPT
from models import PaperCandidate
from storage import storage
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def search_related_papers(paper_title: str, max_results: int = 10) -> List[dict]:
    try:
        result = tavily.search(
            query=f'papers citing "{paper_title}" OR related to "{paper_title}"',
            include_domains=["arxiv.org"],
            max_results=max_results,
            search_depth="advanced"
        )
        return result.get("results", [])
    except Exception as e:
        print(f"Tavily search error: {e}")
        return []


def find_related_agent(state: dict) -> dict:
    message = state.get("user_message", "")

    paper_query = invoke_bedrock(
        PAPER_TITLE_EXTRACTION_PROMPT.format(message=message),
        max_tokens=100,
        temperature=0
    ).strip()

    all_papers = storage.get_all_papers()
    source_paper_id = None

    for paper in all_papers:
        if paper_query.lower() in paper.title.lower():
            source_paper_id = paper.id
            paper_query = paper.title
            break

    search_results = search_related_papers(paper_query)

    if not search_results:
        return {
            **state,
            "paper_candidates": [],
            "response": f"No related papers found for '{paper_query}'."
        }

    existing_ids = {p.id for p in all_papers}
    candidates = []
    seen_ids = set()

    for result in search_results:
        url = result.get("url", "")
        arxiv_id = extract_arxiv_id(url)

        if not arxiv_id or arxiv_id in existing_ids or arxiv_id in seen_ids:
            continue

        seen_ids.add(arxiv_id)
        candidates.append(PaperCandidate(
            arxiv_id=arxiv_id,
            title=result.get("title", f"Paper {arxiv_id}"),
            authors=[],
            year=0,
            source_paper_id=source_paper_id
        ))

        if len(candidates) >= 5:
            break

    if not candidates:
        return {
            **state,
            "paper_candidates": [],
            "response": f"Found results for '{paper_query}', but all are already in your collection."
        }

    return {
        **state,
        "paper_candidates": candidates,
        "response": f"Found {len(candidates)} papers related to '{paper_query}':"
    }
