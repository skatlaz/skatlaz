# =========================
# skatlaz/domain_pipeline.py
# =========================
from .czds import download_zone
from .zone_parser import parse_zone_file
from .domain_db import insert_domains


def run_pipeline(api_key, tld="com"):
    file_path = download_zone(api_key, tld)
    domains = parse_zone_file(file_path)
    insert_domains(domains)

    return len(domains)
