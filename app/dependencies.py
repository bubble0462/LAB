from __future__ import annotations

from collections.abc import Generator

from app.database import SessionLocal


def get_db_session() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

