from flask import Blueprint, request, jsonify
from skatlaz_scrapgram.models import users, User
from skatlaz_scrapgram.auth import send_email_code, verify_code

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/register", methods=["POST"])
def register():
    data = request.json
    send_email_code(data["email"])
    return {"msg": "Código enviado"}

@bp.route("/verify", methods=["POST"])
def verify():
    data = request.json
    if verify_code(data["email"], data["code"]):
        user = User(data["username"], data["email"])
        users.append(user)
        return {"msg": "Usuário criado"}
    return {"error": "Código inválido"}, 400

@bp.route("/search/<username>")
def search(username):
    result = [u.username for u in users if username in u.username]
    return jsonify(result)
