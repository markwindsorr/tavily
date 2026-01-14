from unittest.mock import patch


class TestExtractAgent:
    def test_extracts_and_summarizes(self):
        with patch("agents.extract.invoke_bedrock") as mock_bedrock, \
                patch("agents.extract.tavily") as mock_tavily:
            mock_bedrock.side_effect = [
                "https://example.com", "Summary of content."]
            mock_tavily.extract.return_value = {
                "results": [{"raw_content": "Page content"}]}

            from agents.extract import extract_agent
            result = extract_agent(
                {"user_message": "Extract https://example.com"})

            assert result["extracted_url"] == "https://example.com"
            assert "Summary" in result["response"]

    def test_no_valid_url(self):
        with patch("agents.extract.invoke_bedrock") as mock_bedrock:
            mock_bedrock.return_value = "no url"

            from agents.extract import extract_agent
            result = extract_agent({"user_message": "Extract content"})

            assert "couldn't find a valid URL" in result["response"]

    def test_detects_arxiv(self):
        with patch("agents.extract.invoke_bedrock") as mock_bedrock, \
                patch("agents.extract.tavily") as mock_tavily:
            mock_bedrock.side_effect = [
                "https://arxiv.org/abs/2401.12345", "Summary."]
            mock_tavily.extract.return_value = {
                "results": [{"raw_content": "content"}]}

            from agents.extract import extract_agent
            result = extract_agent({"user_message": "Extract arxiv link"})

            assert result["extracted_arxiv_id"] == "2401.12345"
