from flask import Blueprint
import requests

bp = Blueprint("giphy", __name__, url_prefix="/giphy")

@bp.route("/<q>")
def giphy(q):
    return requests.get(f"https://api.giphy.com/v1/gifs/search?q={q}&api_key=KEY").json()
