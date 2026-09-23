"""FastAPI application entry point.

Exposes the upload workflow and results API. Run by uvicorn (see docker-compose.yml):
    uvicorn app.main:app --host 0.0.0.0 --port 8000
OpenAPI docs are auto-generated at /docs.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config.settings import settings
from app.db.base import init_db

logging.basicConfig(level=logging.INFO, format="%(message)s")
for _noisy in ("httpx", "primp", "langchain_google_genai", "google_genai", "google.genai"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)
logging.getLogger("ddgs").setLevel(logging.CRITICAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # ensure tables exist on startup
    yield


app = FastAPI(title="Opportunity Analysis Engine", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
