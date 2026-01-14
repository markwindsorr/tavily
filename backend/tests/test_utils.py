from agents.utils import extract_arxiv_id, parse_citations


class TestExtractArxivId:
    def test_extract_from_abs_url(self):
        assert extract_arxiv_id(
            "https://arxiv.org/abs/2401.12345") == "2401.12345"

    def test_extract_from_pdf_url(self):
        assert extract_arxiv_id(
            "https://arxiv.org/pdf/2401.12345.pdf") == "2401.12345"

    def test_extract_with_version(self):
        assert extract_arxiv_id(
            "https://arxiv.org/abs/2401.12345v2") == "2401.12345v2"

    def test_extract_from_plain_text(self):
        assert extract_arxiv_id("Check out paper 2401.12345") == "2401.12345"

    def test_no_arxiv_id_returns_none(self):
        assert extract_arxiv_id("regular text") is None


class TestParseCitations:
    def test_parse_single_citation(self):
        text = "TITLE: Attention Is All You Need | ARXIV: 1706.03762 | AUTHOR: Vaswani"
        result = parse_citations(text)
        assert len(result) == 1
        assert result[0]["title"] == "Attention Is All You Need"
        assert result[0]["arxiv_id"] == "1706.03762"

    def test_parse_citation_without_arxiv(self):
        text = "TITLE: Some Paper | AUTHOR: Author"
        result = parse_citations(text)
        assert len(result) == 1
        assert "arxiv_id" not in result[0]

    def test_parse_empty_text(self):
        assert parse_citations("") == []
