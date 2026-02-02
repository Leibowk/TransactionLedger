"""Pytest fixtures: app, client with overridden get_db, test DB session and account."""
from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.db import engine, get_db
from app.main import app
from app.models import Account, AccountType, Member


@pytest.fixture
def db_connection():
    """Create a connection and outer transaction; roll back in teardown for isolation."""
    connection = engine.connect()
    trans = connection.begin()
    try:
        yield connection
    finally:
        try:
            trans.rollback()
        except Exception:
            pass
        connection.close()


@pytest.fixture
def db_session(db_connection):
    """Session bound to the test connection; all work is rolled back after the test."""
    session = Session(
        bind=db_connection,
        autocommit=False,
        autoflush=False,
    )
    # Bump sequences so inserts get ids not used by seed data (avoids UniqueViolation).
    session.execute(text(
        "SELECT setval(pg_get_serial_sequence('members', 'id'), "
        "COALESCE((SELECT MAX(id) FROM members), 0) + 1)"
    ))
    session.execute(text(
        "SELECT setval(pg_get_serial_sequence('accounts', 'id'), "
        "COALESCE((SELECT MAX(id) FROM accounts), 0) + 1)"
    ))
    session.execute(text(
        "SELECT setval(pg_get_serial_sequence('transactions', 'id'), "
        "COALESCE((SELECT MAX(id) FROM transactions), 0) + 1)"
    ))
    session.flush()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_account(db_session):
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
    db_session.flush()

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
    db_session.flush()

    return account


@pytest.fixture
def client(db_session, test_account):
    """TestClient with get_db overridden to use the test session (same session sees test_account)."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
