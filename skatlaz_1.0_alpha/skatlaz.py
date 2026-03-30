# skatlaz.py

import sys
from datetime import datetime

# 🔥 importe seu sistema completo
from orchestrator_loop import AutoAgentSystem
from memory.persistent_memory import MultiUserMemory
from core.safe import safe_execute
from core.bootstrap import inject_globals
inject_globals()
from rich import print


# =========================
# CONFIG
# =========================
USER_ID = "default_user"

system = AutoAgentSystem()
memory = MultiUserMemory()


# =========================
# PROMPT BASE (IDENTIDADE)
# =========================
SYSTEM_PROMPT = """
You are SKATLAZ AI.

You are:
- intelligent
- direct
- technical when needed
- capable of coding, research, and creative writing

Always:
- give structured answers
- explain when necessary
- be concise but complete
"""


# =========================
# CORE CHAT
# =========================
def run_chat(user_input):
    # 🔥 memória semântica
    context = "\n".join(memory.retrieve(USER_ID, user_input))

    full_prompt = f"""
{SYSTEM_PROMPT}

Memory:
{context}

User:
{user_input}
"""

    response = system.run(full_prompt)

    # 🔥 salvar memória
    memory.add(USER_ID, f"{datetime.now()} | {user_input}")
    memory.add(USER_ID, response)

    return response


# =========================
# CLI LOOP
# =========================
import traceback


print("safe_execute:", safe_execute)

def main():
    print("\n🚀 SKATLAZ AI (SAFE MODE)\n")
    print("💬 Ask for Skatlaz:\n")
    while True:
        try:
            user = input("> ").strip()

            if not user:
                continue

            if user.lower() in ["exit", "quit"]:
                break

            print("\n🤖 Thinking...\n")

            response = safe_execute(
                lambda: run_chat(user),
                fallback="⚠️ Something went wrong, but system recovered."
            )

            print("\n📢", response, "\n")

        except KeyboardInterrupt:
            break

        except Exception:
            traceback.print_exc()

# =========================
# ENTRYPOINT
# =========================
if __name__ == "__main__":
    main()
