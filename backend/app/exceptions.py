class DomainError(Exception):
    """Base for domain exceptions mapped to HTTP errors."""
    pass


class InsufficientFundsError(DomainError):
    """Raised when a debit would exceed the account's available balance."""
    pass


class AccountNotFoundError(DomainError):
    """Raised when an account is not found (e.g. when locking for update)."""
    pass


class TransactionNotFoundError(DomainError):
    """Raised when a transaction does not exist or does not belong to the given account."""
    pass


class InvalidTransitionError(DomainError):
    """Raised when a transaction status transition is not allowed (e.g. not PENDING)."""
    pass
