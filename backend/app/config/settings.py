"""Central configuration.

The single place that reads the environment, so the rest of the code imports `settings` and
never touches os.environ or the .env file directly. Secrets come from the environment, never
hard-coded.
"""

import os

from dotenv import load_dotenv

# Convenience when running outside a container; inside Docker these come from compose env_file.
load_dotenv()


class Settings:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "google")

    # Which scorer the Analyst uses: "keyword" (free, offline, instant) or "llm" (Gemini crew).
    # Default keyword so uploads never hit the LLM quota out of the box.
    SCORER: str = os.getenv("SCORER", "keyword")

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")  # Phase 4

    # Phase 3: bounded re-research loop + web search.
    MAX_LOOPS: int = int(os.getenv("MAX_LOOPS", "2"))            # max Researcher passes (termination guard)
    SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "4"))

    # Phase 5: allowed browser origins for the React frontend (comma-separated).
    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
        ).split(",") if o.strip()
    ]


settings = Settings()
