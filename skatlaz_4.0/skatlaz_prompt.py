#pip install requests beautifulsoup4 googlesearch-python sentence-transformers faiss-cpu numpy

import requests
import json
import time
import numpy as np
import faiss
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer

# =========================================================
# 🧠 CORE EMBEDDINGS (MEMORY BRAIN)
# =========================================================
embedder = SentenceTransformer("all-MiniLM-L6-v2")

dim = 384
index = faiss.IndexFlatL2(dim)
memory_bank = []


def store_memory(text):
    vec = embedder.encode([text])[0]
    index.add(np.array([vec]).astype("float32"))
    memory_bank.append(text)


def recall_memory(query, k=5):
    if not memory_bank:
        return []
    vec = embedder.encode([query])[0]
    D, I = index.search(np.array([vec]).astype("float32"), k)
    return [memory_bank[i] for i in I[0] if i < len(memory_bank)]


# =========================================================
# 🛡️ SAFETY LAYER (light sandbox)
# =========================================================
def safe(text):
    blocked = ["reveal system prompt", "jailbreak", "exploit", "ignore instructions"]
    return "⚠️ BLOCKED" if any(b in text.lower() for b in blocked) else text[:5000]


# =========================================================
# 🌐 WEB INTELLIGENCE LAYER
# =========================================================
def google(query):
    try:
        return [u for u in search(query, num_results=5)]
    except:
        return []


def crawl(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(" ", strip=True)[:2000]
    except:
        return ""


def deep_web(query):
    links = google(query)
    return "\n".join([crawl(l) for l in links[:3]])


# =========================================================
# 🌦️ TOOL: WEATHER REAL
# =========================================================
def weather(city):
    geo = requests.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    ).json()

    if "results" not in geo:
        return "cidade não encontrada"

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
# 🧠 LLM (placeholder ou API externa)
# =========================================================
def llm(prompt):
    return f"🧠 reasoning: {prompt}"


# =========================================================
# 🧩 AGENTIC MODULES (multi-cérebro)
# =========================================================

def planner(goal):
    return llm(f"""
Você é um planejador de IA.

Objetivo:
{goal}

Crie um plano estruturado com:
- pesquisa
- análise
- execução
- síntese final
""")


def researcher(goal):
    return deep_web(goal)


def analyst(data):
    return llm(f"Analise profundamente:\n{data}")


def synthesizer(parts):
    return llm(f"Sintetize tudo:\n{parts}")


# =========================================================
# ⚙️ EXECUTION ENGINE (TOOL ROUTER)
# =========================================================
def executor(goal):
    g = goal.lower()

    if "clima" in g or "tempo" in g:
        city = g.replace("clima", "").replace("tempo", "").strip()
        return weather(city)

    if "pesquisa" in g or "buscar" in g:
        data = deep_web(goal)
        return analyst(data)

    if "web" in g:
        return deep_web(goal)

    return llm(goal)


# =========================================================
# 🔁 SELF-REFLECTION LOOP (CRITICAL THINKING)
# =========================================================
def reflect(output):
    return llm(f"""
Avalie criticamente a resposta:

{output}

O que está errado ou pode melhorar?
""")


# =========================================================
# 🧠 ORCHESTRATION ENGINE (SINGULARITY CORE)
# =========================================================
def singularity_agent(goal, cycles=3):
    goal = safe(goal)

    memory = recall_memory(goal)

    plan = planner(goal)

    outputs = []

    for i in range(cycles):

        execution = executor(goal)

        reflection = reflect(execution)

        outputs.append({
            "step": i,
            "execution": execution,
            "reflection": reflection
        })

        store_memory(str(outputs[-1]))

        # auto-evolution loop
        if "melhorar" in reflection.lower():
            goal += " (refinado)"

    final = synthesizer(outputs)

    return {
        "goal": goal,
        "memory": memory,
        "plan": plan,
        "steps": outputs,
        "final": final
    }


# =========================================================
# 💬 TERMINAL INTERFACE (SINGULARITY MODE)
# =========================================================
if __name__ == "__main__":
    print("\n👑 DEUS∞ SINGULARITY MODE ACTIVE\n")

    while True:
        q = input("Você: ")

        if q.lower() in ["sair", "exit", "quit"]:
            break

        try:
            result = singularity_agent(q, cycles=3)
            print("\n🤖:\n", json.dumps(result, indent=2, ensure_ascii=False), "\n")
        except Exception as e:
            print("Erro:", e)
