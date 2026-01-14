from unittest.mock import patch
from datetime import datetime
from models import Paper


class TestAnswerAgent:
    def test_generates_answer(self):
        with patch("agents.answer.storage") as mock_storage, \
                patch("agents.answer.tavily") as mock_tavily, \
                patch("agents.answer.invoke_bedrock") as mock_bedrock:
            paper = Paper(
                id="paper1", title="Test", authors=["A"], summary="About transformers",
                published=datetime(2024, 1, 1), pdf_url="url",
                key_concepts=["transformers"]
            )
            mock_storage.get_all_papers.return_value = [paper]
            mock_storage.get_edges.return_value = []
            mock_tavily.search.return_value = {"results": []}
            mock_bedrock.return_value = "Answer about transformers."

            from agents.answer import answer_agent
            result = answer_agent({"user_message": "What are transformers?"})
            assert result["response"] == "Answer about transformers."

    def test_includes_search_results(self):
        with patch("agents.answer.storage") as mock_storage, \
                patch("agents.answer.tavily") as mock_tavily, \
                patch("agents.answer.invoke_bedrock") as mock_bedrock:
            mock_storage.get_all_papers.return_value = []
            mock_storage.get_edges.return_value = []
            mock_tavily.search.return_value = {
                "results": [{"title": "Result", "content": "Info"}]
            }
            mock_bedrock.return_value = "Answer"

            from agents.answer import answer_agent
            result = answer_agent({"user_message": "Question"})
            assert result["response"] == "Answer"


class TestBuildContext:
    def test_empty_papers(self):
        from agents.answer import build_papers_context
        assert "No papers" in build_papers_context([])

    def test_empty_edges(self):
        from agents.answer import build_edges_context
        assert "No connections" in build_edges_context([], [])
