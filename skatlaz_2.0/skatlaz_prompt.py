#pip install requests beautifulsoup4 googlesearch-python sentence-transformers faiss-cpu numpy

import requests
import json
import time
import re
import numpy as np
import faiss
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer

# =========================================================
# 🧠 EMBEDDINGS (RAG CORE)
# =========================================================
embedder = SentenceTransformer("all-MiniLM-L6-v2")

dim = 384
index = faiss.IndexFlatL2(dim)
memory_store = []


def add_memory(text):
    vec = embedder.encode([text])[0]
    index.add(np.array([vec]).astype("float32"))
    memory_store.append(text)


def search_memory(query, k=5):
    if len(memory_store) == 0:
        return []
    vec = embedder.encode([query])[0]
    D, I = index.search(np.array([vec]).astype("float32"), k)
    return [memory_store[i] for i in I[0] if i < len(memory_store)]


# =========================================================
# 🛡️ SAFETY LAYER (basic sandbox)
# =========================================================
def sanitize(text):
    blacklist = ["reveal system prompt", "ignore instructions", "jailbreak", "exploit"]
    if any(b in text.lower() for b in blacklist):
        return "⚠️ BLOQUEADO"
    return text[:4000]


# =========================================================
# 🌐 WEB TOOLS
# =========================================================
def google_search(query):
    try:
        return [url for url in search(query, num_results=5)]
    except:
        return []


def scrape(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(" ", strip=True)[:2000]
    except:
        return ""


def deep_web(query):
    links = google_search(query)
    return "\n".join([scrape(l) for l in links[:3]])


# =========================================================
# 🌦️ WEATHER (REAL API)
# =========================================================
def weather(city):
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

    t = w["current_weather"]["temperature"]
    wind = w["current_weather"]["windspeed"]

    return f"🌦️ {name}: {t}°C | vento {wind} km/h"


# =========================================================
# 🧠 BASIC LLM FALLBACK
# =========================================================
def llm(prompt):
    return f"🧠 (fallback) {prompt}"


# =========================================================
# 🧩 TOOL SYSTEM
# =========================================================
TOOLS = {
    "weather": weather,
    "web": deep_web,
    "search": google_search,
    "memory": search_memory
}


# =========================================================
# 🧠 PLANNER (AUTONOMOUS DECISION MAKER)
# =========================================================
def planner(goal):
    g = goal.lower()

    plan = []

    if "clima" in g or "tempo" in g:
        plan.append(("weather", goal))

    elif "pesquisa" in g or "buscar" in g:
        plan.append(("web", goal))

    elif "lembrar" in g:
        plan.append(("memory", goal))

    else:
        plan.append(("llm", goal))

    return plan


# =========================================================
# ⚙️ EXECUTOR
# =========================================================
def executor(plan):
    results = []

    for tool, arg in plan:
        if tool in TOOLS:
            try:
                results.append(TOOLS[tool](arg))
            except:
                results.append("Erro tool")
        else:
            results.append(llm(arg))

    return results


# =========================================================
# 🧠 REFLECTION LOOP (AUTO IMPROVEMENT SIMULATION)
# =========================================================
def reflect(results):
    if any("Erro" in str(r) for r in results):
        return "⚠️ Ajuste necessário no plano"
    return "✔️ Execução bem-sucedida"


# =========================================================
# 🤖 DEUS++ AGENT CORE
# =========================================================
def agent(goal, loops=2):
    goal = sanitize(goal)

    context = search_memory(goal)

    final_output = None

    for i in range(loops):
        plan = planner(goal)

        results = executor(plan)

        reflection = reflect(results)

        final_output = {
            "goal": goal,
            "memory": context,
            "plan": plan,
            "results": results,
            "reflection": reflection
        }

        # auto memory update
        add_memory(str(final_output))

        # loop autonomy (refine goal if needed)
        if "Erro" in reflection:
            goal += " (retry improved)"

    return final_output


# =========================================================
# 💬 INTERFACE DEUS MODE
# =========================================================
if __name__ == "__main__":
    print("\n👑 DEUS++ AUTONOMOUS AGENT ONLINE\n")

    while True:
        user = input("Você: ")

        if user.lower() in ["sair", "exit", "quit"]:
            break

        try:
            output = agent(user, loops=2)
            print("\n🤖:", json.dumps(output, indent=2, ensure_ascii=False), "\n")
        except Exception as e:
            print("Erro:", e)
