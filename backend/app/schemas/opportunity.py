"""Normalized opportunity record.

The internal shape every opportunity is validated into before analysis. The Phase 5 parser maps
the relevant columns of the uploaded Excel onto these fields.
"""

from datetime import date

from pydantic import BaseModel


class Opportunity(BaseModel):
    id: str                        # "Numéro d'ordre" (numeric in Excel, stored as str)
    reference: str                 # "Référence", e.g. "004/AO/2026/DSTD"
    title: str                     # short title (derived from "Objet")
    description: str               # full requirement text ("Objet")
    client: str | None = None      # "Organisme"
    city: str | None = None        # "Ville"
    budget: str | None = None      # "Budget" (free-text, often empty)
    deposit: str | None = None     # "Caution" (bid guarantee)
    deadline: date | None = None   # "Date limite"
