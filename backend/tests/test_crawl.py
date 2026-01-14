from unittest.mock import patch


class TestCrawlAgent:
    def test_crawls_and_finds_papers(self):
        with patch("agents.crawl.invoke_bedrock") as mock_bedrock, \
                patch("agents.crawl.tavily") as mock_tavily:
            mock_bedrock.side_effect = ["https://example.com", "instructions"]
            mock_tavily.crawl.return_value = {
                "results": [{"url": "https://arxiv.org/abs/2401.00001", "title": "Paper", "raw_content": ""}]
            }

            from agents.crawl import crawl_agent
            result = crawl_agent({"user_message": "Crawl site"})

            assert len(result["paper_candidates"]) == 1
            assert result["paper_candidates"][0].arxiv_id == "2401.00001"

    def test_no_results(self):
        with patch("agents.crawl.invoke_bedrock") as mock_bedrock, \
                patch("agents.crawl.tavily") as mock_tavily:
            mock_bedrock.side_effect = ["https://example.com", "instructions"]
            mock_tavily.crawl.return_value = {"results": []}

            from agents.crawl import crawl_agent
            result = crawl_agent({"user_message": "Crawl site"})

            assert result["paper_candidates"] == []


class TestMapAgent:
    def test_maps_and_finds_papers(self):
        with patch("agents.crawl.invoke_bedrock") as mock_bedrock, \
                patch("agents.crawl.tavily") as mock_tavily:
            mock_bedrock.return_value = "https://arxiv.org"
            mock_tavily.map.return_value = {
                "urls": ["https://arxiv.org/abs/2401.00001"]}

            from agents.crawl import map_agent
            result = map_agent({"user_message": "Map site"})

            assert len(result["paper_candidates"]) == 1

    def test_no_paper_urls(self):
        with patch("agents.crawl.invoke_bedrock") as mock_bedrock, \
                patch("agents.crawl.tavily") as mock_tavily:
            mock_bedrock.return_value = "https://example.com"
            mock_tavily.map.return_value = {
                "urls": ["https://example.com/about"]}

            from agents.crawl import map_agent
            result = map_agent({"user_message": "Map site"})

            assert result["paper_candidates"] == []
