"""Keyword + rules scorer — a free, offline, deterministic alternative to the LLM Analyst.

Produces the same AnalystOutput as the LLM path. It scores the four textual criteria with French
lexicons (accent-folded substring matching) and the two numeric criteria with simple rules on the
deadline/budget/caution. Lexicons are seeded from the profile plus built-in domain terms, and are
meant to be tuned over time. `gaps` is always empty so keyword mode never triggers re-research.
"""

import re
import unicodedata
from datetime import date

from app.schemas.analyst_output import AnalystOutput


def _fold(s) -> str:
    """Lowercase + strip accents, so 'Référence' and 'reference' match."""
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return f" {s.lower()} "


# --- lexicons (accent-folded, lowercase) ---
PRIORITY_TECH = [
    "data", "donnee", "intelligence artificielle", "big data", "cloud", "azure", "aws",
    "gcp", "cybersecurite", "cyber", "securite informatique", "datacenter", "data center",
    "soc", "siem", "analytics", "machine learning",
]
CORE_IT = [
    "developpement", "logiciel", "informatique", "application", "applicatif",
    "systeme d'information", "integration", "tma", "maintenance applicative",
    "assistance technique", "digital", "numerique", "transformation digitale", "mobile",
    "web", "portail", "plateforme", "erp", "progiciel", " api ", "devops", "centre de service",
    "pole de competences", "referencement", "gmao", "infogerance", "tierce maintenance", "conseil si",
]
EXCLUSION = [
    "mobilier", "nettoyage", "gardiennage", "btp", "travaux", "genie civil", "batiment",
    "vehicule", "carburant", "restauration", "climatisation", "impression", "papeterie",
    "fourniture de bureau", "amenagement", "espaces verts",
]
SERVICE = [
    "assistance", "tma", "maintenance", "integration", "mise en oeuvre", "mise en service",
    "forfait", "centre de service", "pole de competences", "audit", "formation", "gouvernance",
    "infogerance", "support", "accompagnement", "prestation", "developpement", "conseil",
]
SALE = ["vente", "acquisition", "achat", "licence", "location", "materiel"]
STRATEGIC_MAJOR = [
    "ministere", "cnss", "cdg", "ocp", "onee", "onda", " adm ", "banque", "bank", "caisse",
    "office national", "agence nationale", "tresorerie", "douane", " dgi ", " tgr ",
]


def _hits(text: str, terms: list[str]) -> list[str]:
    return [t for t in terms if t.strip() and t in text]


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _to_number(v):
    if v in (None, ""):
        return None
    digits = re.sub(r"\D", "", str(v))
    return int(digits) if digits else None


