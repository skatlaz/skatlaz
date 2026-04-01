from flask import Blueprint, request
from skatlaz_scrapgram.auth import send_code, verify_code

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/register", methods=["POST"])
def register():
    send_code(request.json["email"])
    return {"msg": "code sent"}

@bp.route("/verify", methods=["POST"])
def verify():
    if verify_code(request.json["email"], request.json["code"]):
        return {"msg": "ok"}
    return {"error": "invalid"}
