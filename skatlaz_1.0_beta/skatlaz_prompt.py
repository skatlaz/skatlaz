#pip install requests beautifulsoup4 googlesearch-python sentence-transformers faiss-cpu numpy

import requests
import numpy as np
import faiss
import json
import time
import re
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer

# =========================================================
# 🧠 EMBEDDINGS MODEL (RAG CORE)
# =========================================================
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# =========================================================
# 💾 VECTOR MEMORY (FAISS)
# =========================================================
dim = 384
index = faiss.IndexFlatL2(dim)
memory_store = []

def add_memory(text):
    vec = embedder.encode([text])[0]
    index.add(np.array([vec]).astype("float32"))
    memory_store.append(text)

def search_memory(query, k=3):
    if len(memory_store) == 0:
        return []
    vec = embedder.encode([query])[0]
    D, I = index.search(np.array([vec]).astype("float32"), k)
    return [memory_store[i] for i in I[0] if i < len(memory_store)]


# =========================================================
# 🛡️ SAFETY LAYER (blindagem)
# =========================================================
def sanitize(text):
    blacklist = ["ignore instructions", "reveal system prompt", "jailbreak"]
    if any(b in text.lower() for b in blacklist):
        return "⚠️ Requisição bloqueada por segurança."
    return text[:3000]


# =========================================================
# 🌐 GOOGLE SEARCH
# =========================================================
def web_search(query):
    try:
        return [url for url in search(query, num_results=5)]
    except:
        return []


# =========================================================
# 🕷️ WEB CRAWLER (multi-page intelligence)
# =========================================================
def crawl(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        return text[:2000]
    except:
        return ""


def deep_crawl(query):
    links = web_search(query)
    data = []
    for l in links[:3]:
        data.append(crawl(l))
    return "\n".join(data)


# =========================================================
# 🌦️ WEATHER (REAL API)
# =========================================================
def weather(city):
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        ).json()

        if "results" not in geo:
            return "Cidade não encontrada."

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        name = geo["results"][0]["name"]

        w = requests.get(
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        ).json()

        temp = w["current_weather"]["temperature"]
        wind = w["current_weather"]["windspeed"]

        return f"🌦️ {name}: {temp}°C | vento {wind} km/h"

    except Exception as e:
        return str(e)


# =========================================================
# 🧠 SIMPLE LLM FALLBACK (pode trocar por HF Inference API)
# =========================================================
def llm(prompt):
    return f"🧠 Resposta (modo deus fallback): {prompt}"


# =========================================================
# 🧩 INTENT ENGINE (AGENT ROUTER)
# =========================================================
def route(query):
    q = query.lower()

    if "clima" in q or "tempo" in q:
        city = re.sub(r"clima|tempo", "", q).strip()
        return weather(city)

    if "pesquise" in q or "buscar" in q:
        data = deep_crawl(query)
        return {"web_context": data}

    if "memória" in q or "lembra" in q:
        return search_memory(query)

    return llm(query)


# =========================================================
# 🤖 GOD AGENT CORE
# =========================================================
def chat(user_input):
    user_input = sanitize(user_input)

    # 🧠 memory retrieval first (RAG)
    memory_context = search_memory(user_input)

    # 🌐 reasoning
    response = route(user_input)

    # 📚 enrich with memory
    if memory_context:
        response = {
            "memory": memory_context,
            "response": response
        }

    # 💾 store memory
    add_memory(user_input)

    return response


# =========================================================
# 💬 CHAT LOOP (GOD MODE)
# =========================================================
if __name__ == "__main__":
    print("\n⚡ GOD AI AGENT ONLINE (WEB + RAG + CRAWL + MEMORY)\n")

    while True:
        msg = input("Você: ")

        if msg.lower() in ["sair", "exit", "quit"]:
            break

        try:
            out = chat(msg)
            print("\n🤖:", out, "\n")
        except Exception as e:
            print("Erro:", e)
