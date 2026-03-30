#agents/base.py

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def run(self, task):
        raise NotImplementedError
