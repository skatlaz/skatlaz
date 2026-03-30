#agents/planner.py

from llm import llm

class PlannerAgent:

    def run(self, goal):
        result = safe_execute(
            lambda: llm("planner", goal),
            fallback="1. Analyze\n2. Generate answer"
        )

        if not result.strip():
            return "1. Analyze\n2. Generate answer"

        return result


