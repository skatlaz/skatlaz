from flask import Blueprint
import requests

bp = Blueprint("giphy", __name__, url_prefix="/giphy")

GIPHY_KEY = "YOUR_KEY"

@bp.route("/<q>")
def search(q):
    url = f"https://api.giphy.com/v1/gifs/search?q={q}&api_key={GIPHY_KEY}&limit=5"
    return requests.get(url).json()
