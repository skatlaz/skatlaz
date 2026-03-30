#orchestrator.py
from agents.manager import ManagerAgent
from agents.research import ResearchAgent
from agents.code import CodeAgent
from agents.creative import CreativeAgent
from agents.game import GameAgent


class Orchestrator:

    def __init__(self):
        self.manager = ManagerAgent()

        self.agents = {
            "research": ResearchAgent(),
            "code": CodeAgent(),
            "creative": CreativeAgent(),
            "game": GameAgent()
        }

    def run(self, user_input):
        plan = self.manager.decide(user_input)

        results = {}

        for agent_name in plan:
            if agent_name in self.agents:
                results[agent_name] = self.agents[agent_name].run(user_input)

        return self.combine(results)

    def combine(self, results):
        output = "\n\n".join(
            f"### {k.upper()}\n{v}"
            for k, v in results.items()
        )
        return output

class AutoAgentSystem:

    def run(self, goal, max_loops=3):

        plan = safe_execute(
            lambda: self.planner.run(goal),
            fallback="1. Answer directly"
        )

        for _ in range(max_loops):

            result = safe_execute(
                lambda: self.executor.run(plan),
                fallback="Execution failed"
            )

            review = safe_execute(
                lambda: self.critic.run(goal, result),
                fallback="APPROVED"
            )

            if "APPROVED" in review.upper():
                return result

            plan = f"""
Improve plan:

{plan}

Feedback:
{review}
"""

        return result or "No output generated."
