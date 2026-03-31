# =========================
# skatlaz/crawler.py
# =========================
import threading, time
from .scraper import scrape
from .whois import save

visited = set()
queue = []


def worker():
    while True:
        if queue:
            url = queue.pop(0)
            if url in visited:
                continue

            visited.add(url)
            data = scrape(url)

            if not data:
                continue

            save(url, data)

            for link in data['links']:
                if link not in visited and len(queue) < 100:
                    queue.append(link)

        time.sleep(1)


def start(seed_urls):
    queue.extend(seed_urls)
    t = threading.Thread(target=worker, daemon=True)
    t.start()
