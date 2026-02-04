"""Pytest fixtures: app, async client with overridden get_db, test DB session and account."""
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db import get_db, ASYNC_DATABASE_URL
from app.main import app
from app.models import Account, AccountType, Member

# Async engine and session for tests (same URL as app)
_test_async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
)
_test_async_session_factory = async_sessionmaker(
    _test_async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture
async def db_connection():
    """Create an async connection and outer transaction; roll back in teardown for isolation."""
    async with _test_async_engine.connect() as conn:
        trans = await conn.begin()
        try:
            yield conn
        finally:
            await trans.rollback()


@pytest.fixture
async def db_session(db_connection):
    """Async session bound to the test connection; all work is rolled back after the test."""
    conn = db_connection
    session = AsyncSession(bind=conn, expire_on_commit=False)
    # Bump sequences so inserts get ids not used by seed data
    await session.execute(text(
        "SELECT setval(pg_get_serial_sequence('members', 'id'), "
        "COALESCE((SELECT MAX(id) FROM members), 0) + 1)"
    ))
    await session.execute(text(
        "SELECT setval(pg_get_serial_sequence('accounts', 'id'), "
        "COALESCE((SELECT MAX(id) FROM accounts), 0) + 1)"
    ))
    await session.execute(text(
        "SELECT setval(pg_get_serial_sequence('transactions', 'id'), "
        "COALESCE((SELECT MAX(id) FROM transactions), 0) + 1)"
    ))
    await session.flush()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
async def test_account(db_session):
    """One test member and account; account has non-zero balances for debit tests."""
    member = Member(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone="555-0000",
        address="123 Test St",
        city="Test City",
        state="TS",
        zip="00000",
        country="US",
    )
    db_session.add(member)
    await db_session.flush()

    account = Account(
        name="Test Checking",
        account_type=AccountType.CHECKING,
        member_id=member.id,
        account_number="123456789012",
        masked_account_number="****9012",
        available_balance=Decimal("100.00"),
        current_balance=Decimal("100.00"),
    )
    db_session.add(account)
    await db_session.flush()

    return account


@pytest.fixture
async def client(db_session, test_account):
    """AsyncClient with get_db overridden to use the test session."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
