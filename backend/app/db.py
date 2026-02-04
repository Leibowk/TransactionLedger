import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, Session

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "")
# Async URL for asyncpg (Alembic and seed script keep using sync postgresql://)
ASYNC_DATABASE_URL = (
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    if DATABASE_URL.startswith("postgresql://")
    else DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg", 1)
    if "postgresql" in DATABASE_URL
    else ""
)

# Sync engine and session for seed script and external tools (e.g. Alembic uses .env URL directly)
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine and session for the FastAPI app
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True,
)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db():
    """Dependency: yields a request-scoped async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
