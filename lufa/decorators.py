from functools import wraps

from flask import abort, current_app


def debug_only(func):
    """Decorator that restricts endpoint access to debug mode only.

    Returns a 404 error if the application is not running in debug mode.
    Use this decorator for debug-only endpoints that should not be accessible in production.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_app.debug:
            abort(404)
        return func(*args, **kwargs)

    return wrapper
