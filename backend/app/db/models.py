"""ORM models: Job and Result (spec §3.2).

A Job represents one uploaded file; each Result belongs to a Job and carries both the
opportunity display fields and its analysis (score, subscores, verdict, action, rationale, sources).
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    done = "done"
    error = "error"


class Job(Base):
    __tablename__ = "job"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.pending)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    completed_rows: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    results: Mapped[list["Result"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class Result(Base):
    __tablename__ = "result"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job.id", ondelete="CASCADE"), index=True)

    # --- opportunity display fields (denormalized for the dashboard / ranked table) ---
    opportunity_id: Mapped[str] = mapped_column(String(100), index=True)  # the Excel "Numéro d'ordre"
    reference: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(Text)
    client: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(255))
    budget: Mapped[str | None] = mapped_column(String(255))
    deposit: Mapped[str | None] = mapped_column(String(255))

    # --- analysis ---
    score: Mapped[int] = mapped_column(Integer)
    subscores: Mapped[dict] = mapped_column(JSONB)       # the 6 criterion keys
    verdict: Mapped[str] = mapped_column(String(50))     # interest class label
    action: Mapped[str] = mapped_column(String(50))      # recommended action
    rationale: Mapped[str] = mapped_column(Text)
    sources: Mapped[list] = mapped_column(JSONB, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped["Job"] = relationship(back_populates="results")
