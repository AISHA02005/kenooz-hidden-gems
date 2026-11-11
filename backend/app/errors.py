from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.exc import TimeoutError as PoolTimeoutError

# Errors that mean "the database is unreachable / overloaded" (retryable).
DB_UNAVAILABLE_ERRORS = (OperationalError, InterfaceError, PoolTimeoutError)

DB_UNAVAILABLE_MESSAGE = "The service is temporarily unavailable. Please try again in a moment."
SUBMISSION_FAILED_MESSAGE = "Failed to save place submission. Please try again."


def is_db_unavailable(exc: BaseException) -> bool:
    return isinstance(exc, DB_UNAVAILABLE_ERRORS)