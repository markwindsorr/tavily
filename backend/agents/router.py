from agents.base import invoke_bedrock
from agents.utils import extract_arxiv_id
from agents.prompts import ROUTER_PROMPT


def router_agent(state: dict) -> dict:
    message = state.get("user_message", "")
    if not message:
        return {**state, "intent": "question", "error": "No message provided"}

    # If we do find an arxiv ID, we assume the user wants to add that paper
    arxiv_id = extract_arxiv_id(message)
    if arxiv_id:
        return {**state, "intent": "add_paper", "arxiv_id": arxiv_id}

    # Use LLM for other intent classification
    response = invoke_bedrock(
        ROUTER_PROMPT.format(message=message),
        max_tokens=20,
        temperature=0
    )

    intent = response.strip().lower()

    if "add_paper" in intent:
        intent = "add_paper"
    elif "search_paper" in intent:
        intent = "search_paper"
    elif "find_related" in intent:
        intent = "find_related"
    elif "find_connections" in intent:
        intent = "find_connections"
    elif "extract" in intent:
        intent = "extract"
    elif "crawl" in intent:
        intent = "crawl"
    elif "map" in intent:
        intent = "map"
    else:
        intent = "question"

    return {**state, "intent": intent}
