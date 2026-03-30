import requests
import json
import numpy as np
import faiss
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer

# =========================================================
# 🧠 GLOBAL MEMORY (RAG SWARM BRAIN)
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
# 🌐 WEB ENGINE (SEARCH + CRAWL)
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
        return soup.get_text(" ", strip=True)[:2000]
    except:
        return ""


def research(query):
    links = search_web(query)
    data = [crawl(l) for l in links[:3]]
    return "\n".join(data)


# =========================================================
# 🧠 SWARM AGENTS
# =========================================================

def planner(query):
    return f"""
[PLANNER]
Objetivo: {query}

Plano:
1. buscar informações
2. analisar evidências
3. gerar hipóteses
4. sintetizar resposta final
"""


def researcher(query):
    return research(query)


def analyst(data):
    return f"[ANALYST]\nResumo analítico:\n{data[:1500]}"


def critic(data):
    return f"[CRITIC]\nPossíveis falhas ou inconsistências:\n- dados incompletos?\n- fontes fracas?\n- viés possível?"


def synthesizer(parts):
    return f"[SYNTHESIZER]\nResposta final:\n{parts}"


# =========================================================
# 🧪 SWARM ORCHESTRATOR
# =========================================================
def swarm(query, cycles=2):
    query = query[:3000]

    memory_context = recall(query)

    plan = planner(query)

    final = None

    for i in range(cycles):

        # 🔎 research
        data = researcher(query)

        # 🧠 analysis
        analysis = analyst(data)

        # ⚖️ critique
        review = critic(data)

        # 🧩 synthesis
        final = synthesizer(
            f"{plan}\n\n{analysis}\n\n{review}"
        )

        # 💾 store experience
        remember(str({
            "query": query,
            "data": data,
            "analysis": analysis,
            "review": review
        }))

        # 🔁 refinement loop
        if "falhas" in review.lower():
            query += " (refinado)"

    return {
        "query": query,
        "memory": memory_context,
        "plan": plan,
        "research": data,
        "analysis": analysis,
        "critique": review,
        "final": final
    }


# =========================================================
# 💬 INTERFACE
# =========================================================
if __name__ == "__main__":
    print("\n🌐👑 OMNISCIENT RESEARCH SWARM ONLINE\n")

    while True:
        q = input("Pergunta: ")

        if q.lower() in ["sair", "exit", "quit"]:
            break

        try:
            result = swarm(q, cycles=2)
            print("\n🧠 RESULTADO FINAL:\n")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("\n")
        except Exception as e:
            print("Erro:", e)
