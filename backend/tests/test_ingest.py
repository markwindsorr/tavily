from unittest.mock import patch, MagicMock


class TestExtractReferencesFromPdf:
    def test_extracts_references_from_json(self):
        with patch("agents.ingest.download_pdf") as mock_dl, \
                patch("agents.ingest.invoke_bedrock_with_pdf") as mock_bedrock:
            mock_dl.return_value = b"pdf bytes"
            mock_bedrock.return_value = '[{"title": "Test Paper", "arxiv_id": "1234.5678", "author": "Smith"}]'

            from agents.ingest import extract_references_from_pdf
            refs = extract_references_from_pdf("http://example.com/paper.pdf")

            assert len(refs) == 1
            assert refs[0].title == "Test Paper"
            assert refs[0].arxiv_id == "1234.5678"
            assert refs[0].author == "Smith"

    def test_returns_empty_on_invalid_json(self):
        with patch("agents.ingest.download_pdf") as mock_dl, \
                patch("agents.ingest.invoke_bedrock_with_pdf") as mock_bedrock:
            mock_dl.return_value = b"pdf bytes"
            mock_bedrock.return_value = "not valid json"

            from agents.ingest import extract_references_from_pdf
            refs = extract_references_from_pdf("http://example.com/paper.pdf")

            assert refs == []

    def test_limits_to_10_references(self):
        with patch("agents.ingest.download_pdf") as mock_dl, \
                patch("agents.ingest.invoke_bedrock_with_pdf") as mock_bedrock:
            mock_dl.return_value = b"pdf bytes"
            refs_json = [{"title": f"Paper {i}", "arxiv_id": f"1234.{i:04d}", "author": "A"} for i in range(15)]
            import json
            mock_bedrock.return_value = json.dumps(refs_json)

            from agents.ingest import extract_references_from_pdf
            refs = extract_references_from_pdf("http://example.com/paper.pdf")

            assert len(refs) == 10


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

            # Create mock arxiv result with proper author structure
            mock_author = MagicMock()
            mock_author.name = "Vaswani"

            mock_result = MagicMock()
            mock_result.get_short_id.return_value = "1706.03762"
            mock_result.title = "Attention Is All You Need"
            mock_result.authors = [mock_author]
            mock_result.published.year = 2017
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

            mock_author = MagicMock()
            mock_author.name = "Author"

            mock_result = MagicMock()
            mock_result.get_short_id.return_value = "2401.00001"
            mock_result.title = "Paper"
            mock_result.authors = [mock_author]
            mock_result.published.year = 2024
            mock_arxiv.return_value = [mock_result]

            from agents.ingest import search_papers_agent
            result = search_papers_agent({"user_message": "Search ML"})

            assert len(result["paper_candidates"]) > 0
