"""Organization profile.

Describes who opportunities are scored for (a fictional ESN — IT-services company). The Analyst compares each
opportunity against this profile to judge business fit.
"""

from pydantic import BaseModel, Field


class Profile(BaseModel):
    name: str
    org_type: str = "ESN"
    core_business: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    strategic_organisms: list[str] = Field(default_factory=list)
    notes: str | None = None
