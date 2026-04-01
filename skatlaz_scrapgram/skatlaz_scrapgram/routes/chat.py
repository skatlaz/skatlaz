from flask import Blueprint, request, jsonify
from skatlaz_scrapgram.models import messages

bp = Blueprint("chat", __name__, url_prefix="/chat")

@bp.route("/send", methods=["POST"])
def send_message():
    data = request.json
    messages.append(data)
    return {"msg": "Mensagem enviada"}

@bp.route("/list")
def list_messages():
    return jsonify(messages)

@bp.route("/delete", methods=["POST"])
def delete_message():
    data = request.json
    messages[:] = [m for m in messages if m["id"] != data["id"]]
    return {"msg": "Mensagem deletada"}
