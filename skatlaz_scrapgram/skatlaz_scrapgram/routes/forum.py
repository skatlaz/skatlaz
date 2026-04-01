from flask import Blueprint, request, jsonify
from skatlaz_scrapgram.models import forums

bp = Blueprint("forum", __name__, url_prefix="/forum")

@bp.route("/create", methods=["POST"])
def create():
    data = request.json
    forums.append(data)
    return {"msg": "forum criado"}

@bp.route("/list")
def list_forum():
    return jsonify(forums)

@bp.route("/delete", methods=["POST"])
def delete():
    title = request.json.get("title")
    forums[:] = [f for f in forums if f.get("title") != title]
    return {"msg": "forum deletado"}
