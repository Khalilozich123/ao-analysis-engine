"""Background job: analyze each opportunity through the graph and persist results.

Runs after the /upload response is sent (FastAPI BackgroundTasks). Opens its own DB session and
commits after every row, so /results reflects progress live. One failing row is recorded as a
skip and never aborts the whole job; a catastrophic failure marks the job 'error'.
"""

import logging
import uuid

from app.config.profile import DEFAULT_PROFILE
from app.db.base import SessionLocal
from app.db.crud import add_result, increment_completed, set_job_status
from app.db.models import JobStatus
from app.graph.opportunity_graph import build_graph

log = logging.getLogger("graph")

_ANALYSIS_KEYS = ("subscores", "score", "verdict", "action", "rationale", "sources")


def process_job(job_id: uuid.UUID, opportunities: list[dict]) -> None:
    graph = build_graph()
    with SessionLocal() as session:
        set_job_status(session, job_id, JobStatus.running)
        session.commit()
        try:
            for opp in opportunities:
                try:
                    final = graph.invoke({"opportunity": opp, "profile": DEFAULT_PROFILE})
                    analysis = {k: final.get(k) for k in _ANALYSIS_KEYS}
                    add_result(session, job_id, opp, analysis)
                except Exception:
                    log.exception("[runner] row failed: %s", opp.get("id"))
                    session.rollback()
                finally:
                    increment_completed(session, job_id)  # advance the bar either way
                    session.commit()
            set_job_status(session, job_id, JobStatus.done)
            session.commit()
        except Exception:
            log.exception("[runner] job failed: %s", job_id)
            session.rollback()
            set_job_status(session, job_id, JobStatus.error)
            session.commit()
