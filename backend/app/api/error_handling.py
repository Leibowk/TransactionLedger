from fastapi import HTTPException

from ..exceptions import (
    DomainError,
    AccountNotFoundError,
    TransactionNotFoundError,
    InsufficientFundsError,
    InvalidTransitionError,
)
from ..services.ledger_service import LedgerService

DOMAIN_EXCEPTION_TO_HTTP = {
    AccountNotFoundError: (404, "Account not found"),
    TransactionNotFoundError: (404, "Transaction not found"),
    InsufficientFundsError: (400, "Insufficient funds"),
    InvalidTransitionError: (400, lambda e: str(e)),
}


async def handle_domain_exception(e: DomainError, ledger: LedgerService) -> None:
    """Roll back the session and raise an HTTPException from a domain exception."""
    await ledger.rollback()
    pair = DOMAIN_EXCEPTION_TO_HTTP.get(type(e))
    if pair is None:
        raise HTTPException(status_code=500, detail="Internal server error")
    status_code, detail = pair
    if callable(detail):
        detail = detail(e)
    raise HTTPException(status_code=status_code, detail=detail)
