from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


async def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        raise RuntimeError(f"Database initialization failed: {exc}") from exc


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
