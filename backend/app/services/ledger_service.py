from decimal import Decimal
from datetime import datetime, timezone

from fastapi import Depends

from .. import models, schemas
from ..models import Account, Transaction
from ..crud import Repository, get_repository
from ..exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidTransitionError,
    TransactionNotFoundError,
)

QUANTIZE = Decimal("0.01")


async def get_ledger_service(repo: Repository = Depends(get_repository)) -> "LedgerService":
    """Dependency: yields a request-scoped ledger service with injected repo."""
    return LedgerService(repo)


class LedgerService:
    """Business logic only. Receives repo via DI; no db."""

    def __init__(self, repo: Repository):
        self._repo = repo

    async def get_account(self, account_id: int) -> Account:
        account = await self._repo.get_account(account_id)
        if account is None:
            raise AccountNotFoundError("Account not found")
        return account

    async def get_account_for_update(self, account_id: int) -> Account:
        account = await self._repo.get_account_for_update(account_id)
        if account is None:
            raise AccountNotFoundError("Account not found")
        return account

    async def get_transaction(self, account_id: int, transaction_id: int) -> Transaction:
        transaction = await self._repo.get_transaction(account_id, transaction_id)
        if transaction is None:
            raise TransactionNotFoundError("Transaction not found")
        return transaction

    async def get_transactions(self, account_id: int):
        return await self._repo.get_transactions(account_id)

    async def create_transaction(self, account: Account, payload: schemas.TransactionCreate):
        if payload.type.value == "DEBIT" and account.available_balance < payload.amount:
            raise InsufficientFundsError("Insufficient funds")

        tx_type = (
            models.TransactionType.CREDIT
            if payload.type.value == "CREDIT"
            else models.TransactionType.DEBIT
        )
        transaction = models.Transaction(
            account_id=account.id,
            amount=payload.amount,
            counterparty=payload.counterparty,
            type=tx_type,
            status=models.TransactionStatus.PENDING,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        amount = Decimal(payload.amount).quantize(QUANTIZE)
        if payload.type.value == "CREDIT":
            account.current_balance = (
                account.current_balance + amount
            ).quantize(QUANTIZE)
        else:
            account.available_balance = (
                account.available_balance - amount
            ).quantize(QUANTIZE)
            account.current_balance = (
                account.current_balance - amount
            ).quantize(QUANTIZE)

        return await self._repo.save_transaction_and_account(transaction, account)

    async def update_transaction_status(
        self, account: Account, transaction: Transaction, new_status: str
    ):
        if transaction.status != models.TransactionStatus.PENDING:
            raise InvalidTransitionError("Transaction is not pending")
        if new_status not in ("SETTLED", "FAILED"):
            raise InvalidTransitionError("Status must be SETTLED or FAILED")

        status_enum = (
            models.TransactionStatus.SETTLED
            if new_status == "SETTLED"
            else models.TransactionStatus.FAILED
        )
        transaction.status = status_enum

        amount = Decimal(transaction.amount).quantize(QUANTIZE)
        is_credit = transaction.type == models.TransactionType.CREDIT

        if new_status == "SETTLED":
            if is_credit:
                account.available_balance = (
                    account.available_balance + amount
                ).quantize(QUANTIZE)
        else:
            if is_credit:
                account.current_balance = (
                    account.current_balance - amount
                ).quantize(QUANTIZE)
            else:
                account.available_balance = (
                    account.available_balance + amount
                ).quantize(QUANTIZE)
                account.current_balance = (
                    account.current_balance + amount
                ).quantize(QUANTIZE)

        return transaction
