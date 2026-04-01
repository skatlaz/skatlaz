import jwt
import datetime
from functools import wraps
from flask import request, jsonify

SECRET = "super_jwt_secret"

def generate_token():
    payload = {
        "admin": True,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            jwt.decode(token, SECRET, algorithms=["HS256"])
        except:
            return jsonify({"error": "Invalid token"}), 403

        return f(*args, **kwargs)
    return decorated
