"""The full opportunity-analysis graph.

    START → supervisor → researcher → analyst → [should_continue?]
                              ↑__________________________| "researcher" (gaps remain, budget left)
                                                          | "decision"
                                                        decision → END

The conditional edge `should_continue` is what makes this a graph rather than a pipeline: it can
send control BACK to the Researcher. `MAX_LOOPS` bounds that so the graph always terminates.
"""

from langgraph.graph import END, START, StateGraph

from app.agents.analyst import analyst_node
from app.agents.decision import decision_node
from app.agents.researcher import researcher_node
from app.agents.supervisor import supervisor_node
from app.config.settings import settings
from app.graph.state import OppState


def should_continue(state: OppState) -> str:
    """Supervisor's completion decision: re-research if gaps remain and budget allows."""
    gaps = state.get("gaps", [])
    loop_count = state.get("loop_count", 0)
    if gaps and loop_count < settings.MAX_LOOPS:
        return "researcher"
    return "decision"


def build_graph():
    builder = StateGraph(OppState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("decision", decision_node)

    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "researcher")
    builder.add_edge("researcher", "analyst")
    builder.add_conditional_edges(
        "analyst",
        should_continue,
        {"researcher": "researcher", "decision": "decision"},
    )
    builder.add_edge("decision", END)
    return builder.compile()
