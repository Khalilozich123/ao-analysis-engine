"""Request/response models for the HTTP API (validated + shown in the OpenAPI docs)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    job_id: uuid.UUID
    total_rows: int


class ResultItem(BaseModel):
    # from_attributes lets us build these straight from SQLAlchemy Result rows.
    model_config = ConfigDict(from_attributes=True)

    opportunity_id: str
    reference: str | None
    title: str
    client: str | None
    city: str | None
    budget: str | None
    deposit: str | None
    score: int
    subscores: dict
    verdict: str
    action: str
    rationale: str
    sources: list
    created_at: datetime


class ResultsResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    total_rows: int
    completed_rows: int
    results: list[ResultItem]


class JobSummary(BaseModel):
    """One past analysis, for the history screen."""

    job_id: uuid.UUID
    filename: str
    status: str
    total_rows: int
    completed_rows: int
    created_at: datetime
