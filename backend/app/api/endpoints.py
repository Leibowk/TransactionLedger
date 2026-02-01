from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, models, db
from ..exceptions import AccountNotFoundError, InsufficientFundsError, InvalidTransitionError, TransactionNotFoundError

router = APIRouter()

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@router.get("/accounts/{account_id}", response_model=schemas.Account)
def read_account(account_id: int, db: Session = Depends(get_db)):
    account = crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.get("/accounts/{account_id}/transactions", response_model=list[schemas.Transaction])
def read_transactions(account_id: int, db: Session = Depends(get_db)):
    return crud.get_transactions(db, account_id)

@router.post("/accounts/{account_id}/transactions", response_model=schemas.Transaction)
def create_transaction(account_id: int, transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_transaction(db, transaction, account_id)
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except InsufficientFundsError:
        raise HTTPException(status_code=400, detail="Insufficient funds")

@router.patch("/accounts/{account_id}/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction_status(
    account_id: int,
    transaction_id: int,
    body: schemas.TransactionStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        return crud.update_transaction_status(db, account_id, transaction_id, body.status)
    except TransactionNotFoundError:
        raise HTTPException(status_code=404, detail="Transaction not found")
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
