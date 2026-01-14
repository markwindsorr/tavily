import arxiv
import re
import time
import requests
from typing import List, Optional


def extract_arxiv_id(text: str) -> Optional[str]:
    match = re.search(r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+(?:v\d+)?)", text)
    if match:
        return match.group(1)
    match = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", text)
    if match:
        return match.group(1)
    return None


def search_arxiv_by_name(query: str, max_results: int = 5, max_retries: int = 3) -> List:
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    client = arxiv.Client(
        page_size=max_results,
        delay_seconds=3.0,
        num_retries=max_retries
    )

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(5 * attempt)
            return list(client.results(search))
        except Exception as e:
            error_str = str(e)
            if ("429" in error_str or "rate" in error_str.lower()) and attempt < max_retries - 1:
                continue
            raise

    return []


def download_pdf(pdf_url: str) -> bytes:
    response = requests.get(pdf_url, timeout=30)
    response.raise_for_status()
    return response.content


def parse_citations(citation_text: str) -> List[dict]:
    citations = []
    for line in citation_text.strip().split("\n"):
        if not line.strip() or not line.startswith("TITLE:"):
            continue

        parts = {}
        for part in line.split("|"):
            part = part.strip()
            if part.startswith("TITLE:"):
                parts["title"] = part[6:].strip()
            elif part.startswith("ARXIV:"):
                arxiv_val = part[6:].strip().lower()
                if arxiv_val and arxiv_val not in ("none", "n/a"):
                    arxiv_id = extract_arxiv_id(arxiv_val)
                    if arxiv_id:
                        parts["arxiv_id"] = arxiv_id
            elif part.startswith("AUTHOR:"):
                parts["author"] = part[7:].strip()

        if parts.get("title"):
            citations.append(parts)

    return citations
