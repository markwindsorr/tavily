from typing import List
from tavily import TavilyClient
from agents.base import invoke_bedrock
from agents.utils import extract_arxiv_id
from agents.prompts import EXTRACT_URL_EXTRACTION_PROMPT, SUMMARIZE_CONTENT_PROMPT
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def extract_url_content(urls: List[str]) -> List[dict]:
    try:
        response = tavily.extract(urls=urls)
        return response.get("results", [])
    except Exception as e:
        print(f"Tavily extract error: {e}")
        return []


def extract_agent(state: dict) -> dict:
    message = state.get("user_message", "")

    url = invoke_bedrock(
        EXTRACT_URL_EXTRACTION_PROMPT.format(message=message),
        max_tokens=200,
        temperature=0
    ).strip()

    if not url or not url.startswith("http"):
        return {
            **state,
            "response": "I couldn't find a valid URL in your message. Please provide a URL to extract content from."
        }

    results = extract_url_content([url])

    if not results:
        return {
            **state,
            "response": f"Could not extract content from '{url}'. The page may not be accessible."
        }

    content = results[0].get("raw_content", "") or results[0].get("content", "")

    if not content:
        return {
            **state,
            "response": f"No content could be extracted from '{url}'."
        }

    arxiv_id = extract_arxiv_id(url)

    summary = invoke_bedrock(
        SUMMARIZE_CONTENT_PROMPT.format(content=content[:10000]),
        max_tokens=1000,
        temperature=0.3
    ).strip()

    response_parts = [summary]

    if arxiv_id:
        response_parts.append(f"\n\nThis appears to be an arXiv paper ({arxiv_id}). Would you like me to add it to your collection?")

    return {
        **state,
        "response": "\n".join(response_parts),
        "extracted_url": url,
        "extracted_arxiv_id": arxiv_id
    }
