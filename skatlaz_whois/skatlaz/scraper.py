# =========================
# skatlaz/scraper.py
# =========================
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def scrape(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')

        title = soup.title.string if soup.title else ''
        desc = soup.find('meta', attrs={'name': 'description'})
        description = desc['content'] if desc else ''

        content = ' '.join([p.get_text() for p in soup.find_all('p')])

        links = []
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a['href'])
            if urlparse(href).scheme in ['http', 'https']:
                links.append(href)

        return {
            "title": title,
            "description": description,
            "content": content[:5000],
            "links": list(set(links))[:20]
        }
    except:
        return None
