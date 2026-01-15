import arxiv
import json
from typing import List
from tavily import TavilyClient
from agents.base import invoke_bedrock, invoke_bedrock_with_pdf
from agents.prompts import CONCEPT_EXTRACTION_PROMPT, PAPER_NAME_EXTRACTION_PROMPT, RELATED_REFERENCE_EXTRACTION_PROMPT
from agents.utils import extract_arxiv_id, search_arxiv_by_name, download_pdf
from models import Paper, PaperCandidate, Reference
from storage import storage
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def extract_key_concepts(title: str, abstract: str) -> List[str]:
    response = invoke_bedrock(
        CONCEPT_EXTRACTION_PROMPT.format(title=title, abstract=abstract),
        max_tokens=100,
        temperature=0
    )
    concepts_text = response.strip()
    concepts = [c.strip() for c in concepts_text.split(",")]
    return concepts[:5]


def extract_references_from_pdf(pdf_url: str) -> List[Reference]:
    try:
        pdf_bytes = download_pdf(pdf_url)
        response = invoke_bedrock_with_pdf(
            RELATED_REFERENCE_EXTRACTION_PROMPT,
            pdf_bytes,
            max_tokens=4000,
            temperature=0
        )
        refs = json.loads(response)
        return [Reference(**r) for r in refs[:10]]
    except Exception as e:
        print(f"Reference extraction failed: {e}")
        return []


def fetch_paper_from_arxiv(arxiv_id: str) -> Paper:
    search = arxiv.Search(id_list=[arxiv_id])
    client = arxiv.Client(page_size=1, delay_seconds=3.0, num_retries=3)
    results = list(client.results(search))
    if not results:
        raise ValueError(f"Paper not found: {arxiv_id}")

    paper = results[0]
    key_concepts = extract_key_concepts(paper.title, paper.summary)
    references = extract_references_from_pdf(paper.pdf_url)

    return Paper(
        id=paper.get_short_id(),
        title=paper.title,
        authors=[author.name for author in paper.authors],
        summary=paper.summary,
        published=paper.published,
        pdf_url=paper.pdf_url,
        key_concepts=key_concepts,
        references=references,
    )


def ingest_agent(state: dict) -> dict:
    message = state.get("user_message", "")
    arxiv_id = state.get("arxiv_id") or extract_arxiv_id(message)

    if not arxiv_id:
        paper_query = invoke_bedrock(
            PAPER_NAME_EXTRACTION_PROMPT.format(message=message),
            max_tokens=100,
            temperature=0
        ).strip()

        try:
            results = search_arxiv_by_name(paper_query, max_results=5)
            if not results:
                return {
                    **state,
                    "error": f"Could not find any papers matching '{paper_query}' on arXiv.",
                    "papers_added": [],
                    "paper_candidates": []
                }

            candidates = []
            for result in results:
                candidates.append(PaperCandidate(
                    arxiv_id=result.get_short_id(),
                    title=result.title,
                    authors=[a.name for a in result.authors[:3]],
                    year=result.published.year
                ))

            return {
                **state,
                "papers_added": [],
                "paper_candidates": candidates,
                "response": f"Found {len(candidates)} papers matching '{paper_query}'. Select one to add:"
            }

        except Exception as e:
            return {
                **state,
                "error": f"Error searching for paper: {str(e)}",
                "papers_added": [],
                "paper_candidates": []
            }

    existing = storage.get_paper(arxiv_id)
    if existing:
        return {
            **state,
            "papers_added": [existing],
            "response": f"Paper '{existing.title}' is already in your collection."
        }

    try:
        paper = fetch_paper_from_arxiv(arxiv_id)
        storage.add_paper(paper)

        return {
            **state,
            "papers_added": [paper],
            "response": f"Added paper: '{paper.title}' by {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}"
        }
    except Exception as e:
        return {
            **state,
            "error": f"Error fetching paper: {str(e)}",
            "papers_added": []
        }


def search_papers_with_tavily(query: str, max_results: int = 5) -> List[dict]:
    try:

        # search_depth: Literal["basic", "advanced", "fast", "ultra-fast"] = None
        result = tavily.search(
            query=f"{query} research paper",
            include_domains=["arxiv.org"],
            max_results=max_results,
            search_depth="advanced"
        )
        return result.get("results", [])
    except Exception as e:
        print(f"Tavily search error: {e}")
        return []


def search_papers_agent(state: dict) -> dict:
    message = state.get("user_message", "")

    paper_query = invoke_bedrock(
        PAPER_NAME_EXTRACTION_PROMPT.format(message=message),
        max_tokens=100,
        temperature=0
    ).strip()

    try:
        tavily_results = search_papers_with_tavily(paper_query)

        if not tavily_results:
            return {
                **state,
                "paper_candidates": [],
                "response": f"No papers found for '{paper_query}'. Try different keywords."
            }

        candidates = []
        seen_ids = set()

        for result in tavily_results:
            url = result.get("url", "")
            arxiv_id = extract_arxiv_id(url)

            if not arxiv_id or arxiv_id in seen_ids:
                continue

            seen_ids.add(arxiv_id)

            try:
                arxiv_results = search_arxiv_by_name(arxiv_id, max_results=1)
                if arxiv_results:
                    paper = arxiv_results[0]
                    candidates.append(PaperCandidate(
                        arxiv_id=paper.get_short_id(),
                        title=paper.title,
                        authors=[a.name for a in paper.authors[:3]],
                        year=paper.published.year
                    ))
            except Exception:
                candidates.append(PaperCandidate(
                    arxiv_id=arxiv_id,
                    title=result.get("title", "Unknown Title"),
                    authors=[],
                    year=0
                ))

            if len(candidates) >= 5:
                break

        if not candidates:
            return {
                **state,
                "paper_candidates": [],
                "response": f"No arXiv papers found for '{paper_query}'. Try different keywords."
            }

        return {
            **state,
            "paper_candidates": candidates,
            "response": f"Found {len(candidates)} papers matching '{paper_query}':"
        }

    except Exception as e:
        return {
            **state,
            "paper_candidates": [],
            "error": f"Error searching for papers: {str(e)}"
        }
