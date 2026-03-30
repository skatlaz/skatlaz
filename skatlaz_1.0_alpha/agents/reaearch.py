#agents/research.py

from skatlaz_llms_prompt import research_topic

class ResearchAgent:
    def run(self, task):
        return research_topic(task)
