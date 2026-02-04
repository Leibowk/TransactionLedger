"""Request-scoped dependencies for account and transaction validation."""

from fastapi import Depends, HTTPException

from ..models import Account, Transaction
from ..services.ledger_service import LedgerService, get_ledger_service
from ..exceptions import AccountNotFoundError, TransactionNotFoundError


async def valid_account(
    account_id: int,
    ledger: LedgerService = Depends(get_ledger_service),
) -> Account:
    """Validate account exists; return it or raise 404. Use for read-only endpoints."""
    try:
        return await ledger.get_account(account_id)
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")


async def valid_account_for_update(
    account_id: int,
    ledger: LedgerService = Depends(get_ledger_service),
) -> Account:
    """Validate account exists and return it locked for update. Use for create/update balance."""
    try:
        return await ledger.get_account_for_update(account_id)
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")


async def valid_transaction(
    account_id: int,
    transaction_id: int,
    ledger: LedgerService = Depends(get_ledger_service),
) -> Transaction:
    """Validate transaction exists for the given account; return it or raise 404."""
    try:
        return await ledger.get_transaction(account_id, transaction_id)
    except TransactionNotFoundError:
        raise HTTPException(status_code=404, detail="Transaction not found")
