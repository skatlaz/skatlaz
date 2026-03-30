# oore/bootstrap.py

import builtins
import traceback


def safe_execute(fn, fallback=None, log=True):
    try:
        return fn()
    except Exception:
        if log:
            traceback.print_exc()
        return fallback


def inject_globals():
    builtins.safe_execute = safe_execute
