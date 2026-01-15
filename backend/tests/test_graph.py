from unittest.mock import MagicMock


class TestRouteByIntent:
    def test_routes_correctly(self):
        from graph import route_by_intent

        assert route_by_intent({"intent": "add_paper"}) == "ingest"
        assert route_by_intent({"intent": "search_paper"}) == "search"
        assert route_by_intent({"intent": "find_related"}) == "related"
        assert route_by_intent({"intent": "find_connections"}) == "connections"
        assert route_by_intent({"intent": "extract"}) == "extract"
        assert route_by_intent({"intent": "crawl"}) == "crawl"
        assert route_by_intent({"intent": "map"}) == "map"
        assert route_by_intent({"intent": "question"}) == "answer"
        assert route_by_intent({"intent": "unknown"}) == "answer"


class TestShouldFindConnections:
    def test_with_papers(self):
        from graph import should_find_connections
        assert should_find_connections(
            {"papers_added": [MagicMock()]}) == "connections"

    def test_without_papers(self):
        from graph import should_find_connections
        assert should_find_connections({"papers_added": []}) == "synthesis"
        assert should_find_connections({}) == "synthesis"


class TestCreateWorkflow:
    def test_creates_workflow(self):
        from graph import create_workflow
        workflow = create_workflow()
        assert workflow is not None
        # create_workflow returns StateGraph, compile() gives the runnable app
        compiled = workflow.compile()
        assert hasattr(compiled, "invoke")
