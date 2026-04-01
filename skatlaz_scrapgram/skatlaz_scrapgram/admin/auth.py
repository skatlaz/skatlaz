from functools import wraps
from flask import request

def admin_required(f):
    @wraps(f)
    def wrap(*a, **k):
        if request.headers.get("admin") != "secret":
            return {"error": "no"}, 403
        return f(*a, **k)
    return wrap
