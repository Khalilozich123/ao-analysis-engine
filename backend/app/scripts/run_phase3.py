"""Phase 3 acceptance harness.

Run inside the container:
    docker compose exec backend python -m app.scripts.run_phase3

Runs the full graph (Supervisor → Researcher → Analyst → re-research loop → Decision) on the
sample opportunity and prints the per-cycle log plus the final verdict, rationale and sources.
"""

import json
import logging
import os
import warnings
from pathlib import Path

os.environ["SCORER"] = "llm"  # this phase demonstrates the full LLM crew + re-research loop

# gemini-3.6-flash ignores `temperature`; silence that repeated UserWarning for a clean demo.
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai.*")

from app.config.rubric import CRITERIA, MAX_TOTAL
from app.config.settings import settings
from app.graph.opportunity_graph import build_graph
from app.schemas.opportunity import Opportunity
from app.schemas.profile import Profile

logging.basicConfig(level=logging.INFO, format="%(message)s")
# Quiet noisy third-party loggers so the per-cycle trace stays readable.
for _noisy in ("httpx", "primp", "langchain_google_genai", "google_genai", "google.genai", "urllib3"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)
logging.getLogger("ddgs").setLevel(logging.CRITICAL)  # hides benign search-engine fallback errors

SAMPLE_PATH = Path("/app/data/sample_opportunity.json")

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


def main() -> None:
    raw = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    opp = Opportunity(**raw)

    print(f"=== Graphe multi-agents (MAX_LOOPS={settings.MAX_LOOPS}) ===\n")
    graph = build_graph()
    final = graph.invoke({
        "opportunity": opp.model_dump(mode="json"),
        "profile": PROFILE.model_dump(),
    })

    print("\n=== RÉSULTAT FINAL ===")
    print(f"Opportunité : {opp.id} — {opp.title}")
    for c in CRITERIA:
        print(f"  {c.label:<28} {final['subscores'][c.key]:>3} / {c.max_points}")
    print(f"  {'TOTAL':<28} {final['score']:>3} / {MAX_TOTAL}")
    print(f"\nVerdict : {final['verdict']}  →  action : {final['action']}")
    print(f"Passes de recherche : {final.get('loop_count', 0)}")
    print(f"Rationale : {final['rationale']}")
    if final.get("sources"):
        print("Sources :")
        for s in final["sources"]:
            print(f"  - {s}")

    # Acceptance sanity checks
    assert final.get("verdict"), "a verdict must always be produced"
    assert "subscores" in final and final["score"] == sum(final["subscores"].values())
    assert final.get("loop_count", 0) >= 1, "at least one research pass must run"
    assert final.get("loop_count", 0) <= settings.MAX_LOOPS, "loop must be bounded by MAX_LOOPS"
    print("\n✅ Phase 3 OK : le graphe termine, verdict + sous-scores + rationale produits.")


if __name__ == "__main__":
    main()
