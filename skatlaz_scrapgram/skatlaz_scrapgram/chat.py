from flask import Blueprint, request, jsonify
from skatlaz_scrapgram.models import messages

bp = Blueprint("chat", __name__, url_prefix="/chat")

@bp.route("/send", methods=["POST"])
def send():
    data = request.json
    messages.append(data)
    return {"ok": True}

@bp.route("/list")
def list_msg():
    return jsonify(messages)
