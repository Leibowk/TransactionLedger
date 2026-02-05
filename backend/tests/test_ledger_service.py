"""LedgerService unit tests: business logic with a fake Repository (no DB)."""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidTransitionError,
    TransactionNotFoundError,
)
from app.models import TransactionStatus, TransactionType
from app.schemas import TransactionCreate, TransactionType as SchemaTransactionType
from app.services.ledger_service import LedgerService


def _make_account(available_balance="100.00", current_balance="100.00", id=1):
    acc = MagicMock()
    acc.id = id
    acc.available_balance = Decimal(available_balance)
    acc.current_balance = Decimal(current_balance)
    return acc


def _make_transaction(amount="10.00", type_=TransactionType.CREDIT, status=TransactionStatus.PENDING):
    tx = MagicMock()
    tx.amount = Decimal(amount)
    tx.type = type_
    tx.status = status
    return tx


async def test_get_account_returns_account_when_found():
    repo = MagicMock()
    account = _make_account()
    repo.get_account = AsyncMock(return_value=account)

    service = LedgerService(repo)
    result = await service.get_account(1)

    assert result is account
    repo.get_account.assert_called_once_with(1)


async def test_get_account_raises_when_not_found():
    repo = MagicMock()
    repo.get_account = AsyncMock(return_value=None)

    service = LedgerService(repo)

    with pytest.raises(AccountNotFoundError):
        await service.get_account(1)


async def test_get_transactions_returns_list_when_account_exists():
    repo = MagicMock()
    account = _make_account()
    repo.get_transactions = AsyncMock(return_value=[])

    service = LedgerService(repo)
    result = await service.get_transactions(account.id)

    assert result == []
    repo.get_transactions.assert_called_once_with(account.id)


async def test_create_transaction_raises_insufficient_funds_for_debit():
    repo = MagicMock()
    account = _make_account(available_balance="10.00", current_balance="10.00")
    repo.get_account_for_update = AsyncMock(return_value=account)

    service = LedgerService(repo)
    payload = TransactionCreate(
        amount=Decimal("50.00"),
        counterparty="Store",
        type=SchemaTransactionType.DEBIT,
    )

    with pytest.raises(InsufficientFundsError):
        await service.create_transaction(account, payload)


async def test_create_transaction_credit_calls_save_transaction_and_account():
    repo = MagicMock()
    account = _make_account()
    returned_tx = MagicMock()
    repo.save_transaction_and_account = AsyncMock(return_value=returned_tx)

    service = LedgerService(repo)
    payload = TransactionCreate(
        amount=Decimal("25.00"),
        counterparty="Employer",
        type=SchemaTransactionType.CREDIT,
    )

    result = await service.create_transaction(account, payload)

    assert result is returned_tx
    repo.save_transaction_and_account.assert_called_once()
    call_args = repo.save_transaction_and_account.call_args
    assert call_args[0][1] is account
    assert call_args[0][0].amount == Decimal("25.00")
    assert call_args[0][0].type == TransactionType.CREDIT
    assert account.current_balance == Decimal("125.00")


async def test_create_transaction_debit_updates_balances():
    repo = MagicMock()
    account = _make_account(available_balance="100.00", current_balance="100.00")
    returned_tx = MagicMock()
    repo.save_transaction_and_account = AsyncMock(return_value=returned_tx)

    service = LedgerService(repo)
    payload = TransactionCreate(
        amount=Decimal("30.00"),
        counterparty="Store",
        type=SchemaTransactionType.DEBIT,
    )

    await service.create_transaction(account, payload)

    assert account.available_balance == Decimal("70.00")
    assert account.current_balance == Decimal("70.00")
    repo.save_transaction_and_account.assert_called_once()


async def test_get_transaction_raises_when_not_found():
    repo = MagicMock()
    repo.get_transaction = AsyncMock(return_value=None)

    service = LedgerService(repo)

    with pytest.raises(TransactionNotFoundError):
        await service.get_transaction(1, 99)


async def test_update_transaction_status_raises_when_not_pending():
    repo = MagicMock()
    account = _make_account()
    tx = _make_transaction(status=TransactionStatus.SETTLED)
    repo.get_transaction = AsyncMock(return_value=tx)

    service = LedgerService(repo)

    with pytest.raises(InvalidTransitionError):
        await service.update_transaction_status(account, tx, "SETTLED")


async def test_update_transaction_status_settle_credit_updates_available_balance():
    repo = MagicMock()
    tx = _make_transaction(amount="20.00", type_=TransactionType.CREDIT)
    account = _make_account(available_balance="80.00", current_balance="100.00")

    service = LedgerService(repo)
    result = await service.update_transaction_status(account, tx, "SETTLED")

    assert result is tx
    assert account.available_balance == Decimal("100.00")
