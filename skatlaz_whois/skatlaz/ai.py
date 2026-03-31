# =========================
# skatlaz/ai.py
# =========================
try:
    from openai import OpenAI
    client = OpenAI()
    ENABLED = True
except:
    ENABLED = False


def answer(query, results):
    if not ENABLED:
        return "AI not configured"

    context = "\n\n".join([r[3][:1000] for r in results])

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": f"Question: {query}\nContext:\n{context}"}
        ]
    )

    return response.choices[0].message.content

