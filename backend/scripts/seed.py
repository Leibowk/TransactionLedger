"""
Seed the database with account id=1 and sample transactions.
Run from backend root: python scripts/seed.py
Use --force to delete existing account 1 and re-seed.
Available/current balances are computed from the transaction list.
"""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta

# Ensure backend root is on path and load .env before importing app
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from dotenv import load_dotenv
load_dotenv(backend_root / ".env")

from app.db import SessionLocal
from app.models import Account, Transaction, TransactionType, TransactionStatus, AccountType

# Single source of truth: transaction list. Balances are computed from this.
TRANSACTIONS = [
    {"amount": Decimal("2000.00"), "counterparty": "Employer", "type": TransactionType.CREDIT, "status": TransactionStatus.SETTLED, "days_ago": 10},
    {"amount": Decimal("5.50"), "counterparty": "Starbucks", "type": TransactionType.DEBIT, "status": TransactionStatus.SETTLED, "days_ago": 8},
    {"amount": Decimal("500.00"), "counterparty": "Transfer", "type": TransactionType.CREDIT, "status": TransactionStatus.SETTLED, "days_ago": 7},
    {"amount": Decimal("1200.00"), "counterparty": "Rent", "type": TransactionType.DEBIT, "status": TransactionStatus.SETTLED, "days_ago": 5},
    {"amount": Decimal("49.99"), "counterparty": "Amazon", "type": TransactionType.DEBIT, "status": TransactionStatus.PENDING, "days_ago": 3},
    {"amount": Decimal("25.00"), "counterparty": "Groceries", "type": TransactionType.DEBIT, "status": TransactionStatus.SETTLED, "days_ago": 2},
    {"amount": Decimal("500.00"), "counterparty": "Direct Deposit", "type": TransactionType.CREDIT, "status": TransactionStatus.PENDING, "days_ago": 1},
    {"amount": Decimal("100.00"), "counterparty": "Refund", "type": TransactionType.CREDIT, "status": TransactionStatus.FAILED, "days_ago": 1},
]


def compute_balances(rows):
    """Available = settled credits - all debits. Current = available + pending credits."""
    settled_credits = sum(r["amount"] for r in rows if r["type"] == TransactionType.CREDIT and r["status"] == TransactionStatus.SETTLED)
    all_debits = sum(r["amount"] for r in rows if r["type"] == TransactionType.DEBIT)
    pending_credits = sum(r["amount"] for r in rows if r["type"] == TransactionType.CREDIT and r["status"] == TransactionStatus.PENDING)
    available = (settled_credits - all_debits).quantize(Decimal("0.01"))
    current = (available + pending_credits).quantize(Decimal("0.01"))
    return available, current


def main():
    force = "--force" in sys.argv
    db = SessionLocal()
    try:
        existing = db.query(Account).filter(Account.id == 1).first()
        if existing and not force:
            print("Account id=1 already exists. Skip seeding.")
            return
        if existing and force:
            db.query(Transaction).filter(Transaction.account_id == 1).delete()
            db.delete(existing)
            db.commit()
            print("Removed existing account id=1. Re-seeding.")

        available_balance, current_balance = compute_balances(TRANSACTIONS)

        account = Account(
            id=1,
            name="Primary Checking",
            account_type=AccountType.CHECKING,
            member_id=1,
            account_number="123456784521",
            masked_account_number="****4521",
            available_balance=available_balance,
            current_balance=current_balance,
        )
        db.add(account)
        db.flush()

        now = datetime.utcnow()
        for row in TRANSACTIONS:
            days_ago = row["days_ago"]
            ts = now - timedelta(days=days_ago)
            db.add(
                Transaction(
                    account_id=1,
                    amount=row["amount"],
                    counterparty=row["counterparty"],
                    type=row["type"],
                    status=row["status"],
                    timestamp=ts,
                )
            )

        db.commit()
        print("Seeded account id=1 and", len(TRANSACTIONS), "transactions.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
