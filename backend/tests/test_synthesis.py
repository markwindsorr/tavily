
from unittest.mock import patch
from datetime import datetime
from models import Paper, Edge, GraphData


class TestSynthesisAgent:
    def test_builds_graph_and_response(self):
        with patch("agents.synthesis.storage") as mock_storage:
            paper = Paper(
                id="paper1", title="Test Paper", authors=["A"], summary="S",
                published=datetime(2024, 1, 1), pdf_url="url", key_concepts=["c"]
            )
            mock_storage.get_graph_data.return_value = GraphData(
                nodes=[paper], edges=[])

            from agents.synthesis import synthesis_agent
            result = synthesis_agent({"response": "Test response"})

            assert "elements" in result["graph_data"]
            assert "Test response" in result["final_response"]

    def test_empty_graph(self):
        with patch("agents.synthesis.storage") as mock_storage:
            mock_storage.get_graph_data.return_value = GraphData(
                nodes=[], edges=[])

            from agents.synthesis import synthesis_agent
            result = synthesis_agent({})

            assert result["graph_data"] == {"elements": []}


class TestBuildCytoscapeGraph:
    def test_builds_node_elements(self):
        from agents.synthesis import build_cytoscape_graph
        paper = Paper(
            id="2401.12345", title="Test", authors=["A"], summary="S",
            published=datetime(2024, 1, 15), pdf_url="url", key_concepts=["c"]
        )
        result = build_cytoscape_graph(GraphData(nodes=[paper], edges=[]))
        assert len(result["elements"]) == 1
        assert result["elements"][0]["data"]["id"] == "2401.12345"

    def test_builds_edge_elements(self):
        from agents.synthesis import build_cytoscape_graph
        paper1 = Paper(id="p1", title="P1", authors=["A"], summary="S",
                       published=datetime(2024, 1, 1), pdf_url="u", key_concepts=[])
        paper2 = Paper(id="p2", title="P2", authors=["B"], summary="S",
                       published=datetime(2024, 1, 2), pdf_url="u", key_concepts=[])
        edge = Edge(id="e1", source_id="p1", target_id="p2",
                    edge_type="shared_concepts")
        result = build_cytoscape_graph(
            GraphData(nodes=[paper1, paper2], edges=[edge]))
        assert len(result["elements"]) == 3
