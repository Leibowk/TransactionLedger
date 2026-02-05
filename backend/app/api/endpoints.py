from fastapi import APIRouter, Depends

from .. import schemas
from ..models import Account
from ..services.ledger_service import LedgerService, get_ledger_service
from ..exceptions import DomainError
from .error_handling import handle_domain_exception
from .dependencies import (
    valid_account,
    valid_account_for_update,
    valid_transaction,
)

router = APIRouter()

RESPONSE_404 = {404: {"description": "Not found"}}


@router.get(
    "/accounts/{account_id}",
    response_model=schemas.Account,
    responses=RESPONSE_404,
)
async def read_account(account: Account = Depends(valid_account)):
    """Account existence validated by valid_account dependency; return it."""
    return account


@router.get(
    "/accounts/{account_id}/transactions",
    response_model=list[schemas.Transaction],
    responses=RESPONSE_404,
)
async def read_transactions(
    account: Account = Depends(valid_account),
    ledger: LedgerService = Depends(get_ledger_service),
):
    return await ledger.get_transactions(account.id)


@router.post(
    "/accounts/{account_id}/transactions",
    response_model=schemas.Transaction,
    responses=RESPONSE_404,
)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    account=Depends(valid_account_for_update),
    ledger: LedgerService = Depends(get_ledger_service),
):
    try:
        return await ledger.create_transaction(account, transaction)
    except DomainError as e:
        await handle_domain_exception(e)


@router.patch(
    "/accounts/{account_id}/transactions/{transaction_id}",
    response_model=schemas.Transaction,
    responses=RESPONSE_404,
)
async def update_transaction_status(
    body: schemas.TransactionStatusUpdate,
    account=Depends(valid_account_for_update),
    transaction=Depends(valid_transaction),
    ledger: LedgerService = Depends(get_ledger_service),
):
    try:
        return await ledger.update_transaction_status(account, transaction, body.status)
    except DomainError as e:
        await handle_domain_exception(e)
