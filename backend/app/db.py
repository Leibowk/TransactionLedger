from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency: yields a request-scoped DB session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
