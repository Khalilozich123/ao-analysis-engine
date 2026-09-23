"""Supervisor node.

Entry point of the graph. Initializes the run and dispatches to the crew. The "are we done?"
decision lives in the conditional edge after the Analyst (see opportunity_graph.should_continue),
which is the supervisor's completion logic.
"""

import logging

log = logging.getLogger("graph")


def supervisor_node(state: dict) -> dict:
    opp = state.get("opportunity", {})
    log.info("[supervisor] start — opportunity %s : %s", opp.get("id"), opp.get("title"))
    # Make sure the loop counter exists before the first Researcher pass.
    return {"loop_count": state.get("loop_count", 0)}
