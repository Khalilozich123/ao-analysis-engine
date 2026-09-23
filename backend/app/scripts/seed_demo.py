"""Seed one job with varied synthetic results (no LLM calls) — for demos/screenshots.

    docker compose exec backend python -m app.scripts.seed_demo
Prints the job_id; open the dashboard at /?job=<id>.
"""

from app.db.base import SessionLocal, init_db
from app.db.crud import add_result, create_job, increment_completed, set_job_status
from app.db.models import JobStatus

ROWS = [
    ("15089240", "15/2026/TGR", "Assistance technique pour le développement informatique",
     "Ministère de l'Économie et des Finances", "Rabat", "2200000", "70000",
     88, "Fort intérêt", "Explorer",
     {"alignement_metier": 29, "type_engagement": 19, "organisme_strategique": 15,
      "domaine_techno": 10, "faisabilite_delai": 8, "conditions_favorables": 7},
     "Cœur de métier IT auprès d'un organisme stratégique ; engagement d'assistance technique pur.",
     ["https://www.marchespublics.gov.ma/ao/15089240"]),
    ("15092080", "004/AO/2026/DSTD", "Fourniture, intégration et maintenance d'une solution de GMAO",
     "SGTUPM Marrakech", "Marrakech", None, "50000",
     57, "À qualifier", "Demander CDC",
     {"alignement_metier": 20, "type_engagement": 11, "organisme_strategique": 7,
      "domaine_techno": 7, "faisabilite_delai": 8, "conditions_favorables": 4},
     "Projet mixte fourniture + intégration/TMA pour une société publique locale.",
     ["https://medias24.com/sgtupm", "https://www.gmao-transport.fr"]),
    ("15093110", "88/2026/ONEE", "Migration cloud et sécurisation du datacenter",
     "ONEE - Office National de l'Électricité", "Casablanca", "4500000", "120000",
     79, "Fort intérêt", "Explorer",
     {"alignement_metier": 27, "type_engagement": 15, "organisme_strategique": 13,
      "domaine_techno": 14, "faisabilite_delai": 6, "conditions_favorables": 4},
     "Cloud + cybersécurité explicites, office stratégique ; délai serré.",
     ["https://www.one.org.ma/ao/88"]),
    ("15094777", "12/2026/COMMUNE", "Fourniture de mobilier de bureau",
     "Commune de Témara", "Témara", "300000", "9000",
     14, "Non pertinent", "Ignorer",
     {"alignement_metier": 0, "type_engagement": 0, "organisme_strategique": 3,
      "domaine_techno": 0, "faisabilite_delai": 6, "conditions_favorables": 5},
     "Achat de mobilier sans aucune prestation IT : hors périmètre ESN.",
     []),
    ("15095320", "45/2026/CNSS", "Refonte du portail assuré et application mobile",
     "CNSS", "Rabat", "3800000", "95000",
     72, "À qualifier", "Demander CDC",
     {"alignement_metier": 24, "type_engagement": 14, "organisme_strategique": 15,
      "domaine_techno": 8, "faisabilite_delai": 6, "conditions_favorables": 5},
     "Développement web/mobile pour un organisme stratégique ; techno prioritaire peu explicite.",
     ["https://www.cnss.ma/ao/45", "https://presse.ma/cnss-portail"]),
    ("15096001", "7/2026/OCP", "Plateforme data & IA de maintenance prédictive",
     "OCP Group", "Khouribga", "6200000", "180000",
     91, "Fort intérêt", "Explorer",
     {"alignement_metier": 30, "type_engagement": 18, "organisme_strategique": 14,
      "domaine_techno": 15, "faisabilite_delai": 7, "conditions_favorables": 7},
     "Data/IA explicite, engagement de service, acteur majeur : opportunité exceptionnelle.",
     ["https://www.ocpgroup.ma/ao/7", "https://leconomiste.com/ocp-ia"]),
    ("15096540", "33/2026/REGION", "Étude de faisabilité d'un SI territorial",
     "Région Souss-Massa", "Agadir", "600000", "15000",
     41, "Faible intérêt", "Surveiller",
     {"alignement_metier": 12, "type_engagement": 8, "organisme_strategique": 7,
      "domaine_techno": 5, "faisabilite_delai": 5, "conditions_favorables": 4},
     "Conseil SI périphérique pour une collectivité ; périmètre et budget limités.",
     ["https://www.souss-massa.ma/ao/33"]),
]


def main() -> None:
    init_db()
    with SessionLocal() as s:
        job = create_job(s, filename="AosMB-demo.xlsx", total_rows=len(ROWS))
        set_job_status(s, job.id, JobStatus.running)
        for (oid, ref, title, client, city, budget, deposit, score, verdict, action,
             subs, rationale, sources) in ROWS:
            add_result(s, job.id, {"id": oid, "reference": ref, "title": title, "client": client,
                                   "city": city, "budget": budget, "deposit": deposit},
                       {"score": score, "verdict": verdict, "action": action, "subscores": subs,
                        "rationale": rationale, "sources": sources})
            increment_completed(s, job.id)
        set_job_status(s, job.id, JobStatus.done)
        s.commit()
        print(f"job_id={job.id}")


if __name__ == "__main__":
    main()
