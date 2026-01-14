
from unittest.mock import patch
from datetime import datetime
from models import Paper


class TestFindRelatedAgent:
    def test_finds_related_papers(self):
        with patch("agents.related.invoke_bedrock") as mock_bedrock, \
                patch("agents.related.storage") as mock_storage, \
                patch("agents.related.tavily") as mock_tavily:
            mock_bedrock.return_value = "attention"
            mock_storage.get_all_papers.return_value = []
            mock_tavily.search.return_value = {
                "results": [{"url": "https://arxiv.org/abs/2401.00001", "title": "Related"}]
            }

            from agents.related import find_related_agent
            result = find_related_agent(
                {"user_message": "Find papers about attention"})

            assert len(result["paper_candidates"]) == 1

    def test_filters_existing_papers(self):
        with patch("agents.related.invoke_bedrock") as mock_bedrock, \
                patch("agents.related.storage") as mock_storage, \
                patch("agents.related.tavily") as mock_tavily:
            existing = Paper(
                id="2401.00001", title="Existing", authors=["A"], summary="S",
                published=datetime(2024, 1, 1), pdf_url="url", key_concepts=[]
            )
            mock_bedrock.return_value = "topic"
            mock_storage.get_all_papers.return_value = [existing]
            mock_tavily.search.return_value = {
                "results": [
                    {"url": "https://arxiv.org/abs/2401.00001", "title": "Existing"},
                    {"url": "https://arxiv.org/abs/2401.00002", "title": "New"}
                ]
            }

            from agents.related import find_related_agent
            result = find_related_agent({"user_message": "Find related"})

            arxiv_ids = [c.arxiv_id for c in result["paper_candidates"]]
            assert "2401.00001" not in arxiv_ids
            assert "2401.00002" in arxiv_ids

    def test_no_results(self):
        with patch("agents.related.invoke_bedrock") as mock_bedrock, \
                patch("agents.related.storage") as mock_storage, \
                patch("agents.related.tavily") as mock_tavily:
            mock_bedrock.return_value = "topic"
            mock_storage.get_all_papers.return_value = []
            mock_tavily.search.return_value = {"results": []}

            from agents.related import find_related_agent
            result = find_related_agent({"user_message": "Find related"})

            assert result["paper_candidates"] == []
            assert "No related papers" in result["response"]
