"""Generate fully SYNTHETIC sample workbooks for testing /upload.

Every value here is invented — organism names, references and tender objects are
fictional and come from NO real, private or subscription source. The column layout
mirrors a generic Moroccan public-procurement export (appels d'offres) so the parser
and scorer can be exercised end-to-end. Output is deterministic (fixed seed).

Run standalone (no app imports needed):
    python backend/app/scripts/make_sample_xlsx.py [output_dir]

Or inside the backend container:
    docker compose exec backend python -m app.scripts.make_sample_xlsx

Writes:
    <output_dir>/sample_opportunities.xlsx   - valid, ~33 varied rows (spans all 4 classes)
    <output_dir>/bad_opportunities.xlsx      - missing the required "Objet" column (tests rejection)
"""

import random
import sys
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook

SEED = 2026
HEADERS = ["N° Ordre", "Référence", "Date limite", "Caution", "Objet", "Organisme", "Ville", "Budget"]

CITIES = [
    "Casablanca", "Rabat", "Marrakech", "Fès", "Tanger", "Agadir", "Meknès",
    "Oujda", "Kénitra", "Tétouan", "Salé", "Nador", "El Jadida", "Safi", "Béni Mellal",
]

# Organism names are invented; they only use generic public-sector words so the scorer's
# "strategic organism" rule has something to match. They are NOT real entities.
ORG_STRATEGIC = [
    "Office National des Systèmes d'Information",
    "Agence Nationale du Numérique",
    "Caisse Nationale de Prévoyance Publique",
    "Ministère de la Modernisation Numérique",
    "Office National de l'Énergie et de l'Eau",
]
ORG_PUBLIC = [
    "Office Régional de Gestion Portuaire",
    "Établissement Public des Transports Urbains",
    "Agence de Développement Territorial",
    "Régie Autonome de Distribution",
]
ORG_LOCAL = [
    "Commune Urbaine du Centre",
    "Conseil Régional de l'Oriental",
    "Province de Kénitra",
    "Préfecture des Arrondissements",
]
ORG_OTHER = [
    "Centre Hospitalier Provincial",
    "Université Nationale des Sciences Appliquées",
    "Direction Régionale de la Formation",
]

# Tender objects curated so the keyword scorer spreads results across the four classes.
STRONG_IT = [  # priority tech (cloud/cyber/data) -> Fort intérêt / haut À qualifier
    "mise en place d'une plateforme cloud et de services de cybersécurité (soc / siem)",
    "prestation d'infogérance et de sécurité informatique du datacenter",
    "projet de transformation digitale et de migration vers le cloud azure",
    "mise en oeuvre d'une solution big data et analytics décisionnel",
    "supervision cybersécurité et centre de service soc managé",
]
SERVICE_IT = [  # core IT services -> À qualifier
    "assistance technique pour le développement d'applications web et mobiles",
    "tierce maintenance applicative (tma) du système d'information",
    "développement et intégration d'un portail web institutionnel",
    "mise en place d'un erp et accompagnement au déploiement",
    "prestation de développement logiciel et de maintenance applicative",
    "assistance et support technique du système d'information",
    "conseil si et gouvernance des systèmes d'information",
]
HARDWARE_MIX = [  # hardware / licences (sale-flavoured) -> Faible / bas À qualifier
    "acquisition de matériel informatique et de licences logicielles",
    "fourniture d'équipements réseau et câblage informatique",
    "achat de serveurs et de matériel de datacenter",
    "location de matériel informatique pour les services administratifs",
]
NON_IT = [  # out of scope -> Non pertinent
    "travaux de construction d'un bâtiment administratif",
    "prestation de nettoyage et de gardiennage des locaux",
    "fourniture de mobilier de bureau",
    "acquisition de véhicules utilitaires",
    "travaux d'aménagement d'espaces verts",
    "fourniture de carburant pour le parc automobile",
    "travaux de génie civil et de voirie",
    "prestation de restauration collective",
]


def _rand_ref(rng: random.Random, i: int) -> str:
    suffix = rng.choice(["", "/DSI", "/DAF", "/DSTD", "/DAL", "/SG"])
    return f"AOO {i:02d}/2026{suffix}"


def _rand_deadline(rng: random.Random) -> date:
    # Mostly future, a few tight/past so the "faisabilité du délai" criterion varies.
    offset = rng.choice([-5, 4, 10, 20, 25, 35, 45, 60, 75, 90])
    return date.today() + timedelta(days=offset)


def _rand_budget(rng: random.Random):
    return rng.choice([None, 300_000, 600_000, 800_000, 1_200_000, 1_500_000, 2_500_000, 4_500_000, None])


def _rand_caution(rng: random.Random):
    return rng.choice([None, 10_000, 20_000, 30_000, 50_000, 70_000, None])


def build_rows(rng: random.Random) -> list[list]:
    # Only a couple of rows combine priority tech WITH a strategic organism, so "Fort intérêt"
    # stays rare (as in the real rubric). Everything else spreads over the lower three classes:
    # strong tech at ordinary orgs and core-IT services -> À qualifier; hardware/licences ->
    # Faible; construction / cleaning / supplies / vehicles -> Non pertinent.
    plan: list[tuple[str, list[str]]] = (
        [(STRONG_IT[0], ORG_STRATEGIC[:1]), (STRONG_IT[1], ORG_STRATEGIC[1:2])]  # ~2 Fort intérêt
        + [(o, ORG_PUBLIC) for o in STRONG_IT[2:]]                                # strong tech, ordinary org
        + [(o, ORG_PUBLIC + ORG_LOCAL + ORG_OTHER) for o in SERVICE_IT]          # À qualifier
        + [(o, ORG_LOCAL + ORG_OTHER) for o in SERVICE_IT[:3]]                   # more À qualifier / Faible
        + [(o, ORG_LOCAL + ORG_OTHER) for o in HARDWARE_MIX]                     # Faible
        + [(o, ORG_OTHER) for o in HARDWARE_MIX[:2]]
        + [(o, ORG_LOCAL + ORG_OTHER) for o in NON_IT]                           # Non pertinent
        + [(o, ORG_OTHER) for o in NON_IT[:3]]
    )
    rng.shuffle(plan)

    base = 15_090_000
    rows: list[list] = []
    for i, (objet, pool) in enumerate(plan, start=1):
        rows.append([
            base + i * 7,
            _rand_ref(rng, i),
            _rand_deadline(rng),
            _rand_caution(rng),
            objet,
            rng.choice(pool),
            rng.choice(CITIES),
            _rand_budget(rng),
        ])
    return rows


def _write(path: Path, headers: list[str], rows: list[list]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for r in rows:
        ws.append(r)
    wb.save(path)
    print(f"wrote {path} ({len(rows)} rows)")


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app/data")
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    rows = build_rows(rng)

    _write(out / "sample_opportunities.xlsx", HEADERS, rows)

    # Malformed workbook: drop the required "Objet" column (index 4) to test rejection.
    bad_headers = [h for i, h in enumerate(HEADERS) if i != 4]
    bad_rows = [[c for i, c in enumerate(r) if i != 4] for r in rows[:3]]
    _write(out / "bad_opportunities.xlsx", bad_headers, bad_rows)


if __name__ == "__main__":
    main()
