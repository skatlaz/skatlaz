# =========================
# skatlaz/whois_cache.py
# =========================
import requests
from .database import connect


def get_cached(domain):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT data FROM whois_cache WHERE domain=?", (domain,))
    row = cur.fetchone()

    conn.close()

    return row[0] if row else None


def save_cache(domain, data):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO whois_cache (domain, data, updated_at)
    VALUES (?, ?, datetime('now'))
    """, (domain, data))

    conn.commit()
    conn.close()
