import requests
import json
import numpy as np
import faiss
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer

# =========================================================
# 🧠 GOD MEMORY CORE (RAG)
# =========================================================
embedder = SentenceTransformer("all-MiniLM-L6-v2")

dim = 384
index = faiss.IndexFlatL2(dim)
memory_store = []


def remember(text):
    vec = embedder.encode([text])[0]
    index.add(np.array([vec]).astype("float32"))
    memory_store.append(text)


def recall(query, k=5):
    if not memory_store:
        return []
    vec = embedder.encode([query])[0]
    D, I = index.search(np.array([vec]).astype("float32"), k)
    return [memory_store[i] for i in I[0] if i < len(memory_store)]


# =========================================================
# 🌐 WEB INTELLIGENCE LAYER
# =========================================================
def google_search(query):
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
    links = google_search(query)
    return "\n".join([crawl(l) for l in links[:3]])


# =========================================================
# 🌤️ TOOLS (WEATHER API)
# =========================================================
def get_weather(city="Sao Paulo"):
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        ).json()

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        ).json()

        return weather["current_weather"]
    except:
        return {"error": "weather unavailable"}


# =========================================================
# 🤖 GOD SWARM AGENTS
# =========================================================

def planner(goal):
    return {
        "goal": goal,
        "strategy": [
            "coletar dados da web",
            "extrair conhecimento relevante",
            "analisar padrões",
            "validar inconsistências",
            "gerar síntese final"
        ]
    }


def researcher(goal):
    return deep_research(goal)


def analyst(data):
    return {
        "insights": data[:2000],
        "type": "analysis"
    }


def critic(data):
    return {
        "issues": [
            "dados podem conter ruído",
            "fontes web não verificadas",
            "possível redundância de conteúdo"
        ]
    }


def synthesizer(goal, analysis, memory):
    return f"""
📘 SKATLAZ GOD CORE v2 REPORT

🎯 Objetivo:
{goal}

🧠 Memória relevante:
{memory}

🔎 Análise:
{analysis['insights']}

⚖️ Crítica:
- dados web podem conter inconsistências
- verificação automática limitada

🧾 Conclusão:
Síntese gerada por swarm cognitivo multi-agente Skatlaz AI.
"""


# =========================================================
# 🧠 EXECUTION ENGINE (SWARM LOOP)
# =========================================================
def run_swarm(goal, cycles=2):
    mem = recall(goal)

    final = None

    for _ in range(cycles):
        web_data = researcher(goal)
        analysis = analyst(web_data)
        critique = critic(web_data)

        final = synthesizer(goal, analysis, mem)

        remember(str({
            "goal": goal,
            "web": web_data,
            "analysis": analysis,
            "critique": critique
        }))

    return final


# =========================================================
# 💬 MULTI-MODE CHAT SYSTEM
# =========================================================
def chat(user_input):

    text = user_input.lower()

    # 🌤️ WEATHER MODE
    if "tempo" in text or "clima" in text:
        return get_weather("Sao Paulo")

    # 🔎 RESEARCH MODE
    elif "pesquisa" in text:
        return run_swarm(user_input)

    # 📖 STORY MODE
    elif "história" in text:
        return f"📖 História gerada:\n{user_input} em narrativa estruturada avançada."

    # 💻 CODE MODE
    elif "código" in text or "code" in text:
        return f"💻 Código gerado:\n# Skatlaz AI code engine output for: {user_input}"

    # 💬 GENERAL MODE
    else:
        return f"🤖 Skatlaz Core:\n{user_input}"


# =========================================================
# 🚀 BOOT SEQUENCE (CUSTOM PROMPT QUE VOCÊ PEDIU)
# =========================================================
if __name__ == "__main__":

    print("🤖 Skatlaz AI starting...\n")

    user_input = input("🤖 Ask to Skatlaz:\n")

    while True:

        if user_input.lower() in ["exit", "quit", "sair"]:
            break

        result = chat(user_input)

        print("\n═══════════════════════════\n")
        print(result)
        print("\n═══════════════════════════\n")

        user_input = input("🤖 Ask to Skatlaz:\n")
