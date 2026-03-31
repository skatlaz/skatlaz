![SKATLAZ.COM](../assets/skatlaz.png)

## skatlaz_whois - Modular Package Structure (pip-ready)

### 🧠 How its works:

from skatlaz import whois, database, crawler, ai

### ▶️ RUNNING ONLY:

skatlaz_whois

or with code:

from skatlaz_whois import run
run()

### 📦 INSTALL:

pip install skatlaz_whois

## 📁 Project Structure

---

### 🤖 AI Answer

```
GET /ask?q=your_question
```

Returns:
- AI-generated answer
- sources used

---

### 🕷️ Start crawler

```
GET /start?url=https://example.com
```

---

## 🧠 AI Configuration

Install OpenAI-compatible client:

```bash
pip install openai
```

Set your API key:

```bash
export OPENAI_API_KEY="your_api_key"
```

If not configured, AI responses will be disabled.

---

## 🧩 Module Usage Example

```python
from skatlaz import search, crawler, ai

results = search.search("python")
answer = ai.answer("What is Python?", results)

crawler.start(["https://example.com"])
```

 =========================
 USAGE WHOIS CZDS - EXAMPLE (PRO LEVEL)
 =========================

```python
from skatlaz.domain_pipeline import run_pipeline
from skatlaz.rdap import rdap_lookup
from skatlaz.whois_cache import get_cached, save_cache

# 1. Download + parse + store millions of domains
count = run_pipeline("YOUR_CZDS_API_KEY", "com")
print("Imported domains:", count)

# 2. RDAP lookup
info = rdap_lookup("google.com")

# 3. Cache WHOIS
if not get_cached("google.com"):
    save_cache("google.com", str(info))
```
ADVANCED CRAWLER

```python
from skatlaz.advanced_crawler import analyze

results = analyze(keyword)
```

RETURN

```json
{
  "site": "www.uol.com.br",
  "description": "UOL - O melhor conteúdo",
  "sections": [
    {
      "name": "Notícias",
      "url": "https://www.uol.com.br/noticias/"
    },
    {
      "name": "Esportes",
      "url": "https://www.uol.com.br/esporte/"
    }
  ],
  "thumbnail": "data:image/gif;base64,R0lGODlh...",
  "thumbnail_path": "thumbnail-1234567890.gif",
  "breadcrumbs": [
    {
      "name": "Home",
      "url": "https://www.uol.com.br/"
    },
    {
      "name": "Notícias",
      "url": "https://www.uol.com.br/noticias/"
    }
  ],
  "search_results": [
    {
      "title": "Título da página encontrada",
      "url": "https://www.uol.com.br/noticias/artigo.html",
      "score": 28,
      "matched_words": ["notícias", "política"],
      "snippet": "...texto com <strong>destaque</strong> da busca..."
    }
  ],
  "internal_pages": [
    {
      "url": "https://www.uol.com.br/noticias/",
      "depth": 1,
      "title": "Últimas Notícias",
      "word_count": 1250
    }
  ],
  "content_index": {
    "https://www.uol.com.br/": {
      "title": "UOL - O melhor conteúdo",
      "url": "https://www.uol.com.br/",
      "top_words": [
        {"word": "notícias", "count": 45},
        {"word": "brasil", "count": 32}
      ],
      "text_snippet": "Primeiros 500 caracteres do texto...",
      "word_count": 2500
    }
  }
}
```
---

 =========================
 RUN EVERYTHING
 =========================

 1. Build and start all services
 docker-compose up --build

 2. Access API
 http://localhost:5000

 3. Start crawler
 http://localhost:5000/start?url=https://wikipedia.org

 4. Search
 http://localhost:5000/search?q=python

 5. AI
 http://localhost:5000/ask?q=What is Python?

 =========================
 NOTES
 =========================
 - Elasticsearch may take ~30s to start
 - PostgreSQL persists data in volume
 - Redis handles crawl queue
 - Worker runs crawling in background

 =========================
 RESULT
 =========================
 One command:
 docker-compose up --build

 You now have:
 - Search engine
 - AI answers
 - Distributed crawler
 - Domain intelligence base

 Running locally like a real startup stack 🚀
 
## ⚠️ Limitations

- Basic ranking (no PageRank yet)
- Simple LIKE-based search (no full-text index)
- No robots.txt compliance
- No distributed crawling

---

## 🛣️ Roadmap

- [ ] Semantic search (embeddings)
- [ ] PageRank implementation
- [ ] Distributed crawler
- [ ] Frontend UI (Google-like)
- [ ] Docker support
- [ ] ElasticSearch integration

---

## 📜 License

MIT License

---

## 💡 Inspiration

- Google Search
- Perplexity AI
- Bing AI

---

## 🤝 Contribution

Pull requests are welcome.
For major changes, open an issue first to discuss what you would like to change.

---

## 👨‍💻 Author

Created as an experimental AI-powered search engine framework.

