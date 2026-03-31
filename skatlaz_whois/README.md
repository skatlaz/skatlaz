# skatlaz_whois - Modular Package Structure (pip-ready)

# =========================
# Project Structure
# =========================
# skatlaz_whois/
# ├── skatlaz/
# │   ├── __init__.py
# │   ├── whois.py
# │   ├── database.py
# │   ├── crawler.py
# │   ├── scraper.py
# │   ├── search.py
# │   ├── ai.py
# │   └── api.py
# ├── skatlaz_whois.py  (main entrypoint)
# ├── pyproject.toml
# └── README.md

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

---

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
