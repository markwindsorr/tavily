import re
from typing import List, Optional
from tavily import TavilyClient
from config import TAVILY_API_KEY
from agents.base import invoke_bedrock
from agents.utils import extract_arxiv_id
from agents.prompts import CRAWL_URL_EXTRACTION_PROMPT, CRAWL_INSTRUCTIONS_PROMPT
from models import PaperCandidate

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def crawl_for_papers(start_url: str, instructions: Optional[str] = None, max_depth: int = 2, limit: int = 20) -> List[dict]:
    try:
        response = tavily.crawl(
            url=start_url,
            max_depth=max_depth,
            max_breadth=10,
            limit=limit,
            instructions=instructions or "Find research papers and their arXiv links. Focus on paper abstract pages."
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Tavily crawl error: {e}")
        return []


def map_site(base_url: str, max_depth: int = 2, max_breadth: int = 50) -> List[str]:
    try:
        response = tavily.map(
            url=base_url,
            max_depth=max_depth,
            max_breadth=max_breadth
        )
        return response.get("urls", [])
    except Exception as e:
        print(f"Tavily map error: {e}")
        return []


def crawl_agent(state: dict) -> dict:
    message = state.get("user_message", "")

    url = invoke_bedrock(
        CRAWL_URL_EXTRACTION_PROMPT.format(message=message),
        max_tokens=200,
        temperature=0
    ).strip()

    instructions = invoke_bedrock(
        CRAWL_INSTRUCTIONS_PROMPT.format(message=message),
        max_tokens=100,
        temperature=0
    ).strip()

    results = crawl_for_papers(url, instructions)

    if not results:
        return {
            **state,
            "paper_candidates": [],
            "response": f"Could not crawl '{url}'. The site may not be accessible or no papers were found."
        }

    candidates = []
    seen_ids = set()

    for result in results:
        result_url = result.get("url", "")
        content = result.get("raw_content", "") or result.get("content", "")

        arxiv_id = extract_arxiv_id(result_url)
        if arxiv_id and arxiv_id not in seen_ids:
            seen_ids.add(arxiv_id)
            title = result.get("title", "Unknown Title")
            candidates.append(PaperCandidate(
                arxiv_id=arxiv_id,
                title=title[:100] if title else "Unknown Title",
                authors=[],
                year=0
            ))

        if content:
            found_ids = re.findall(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)", content)
            for found_id in found_ids:
                if found_id not in seen_ids:
                    seen_ids.add(found_id)
                    candidates.append(PaperCandidate(
                        arxiv_id=found_id,
                        title=f"Paper {found_id}",
                        authors=[],
                        year=0
                    ))

        if len(candidates) >= 10:
            break

    if not candidates:
        return {
            **state,
            "paper_candidates": [],
            "response": f"Crawled {len(results)} pages from '{url}' but found no arXiv papers."
        }

    return {
        **state,
        "paper_candidates": candidates,
        "response": f"Found {len(candidates)} papers by crawling '{url}':"
    }


def map_agent(state: dict) -> dict:
    message = state.get("user_message", "")

    url = invoke_bedrock(
        CRAWL_URL_EXTRACTION_PROMPT.format(message=message),
        max_tokens=200,
        temperature=0
    ).strip()

    urls = map_site(url)

    if not urls:
        return {
            **state,
            "paper_candidates": [],
            "response": f"Could not map '{url}'. The site may not be accessible."
        }

    paper_urls = [u for u in urls if "/abs/" in u or "/pdf/" in u]

    candidates = []
    seen_ids = set()

    for paper_url in paper_urls:
        arxiv_id = extract_arxiv_id(paper_url)
        if arxiv_id and arxiv_id not in seen_ids:
            seen_ids.add(arxiv_id)
            candidates.append(PaperCandidate(
                arxiv_id=arxiv_id,
                title=f"Paper {arxiv_id}",
                authors=[],
                year=0
            ))

        if len(candidates) >= 15:
            break

    if not candidates:
        return {
            **state,
            "paper_candidates": [],
            "mapped_urls": urls[:20],
            "response": f"Mapped {len(urls)} URLs from '{url}' but found no arXiv paper links."
        }

    return {
        **state,
        "paper_candidates": candidates,
        "mapped_urls": urls[:20],
        "response": f"Mapped site and found {len(candidates)} papers available:"
    }
