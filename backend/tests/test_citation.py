from unittest.mock import patch, MagicMock
from datetime import datetime
from models import Paper


class TestCitationAgent:
    def test_needs_at_least_two_papers(self):
        with patch("agents.citation.storage") as mock_storage:
            mock_storage.get_all_papers.return_value = [MagicMock()]
            from agents.citation import citation_agent
            result = citation_agent({"papers_added": []})
            assert result["citation_edges"] == []
            assert "at least 2 papers" in result["citation_message"]

    def test_finds_shared_concepts(self):
        with patch("agents.citation.storage") as mock_storage:
            paper1 = Paper(
                id="paper1", title="Paper One", authors=["A"], summary="S",
                published=datetime(2024, 1, 1), pdf_url="url",
                key_concepts=["transformers", "nlp"]
            )
            paper2 = Paper(
                id="paper2", title="Paper Two", authors=["B"], summary="S",
                published=datetime(2024, 1, 2), pdf_url="url",
                key_concepts=["transformers", "vision"]
            )
            mock_storage.get_all_papers.return_value = [paper1, paper2]
            mock_storage.get_edges.return_value = []
            mock_storage.add_edge.side_effect = lambda e: e

            from agents.citation import citation_agent
            result = citation_agent({"papers_added": [paper1]})
            assert len(result["citation_edges"]) == 1

    def test_no_shared_concepts(self):
        with patch("agents.citation.storage") as mock_storage:
            paper1 = Paper(
                id="paper1", title="Paper One", authors=["A"], summary="S",
                published=datetime(2024, 1, 1), pdf_url="url",
                key_concepts=["quantum"]
            )
            paper2 = Paper(
                id="paper2", title="Paper Two", authors=["B"], summary="S",
                published=datetime(2024, 1, 2), pdf_url="url",
                key_concepts=["biology"]
            )
            mock_storage.get_all_papers.return_value = [paper1, paper2]
            mock_storage.get_edges.return_value = []

            from agents.citation import citation_agent
            result = citation_agent({"papers_added": [paper1]})
            assert result["citation_edges"] == []
