#agents/creative.py

from skatlaz_llms_prompt import generate_article

class CreativeAgent:
    def run(self, task):
        return generate_article(task)
