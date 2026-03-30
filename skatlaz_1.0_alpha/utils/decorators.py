# oore/decorators.py

import builtins
import traceback

from core.safe import safe_execute

def safe(fn):
    def wrapper(*args, **kwargs):
        return safe_execute(lambda: fn(*args, **kwargs))
    return wrapper
