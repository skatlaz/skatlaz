from flask import Blueprint, request
from skatlaz_scrapgram.storage.upload import save_file

bp = Blueprint("files", __name__, url_prefix="/files")

@bp.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file:
        return {"error": "no file"}, 400

    path = save_file(file)

    return {"msg": "ok", "path": path}
