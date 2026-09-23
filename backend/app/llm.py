"""LLM factory.

WHY A FACTORY: the spec wants the LLM "configured once and swappable without touching graph
logic." So every agent/node will call `get_llm()` instead of constructing a model directly.
To switch providers later (OpenAI, Groq, ...), you add a branch here and change LLM_PROVIDER
in .env — no other file changes.

WHAT IT RETURNS: a LangChain "chat model" object. Every LangChain chat model shares the same
interface, e.g. `model.invoke("some prompt")` returns a message with a `.content` string. That
shared interface is exactly why swapping providers doesn't ripple through the rest of the code.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings


def get_llm():
    """Build and return the configured chat model.

    Phase 1 implements only the "google" branch. Later phases can add "openai", "groq", etc.
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "google":
        if not settings.GOOGLE_API_KEY:
            # Fail loudly and clearly rather than getting a cryptic auth error deep in a call.
            raise RuntimeError(
                "GOOGLE_API_KEY is empty. Copy backend/.env.example to backend/.env and paste "
                "your free key from https://aistudio.google.com"
            )
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,  # deterministic-ish output; good for reproducible scoring later
        )

    # Any other value is a configuration mistake — say so clearly.
    raise ValueError(
        f"Unsupported LLM_PROVIDER '{settings.LLM_PROVIDER}'. Phase 1 supports only 'google'."
    )


def message_text(response) -> str:
    """Extract plain text from a chat response.

    Simple models return `.content` as a string; newer Gemini models return a list of content
    blocks like [{'type': 'text', 'text': ...}]. This normalizes both to one string.
    """
    content = response.content
    if isinstance(content, str):
        return content.strip()
    parts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in content]
    return "".join(parts).strip()
