import functools
from django.core.management.base import CommandError
from utils.logger import logger  

def exception_handler(func):
    """
    Decorator for Django management command methods (e.g., handle()).
    Wraps the function in a try/except block to catch common exceptions,
    log them, and raise a CommandError for Django’s management command interface.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, AttributeError, TypeError, KeyError, IndexError) as err:
            logger.error(f"Handled known exception: {err}", exc_info=True)
            raise CommandError(f"Execution halted due to: {err}")
        except Exception as err:
            logger.error("Unhandled exception occurred", exc_info=True)
            raise CommandError("An unexpected error occurred. See logs for details.")
    return wrapper
