from decimal import Decimal
from datetime import datetime

from fastapi import Depends

from .. import models, schemas
from ..crud import Repository, get_repository
from ..exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidTransitionError,
    TransactionNotFoundError,
)

QUANTIZE = Decimal("0.01")


def get_ledger_service(repo: Repository = Depends(get_repository)) -> "LedgerService":
    """Dependency: yields a request-scoped ledger service with injected repo."""
    return LedgerService(repo)


class LedgerService:
    """Business logic only. Receives repo via DI; no db."""

    def __init__(self, repo: Repository):
        self._repo = repo

    def rollback(self) -> None:
        self._repo.rollback()

    def get_account(self, account_id: int):
        account = self._repo.get_account(account_id)
        if account is None:
            raise AccountNotFoundError("Account not found")
        return account

    def get_transactions(self, account_id: int):
        if self._repo.get_account(account_id) is None:
            raise AccountNotFoundError("Account not found")
        return self._repo.get_transactions(account_id)

    def create_transaction(self, account_id: int, payload: schemas.TransactionCreate):
        account = self._repo.get_account_for_update(account_id)
        if account is None:
            raise AccountNotFoundError("Account not found")

        if payload.type.value == "DEBIT" and account.available_balance < payload.amount:
            raise InsufficientFundsError("Insufficient funds")

        tx_type = (
            models.TransactionType.CREDIT
            if payload.type.value == "CREDIT"
            else models.TransactionType.DEBIT
        )
        transaction = self._repo.insert_transaction(
            account_id=account_id,
            amount=payload.amount,
            counterparty=payload.counterparty,
            type=tx_type,
            status=models.TransactionStatus.PENDING,
            timestamp=datetime.utcnow(),
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

        self._repo.commit()
        self._repo.refresh(transaction)
        return transaction

    def update_transaction_status(
        self, account_id: int, transaction_id: int, new_status: str
    ):
        transaction = self._repo.get_transaction(account_id, transaction_id)
        if transaction is None:
            raise TransactionNotFoundError("Transaction not found")
        if transaction.status != models.TransactionStatus.PENDING:
            raise InvalidTransitionError("Transaction is not pending")
        if new_status not in ("SETTLED", "FAILED"):
            raise InvalidTransitionError("Status must be SETTLED or FAILED")

        account = self._repo.get_account_for_update(account_id)
        if account is None:
            raise AccountNotFoundError("Account not found")

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

        self._repo.commit()
        self._repo.refresh(transaction)
        return transaction
