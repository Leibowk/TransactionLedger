from fastapi import APIRouter, Depends

from .. import schemas
from ..services.ledger_service import LedgerService, get_ledger_service
from ..exceptions import DomainError
from .error_handling import handle_domain_exception

router = APIRouter()


@router.get("/accounts/{account_id}", response_model=schemas.Account)
def read_account(account_id: int, ledger: LedgerService = Depends(get_ledger_service)):
    try:
        return ledger.get_account(account_id)
    except DomainError as e:
        handle_domain_exception(e, ledger)


@router.get("/accounts/{account_id}/transactions", response_model=list[schemas.Transaction])
def read_transactions(
    account_id: int, ledger: LedgerService = Depends(get_ledger_service)
):
    try:
        return ledger.get_transactions(account_id)
    except DomainError as e:
        handle_domain_exception(e, ledger)


@router.post("/accounts/{account_id}/transactions", response_model=schemas.Transaction)
def create_transaction(
    account_id: int,
    transaction: schemas.TransactionCreate,
    ledger: LedgerService = Depends(get_ledger_service),
):
    try:
        return ledger.create_transaction(account_id, transaction)
    except DomainError as e:
        handle_domain_exception(e, ledger)


@router.patch(
    "/accounts/{account_id}/transactions/{transaction_id}",
    response_model=schemas.Transaction,
)
def update_transaction_status(
    account_id: int,
    transaction_id: int,
    body: schemas.TransactionStatusUpdate,
    ledger: LedgerService = Depends(get_ledger_service),
):
    try:
        return ledger.update_transaction_status(
            account_id, transaction_id, body.status
        )
    except DomainError as e:
        handle_domain_exception(e, ledger)
