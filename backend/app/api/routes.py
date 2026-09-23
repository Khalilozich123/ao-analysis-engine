"""API routes: upload an Excel, then poll for results."""

import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Response, UploadFile

from app.api.schemas import JobSummary, ResultItem, ResultsResponse, UploadResponse
from app.db.base import SessionLocal
from app.db.crud import create_job, get_job, get_results, list_jobs
from app.workflow.excel import parse_opportunities
from app.workflow.excel_export import build_xlsx
from app.workflow.runner import process_job

_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _filter_rows(rows, verdict, search, top):
    """Apply the same filters the dashboard offers: by class, text search, Top N (rows are score-desc)."""
    out = rows
    if verdict:
        out = [r for r in out if r.verdict == verdict]
    if search:
        q = search.lower()
        out = [
            r for r in out
            if q in (r.title or "").lower() or q in (r.reference or "").lower()
            or q in (r.client or "").lower() or q in (r.opportunity_id or "").lower()
        ]
    if top and top > 0:
        out = out[:top]
    return out

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload(background: BackgroundTasks, file: UploadFile = File(...)) -> UploadResponse:
    if not (file.filename or "").lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Un fichier .xlsx est requis.")

    data = await file.read()
    try:
        opportunities = parse_opportunities(data)  # raises ValueError on missing columns
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not opportunities:
        raise HTTPException(status_code=400, detail="Aucune opportunité valide trouvée dans le fichier.")

    # Per-file dedupe only: the parser already dropped duplicate ids within this file, so each
    # upload is a self-contained job that analyzes its whole file.
    with SessionLocal() as session:
        job = create_job(session, filename=file.filename, total_rows=len(opportunities))
        session.commit()
        job_id = job.id

    background.add_task(process_job, job_id, [o.model_dump(mode="json") for o in opportunities])
    return UploadResponse(job_id=job_id, total_rows=len(opportunities))


@router.get("/jobs", response_model=list[JobSummary])
def jobs() -> list[JobSummary]:
    with SessionLocal() as session:
        return [
            JobSummary(
                job_id=j.id,
                filename=j.filename,
                status=j.status.value,
                total_rows=j.total_rows,
                completed_rows=j.completed_rows,
                created_at=j.created_at,
            )
            for j in list_jobs(session)
        ]


@router.get("/results/{job_id}/export")
def export(
    job_id: uuid.UUID,
    verdict: str | None = None,
    search: str | None = None,
    top: int | None = None,
) -> Response:
    with SessionLocal() as session:
        job = get_job(session, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job introuvable.")
        rows = _filter_rows(get_results(session, job_id), verdict, search, top)
        data = build_xlsx(rows)

    stem = (job.filename or "analyse").rsplit(".", 1)[0]
    return Response(
        content=data,
        media_type=_XLSX_MIME,
        headers={"Content-Disposition": f'attachment; filename="analyse-{stem}.xlsx"'},
    )


@router.get("/results/{job_id}", response_model=ResultsResponse)
def results(job_id: uuid.UUID) -> ResultsResponse:
    with SessionLocal() as session:
        job = get_job(session, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job introuvable.")
        rows = get_results(session, job_id)
        return ResultsResponse(
            job_id=job.id,
            status=job.status.value,
            total_rows=job.total_rows,
            completed_rows=job.completed_rows,
            results=[ResultItem.model_validate(r) for r in rows],
        )
