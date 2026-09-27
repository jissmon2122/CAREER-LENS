import os
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Singleton service for generating vector embeddings and computing cosine similarity
    using sentence-transformers/all-MiniLM-L6-v2 on CPU.
    """
    def __init__(self):
        self.model = None
        self.np = None
        self._is_available = False
        self._model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._cache = {}

    def initialize(self, model_name=None):
        if model_name:
            self._model_name = model_name
        try:
            import numpy as np
            self.np = np
            self._is_available = True
            logger.info(f"AI Embedding Service initialized for model '{self._model_name}' (Lazy Loading).")
        except Exception as e:
            logger.warning(f"AI Embedding Service unavailable: {e}")
            self._is_available = False

    def _ensure_model_loaded(self):
        if not self._is_available:
            return False
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Lazy loading AI Model '{self._model_name}' on CPU...")
                self.model = SentenceTransformer(self._model_name, device='cpu')
                logger.info(f"AI Model '{self._model_name}' successfully loaded into memory.")
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model: {e}")
                self._is_available = False
                return False
        return True

    def is_available(self) -> bool:
        return self._is_available

    def get_embedding(self, text: str):
        """
        Generate a normalized 384-dimensional vector embedding for the given text.
        Uses in-memory dictionary caching to avoid redundant model inference.
        Returns numpy array or None.
        """
        if not self.is_available() or not text or not text.strip():
            return None
        
        clean_text = text.strip()
        if clean_text in self._cache:
            return self._cache[clean_text]

        if not self._ensure_model_loaded():
            return None
        try:
            embedding = self.model.encode(clean_text, convert_to_numpy=True, normalize_embeddings=True)
            if len(self._cache) > 10000:
                self._cache.clear()
            self._cache[clean_text] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            return None

    def cosine_similarity(self, vec1, vec2) -> float:
        """
        Compute cosine similarity between two vector representations.
        Returns float value normalized between 0.0 and 1.0.
        """
        if vec1 is None or vec2 is None:
            return 0.0
        try:
            np = self.np
            if np is None:
                import numpy as np
            v1 = np.array(vec1, dtype=np.float32)
            v2 = np.array(vec2, dtype=np.float32)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            sim = float(np.dot(v1, v2) / (norm1 * norm2))
            return max(0.0, min(1.0, sim))
        except Exception as e:
            logger.error(f"Error computing cosine similarity: {e}")
            return 0.0

    def compute_text_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two raw text blocks.
        Returns percentage score from 0.0 to 100.0.
        """
        if not self.is_available():
            return 0.0
        vec1 = self.get_embedding(text1)
        vec2 = self.get_embedding(text2)
        sim = self.cosine_similarity(vec1, vec2)
        return round(sim * 100.0, 1)

embedding_service = EmbeddingService()
