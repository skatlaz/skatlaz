# =========================
# skatlaz/api.py
# =========================
from flask import Flask, request, jsonify
from .search import search
from .ai import answer
from .crawler import start

app = Flask(__name__)


@app.route('/search')
def api_search():
    q = request.args.get('q', '')
    results = search(q)

    return jsonify([
        {
            "title": r[0],
            "description": r[1],
            "url": r[2],
            "thumbnail": f"https://image.thum.io/get/{r[2]}"
        }
        for r in results
    ])


@app.route('/ask')
def api_ask():
    q = request.args.get('q', '')
    results = search(q)

    return jsonify({
        "answer": answer(q, results),
        "sources": [r[2] for r in results]
    })


@app.route('/start')
def api_start():
    url = request.args.get('url')
    start([url])
    return jsonify({"status": "started"})
