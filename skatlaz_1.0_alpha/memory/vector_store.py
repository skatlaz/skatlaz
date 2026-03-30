#memory/vector_store.py

import faiss
import numpy as np
import pickle
import os

class PersistentVectorStore:

    def __init__(self, path, dim=384):
        self.path = path
        self.index_path = os.path.join(path, "index.faiss")
        self.data_path = os.path.join(path, "texts.pkl")

        os.makedirs(path, exist_ok=True)

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.data_path, "rb") as f:
                self.texts = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dim)
            self.texts = []

    def add(self, text, vector):
        self.index.add(np.array([vector]).astype("float32"))
        self.texts.append(text)
        self.save()

    def search(self, vector, k=5):
        try:
            if len(self.texts) == 0:
                return []

            D, I = self.index.search(
                np.array([vector]).astype("float32"),
                k
            )

            results = []
            for i in I[0]:
                if isinstance(i, (int, np.integer)) and 0 <= i < len(self.texts):
                    results.append(self.texts[i])

            return results

        except Exception:
            return []

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.data_path, "wb") as f:
            pickle.dump(self.texts, f)
