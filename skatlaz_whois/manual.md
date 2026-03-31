## ▶️ Usage Guide

This section explains how to run and use **skatlaz_whois** as a search engine and AI assistant.

---

### 1. Start the Engine

Run the main entrypoint:

```bash
python skatlaz_whois.py
```

This will:
- Initialize the database
- Start the crawler
- Launch the API server (Flask)

Default server:

```
http://localhost:5000
```

---

### 2. Start Crawling Websites

To begin indexing the web, provide a seed URL:

```
GET /start?url=https://example.com
```

Example:

```
http://localhost:5000/start?url=https://wikipedia.org
```

The crawler will:
- Visit the page
- Extract content
- Follow links automatically
- Store results in the database

---

### 3. Perform a Search (Google-style)

```
GET /search?q=your_query
```

Example:

Created as an experimental AI-powered search engine framework.


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
