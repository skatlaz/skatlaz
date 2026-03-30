#memory/memory.py

from memory.embedder import embed
from memory.vector_store import VectorStore


class LongTermMemory:

    def __init__(self):
        self.store = VectorStore()

    def add(self, text):
        vector = embed([text])[0]
        self.store.add(text, vector)

    def retrieve(self, user_id, query):
        try:
            store = self._get_store(user_id)

            if not query:
                return []

            vec = embed([query])[0]
            return store.search(vec)

        except:
            return []
