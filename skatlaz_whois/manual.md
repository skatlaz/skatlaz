# SKATLAZ WHOIS

---

## ▶️ Usage Guide

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
