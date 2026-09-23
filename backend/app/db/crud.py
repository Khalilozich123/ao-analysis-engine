"""Data-access helpers for jobs and results.

Each helper takes an open Session; the caller owns the transaction (commits). This keeps the
functions composable for the Phase 5 background job, which creates a job, then adds results and
advances progress one row at a time.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Job, JobStatus, Result


def create_job(session: Session, filename: str, total_rows: int) -> Job:
    job = Job(filename=filename, total_rows=total_rows, status=JobStatus.pending)
    session.add(job)
    session.flush()  # assign job.id without ending the transaction
    return job


def set_job_status(session: Session, job_id: uuid.UUID, status: JobStatus) -> None:
    session.get(Job, job_id).status = status


def increment_completed(session: Session, job_id: uuid.UUID, by: int = 1) -> None:
    session.get(Job, job_id).completed_rows += by


def add_result(session: Session, job_id: uuid.UUID, opportunity: dict, analysis: dict) -> Result:
    """Persist one analyzed opportunity.

    `opportunity` is a normalized Opportunity dict; `analysis` is the graph output
    (subscores, score, verdict, action, rationale, sources).
    """
    result = Result(
        job_id=job_id,
        opportunity_id=str(opportunity.get("id", "")),
        reference=opportunity.get("reference"),
        title=opportunity.get("title", ""),
        client=opportunity.get("client"),
        city=opportunity.get("city"),
        budget=opportunity.get("budget"),
        deposit=opportunity.get("deposit"),
        score=analysis.get("score") or 0,
        subscores=analysis.get("subscores") or {},
        verdict=analysis.get("verdict") or "",
        action=analysis.get("action") or "",
        rationale=analysis.get("rationale") or "",
        sources=analysis.get("sources") or [],
    )
    session.add(result)
    session.flush()
    return result


def get_job(session: Session, job_id: uuid.UUID) -> Job | None:
    return session.get(Job, job_id)


def get_results(session: Session, job_id: uuid.UUID) -> list[Result]:
    """Results for a job, highest score first (the dashboard's ranked order)."""
    stmt = select(Result).where(Result.job_id == job_id).order_by(Result.score.desc())
    return list(session.scalars(stmt))


def list_jobs(session: Session) -> list[Job]:
    return list(session.scalars(select(Job).order_by(Job.created_at.desc())))


def existing_opportunity_ids(session: Session) -> set[str]:
    """All opportunity ids already analyzed (any job) — used to dedupe new uploads."""
    return set(session.scalars(select(Result.opportunity_id).distinct()))
