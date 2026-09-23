"""Phase 4 acceptance harness.

Run inside the container:
    docker compose exec backend python -m app.scripts.run_phase4

Creates a job, inserts sample results through the helpers, advances progress, then reads
everything back. Run it again after `docker compose restart db` to prove data persists.
"""

from app.db.base import SessionLocal, init_db
from app.db.crud import (
    add_result, create_job, get_job, get_results, increment_completed, list_jobs, set_job_status,
)
from app.db.models import JobStatus

# Two canned analyses (shape = graph output). No LLM needed — this phase tests persistence only.
SAMPLE_ROWS = [
    {
        "opportunity": {"id": "15089240", "reference": "15/2026/TGR", "title": "Assistance technique développement informatique",
                         "client": "Ministère de l'Économie et des Finances", "city": "Rabat", "budget": "2200000", "deposit": "70000"},
        "analysis": {"score": 85, "verdict": "Fort intérêt", "action": "Explorer",
                     "subscores": {"alignement_metier": 28, "type_engagement": 18, "organisme_strategique": 15,
                                   "domaine_techno": 12, "faisabilite_delai": 7, "conditions_favorables": 5},
                     "rationale": "Alignée avec le cœur de métier de l'ESN ; organisme stratégique.",
                     "sources": ["https://www.marchespublics.gov.ma/..."]},
    },
    {
        "opportunity": {"id": "15092080", "reference": "004/AO/2026/DSTD", "title": "Solution de GMAO",
                        "client": "SGTUPM Marrakech", "city": "Marrakech", "budget": None, "deposit": "50000"},
        "analysis": {"score": 58, "verdict": "À qualifier", "action": "Demander CDC",
                     "subscores": {"alignement_metier": 20, "type_engagement": 11, "organisme_strategique": 7,
                                   "domaine_techno": 7, "faisabilite_delai": 8, "conditions_favorables": 5},
                     "rationale": "Projet mixte fourniture + intégration/TMA pour une société publique locale.",
                     "sources": ["https://medias24.com/..."]},
    },
]


def main() -> None:
    init_db()  # idempotent: creates tables if absent

    with SessionLocal() as session:
        job = create_job(session, filename="AosMB-sample.xlsx", total_rows=len(SAMPLE_ROWS))
        set_job_status(session, job.id, JobStatus.running)
        for row in SAMPLE_ROWS:
            add_result(session, job.id, row["opportunity"], row["analysis"])
            increment_completed(session, job.id)          # advance the progress bar
        set_job_status(session, job.id, JobStatus.done)
        session.commit()
        job_id = job.id

    # Read it back in a fresh session (proves it round-trips through the DB).
    with SessionLocal() as session:
        job = get_job(session, job_id)
        results = get_results(session, job_id)
        print(f"Job {job.id}")
        print(f"  fichier : {job.filename}")
        print(f"  statut  : {job.status.value}   progression : {job.completed_rows}/{job.total_rows}")
        print("  résultats (triés par score) :")
        for r in results:
            print(f"    [{r.score:>3}] {r.verdict:<14} {r.action:<13} {r.title[:45]}")

        assert job.status == JobStatus.done
        assert job.completed_rows == job.total_rows == len(SAMPLE_ROWS)
        assert len(results) == len(SAMPLE_ROWS)
        assert results[0].score >= results[-1].score  # ordered desc

        total_jobs = len(list_jobs(session))
        print(f"\nJobs totaux en base : {total_jobs}  (augmente à chaque exécution → persistance)")

    print("\n✅ Phase 4 OK : job + résultats écrits via les helpers, relus avec la bonne progression.")


if __name__ == "__main__":
    main()
