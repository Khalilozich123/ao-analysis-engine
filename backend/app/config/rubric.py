"""Scoring rubric — configuration, not hardcoded logic.

The six scoring criteria (subtractive scoring, total 100) and the interest classes. Keeping this
here means the Analyst, the Decision step and the dashboard all read the same definition.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Criterion:
    key: str          # must match the field name on AnalystOutput
    max_points: int
    label: str        # French label for prompts / UI


# Order matters only for display. `key` is the contract shared with AnalystOutput.
CRITERIA: list[Criterion] = [
    Criterion("alignement_metier", 30, "Alignement métier"),
    Criterion("type_engagement", 20, "Type d'engagement"),
    Criterion("organisme_strategique", 15, "Organisme stratégique"),
    Criterion("domaine_techno", 15, "Domaine techno prioritaire"),
    Criterion("faisabilite_delai", 10, "Faisabilité du délai"),
    Criterion("conditions_favorables", 10, "Conditions favorables"),
]

# Derived, so it can never drift from the criteria above.
MAX_TOTAL: int = sum(c.max_points for c in CRITERIA)  # == 100


@dataclass(frozen=True)
class InterestClass:
    min_score: int    # inclusive lower bound
    label: str
    action: str


# Ordered high → low. The Decision step (Phase 3) picks the first class whose min_score is met.
CLASSES: list[InterestClass] = [
    InterestClass(75, "Fort intérêt", "Explorer"),
    InterestClass(50, "À qualifier", "Demander CDC"),
    InterestClass(25, "Faible intérêt", "Surveiller"),
    InterestClass(0, "Non pertinent", "Ignorer"),
]


def classify(score: int) -> InterestClass:
    """Map a 0-100 score to its interest class + recommended action (deterministic)."""
    for cls in CLASSES:
        if score >= cls.min_score:
            return cls
    return CLASSES[-1]
