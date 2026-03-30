#agents/game.py

from skatlaz_llms_prompt import generate_game

class GameAgent:
    def run(self, task):
        return generate_game(task)
