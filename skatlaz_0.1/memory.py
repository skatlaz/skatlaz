# memory.py

class AgentMemory:
    def __init__(self):
        self.steps = []

    def add(self, thought, action, observation):
        self.steps.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })

    def format(self):
        text = ""
        for s in self.steps:
            text += f"""
Thought: {s['thought']}
Action: {s['action']}
Observation: {s['observation']}
"""
        return text
