"""SQLite persistence (SQLAlchemy); swap DATABASE_URL to another SQL driver if desired."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL


def ensure_sqlite_directory(url: str) -> None:
    if url.startswith("sqlite:///") and ":memory:" not in url:
        # SQLite URL can be relative (sqlite:///./data/db.sqlite3) or absolute.
        database_path = url.removeprefix("sqlite:///")
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)


ensure_sqlite_directory(DATABASE_URL)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
