from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from .exceptions import AccountNotFoundError, InsufficientFundsError, InvalidTransitionError, TransactionNotFoundError
from datetime import datetime

# Account CRUD

def get_account(db: Session, account_id: int):
    return (
        db.query(models.Account)
        .options(joinedload(models.Account.member))
        .filter(models.Account.id == account_id)
        .first()
    )

# Transaction CRUD

def get_transactions(db: Session, account_id: int):
    return db.query(models.Transaction).filter(models.Transaction.account_id == account_id).order_by(models.Transaction.timestamp.desc()).all()

def get_transaction(db: Session, account_id: int, transaction_id: int):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.account_id == account_id, models.Transaction.id == transaction_id)
        .first()
    )

def update_transaction_status(db: Session, account_id: int, transaction_id: int, new_status: str):
    transaction = get_transaction(db, account_id, transaction_id)
    if not transaction:
        raise TransactionNotFoundError("Transaction not found")
    if transaction.status != models.TransactionStatus.PENDING:
        raise InvalidTransitionError("Transaction is not pending")
    if new_status not in ("SETTLED", "FAILED"):
        raise InvalidTransitionError("Status must be SETTLED or FAILED")

    account = (
        db.query(models.Account)
        .filter(models.Account.id == account_id)
        .with_for_update()
        .first()
    )
    if not account:
        raise AccountNotFoundError("Account not found")

    status_enum = models.TransactionStatus.SETTLED if new_status == "SETTLED" else models.TransactionStatus.FAILED
    transaction.status = status_enum

    amount = Decimal(transaction.amount)
    is_credit = transaction.type == models.TransactionType.CREDIT

    if new_status == "SETTLED":
        if is_credit:
            account.available_balance = (account.available_balance + amount).quantize(Decimal("0.01"))
    else:
        if is_credit:
            account.current_balance = (account.current_balance - amount).quantize(Decimal("0.01"))
        else:
            account.available_balance = (account.available_balance + amount).quantize(Decimal("0.01"))
            account.current_balance = (account.current_balance + amount).quantize(Decimal("0.01"))

    db.commit()
    db.refresh(transaction)
    return transaction

def create_transaction(db: Session, transaction: schemas.TransactionCreate, account_id: int):
    account = (
        db.query(models.Account)
        .filter(models.Account.id == account_id)
        .with_for_update()
        .first()
    )
    if not account:
        raise AccountNotFoundError("Account not found")

    is_debit = transaction.type.value == "DEBIT"
    if is_debit:
        if account.available_balance < transaction.amount:
            raise InsufficientFundsError("Insufficient funds")

    db_transaction = models.Transaction(
        account_id=account_id,
        amount=transaction.amount,
        counterparty=transaction.counterparty,
        type=models.TransactionType.CREDIT if transaction.type.value == "CREDIT" else models.TransactionType.DEBIT,
        status=models.TransactionStatus.PENDING,
        timestamp=datetime.utcnow()
    )
    db.add(db_transaction)
    db.flush()

    amount = Decimal(transaction.amount)
    if transaction.type.value == "CREDIT":
        account.current_balance = (account.current_balance + amount).quantize(Decimal("0.01"))
    else:
        account.available_balance = (account.available_balance - amount).quantize(Decimal("0.01"))
        account.current_balance = (account.current_balance - amount).quantize(Decimal("0.01"))

    db.commit()
    db.refresh(db_transaction)
    return db_transaction
