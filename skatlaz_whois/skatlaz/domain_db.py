# =========================
# skatlaz/domain_db.py
# =========================
from .database import connect


def init_domain_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS domains (
        domain TEXT PRIMARY KEY,
        tld TEXT,
        last_checked TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS whois_cache (
        domain TEXT PRIMARY KEY,
        data TEXT,
        updated_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_domains(domains):
    conn = connect()
    cur = conn.cursor()

    for d in domains:
        tld = d.split('.')[-1]
        try:
            cur.execute("INSERT OR IGNORE INTO domains VALUES (?, ?, datetime('now'))", (d, tld))
        except:
            pass

    conn.commit()
    conn.close()
