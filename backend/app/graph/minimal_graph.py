"""Minimal one-node LangGraph graph.

A single pass-through node over a typed state. This is the structural seed of the full
Supervisor → Researcher → Analyst → Decision graph built in Phase 3.
"""

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph


class PassthroughState(TypedDict):
    opportunity: dict[str, Any]
    message: str


def greet_node(state: PassthroughState) -> dict:
    # A node reads the state and returns only the keys it changes; LangGraph merges them back in.
    opp = state["opportunity"]
    return {"message": f"Opportunité '{opp['title']}' reçue par le graphe."}


def build_graph():
    builder = StateGraph(PassthroughState)
    builder.add_node("greet", greet_node)
    builder.add_edge(START, "greet")
    builder.add_edge("greet", END)
    return builder.compile()