def keyword_score(opportunity: dict, profile: dict) -> AnalystOutput:
    text = _fold(" ".join(str(opportunity.get(k, "")) for k in ("title", "description", "client", "city")))
    client_text = _fold(opportunity.get("client", ""))

    # Profile-driven terms fold into the lexicons.
    core = set(_hits(text, CORE_IT)) | {t for t in profile.get("core_business", []) if _fold(t).strip() in text}
    prio = _hits(text, PRIORITY_TECH)
    excl = set(_hits(text, EXCLUSION)) | {t for t in profile.get("exclusions", []) if _fold(t).strip() in text}
    serv = _hits(text, SERVICE)
    sale = _hits(text, SALE)
    has_it = bool(core or prio)

    strong, core_n, excl_n = len(prio), len(core), len(excl)
    serv_n, sale_n = len(serv), len(sale)

    # 1. Alignement métier (0-30) — graded by strength of IT evidence, penalized by non-IT terms.
    if strong >= 1:
        alignement = 24 + min(6, (strong - 1) * 3 + core_n)      # 24..30
    elif core_n >= 1:
        alignement = 8 + min(14, core_n * 5)                      # 13..22
    else:
        alignement = 0
    if excl_n:
        alignement = 0 if not has_it else max(6, alignement - 4 * excl_n)  # goods + real IT stays mid

    # 2. Type d'engagement (0-20) — graded by service vs sale term counts.
    if excl_n and not serv_n and not has_it:
        type_engagement = 0
    elif serv_n and not sale_n:
        type_engagement = 13 + min(7, serv_n * 2)                 # 15..20
    elif serv_n and sale_n:
        type_engagement = 8 + min(4, max(0, serv_n - sale_n) * 2) # 8..12 (mixed)
    elif sale_n:
        type_engagement = max(0, 4 - sale_n)                      # 0..3
    else:
        type_engagement = 6

    # 3. Organisme stratégique (0-15) — more buckets for a finer spread.
    profile_orgs = [_fold(o).strip() for o in profile.get("strategic_organisms", [])]
    if any(m.strip() in client_text for m in STRATEGIC_MAJOR + profile_orgs):
        organisme = 15
    elif any(w in client_text for w in ("office", "regie", "etablissement public", "autorite", "agence")):
        organisme = 11
    elif any(w in client_text for w in ("commune", "collectivite", "prefecture")):
        organisme = 3
    elif any(w in client_text for w in ("province", "region", "conseil")):
        organisme = 6
    elif client_text.strip():
        organisme = 8
    else:
        organisme = 5

    # 4. Domaine techno prioritaire (0-15) — graded by count of priority-tech hits.
    if strong >= 2:
        domaine_techno = 15
    elif strong == 1:
        domaine_techno = 11
    elif core_n >= 2:
        domaine_techno = 7
    elif core_n == 1:
        domaine_techno = 5
    else:
        domaine_techno = 0

    # 5. Faisabilité du délai (0-10) — finer buckets on days-to-deadline.
    deadline = opportunity.get("deadline")
    if deadline:
        try:
            days = (date.fromisoformat(str(deadline)[:10]) - date.today()).days
            faisabilite = (
                2 if days < 0 else 3 if days < 7 else 5 if days < 15 else
                7 if days < 30 else 9 if days < 60 else 10
            )
        except ValueError:
            faisabilite = 5
    else:
        faisabilite = 5

    # 6. Conditions favorables (0-10) — budget clarity + reasonable caution ratio.
    b, c = _to_number(opportunity.get("budget")), _to_number(opportunity.get("deposit"))
    conditions = 0
    if b:
        conditions += 5 + (1 if b >= 1_000_000 else 0)
    if c:
        conditions += 2
    if b and c:
        ratio = c / b
        conditions += 2 if ratio <= 0.02 else 1 if ratio <= 0.05 else 0
    if not b and not c:
        conditions = 2

    # Detected labels + a concise justification.
    domaine_detecte = (
        "Data / IA / Cloud / Cyber" if prio else
        "Développement / SI" if has_it else
        "Hors IT (fournitures / travaux)" if excl else "Indéterminé"
    )
    engagement_detecte = (
        "Service / TMA" if type_engagement >= 16 else
        "Mixte" if type_engagement >= 8 else
        "Vente / fourniture" if sale else "Indéterminé"
    )
    if alignement == 0:
        driver = "Hors périmètre IT d'une ESN."
    elif alignement >= 25 and organisme == 15:
        driver = "Cœur de métier IT auprès d'un organisme stratégique."
    elif alignement >= 25:
        driver = "Alignement métier IT fort."
    else:
        driver = "Alignement IT partiel ou périphérique."
    justification = f"Analyse par mots-clés — domaine « {domaine_detecte} », engagement « {engagement_detecte} ». {driver}"

    return AnalystOutput(
        alignement_metier=_clamp(alignement, 0, 30),
        type_engagement=_clamp(type_engagement, 0, 20),
        organisme_strategique=_clamp(organisme, 0, 15),
        domaine_techno=_clamp(domaine_techno, 0, 15),
        faisabilite_delai=_clamp(faisabilite, 0, 10),
        conditions_favorables=_clamp(conditions, 0, 10),
        domaine_detecte=domaine_detecte,
        type_engagement_detecte=engagement_detecte,
        justification=justification,
        gaps=[],
    )
