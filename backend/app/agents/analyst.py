"""Analyst node.

Sends one opportunity (+ research notes + profile) to the LLM using the ESN scoring rubric,
and returns validated sub-scores via structured output. It is the single authority on the
numbers; it does NOT decide the final verdict (that is the Decision step in Phase 3).
"""

from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from app.analysis.keyword_scorer import keyword_score
from app.analysis.scoring import aggregate_score
from app.config.rubric import CRITERIA
from app.config.settings import settings
from app.llm import get_llm
from app.schemas.analyst_output import AnalystOutput

_SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "analyst_system_v1.fr.md"


def _load_system_prompt() -> str:
    """Read the French scoring instructions (prompts are source code)."""
    return _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def _format_human_message(opportunity: dict, profile: dict, research_notes: str) -> str:
    """Lay out the opportunity, the profile and the research notes for the model."""
    opp_lines = "\n".join(f"- {k}: {v}" for k, v in opportunity.items() if v not in (None, ""))
    return (
        "PROFIL DE L'ENTREPRISE (pour qui on score) :\n"
        f"- cœur de métier : {', '.join(profile.get('core_business', []))}\n"
        f"- à exclure : {', '.join(profile.get('exclusions', []))}\n"
        f"- organismes stratégiques : {', '.join(profile.get('strategic_organisms', []))}\n\n"
        "OPPORTUNITÉ À ANALYSER :\n"
        f"{opp_lines}\n\n"
        "NOTES DE RECHERCHE (contexte complémentaire) :\n"
        f"{research_notes or '(aucune)'}"
    )


def analyze(opportunity: dict, profile: dict, research_notes: str = "") -> AnalystOutput:
    """Run the Analyst once and return the validated structured output."""
    # with_structured_output binds the Pydantic schema so the model MUST return those fields,
    # parsed and validated — no free-text score leakage.
    model = get_llm().with_structured_output(AnalystOutput)
    messages = [
        SystemMessage(_load_system_prompt()),
        HumanMessage(_format_human_message(opportunity, profile, research_notes)),
    ]
    return model.invoke(messages)


def analyst_node(state: dict) -> dict:
    """Graph node: score the opportunity via the configured scorer (keyword or LLM)."""
    if settings.SCORER.lower() == "keyword":
        result = keyword_score(state["opportunity"], state.get("profile", {}))
    else:
        result = analyze(
            opportunity=state["opportunity"],
            profile=state.get("profile", {}),
            research_notes=state.get("research_notes", ""),
        )
    subscores = {c.key: getattr(result, c.key) for c in CRITERIA}
    return {
        "subscores": subscores,
        "score": aggregate_score(result),
        "gaps": result.gaps,
        "domaine_detecte": result.domaine_detecte,
        "type_engagement_detecte": result.type_engagement_detecte,
        "analyst_justification": result.justification,
    }
