"""Phase 2 acceptance harness.

Run inside the container:
    docker compose exec backend python -m app.scripts.run_phase2

Proves: given an opportunity + hand-written research notes, the Analyst returns six numeric
sub-scores that aggregate to a correct 0-100 total, parsed reliably into the Pydantic model.
(The Researcher that would produce the notes automatically arrives in Phase 3.)
"""

import json
import os
from pathlib import Path

os.environ["SCORER"] = "llm"  # this phase demonstrates the LLM Analyst specifically

from app.agents.analyst import analyst_node
from app.config.rubric import CRITERIA, MAX_TOTAL, classify
from app.schemas.opportunity import Opportunity
from app.schemas.profile import Profile

SAMPLE_PATH = Path("/app/data/sample_opportunity.json")

# The ESN profile we score against (would normally be loaded from a file/DB).
PROFILE = Profile(
    name="ESN",
    org_type="ESN",
    core_business=[
        "développement logiciel", "data", "IA", "cloud", "cybersécurité",
        "TMA", "assistance technique", "intégration", "conseil SI", "transformation digitale",
    ],
    exclusions=["vente de licences", "matériel", "fournitures", "travaux", "BTP", "nettoyage", "gardiennage"],
    strategic_organisms=["ministère", "CNSS", "CDG", "banque", "office majeur"],
)

# Hand-written research notes for this opportunity (Phase 3's Researcher will generate these).
RESEARCH_NOTES = (
    "La SGTUPM est la société publique de gestion du transport urbain de Marrakech. "
    "Le besoin porte sur une solution logicielle de GMAO (gestion de maintenance assistée par "
    "ordinateur) avec intégration, mise en service et maintenance : il s'agit donc d'un vrai "
    "projet d'intégration et de TMA, pas d'un simple achat de licence. Délai de 5 mois jugé "
    "serré mais réaliste. Budget non précisé dans l'avis."
)


def main() -> None:
    raw = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    opp = Opportunity(**raw)

    print(f"=== Analyse : {opp.id} — {opp.title} ===\n")

    state = {
        "opportunity": opp.model_dump(mode="json"),
        "profile": PROFILE.model_dump(),
        "research_notes": RESEARCH_NOTES,
    }
    out = analyst_node(state)

    # Per-criterion breakdown
    print("Sous-scores :")
    for c in CRITERIA:
        print(f"  {c.label:<28} {out['subscores'][c.key]:>3} / {c.max_points}")
    print(f"  {'TOTAL':<28} {out['score']:>3} / {MAX_TOTAL}")

    # Deterministic class preview (formalized in the Decision step, Phase 3)
    cls = classify(out["score"])
    print(f"\nClasse (aperçu) : {cls.label}  →  action : {cls.action}")
    print(f"Domaine détecté : {out['domaine_detecte']}")
    print(f"Type d'engagement : {out['type_engagement_detecte']}")
    print(f"Justification : {out['analyst_justification']}")
    if out["gaps"]:
        print("Informations manquantes (gaps) :")
        for g in out["gaps"]:
            print(f"  - {g}")

    # Acceptance sanity checks
    assert set(out["subscores"]) == {c.key for c in CRITERIA}, "missing/extra sub-scores"
    assert out["score"] == sum(out["subscores"].values()), "total must equal the sub-score sum"
    assert 0 <= out["score"] <= MAX_TOTAL, "total out of range"
    print("\n✅ Phase 2 OK : 6 sous-scores typés, total cohérent, sortie parsée sans fuite de texte.")


if __name__ == "__main__":
    main()
