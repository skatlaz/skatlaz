# utils/safe.py

import traceback

def safe_execute(fn, fallback=None):
    try:
        return fn()
    except Exception as e:
        print("Erro:", e)
        return fallback


def safe_list(lst):
    return lst if isinstance(lst, list) else []


def safe_str(x):
    return str(x) if x is not None else ""


def safe_join(lst):
    return "\n".join([safe_str(x) for x in safe_list(lst)])
