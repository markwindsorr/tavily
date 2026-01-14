from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

EdgeType = Literal["citation", "shared_concepts", "manual"]

Role = Literal["user", "assistant"]


class Citation(BaseModel):
    title: str
    arxiv_id: Optional[str] = None
    author: Optional[str] = None


class Paper(BaseModel):
    id: str
    title: str
    authors: List[str]
    summary: str
    published: datetime
    pdf_url: str
    key_concepts: List[str] = []
    citations: List[Citation] = []

    @property
    def arxiv_url(self) -> str:
        return f"https://arxiv.org/abs/{self.id}"

    @property
    def year(self) -> int:
        return self.published.year


class Edge(BaseModel):
    id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    evidence: Optional[str] = None
    created_at: Optional[datetime] = None


class ChatMessage(BaseModel):
    role: Role
    content: str
    created_at: Optional[datetime] = None


class GraphData(BaseModel):
    nodes: List[Paper]
    edges: List[Edge]


class ChatRequest(BaseModel):
    message: str


class PaperCandidate(BaseModel):
    arxiv_id: str
    title: str
    authors: List[str]
    year: int
    source_paper_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    graph_updated: bool = False
    papers_added: List[str] = []
    paper_candidates: List[PaperCandidate] = []


class AddPaperRequest(BaseModel):
    arxiv_id: str


class SelectPaperRequest(BaseModel):
    arxiv_id: str
    source_paper_id: Optional[str] = None
