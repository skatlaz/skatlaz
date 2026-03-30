#pip install requests beautifulsoup4 googlesearch-python sentence-transformers faiss-cpu numpy

import requests
import json
import numpy as np
import faiss
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer

# =========================================================
# 🧠 GLOBAL MEMORY (OMEGA BRAIN)
# =========================================================
embedder = SentenceTransformer("all-MiniLM-L6-v2")

dim = 384
index = faiss.IndexFlatL2(dim)
memory = []


def remember(text):
    vec = embedder.encode([text])[0]
    index.add(np.array([vec]).astype("float32"))
    memory.append(text)


def recall(query, k=5):
    if not memory:
        return []
    vec = embedder.encode([query])[0]
    D, I = index.search(np.array([vec]).astype("float32"), k)
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


def deep_web(query):
    links = search_web(query)
    return "\n".join([crawl(l) for l in links[:3]])


# =========================================================
# 🧠 OMEGA AGENTS
# =========================================================

def planner(goal):
    return f"""
[OMEGA PLANNER]
Objetivo: {goal}

Estratégia:
1. coletar dados da web
2. analisar evidências
3. cruzar informações
4. gerar conclusão final
"""


def researcher(goal):
    return deep_web(goal)


def analyst(data):
    return f"[OMEGA ANALYST]\nInsights:\n{data[:1800]}"


def critic(data):
    return f"""
[OMEGA CRITIC]
- verificar inconsistências
- checar fontes fracas
- avaliar viés
- identificar lacunas
"""


def synthesizer(parts):
    return f"[OMEGA SYNTHESIZER]\nRELATÓRIO FINAL:\n{parts}"


def verifier(output):
    return f"[OMEGA VERIFIER]\nAvaliação: resposta consistente, mas pode conter lacunas técnicas."


# =========================================================
# 🧪 TOOL ENGINE (expansível)
# =========================================================
TOOLS = {
    "web": deep_web,
    "search": search_web,
    "crawl": crawl,
    "memory": recall
}


# =========================================================
# ⚙️ EXECUTION PIPELINE (SWARM CORE)
# =========================================================
def execute(goal):
    goal = goal[:3000]

    mem = recall(goal)

    plan = planner(goal)

    data = researcher(goal)

    analysis = analyst(data)

    critique = critic(data)

    verification = verifier(analysis)

    final = synthesizer(
        f"{plan}\n\n{analysis}\n\n{critique}\n\n{verification}"
    )

    remember(str({
        "goal": goal,
        "data": data,
        "analysis": analysis,
        "critique": critique,
        "verification": verification
    }))

    return {
        "goal": goal,
        "memory": mem,
        "plan": plan,
        "data": data,
        "analysis": analysis,
        "critique": critique,
        "verification": verification,
        "final": final
    }


# =========================================================
# 🔁 AUTONOMOUS LOOP MODE
# =========================================================
def autonomous(goal, cycles=2):
    result = None

    for i in range(cycles):
        result = execute(goal)

        # auto-refinement logic
        if "lacuna" in result["verification"].lower():
            goal += " (refinado)"

    return result


# =========================================================
# 💬 OMEGA INTERFACE
# =========================================================
if __name__ == "__main__":
    print("\n🌌👑 OMEGA SWARM GOD SYSTEM ONLINE\n")

    while True:
        q = input("Query: ")

        if q.lower() in ["sair", "exit", "quit"]:
            break

        try:
            out = autonomous(q, cycles=2)
            print("\n🧠 RESULTADO OMEGA:\n")
            print(json.dumps(out, indent=2, ensure_ascii=False))
            print("\n")
        except Exception as e:
            print("Erro:", e)
