from flask import Blueprint, jsonify
from .auth import admin_required
from .monitor import stats
from .jwt_auth import jwt_required, generate_token

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/stats")
@jwt_required
def s():
    return jsonify(stats())

@bp.route("/users")
@jwt_required
def users():
    return jsonify([u.username for u in users])

@bp.route("/messages")
@jwt_required
def messages_list():
    return jsonify(messages)

@bp.route("/logs")
@jwt_required
def logs():
    return jsonify(get_logs())

@bp.route("/login", methods=["POST"])
def login():
    data = request.json

    if data.get("password") == "admin123":
        return {"token": generate_token()}

    return {"error": "invalid"}, 403
