"""Decision node.

Deterministic: maps the Analyst's score to an interest class + action (via the rubric config)
and composes the final rationale, citing the gathered sources and noting any remaining gaps.
It never re-scores — that keeps the verdict reproducible.
"""

import logging

from app.config.rubric import MAX_TOTAL, classify

log = logging.getLogger("graph")


def decision_node(state: dict) -> dict:
    score = state.get("score", 0)
    cls = classify(score)
    gaps = state.get("gaps", [])
    sources = state.get("sources", [])
    justification = state.get("analyst_justification", "")

    parts = [f"Score {score}/{MAX_TOTAL} → {cls.label}.", justification]
    if gaps:
        parts.append("Incertitudes restantes : " + " ; ".join(gaps) + ".")
    if sources:
        parts.append("Sources : " + ", ".join(sources[:5]) + ".")
    rationale = " ".join(p for p in parts if p)

    log.info("[decision] %s (score=%d) → action: %s", cls.label, score, cls.action)
    return {"verdict": cls.label, "action": cls.action, "rationale": rationale}
