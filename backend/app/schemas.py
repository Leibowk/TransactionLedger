from pydantic import BaseModel, condecimal
from typing import Optional
from datetime import datetime
import enum

class TransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"

class AccountBase(BaseModel):
    name: str
    masked_account_number: str

class Account(AccountBase):
    id: int
    available_balance: condecimal(max_digits=18, decimal_places=2)
    current_balance: condecimal(max_digits=18, decimal_places=2)

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    amount: condecimal(max_digits=18, decimal_places=2)
    counterparty: str
    type: TransactionType

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    account_id: int
    status: TransactionStatus
    timestamp: datetime

    class Config:
        orm_mode = True
