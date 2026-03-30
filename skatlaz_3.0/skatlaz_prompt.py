#pip install requests beautifulsoup4 googlesearch-python sentence-transformers faiss-cpu numpy openai

import os
import json
import time
import requests
import numpy as np
import faiss
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer

# =========================================================
# 🧠 LLM BACKEND (OpenAI opcional / fallback local)
# =========================================================
USE_OPENAI = False  # coloque True se tiver API key

if USE_OPENAI:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def llm(prompt):
    if USE_OPENAI:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    return f"🧠 fallback reasoning: {prompt}"


# =========================================================
# 🧠 MEMORY (VECTOR + LONG TERM)
# =========================================================
embedder = SentenceTransformer("all-MiniLM-L6-v2")

dim = 384
index = faiss.IndexFlatL2(dim)
memory = []


def remember(text):
    v = embedder.encode([text])[0]
    index.add(np.array([v]).astype("float32"))
    memory.append(text)


def recall(query, k=5):
    if not memory:
        return []
    v = embedder.encode([query])[0]
    D, I = index.search(np.array([v]).astype("float32"), k)
    return [memory[i] for i in I[0] if i < len(memory)]


# =========================================================
# 🌐 WEB BRAIN (SEARCH + CRAWL)
# =========================================================
def search_web(query):
    try:
        return [u for u in search(query, num_results=5)]
    except:
        return []


def crawl(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(" ", strip=True)[:2500]
    except:
        return ""


def deep_research(query):
    links = search_web(query)
    data = [crawl(l) for l in links[:3]]
    return "\n".join(data)


# =========================================================
# 🌦️ TOOL: WEATHER
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
# 🧩 AGENT ROLES (multi-cérebro)
# =========================================================

def planner(goal):
    prompt = f"""
Você é um planner de IA.

Objetivo: {goal}

Crie um plano com passos curtos usando:
- search
- crawl
- weather
- reasoning

Retorne apenas passos numerados.
"""
    return llm(prompt)


def researcher(goal):
    return deep_research(goal)


def analyst(data):
    return llm(f"Analise e resuma:\n{data}")


def executor(goal):
    if "clima" in goal or "tempo" in goal:
        return weather(goal.replace("clima", "").strip())

    if "pesquisa" in goal or "buscar" in goal:
        data = deep_research(goal)
        return analyst(data)

    return llm(goal)


# =========================================================
# 🔁 SELF REFLECTION LOOP
# =========================================================
def reflect(output):
    prompt = f"""
Avalie a resposta:

{output}

Ela está boa? Se não, diga como melhorar.
"""
    return llm(prompt)


# =========================================================
# 🧠 GOD CORE LOOP
# =========================================================
def god_agent(goal, cycles=2):
    goal = goal[:3000]

    context = recall(goal)

    plan = planner(goal)

    result = None

    for i in range(cycles):
        execution = executor(goal)

        reflection = reflect(execution)

        result = {
            "goal": goal,
            "memory": context,
            "plan": plan,
            "execution": execution,
            "reflection": reflection
        }

        remember(str(result))

        # auto-improvement loop
        if "melhorar" in reflection.lower():
            goal += " (refinado)"

    return result


# =========================================================
# 💬 CHAT INTERFACE
# =========================================================
if __name__ == "__main__":
    print("\n👑 DEUS+++ TRANSCENDENTAL AI ONLINE\n")

    while True:
        q = input("Você: ")

        if q.lower() in ["sair", "exit", "quit"]:
            break

        try:
            out = god_agent(q, cycles=2)
            print("\n🤖:\n", json.dumps(out, indent=2, ensure_ascii=False), "\n")
        except Exception as e:
            print("Erro:", e)
