# Product Requirements: TransactionLedger

## 1. Project Overview

The objective is to build a **Transaction Ledger**—a focused web application that acts as a bank account snapshot. The system must provide:

- A clear view of a single account's financial standing
- A detailed history of fund movements
- The ability to initiate and manage new transactions

> In the banking world, accuracy is non-negotiable. This project is designed to test your ability to manage data integrity, handle various transaction states, and build a clean, functional interface for financial data.

---

## 2. Core Functional Requirements

### A. Account Summary

The application must display a **Snapshot** of the current account. This includes:

- **Account Metadata:**
  - Account Name
  - Masked Account Number
- **Dual-Balance Tracking:**
  - **Available Balance:** Funds that are cleared and ready for use
  - **Current Balance:** The total "paper" value of the account (including pending deposits that have not yet cleared)

### B. Transaction Management

Users must be able to view and create transactions through a centralized ledger:

- **The Ledger:**
  - A chronological list of all activity (Deposits and Withdrawals)
- **Transaction Details:**
  - Amount
  - Counterparty (e.g., "Starbucks")
  - Type (Credit/Debit)
  - Status
  - Timestamp
- **Transaction Creation:**
  - A form to initiate new movements of funds
    - **Deposits (Credits):** Should enter the system as `PENDING`
    - **Withdrawals (Debits):** Must immediately deduct from the **Available Balance** to prevent over-spending, but remain `PENDING` until settled

### C. State Transitions

The system must demonstrate a **Settlement** flow to simulate real-world banking:

- Transactions must be able to move from a `PENDING` state to a `SETTLED` or `FAILED` state
- The UI should provide a mechanism to trigger these transitions to demonstrate how balances update in response to status changes

---

## 3. Technical Constraints & Expectations

### Data Integrity

- **ACID Compliance:** The system must ensure that a transaction record and the account balance update are treated as an atomic unit. One cannot succeed without the other.
- **No Floating Points:** All financial math must be handled with decimal precision to avoid rounding errors.

### API Design

Provide a RESTful interface to:

- Fetch account details and balances
- List all transactions
- Create a new transaction
- Update a transaction status (simulating a bank's clearing process)

### User Experience

- The interface should be professional and "fintech-focused"—prioritizing clarity, scannability of data, and immediate feedback for user actions (e.g., showing an error if a withdrawal exceeds the available balance)

---

## 4. Evaluation Criteria

We are looking for:

- **Edge Case Handling:** How does your code handle "Insufficient Funds" or invalid state transitions?
- **Schema Design:** Is your database structured for auditability? Can we see a clear history of what happened and when?
- **Code Quality:** Is your logic separated clearly (e.g., business logic vs. API routing)?