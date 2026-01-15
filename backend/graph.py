from langgraph.graph import StateGraph, END
from state import ResearchGraphState
from agents import router_agent, ingest_agent, connection_agent, answer_agent, synthesis_agent
from agents.ingest import search_papers_agent
from agents.related import find_related_agent
from agents.extract import extract_agent
from agents.crawl import crawl_agent, map_agent


def route_by_intent(state: ResearchGraphState) -> str:
    intent = state.get("intent", "question")

    if intent == "add_paper":
        return "ingest"
    elif intent == "search_paper":
        return "search"
    elif intent == "find_related":
        return "related"
    elif intent == "find_connections":
        return "connections"
    elif intent == "extract":
        return "extract"
    elif intent == "crawl":
        return "crawl"
    elif intent == "map":
        return "map"
    else:
        return "answer"


def should_find_connections(state: ResearchGraphState) -> str:
    papers_added = state.get("papers_added", [])
    if papers_added:
        return "connections"
    else:
        return "synthesis"


def create_workflow() -> StateGraph:

    workflow = StateGraph(ResearchGraphState)

    workflow.add_node("router", router_agent)
    workflow.add_node("ingest", ingest_agent)
    workflow.add_node("search", search_papers_agent)
    workflow.add_node("related", find_related_agent)
    workflow.add_node("connections", connection_agent)
    workflow.add_node("answer", answer_agent)
    workflow.add_node("extract", extract_agent)
    workflow.add_node("crawl", crawl_agent)
    workflow.add_node("map", map_agent)
    workflow.add_node("synthesis", synthesis_agent)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "ingest": "ingest",
            "search": "search",
            "related": "related",
            "connections": "connections",
            "answer": "answer",
            "extract": "extract",
            "crawl": "crawl",
            "map": "map",
        }
    )

    workflow.add_conditional_edges(
        "ingest",
        should_find_connections,
        {
            "connections": "connections",
            "synthesis": "synthesis",
        }
    )

    workflow.add_edge("search", "synthesis")
    workflow.add_edge("related", "synthesis")
    workflow.add_edge("connections", "synthesis")
    workflow.add_edge("answer", "synthesis")
    workflow.add_edge("extract", "synthesis")
    workflow.add_edge("crawl", "synthesis")
    workflow.add_edge("map", "synthesis")

    workflow.add_edge("synthesis", END)

    return workflow


workflow = create_workflow()
app = workflow.compile()


def run_pipeline(user_message: str) -> dict:

    initial_state: ResearchGraphState = {
        "user_message": user_message,
        "papers_added": [],
        "connection_edges": [],
    }
    result = app.invoke(initial_state)

    return result
