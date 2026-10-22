"""Runtime configuration; environment variables are never checked into Git."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/analysis.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
MAX_LOG_BYTES = 256 * 1024
MAX_LLM_LOG_CHARS = 7_000
