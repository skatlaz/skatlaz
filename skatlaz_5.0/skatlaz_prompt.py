#pip install requests beautifulsoup4 googlesearch-python sentence-transformers faiss-cpu numpy

import requests
import json
import numpy as np
import faiss
from bs4 import BeautifulSoup
from googlesearch import search
from sentence_transformers import SentenceTransformer
import time

# =========================================================
# 🧠 SCIENTIFIC MEMORY (RAG CORE)
# =========================================================
embedder = SentenceTransformer("all-MiniLM-L6-v2")

dim = 384
index = faiss.IndexFlatL2(dim)
memory = []


def store(text):
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
# 🌐 SCIENTIFIC WEB RESEARCH LAYER
# =========================================================
def search_web(query):
    try:
        return [u for u in search(query, num_results=5)]
    except:
        return []


def fetch(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(" ", strip=True)[:2500]
    except:
        return ""


def research_paper(query):
    links = search_web(query)
    return [fetch(l) for l in links[:3]]


# =========================================================
# 🧠 SCIENTIFIC LLM (fallback or API hook)
# =========================================================
def llm(prompt):
    return f"🧠 scientific reasoning:\n{prompt}"


# =========================================================
# 🔬 SCIENTIFIC PLANNER
# =========================================================
def planner(question):
    return llm(f"""
Você é um cientista IA.

Pergunta:
{question}

Crie um plano científico:
1. hipóteses
2. busca de evidências
3. análise
4. conclusão
""")


# =========================================================
# 📚 EVIDENCE ANALYZER
# =========================================================
def analyze(evidence):
    return llm(f"""
Analise os seguintes dados científicos:

{evidence}

Extraia:
- padrões
- insights
- possíveis explicações
""")


# =========================================================
# 🧪 HYPOTHESIS GENERATOR
# =========================================================
def hypothesis(question, context):
    return llm(f"""
Baseado na pergunta:
{question}

E contexto:
{context}

Gere hipóteses científicas plausíveis.
""")


# =========================================================
# 🔁 SCIENTIFIC REFLECTION LOOP
# =========================================================
def reflect(answer):
    return llm(f"""
Revise criticamente esta resposta científica:

{answer}

Está correta? O que falta? Quais erros potenciais?
""")


# =========================================================
# ⚛️ AUTONOMOUS SCIENTIST CORE
# =========================================================
def scientist(question, cycles=3):
    question = question[:3000]

    context_memory = recall(question)

    plan = planner(question)

    evidence = research_paper(question)

    hypothesis_block = hypothesis(question, evidence)

    final_output = None

    for i in range(cycles):

        analysis = analyze(evidence)

        reflection = reflect(analysis)

        final_output = {
            "question": question,
            "memory": context_memory,
            "plan": plan,
            "evidence": evidence,
            "hypothesis": hypothesis_block,
            "analysis": analysis,
            "reflection": reflection,
            "cycle": i
        }

        store(str(final_output))

        # auto-refinement loop
        if "falta" in reflection.lower():
            question += " (refinado)"

    return final_output


# =========================================================
# 💬 SCIENTIFIC CHAT INTERFACE
# =========================================================
if __name__ == "__main__":
    print("\n⚛️ SINGULARITY++ AUTONOMOUS SCIENTIST ONLINE\n")

    while True:
        q = input("Pergunta científica: ")

        if q.lower() in ["sair", "exit", "quit"]:
            break

        try:
            result = scientist(q, cycles=3)
            print("\n🧪 RESULTADO:\n")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("\n")
        except Exception as e:
            print("Erro:", e)
