# pip install requests beautifulsoup4 googlesearch-python sentence-transformers faiss-cpu numpy

import requests
import json
import numpy as np
import faiss
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer

# =========================================================
# 🧠 OMEGA MEMORY CORE (RAG)
# =========================================================
embedder = SentenceTransformer("all-MiniLM-L6-v2")

dim = 384
index = faiss.IndexFlatL2(dim)
memory_store = []


def remember(text: str):
    vec = embedder.encode([text])[0]
    index.add(np.array([vec]).astype("float32"))
    memory_store.append(text)


def recall(query: str, k=5):
    if not memory_store:
        return []
    vec = embedder.encode([query])[0]
    D, I = index.search(np.array([vec]).astype("float32"), k)
    return [memory_store[i] for i in I[0] if i < len(memory_store)]


# =========================================================
# 🌐 WEB LAYER (GOOGLE + SCRAPING)
# =========================================================
def google_search(query, limit=5):
    try:
        return [url for url in search(query, num_results=limit)]
    except:
        return []


def scrape(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        return text[:2500]
    except:
        return ""


def web_research(query):
    urls = google_search(query)
    contents = [scrape(u) for u in urls[:3]]
    return "\n".join(contents)


# =========================================================
# 🧠 OMEGA AGENTS
# =========================================================

def planner(goal):
    return {
        "goal": goal,
        "steps": [
            "buscar dados na web",
            "extrair informações relevantes",
            "analisar padrões",
            "validar consistência",
            "gerar resposta final estruturada"
        ]
    }


def researcher(goal):
    return web_research(goal)


def analyst(data):
    return {
        "insights": data[:2000],
        "type": "analysis"
    }


def critic(data):
    return {
        "issues": [
            "possível informação incompleta",
            "fontes podem ser redundantes",
            "verificar confiabilidade"
        ]
    }


def writer(goal, analysis, memory):
    return f"""
# 📘 RELATÓRIO FINAL OMEGA+

## 🎯 Objetivo
{goal}

## 🧠 Memória relevante
{memory}

## 🔎 Análise
{analysis['insights']}

## ⚖️ Crítica
- possível viés em fontes web
- dados não verificados totalmente

## 🧾 Conclusão
Síntese baseada em múltiplas fontes web + memória vetorial.
"""


# =========================================================
# 🔁 OMEGA ORCHESTRATOR (SWARM LOOP)
# =========================================================
def run_omega(goal, cycles=2):
    goal = goal[:3000]

    mem = recall(goal)

    plan = planner(goal)

    final = None

    for i in range(cycles):
        web_data = researcher(goal)

        analysis = analyst(web_data)

        critique = critic(web_data)

        final = writer(goal, analysis, mem)

        remember(str({
            "goal": goal,
            "web": web_data,
            "analysis": analysis,
            "critique": critique
        }))

        # auto-refinement simples
        if "incompleta" in str(critique):
            goal += " mais detalhes técnicos"

    return {
        "goal": goal,
        "plan": plan,
        "memory": mem,
        "analysis": analysis,
        "critique": critique,
        "final_report": final
    }


# =========================================================
# 💬 CHAT MODE (EXTENSÍVEL)
# =========================================================
def chat(user_input):
    if "pesquisa" in user_input.lower():
        return run_omega(user_input)

    elif "história" in user_input.lower():
        return f"📖 História gerada:\n{user_input} em versão narrativa estruturada."

    elif "tempo" in user_input.lower():
        return "🌤️ Use API de clima (Open-Meteo ou WeatherAPI) para dados reais."

    else:
        return f"💬 Resposta padrão inteligente: {user_input}"


# =========================================================
# 🚀 MAIN LOOP
# =========================================================
if __name__ == "__main__":
    print("\n💀 OMEGA+ GOD RESEARCH PLATFORM ONLINE\n")

    while True:
        q = input("Query: ")

        if q.lower() in ["exit", "quit", "sair"]:
            break

        try:
            result = chat(q)
            print("\n🧠 OUTPUT:\n")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("\n")
        except Exception as e:
            print("Erro:", e)
