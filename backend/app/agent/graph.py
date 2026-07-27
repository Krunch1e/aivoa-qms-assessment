"""
LangGraph wiring. Routing is deliberately simple rules-based logic (see
AGENTS.md for why) rather than an LLM classifier — fewer moving parts to
debug under a deadline, and it's easy to explain live in an interview.
"""

from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END

from ..models import Complaint
from . import tools


class AgentState(TypedDict):
    user_message: str
    current_complaint: Optional[Complaint]
    file_bytes: Optional[bytes]
    filename: Optional[str]
    reply: Optional[str]
    result_complaint: Optional[Complaint]
    tool_used: Optional[str]


def route(state: AgentState) -> Literal["extract", "edit", "log"]:
    if state.get("file_bytes"):
        return "extract"
    if state.get("current_complaint") is not None:
        return "edit"
    return "log"


def log_node(state: AgentState) -> AgentState:
    reply, complaint = tools.log_complaint(state["user_message"])
    state["reply"] = reply
    state["result_complaint"] = complaint
    state["tool_used"] = "log_complaint"
    return state


def edit_node(state: AgentState) -> AgentState:
    reply, complaint = tools.edit_complaint(state["user_message"], state["current_complaint"])
    state["reply"] = reply
    state["result_complaint"] = complaint
    state["tool_used"] = "edit_complaint"
    return state


def extract_node(state: AgentState) -> AgentState:
    reply, complaint = tools.extract_document(state["file_bytes"], state["filename"])
    state["reply"] = reply
    state["result_complaint"] = complaint
    state["tool_used"] = "extract_document"
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("log", log_node)
    graph.add_node("edit", edit_node)
    graph.add_node("extract", extract_node)

    graph.set_conditional_entry_point(
        route,
        {"log": "log", "edit": "edit", "extract": "extract"},
    )

    graph.add_edge("log", END)
    graph.add_edge("edit", END)
    graph.add_edge("extract", END)

    return graph.compile()


# compiled once at import time, reused across requests
agent_app = build_graph()
