"""LedgerService unit tests: business logic with a fake Repository (no DB)."""
from decimal import Decimal
from unittest.mock import MagicMock

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


def _make_account(available_balance="100.00", current_balance="100.00"):
    acc = MagicMock()
    acc.available_balance = Decimal(available_balance)
    acc.current_balance = Decimal(current_balance)
    return acc


def _make_transaction(amount="10.00", type_=TransactionType.CREDIT, status=TransactionStatus.PENDING):
    tx = MagicMock()
    tx.amount = Decimal(amount)
    tx.type = type_
    tx.status = status
    return tx


def test_get_account_returns_account_when_found():
    repo = MagicMock()
    account = _make_account()
    repo.get_account.return_value = account

    service = LedgerService(repo)
    result = service.get_account(1)

    assert result is account
    repo.get_account.assert_called_once_with(1)


def test_get_account_raises_when_not_found():
    repo = MagicMock()
    repo.get_account.return_value = None

    service = LedgerService(repo)

    with pytest.raises(AccountNotFoundError):
        service.get_account(1)


def test_get_transactions_raises_when_account_not_found():
    repo = MagicMock()
    repo.get_account.return_value = None

    service = LedgerService(repo)

    with pytest.raises(AccountNotFoundError):
        service.get_transactions(1)


def test_get_transactions_returns_list_when_account_exists():
    repo = MagicMock()
    account = _make_account()
    repo.get_account.return_value = account
    repo.get_transactions.return_value = []

    service = LedgerService(repo)
    result = service.get_transactions(1)

    assert result == []
    repo.get_transactions.assert_called_once_with(1)


def test_create_transaction_raises_when_account_not_found():
    repo = MagicMock()
    repo.get_account_for_update.return_value = None

    service = LedgerService(repo)
    payload = TransactionCreate(
        amount=Decimal("10.00"),
        counterparty="X",
        type=SchemaTransactionType.CREDIT,
    )

    with pytest.raises(AccountNotFoundError):
        service.create_transaction(1, payload)


def test_create_transaction_raises_insufficient_funds_for_debit():
    repo = MagicMock()
    account = _make_account(available_balance="10.00", current_balance="10.00")
    repo.get_account_for_update.return_value = account

    service = LedgerService(repo)
    payload = TransactionCreate(
        amount=Decimal("50.00"),
        counterparty="Store",
        type=SchemaTransactionType.DEBIT,
    )

    with pytest.raises(InsufficientFundsError):
        service.create_transaction(1, payload)


def test_create_transaction_credit_calls_commit_and_refresh():
    repo = MagicMock()
    account = _make_account()
    repo.get_account_for_update.return_value = account
    inserted = MagicMock()
    repo.insert_transaction.return_value = inserted

    service = LedgerService(repo)
    payload = TransactionCreate(
        amount=Decimal("25.00"),
        counterparty="Employer",
        type=SchemaTransactionType.CREDIT,
    )

    result = service.create_transaction(1, payload)

    assert result is inserted
    repo.insert_transaction.assert_called_once()
    repo.commit.assert_called_once()
    repo.refresh.assert_called_once_with(inserted)
    assert account.current_balance == Decimal("125.00")


def test_create_transaction_debit_updates_balances():
    repo = MagicMock()
    account = _make_account(available_balance="100.00", current_balance="100.00")
    repo.get_account_for_update.return_value = account
    inserted = MagicMock()
    repo.insert_transaction.return_value = inserted

    service = LedgerService(repo)
    payload = TransactionCreate(
        amount=Decimal("30.00"),
        counterparty="Store",
        type=SchemaTransactionType.DEBIT,
    )

    service.create_transaction(1, payload)

    assert account.available_balance == Decimal("70.00")
    assert account.current_balance == Decimal("70.00")


def test_update_transaction_status_raises_when_transaction_not_found():
    repo = MagicMock()
    repo.get_transaction.return_value = None

    service = LedgerService(repo)

    with pytest.raises(TransactionNotFoundError):
        service.update_transaction_status(1, 99, "SETTLED")


def test_update_transaction_status_raises_when_not_pending():
    repo = MagicMock()
    tx = _make_transaction(status=TransactionStatus.SETTLED)
    repo.get_transaction.return_value = tx

    service = LedgerService(repo)

    with pytest.raises(InvalidTransitionError):
        service.update_transaction_status(1, 1, "SETTLED")


def test_update_transaction_status_raises_when_account_not_found():
    repo = MagicMock()
    tx = _make_transaction()
    repo.get_transaction.return_value = tx
    repo.get_account_for_update.return_value = None

    service = LedgerService(repo)

    with pytest.raises(AccountNotFoundError):
        service.update_transaction_status(1, 1, "SETTLED")


def test_update_transaction_status_settle_credit_updates_available_balance():
    repo = MagicMock()
    tx = _make_transaction(amount="20.00", type_=TransactionType.CREDIT)
    account = _make_account(available_balance="80.00", current_balance="100.00")
    repo.get_transaction.return_value = tx
    repo.get_account_for_update.return_value = account

    service = LedgerService(repo)
    result = service.update_transaction_status(1, 1, "SETTLED")

    assert result is tx
    assert account.available_balance == Decimal("100.00")
    repo.commit.assert_called_once()
    repo.refresh.assert_called_once_with(tx)


def test_rollback_calls_repo_rollback():
    repo = MagicMock()
    service = LedgerService(repo)
    service.rollback()
    repo.rollback.assert_called_once()
