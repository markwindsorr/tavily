
from unittest.mock import patch, MagicMock


class TestIngestAgent:
    def test_ingest_with_arxiv_id(self):
        with patch("agents.ingest.storage") as mock_storage, \
                patch("agents.ingest.fetch_paper_from_arxiv") as mock_fetch:
            mock_storage.get_paper.return_value = None
            mock_paper = MagicMock(
                id="2401.12345", title="Test", authors=["Author"])
            mock_fetch.return_value = mock_paper

            from agents.ingest import ingest_agent
            result = ingest_agent(
                {"user_message": "Add", "arxiv_id": "2401.12345"})

            assert len(result["papers_added"]) == 1
            mock_storage.add_paper.assert_called_once()

    def test_ingest_existing_paper(self):
        with patch("agents.ingest.storage") as mock_storage:
            existing = MagicMock(id="2401.12345", title="Existing")
            mock_storage.get_paper.return_value = existing

            from agents.ingest import ingest_agent
            result = ingest_agent(
                {"user_message": "Add", "arxiv_id": "2401.12345"})

            assert "already in your collection" in result["response"]

    def test_ingest_search_when_no_id(self):
        with patch("agents.ingest.invoke_bedrock") as mock_bedrock, \
                patch("agents.ingest.search_arxiv_by_name") as mock_search, \
                patch("agents.ingest.extract_arxiv_id") as mock_extract:
            mock_extract.return_value = None
            mock_bedrock.return_value = "attention paper"
            mock_result = MagicMock()
            mock_result.get_short_id.return_value = "1706.03762"
            mock_result.title = "Attention"
            mock_result.authors = [MagicMock(name="A")]
            mock_result.published = MagicMock(year=2017)
            mock_search.return_value = [mock_result]

            from agents.ingest import ingest_agent
            result = ingest_agent(
                {"user_message": "Add attention paper", "arxiv_id": None})

            assert len(result["paper_candidates"]) > 0


class TestSearchPapersAgent:
    def test_search_returns_candidates(self):
        with patch("agents.ingest.invoke_bedrock") as mock_bedrock, \
                patch("agents.ingest.tavily") as mock_tavily, \
                patch("agents.ingest.search_arxiv_by_name") as mock_arxiv:
            mock_bedrock.return_value = "ML"
            mock_tavily.search.return_value = {
                "results": [{"url": "https://arxiv.org/abs/2401.00001", "title": "Paper"}]
            }
            mock_result = MagicMock()
            mock_result.get_short_id.return_value = "2401.00001"
            mock_result.title = "Paper"
            mock_result.authors = [MagicMock(name="A")]
            mock_result.published = MagicMock(year=2024)
            mock_arxiv.return_value = [mock_result]

            from agents.ingest import search_papers_agent
            result = search_papers_agent({"user_message": "Search ML"})

            assert len(result["paper_candidates"]) > 0
