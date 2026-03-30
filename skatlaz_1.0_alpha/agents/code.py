#agents/code.py

from skatlaz_llms_prompt import generate_code

class CodeAgent:
    def run(self, task):
        return generate_code(task)
