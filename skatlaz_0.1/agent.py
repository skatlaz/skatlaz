# agent.py

from tools import TOOLS
from llm import llm
from memory import AgentMemory


class Agent:

    def __init__(self):
        self.memory = AgentMemory()

    def run(self, user_input, max_steps=3):

        for step in range(max_steps):

            prompt = self.build_prompt(user_input)

            response = llm(prompt)

            # 🔥 parse simples (MVP)
            if "Action:" in response:
                action_line = [l for l in response.split("\n") if "Action:" in l][0]
                action = action_line.replace("Action:", "").strip()

                tool_name, tool_input = action.split("(", 1)
                tool_input = tool_input.rstrip(")")

                if tool_name in TOOLS:
                    result = TOOLS[tool_name](tool_input)

                    self.memory.add(
                        thought="Used tool",
                        action=action,
                        observation=str(result)
                    )

                    continue

            return response

        return "Max steps reached."

    def build_prompt(self, user_input):
        return f"""
You are an AI agent.

You can use tools.

Available tools:
- search(query)
- code(prompt)
- image(prompt)

Use format:

Thought: what you think
Action: tool(input)

OR final answer:

Final: answer

Memory:
{self.memory.format()}

User:
{user_input}
"""
