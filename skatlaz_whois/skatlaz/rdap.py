# =========================
# skatlaz/rdap.py
# =========================
import requests

RDAP_SERVERS = {
    "com": "https://rdap.verisign.com/com/v1/domain/",
    "net": "https://rdap.verisign.com/net/v1/domain/",
    "org": "https://rdap.publicinterestregistry.org/rdap/org/domain/"
}


def rdap_lookup(domain):
    tld = domain.split('.')[-1]
    base = RDAP_SERVERS.get(tld)

    if not base:
        return None

    try:
        r = requests.get(base + domain, timeout=5)
        return r.json()
    except:
        return None
