from unittest.mock import MagicMock


class TestRouteByIntent:
    def test_routes_correctly(self):
        from graph import route_by_intent

        assert route_by_intent({"intent": "add_paper"}) == "ingest"
        assert route_by_intent({"intent": "search_paper"}) == "search"
        assert route_by_intent({"intent": "find_related"}) == "related"
        assert route_by_intent({"intent": "find_connections"}) == "citations"
        assert route_by_intent({"intent": "extract"}) == "extract"
        assert route_by_intent({"intent": "crawl"}) == "crawl"
        assert route_by_intent({"intent": "map"}) == "map"
        assert route_by_intent({"intent": "question"}) == "answer"
        assert route_by_intent({"intent": "unknown"}) == "answer"


class TestShouldFindCitations:
    def test_with_papers(self):
        from graph import should_find_citations
        assert should_find_citations(
            {"papers_added": [MagicMock()]}) == "citations"

    def test_without_papers(self):
        from graph import should_find_citations
        assert should_find_citations({"papers_added": []}) == "synthesis"
        assert should_find_citations({}) == "synthesis"


class TestCreateWorkflow:
    def test_creates_workflow(self):
        from graph import create_workflow
        workflow = create_workflow()
        assert workflow is not None
        # create_workflow returns StateGraph, compile() gives the runnable app
        compiled = workflow.compile()
        assert hasattr(compiled, "invoke")
