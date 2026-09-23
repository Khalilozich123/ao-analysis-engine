"""OppState — the shared state passed between graph nodes.

Replaces the tiny PassthroughState from Phase 1. Declared `total=False` so nodes can fill it
incrementally (each node returns only the keys it sets). Phase 2 uses the Analyst keys; the
Researcher/Decision keys are populated in Phase 3.
"""

from typing import Any, TypedDict


class OppState(TypedDict, total=False):
    # --- inputs ---
    opportunity: dict[str, Any]   # one normalized Opportunity (as a dict)
    profile: dict[str, Any]       # the organization Profile (as a dict)
    config: dict[str, Any]        # run options (e.g. max re-research loops) — Phase 3

    # --- research (Phase 3) ---
    research_notes: str           # context gathered by the Researcher
    sources: list[str]            # URLs / references collected

    # --- analysis (Phase 2, set by the Analyst) ---
    subscores: dict[str, int]     # per-criterion scores, keyed by Criterion.key
    score: int                    # aggregate 0-100
    gaps: list[str]               # missing info on principal criteria
    domaine_detecte: str          # detected domain
    type_engagement_detecte: str  # detected engagement type
    analyst_justification: str    # the Analyst's own 1-2 sentence note

    # --- decision (Phase 3) ---
    loop_count: int               # Researcher passes performed (termination guard)
    verdict: str                  # interest class label (Fort intérêt / À qualifier / ...)
    action: str                   # recommended action (Explorer / Demander CDC / ...)
    rationale: str                # final justification stored with the result
