# =========================
# skatlaz/czds.py
# =========================
import requests
import os

CZDS_BASE = "https://czds.icann.org"


def download_zone(api_key, tld, output_dir="zones"):
    os.makedirs(output_dir, exist_ok=True)

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    url = f"{CZDS_BASE}/czds/downloads/{tld}.zone"

    r = requests.get(url, headers=headers, stream=True)

    file_path = os.path.join(output_dir, f"{tld}.zone")

    with open(file_path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    return file_path
