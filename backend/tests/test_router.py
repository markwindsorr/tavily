
from unittest.mock import patch


class TestRouterAgent:
    def test_empty_message_defaults_to_question(self):
        with patch("agents.router.invoke_bedrock"):
            from agents.router import router_agent
            result = router_agent({"user_message": ""})
            assert result["intent"] == "question"
            assert result["error"] == "No message provided"

    def test_message_with_arxiv_id(self):
        with patch("agents.router.invoke_bedrock"):
            from agents.router import router_agent
            result = router_agent({"user_message": "Add paper 2401.12345"})
            assert result["intent"] == "add_paper"
            assert result["arxiv_id"] == "2401.12345"

    def test_llm_intent_classification(self):
        with patch("agents.router.invoke_bedrock") as mock:
            mock.return_value = "search_paper"
            from agents.router import router_agent
            result = router_agent({"user_message": "Find papers about ML"})
            assert result["intent"] == "search_paper"

    def test_unknown_intent_defaults_to_question(self):
        with patch("agents.router.invoke_bedrock") as mock:
            mock.return_value = "unknown_xyz"
            from agents.router import router_agent
            result = router_agent({"user_message": "Something"})
            assert result["intent"] == "question"
