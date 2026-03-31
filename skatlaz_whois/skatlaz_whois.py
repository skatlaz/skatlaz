# =========================
# skatlaz_whois.py (ENTRYPOINT)
# =========================
from skatlaz.database import init_db
from skatlaz.api import app
from skatlaz.crawler import start


def run():
    init_db()
    start(["https://example.com"])
    app.run(debug=True)


if __name__ == '__main__':
    run()
