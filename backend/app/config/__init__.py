# `app.config` package. Re-export `settings` so `from app.config import settings` keeps working.
from app.config.settings import settings

__all__ = ["settings"]
