"""Default organization profile (a fictional ESN) the graph scores against.

A plain dict so it drops straight into the graph state. Mirrors the Profile schema fields.
"""

DEFAULT_PROFILE: dict = {
    "name": "ESN",
    "org_type": "ESN",
    "core_business": [
        "développement logiciel", "data", "IA", "cloud", "cybersécurité",
        "TMA", "assistance technique", "intégration", "conseil SI", "transformation digitale",
    ],
    "exclusions": [
        "vente de licences", "matériel", "fournitures", "travaux", "BTP", "nettoyage", "gardiennage",
    ],
    "strategic_organisms": ["ministère", "CNSS", "CDG", "banque", "office majeur"],
}
