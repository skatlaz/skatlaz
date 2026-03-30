#memory/persistent_memory.py

import os
from memory.embedder import embed
from memory.vector_store import PersistentVectorStore


class MultiUserMemory:

    def __init__(self, base_path="memory_store"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _get_store(self, user_id):
        path = os.path.join(self.base_path, user_id)
        return PersistentVectorStore(path)

    def add(self, user_id, text):
        store = self._get_store(user_id)
        vec = embed([text])[0]
        store.add(text, vec)

    def retrieve(self, user_id, query):
        store = self._get_store(user_id)
        vec = embed([query])[0]
        return store.search(vec)
