class InsufficientFundsError(Exception):
    """Raised when a debit would exceed the account's available balance."""
    pass


class AccountNotFoundError(Exception):
    """Raised when an account is not found (e.g. when locking for update)."""
    pass


class TransactionNotFoundError(Exception):
    """Raised when a transaction does not exist or does not belong to the given account."""
    pass


class InvalidTransitionError(Exception):
    """Raised when a transaction status transition is not allowed (e.g. not PENDING)."""
    pass
