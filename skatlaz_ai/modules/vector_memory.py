"""
Vector Memory Module - RAG (Retrieval-Augmented Generation) implementation
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

class VectorMemory:
    """Vector-based memory system for RAG"""
    
    def __init__(self, memory_path: str = "memory"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(exist_ok=True)
        
        self.documents = []
        self.embeddings = []
        self.index_file = self.memory_path / "index.json"
        
        self._load_index()
        
    def _load_index(self):
        """Load existing memory index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    # Load embeddings as numpy arrays
                    embeddings_data = data.get('embeddings', [])
                    self.embeddings = [np.array(emb) for emb in embeddings_data]
            except Exception as e:
                print(f"Error loading memory index: {e}")
    
    def _save_index(self):
        """Save memory index"""
        data = {
            'documents': self.documents,
            'embeddings': [emb.tolist() for emb in self.embeddings]
        }
        with open(self.index_file, 'w') as f:
            json.dump(data, f)
    
    def add_document(self, text: str, metadata: Optional[Dict] = None):
        """Add document to memory"""
        # Simple TF-IDF vectorization for now
        vector = self._simple_vectorize(text)
        
        doc_id = hashlib.md5(text.encode()).hexdigest()
        
        document = {
            'id': doc_id,
            'text': text,
            'metadata': metadata or {},
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        self.documents.append(document)
        self.embeddings.append(vector)
        
        # Limit memory size
        if len(self.documents) > 1000:
            self.documents = self.documents[-1000:]
            self.embeddings = self.embeddings[-1000:]
            
        self._save_index()
    
    def query(self, query: str, top_k: int = 3) -> str:
        """Query memory and return relevant documents"""
        if not self.documents:
            return "No memory available yet."
        
        # Vectorize query
        query_vector = self._simple_vectorize(query)
        
        # Calculate similarities
        similarities = []
        for i, doc_vector in enumerate(self.embeddings):
            sim = self._cosine_similarity(query_vector, doc_vector)
            similarities.append((sim, i))
        
        # Get top-k
        similarities.sort(reverse=True)
        top_indices = [idx for _, idx in similarities[:top_k]]
        
        # Build response
        response = "📚 **Relevant Memory Found:**\n\n"
        for idx in top_indices:
            doc = self.documents[idx]
            response += f"📄 {doc['text'][:200]}...\n"
            response += f"   (Similarity: {similarities[idx][0]:.2f})\n\n"
        
        return response if similarities[0][0] > 0.1 else "No relevant memory found."
    
    def _simple_vectorize(self, text: str) -> np.ndarray:
        """Simple TF-IDF-like vectorization"""
        # Simple word frequency vector
        words = text.lower().split()
        word_set = set(words)
        vector = []
        
        # Use top 100 words for vector
        for word in sorted(word_set)[:100]:
            vector.append(words.count(word))
            
        # Pad or truncate to fixed size
        vector = np.array(vector[:100])
        if len(vector) < 100:
            vector = np.pad(vector, (0, 100 - len(vector)))
            
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search memory and return documents"""
        if not self.documents:
            return []
        
        query_vector = self._simple_vectorize(query)
        
        similarities = []
        for i, doc_vector in enumerate(self.embeddings):
            sim = self._cosine_similarity(query_vector, doc_vector)
            similarities.append((sim, i))
        
        similarities.sort(reverse=True)
        top_indices = [idx for _, idx in similarities[:top_k]]
        
        return [self.documents[idx] for idx in top_indices]
    
    def recall(self, topic: str) -> str:
        """Recall information about a specific topic"""
        results = self.search(topic, top_k=2)
        
        if not results:
            return f"No information found about '{topic}'."
        
        response = f"💭 **Recalling information about '{topic}':**\n\n"
        for doc in results:
            response += f"• {doc['text'][:300]}...\n\n"
            
        return response
