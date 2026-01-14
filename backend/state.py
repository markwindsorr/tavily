from typing import TypedDict, List, Optional, Literal
from models import Paper, Edge, PaperCandidate

Intent = Literal[
    "add_paper",
    "search_paper",
    "find_related",
    "find_connections",
    "question",
    "extract",
    "crawl",
    "map",
]


class ResearchGraphState(TypedDict, total=False):

    user_message: str
    intent: Intent
    arxiv_id: Optional[str]  # Extracted arXiv ID (if found in message)

    papers_added: List[Paper]
    paper_candidates: List[PaperCandidate]

    citation_edges: List[Edge]
    citation_message: str

    extracted_url: Optional[str]
    extracted_arxiv_id: Optional[str]

    mapped_urls: List[str]

    graph_data: dict
    final_response: str

    response: str
    error: Optional[str]
