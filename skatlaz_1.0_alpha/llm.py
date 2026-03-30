from utils.safe import safe_execute, safe_join

def llm(user_id, prompt):
    def run():
        mem = memory.retrieve(user_id, prompt)
        context = safe_join(mem)

        final_prompt = f"""
Memory:
{context}

User:
{prompt}

Assistant:
"""

        return generate_text(final_prompt)

    response = safe_execute(run, fallback="Sorry, I had an internal error.")

    # nunca quebrar
    try:
        memory.add(user_id, f"{prompt} -> {response}")
    except:
        pass

    return response
