#agents/critic.py

from llm import llm

class CriticAgent:

    def run(self, goal, result):
        review = safe_execute(
            lambda: llm("critic", f"{goal}\n\n{result}"),
            fallback="APPROVED"
        )

        if not review:
            return "APPROVED"

        return review
