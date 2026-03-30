#agents/manager.py

from skatlaz.llm import llm

class ManagerAgent:

    def decide(self, user_input):
        prompt = f"""
You are an AI manager.

Decide which agents to use:

Agents:
- research
- code
- creative
- game

User request:
{user_input}

Return a list like:
research, code
"""

        result = llm(prompt)

        return [x.strip() for x in result.split(",")]
