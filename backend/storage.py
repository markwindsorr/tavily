from typing import List, Optional
from datetime import datetime
from supabase import create_client, Client
from models import Paper, Edge, GraphData, Citation, ChatMessage, Role
from config import SUPABASE_URL, SUPABASE_KEY


class Storage:

    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def add_paper(self, paper: Paper) -> Paper:
        data = {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "summary": paper.summary,
            "published": paper.published.isoformat(),
            "pdf_url": paper.pdf_url,
            "key_concepts": paper.key_concepts,
            "citations": [c.model_dump() for c in paper.citations],
        }
        self.client.table("papers").upsert(data).execute()
        return paper

    def get_paper(self, paper_id: str) -> Optional[Paper]:
        result = self.client.table("papers").select("*").eq("id", paper_id).execute()
        if result.data:
            return self._row_to_paper(result.data[0])
        return None

    def get_all_papers(self) -> List[Paper]:
        result = self.client.table("papers").select("*").order("created_at", desc=True).execute()
        return [self._row_to_paper(row) for row in result.data]

    def add_edge(self, edge: Edge) -> Edge:
        data = {
            "id": edge.id,
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "edge_type": edge.edge_type,
            "evidence": edge.evidence,
        }
        self.client.table("edges").upsert(data).execute()
        return edge

    def get_edges(self) -> List[Edge]:
        result = self.client.table("edges").select("*").execute()
        return [self._row_to_edge(row) for row in result.data]

    def get_graph_data(self) -> GraphData:
        return GraphData(nodes=self.get_all_papers(), edges=self.get_edges())

    def delete_edge(self, edge_id: str):
        self.client.table("edges").delete().eq("id", edge_id).execute()

    def delete_paper(self, paper_id: str):
        self.client.table("edges").delete().eq("source_id", paper_id).execute()
        self.client.table("edges").delete().eq("target_id", paper_id).execute()
        self.client.table("papers").delete().eq("id", paper_id).execute()

    def add_chat_message(self, role: Role, content: str):
        self.client.table("chat_history").insert({"role": role, "content": content}).execute()

    def get_chat_history(self) -> List[ChatMessage]:
        result = self.client.table("chat_history").select("*").order("created_at").execute()
        return [self._row_to_chat_message(row) for row in result.data]

    def _row_to_chat_message(self, row: dict) -> ChatMessage:
        return ChatMessage(
            role=row["role"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")) if row.get("created_at") else None,
        )

    def clear_chat_history(self):
        self.client.table("chat_history").delete().not_.is_("id", "null").execute()

    def _row_to_paper(self, row: dict) -> Paper:
        raw_citations = row.get("citations") or []
        citations = [Citation(**c) for c in raw_citations if isinstance(c, dict)]
        return Paper(
            id=row["id"],
            title=row["title"],
            authors=row["authors"],
            summary=row["summary"],
            published=datetime.fromisoformat(row["published"].replace("Z", "+00:00")),
            pdf_url=row["pdf_url"],
            key_concepts=row.get("key_concepts", []),
            citations=citations,
        )

    def _row_to_edge(self, row: dict) -> Edge:
        return Edge(
            id=row["id"],
            source_id=row["source_id"],
            target_id=row["target_id"],
            edge_type=row["edge_type"],
            evidence=row.get("evidence"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")) if row.get("created_at") else None,
        )


storage = Storage()
