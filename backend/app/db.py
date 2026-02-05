from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import get_database_config

_db_config = get_database_config()

# Exported for tests and tools that need the async URL
ASYNC_DATABASE_URL = _db_config.async_database_url

# Sync engine and session for seed script and external tools (e.g. Alembic uses .env URL directly)
engine = create_engine(_db_config.DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine and session for the FastAPI app
async_engine = create_async_engine(
    _db_config.async_database_url,
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
    """Dependency: yields a request-scoped async DB session. Commits on success, rolls back on exception."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
