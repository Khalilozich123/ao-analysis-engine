"""Phase 1 acceptance harness.

Run it INSIDE the container from /app as a module (so the `app.` imports resolve):

    docker compose exec backend python -m app.scripts.run_phase1

It proves the three Phase-1 acceptance points:
  1. A sample opportunity validates cleanly against the Pydantic schema...
  2. ...and a deliberately-broken one is REJECTED with a clear error.
  3. The one-node LangGraph graph runs, and one real Gemini call returns a completion.

User-facing messages are in French (the app is French); code and comments stay in English.

NOTE: this script imports the three files YOU write (Opportunity, Profile, build_graph). Until
those are completed it will stop with a clear NotImplementedError pointing you to the file.
"""

import json
from pathlib import Path

from pydantic import ValidationError

from app.graph.minimal_graph import build_graph
from app.llm import get_llm
from app.schemas.opportunity import Opportunity

# Path to the sample file, mounted at /app/data by docker-compose.
SAMPLE_PATH = Path("/app/data/sample_opportunity.json")


def check_schema() -> Opportunity:
    """Acceptance 1 & 2: valid data passes, invalid data is rejected."""
    print("=== 1. Validation du schéma (Pydantic) ===")

    # --- valid case ---
    raw = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    opp = Opportunity(**raw)  # raises ValidationError if the data doesn't fit the model
    print(f"✅ Opportunité valide : {opp.id} — {opp.title}")
    print(f"   (deadline analysée comme un type date : {opp.deadline!r})")

    # --- invalid case: drop a required field to prove the model rejects bad data ---
    broken = {k: v for k, v in raw.items() if k != "title"}  # remove the required 'title'
    try:
        Opportunity(**broken)
        print("❌ ERREUR : une opportunité sans 'title' aurait dû être rejetée !")
    except ValidationError as exc:
        # This is the SUCCESS path — Pydantic caught the missing required field.
        first_error = exc.errors()[0]
        print(f"✅ Donnée invalide correctement rejetée : champ '{first_error['loc'][0]}' "
              f"— {first_error['msg']}")

    return opp


def check_graph(opp: Opportunity) -> None:
    """Acceptance 3a: the one-node graph runs and returns merged state."""
    print("\n=== 2. Exécution du graphe LangGraph (un seul nœud) ===")
    graph = build_graph()
    # invoke() runs START -> node -> END and returns the final merged state dict.
    result = graph.invoke({"opportunity": opp.model_dump(), "message": ""})
    print(f"✅ Le graphe a répondu : {result['message']}")


def _message_text(response) -> str:
    """Extract plain text from a LangChain chat response.

    WHY THIS HELPER: older/simpler models return `response.content` as a plain string, but newer
    Gemini models (3.x) return a LIST of structured content blocks like
    [{'type': 'text', 'text': '...'}]. This normalizes both shapes to one string.
    """
    content = response.content
    if isinstance(content, str):
        return content.strip()
    # content is a list of blocks: keep the text of each text-block.
    parts = []
    for block in content:
        if isinstance(block, dict):
            parts.append(block.get("text", ""))
        else:
            parts.append(str(block))
    return "".join(parts).strip()


def check_llm() -> None:
    """Acceptance 3b: one real LLM call through LangChain (Gemini)."""
    print("\n=== 3. Appel LLM réel via LangChain (Gemini) ===")
    llm = get_llm()
    response = llm.invoke("Réponds en une phrase : qu'est-ce qu'un appel d'offres ?")
    print("✅ Réponse du modèle :")
    print(f"   {_message_text(response)}")


def main() -> None:
    opp = check_schema()
    check_graph(opp)
    check_llm()
    print("\n🎉 Phase 1 terminée : schéma, graphe et LLM fonctionnent.")


if __name__ == "__main__":
    main()
