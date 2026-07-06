from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """
    pass


def _ensure_sqlite_parent_directory() -> None:
    """
    Ensure the parent directory exists when using a local SQLite database.
    """
    database_url = settings.ticket_database_url

    if not database_url.startswith("sqlite:///"):
        return

    db_path = database_url.replace("sqlite:///", "", 1)
    parent = Path(db_path).parent
    parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent_directory()

connect_args = {}

if settings.ticket_database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }

engine = create_engine(
    settings.ticket_database_url,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def create_tables() -> None:
    """
    Create database tables.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()