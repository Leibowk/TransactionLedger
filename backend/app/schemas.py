from pydantic import BaseModel, ConfigDict, condecimal
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

class AccountType(str, enum.Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"

class Member(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip: str
    country: str

class AccountBase(BaseModel):
    name: str
    masked_account_number: str

class Account(AccountBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    account_type: AccountType
    member_id: int
    available_balance: condecimal(max_digits=18, decimal_places=2)
    current_balance: condecimal(max_digits=18, decimal_places=2)
    member: Member

class TransactionBase(BaseModel):
    amount: condecimal(max_digits=18, decimal_places=2)
    counterparty: str
    type: TransactionType

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    account_id: int
    status: TransactionStatus
    timestamp: datetime
