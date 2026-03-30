#orchestrator_loop.py

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.critic import CriticAgent


class AutoAgentSystem:

    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.critic = CriticAgent()

    def run(self, goal, max_loops=3):

        print("🧠 Planning...")
        plan = self.planner.run(goal)

        for i in range(max_loops):
            print(f"\n⚙️ Execution loop {i+1}...")

            result = self.executor.run(plan)

            print("\n🧪 Critic reviewing...")
            review = self.critic.run(goal, result)

            print("\nCritic:", review)

            if "APPROVED" in review.upper():
                return result

            # 🔥 feedback loop
            plan = f"""
Improve this plan based on feedback:

Plan:
{plan}

Feedback:
{review}
"""

        return result
