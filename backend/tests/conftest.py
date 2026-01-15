import os
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

# Set dummy env vars before any imports that need them
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key-for-testing-only")
os.environ.setdefault("TAVILY_API_KEY", "test-tavily-key")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock supabase.create_client before storage imports it
_mock_supabase = MagicMock()
sys.modules['supabase'] = _mock_supabase
_mock_supabase.create_client = MagicMock(return_value=MagicMock())

import pytest
from models import Paper, Edge, GraphData


@pytest.fixture
def sample_paper():
    return Paper(
        id="2401.12345",
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        summary="The dominant sequence transduction models...",
        published=datetime(2017, 6, 12),
        pdf_url="https://arxiv.org/pdf/2401.12345.pdf",
        key_concepts=["transformers", "attention"],
        references=[]
    )


@pytest.fixture
def sample_paper_2():
    return Paper(
        id="2401.54321",
        title="BERT",
        authors=["Jacob Devlin"],
        summary="We introduce BERT...",
        published=datetime(2018, 10, 11),
        pdf_url="https://arxiv.org/pdf/2401.54321.pdf",
        key_concepts=["transformers", "pre-training"],
        references=[]
    )


@pytest.fixture
def sample_edge(sample_paper, sample_paper_2):
    return Edge(
        id="edge-001",
        source_id=sample_paper.id,
        target_id=sample_paper_2.id
    )


@pytest.fixture
def mock_storage(sample_paper, sample_paper_2, sample_edge):
    mock = MagicMock()
    papers = {sample_paper.id: sample_paper, sample_paper_2.id: sample_paper_2}
    mock.get_paper.side_effect = lambda paper_id: papers.get(paper_id)
    mock.get_all_papers.return_value = list(papers.values())
    mock.get_edges.return_value = [sample_edge]
    mock.get_graph_data.return_value = GraphData(nodes=list(papers.values()), edges=[sample_edge])
    mock.add_paper.side_effect = lambda paper: paper
    mock.add_edge.side_effect = lambda edge: edge
    return mock


@pytest.fixture
def empty_storage():
    mock = MagicMock()
    mock.get_paper.return_value = None
    mock.get_all_papers.return_value = []
    mock.get_edges.return_value = []
    mock.get_graph_data.return_value = GraphData(nodes=[], edges=[])
    mock.add_paper.side_effect = lambda paper: paper
    mock.add_edge.side_effect = lambda edge: edge
    return mock
