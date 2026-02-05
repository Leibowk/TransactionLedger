from decimal import Decimal
from datetime import datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .db import get_db


def get_repository(db: AsyncSession = Depends(get_db)) -> "Repository":
    """Dependency: yields a request-scoped repository (crud + session)."""
    return Repository(db)


class Repository:
    """Holds the async DB session. Only crud layer touches db."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_account(self, account_id: int):
        result = await self._db.execute(
            select(models.Account)
            .options(joinedload(models.Account.member))
            .where(models.Account.id == account_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_account_for_update(self, account_id: int):
        result = await self._db.execute(
            select(models.Account)
            .where(models.Account.id == account_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_transactions(self, account_id: int):
        result = await self._db.execute(
            select(models.Transaction)
            .where(models.Transaction.account_id == account_id)
            .order_by(models.Transaction.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_transaction(self, account_id: int, transaction_id: int):
        result = await self._db.execute(
            select(models.Transaction).where(
                models.Transaction.account_id == account_id,
                models.Transaction.id == transaction_id,
            )
        )
        return result.scalar_one_or_none()

    async def insert_transaction(
        self,
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
        self._db.add(transaction)
        await self._db.flush()
        return transaction

    async def save_transaction_and_account(
        self, transaction: models.Transaction, account: models.Account
    ) -> models.Transaction:
        """Add transaction and flush; account is already tracked and mutated."""
        self._db.add(transaction)
        await self._db.flush()
        return transaction

    async def rollback(self) -> None:
        await self._db.rollback()
