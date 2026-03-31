# =========================
# skatlaz/zone_parser.py
# =========================

def parse_zone_file(file_path):
    domains = []

    with open(file_path, "r", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) > 0:
                domain = parts[0].rstrip('.')
                domains.append(domain)

    return domains
