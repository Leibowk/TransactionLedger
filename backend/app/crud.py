from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from fastapi import Depends

from . import models
from .db import get_db

# Repository: request-scoped wrapper over a session. Injected via get_repository.


def get_repository(db: Session = Depends(get_db)) -> "Repository":
    """Dependency: yields a request-scoped repository (crud + session)."""
    return Repository(db)


class Repository:
    """Holds the DB session and delegates to crud. Only crud layer touches db."""

    def __init__(self, db: Session):
        self._db = db

    def get_account(self, account_id: int):
        return get_account(self._db, account_id)

    def get_account_for_update(self, account_id: int):
        return get_account_for_update(self._db, account_id)

    def get_transactions(self, account_id: int):
        return get_transactions(self._db, account_id)

    def get_transaction(self, account_id: int, transaction_id: int):
        return get_transaction(self._db, account_id, transaction_id)

    def insert_transaction(
        self,
        account_id: int,
        amount: Decimal,
        counterparty: str,
        type: models.TransactionType,
        status: models.TransactionStatus,
        timestamp: datetime,
    ):
        return insert_transaction(
            self._db,
            account_id,
            amount,
            counterparty,
            type,
            status,
            timestamp,
        )

    def commit(self) -> None:
        commit(self._db)

    def rollback(self) -> None:
        rollback(self._db)

    def refresh(self, *objs) -> None:
        refresh(self._db, *objs)


# Account repository

def get_account(db: Session, account_id: int):
    return (
        db.query(models.Account)
        .options(joinedload(models.Account.member))
        .filter(models.Account.id == account_id)
        .first()
    )

def get_account_for_update(db: Session, account_id: int):
    return (
        db.query(models.Account)
        .filter(models.Account.id == account_id)
        .with_for_update()
        .first()
    )

# Transaction repository

def get_transactions(db: Session, account_id: int):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.account_id == account_id)
        .order_by(models.Transaction.timestamp.desc())
        .all()
    )

def get_transaction(db: Session, account_id: int, transaction_id: int):
    return (
        db.query(models.Transaction)
        .filter(
            models.Transaction.account_id == account_id,
            models.Transaction.id == transaction_id,
        )
        .first()
    )

def insert_transaction(
    db: Session,
    account_id: int,
    amount: Decimal,
    counterparty: str,
    type: models.TransactionType,
    status: models.TransactionStatus,
    timestamp: datetime,
):
    transaction = models.Transaction(
        account_id=account_id,
        amount=amount,
        counterparty=counterparty,
        type=type,
        status=status,
        timestamp=timestamp,
    )
    db.add(transaction)
    db.flush()
    return transaction


def commit(db: Session) -> None:
    """Persist pending changes. Call after service has applied mutations."""
    db.commit()


def rollback(db: Session) -> None:
    """Roll back the current transaction. Call on domain errors."""
    db.rollback()


def refresh(db: Session, *objs) -> None:
    """Reload one or more instances from the database."""
    for obj in objs:
        db.refresh(obj)
