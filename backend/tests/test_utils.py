from agents.utils import extract_arxiv_id


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
