from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

# Account CRUD

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id == account_id).first()

# Transaction CRUD

def get_transactions(db: Session, account_id: int):
    return db.query(models.Transaction).filter(models.Transaction.account_id == account_id).order_by(models.Transaction.timestamp.desc()).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate, account_id: int):
    db_transaction = models.Transaction(
        account_id=account_id,
        amount=transaction.amount,
        counterparty=transaction.counterparty,
        type=transaction.type,
        status=models.TransactionStatus.PENDING,
        timestamp=datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
