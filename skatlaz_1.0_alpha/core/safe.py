#core/safe.py
import traceback

def safe_execute(fn, fallback=None, log=True):
    try:
        return fn()
    except Exception:
        if log:
            traceback.print_exc()
        return fallback


def safe_join(lst):
    if not isinstance(lst, list):
        return ""
    return "\n".join(str(x) for x in lst if x)


def safe_list(x):
    return x if isinstance(x, list) else []
