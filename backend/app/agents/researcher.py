"""Researcher node.

Gathers external context with a LangChain web-search tool (DuckDuckGo) and condenses it into
`research_notes` + `sources`. On a re-research pass it targets the `gaps` the Analyst reported.
Designed to degrade gracefully: if search is unavailable, the graph still proceeds.
"""

import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import settings
from app.llm import get_llm, message_text

log = logging.getLogger("graph")
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "researcher_v1.fr.md"


def _web_search(query: str, max_results: int) -> list[dict]:
    """Return a list of {title, snippet, link}; empty on any failure (non-fatal)."""
    try:
        from langchain_community.tools import DuckDuckGoSearchResults

        tool = DuckDuckGoSearchResults(output_format="list")
        res = tool.invoke(query)
        if isinstance(res, list):
            return res[:max_results]
        return [{"title": "", "snippet": str(res), "link": ""}]
    except Exception as exc:  # rate limit, dependency, network…
        log.warning("[researcher] web search unavailable: %s", exc)
        return []


def _build_query(opp: dict, gaps: list[str]) -> str:
    base = " ".join(str(opp.get(k, "")) for k in ("title", "client", "city")).strip()
    if gaps:
        base = f"{base} {' '.join(gaps[:2])}"
    return base


def _summarize(opp: dict, gaps: list[str], snippets: str) -> str:
    human = (
        f"OPPORTUNITÉ : {opp.get('title')} — client : {opp.get('client')} ({opp.get('city')})\n"
        f"LACUNES À COMBLER : {', '.join(gaps) or 'aucune'}\n\n"
        f"RÉSULTATS DE RECHERCHE :\n{snippets}"
    )
    resp = get_llm().invoke([
        SystemMessage(_PROMPT_PATH.read_text(encoding="utf-8")),
        HumanMessage(human),
    ])
    return message_text(resp)


def researcher_node(state: dict) -> dict:
    # Only the LLM scorer consumes research notes; keyword mode skips search entirely (no cost).
    if settings.SCORER.lower() != "llm":
        return {"loop_count": state.get("loop_count", 0) + 1}

    opp = state["opportunity"]
    gaps = state.get("gaps", [])
    loop = state.get("loop_count", 0) + 1
    query = _build_query(opp, gaps)
    log.info("[researcher] pass %d — query: %s", loop, query)

    results = _web_search(query, settings.SEARCH_MAX_RESULTS)
    sources = [r.get("link") for r in results if r.get("link")]
    snippets = "\n".join(f"- {r.get('title', '')}: {r.get('snippet', '')}" for r in results)

    if snippets:
        notes = _summarize(opp, gaps, snippets)
    else:
        notes = "Aucune information externe exploitable ; analyse sur la base de l'avis seul."

    # Accumulate notes and de-duplicate sources across loops.
    prev = state.get("research_notes", "")
    combined = f"{prev}\n\n[Passe {loop}] {notes}".strip() if prev else notes
    merged_sources = list(dict.fromkeys([*state.get("sources", []), *sources]))

    log.info("[researcher] %d source(s) collected", len(merged_sources))
    return {"research_notes": combined, "sources": merged_sources, "loop_count": loop}
