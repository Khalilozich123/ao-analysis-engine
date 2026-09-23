"""Score aggregation."""

from app.config.rubric import CRITERIA
from app.schemas.analyst_output import AnalystOutput


def aggregate_score(output: AnalystOutput) -> int:
    """Total 0-100 = the sum of the six criterion sub-scores (stays in sync with CRITERIA)."""
    return sum(getattr(output, c.key) for c in CRITERIA)
