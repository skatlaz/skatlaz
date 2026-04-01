from flask import Blueprint, request, jsonify
from skatlaz_scrapgram.models import groups

bp = Blueprint("groups", __name__, url_prefix="/groups")

@bp.route("/create", methods=["POST"])
def create():
    data = request.json
    groups.append(data)
    return {"msg": "grupo criado"}

@bp.route("/list")
def list_groups():
    return jsonify(groups)

@bp.route("/delete", methods=["POST"])
def delete():
    name = request.json.get("name")
    groups[:] = [g for g in groups if g.get("name") != name]
    return {"msg": "grupo deletado"}
