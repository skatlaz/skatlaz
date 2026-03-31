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

### =========================
### USAGE WHOIS CZDS - EXAMPLE (PRO LEVEL)
### =========================

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

