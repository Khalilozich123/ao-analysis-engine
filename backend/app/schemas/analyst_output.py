"""Structured output schema for the Analyst.

Returned via `with_structured_output`, so the LLM answer is validated into typed fields. Field
names match app/config/rubric.py (CRITERIA) and the keys the Analyst node reads. The per-field
descriptions are sent to the model as guidance, so they restate each criterion's scale.
"""

from pydantic import BaseModel, Field


class AnalystOutput(BaseModel):
    alignement_metier: int = Field(
        ge=0, le=30,
        description="Alignement métier (0-30) : 30 = cœur de métier IT évident ; 15 = IT partiel ; 0 = hors IT.",
    )
    type_engagement: int = Field(
        ge=0, le=20,
        description="Type d'engagement (0-20) : 20 = service/assistance/TMA pur ; 10 = mixte ; 0 = vente licence/matériel.",
    )
    organisme_strategique: int = Field(
        ge=0, le=15,
        description="Organisme stratégique (0-15) : 15 = ministère/CNSS/CDG/banque/office majeur ; 7 = public standard ; 3 = collectivité mineure.",
    )
    domaine_techno: int = Field(
        ge=0, le=15,
        description="Domaine techno prioritaire (0-15) : 15 = data/IA/cloud/cyber explicite ; 7 = digital générique ; 0 = aucune.",
    )
    faisabilite_delai: int = Field(
        ge=0, le=10,
        description="Faisabilité du délai (0-10) : selon le réalisme réel du délai, pas par défaut.",
    )
    conditions_favorables: int = Field(
        ge=0, le=10,
        description="Conditions favorables (0-10) : budget clair, caution raisonnable, etc.",
    )

    domaine_detecte: str = Field(description="Domaine détecté, en quelques mots.")
    type_engagement_detecte: str = Field(description="Type d'engagement détecté, en quelques mots.")
    justification: str = Field(description="1-2 phrases mentionnant le critère décisif.")
    gaps: list[str] = Field(
        default_factory=list,
        description="Informations manquantes sur les critères PRINCIPAUX qui pourraient changer le score. Vide si aucune.",
    )
