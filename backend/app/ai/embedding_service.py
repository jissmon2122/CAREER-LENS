import os
import gc
import logging
import threading
from collections import OrderedDict

# Enforce thread and memory limits for low-RAM containers (Render 512MB)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Singleton service for generating vector embeddings and computing cosine similarity
    using sentence-transformers/all-MiniLM-L6-v2 on CPU with strict 512MB RAM constraints.
    """
    MAX_CACHE_SIZE = 500  # Capped bounded LRU cache (approx 1-2 MB RAM)

    def __init__(self):
        self.model = None
        self.np = None
        self._torch = None
        self._is_available = False
        self._is_loading = False
        self._model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._cache = OrderedDict()
        self._lock = threading.Lock()

    def initialize(self, model_name=None, preload=True):
        if model_name:
            self._model_name = model_name
        try:
            import numpy as np
            self.np = np
            self._is_available = True
            logger.info(f"AI Embedding Service initialized for model '{self._model_name}'.")
            if preload:
                self._ensure_model_loaded(blocking=False)
        except Exception as e:
            logger.warning(f"AI Embedding Service unavailable: {e}")
            self._is_available = False

    def _ensure_model_loaded(self, blocking=False):
        if not self._is_available:
            return False
        if self.model is not None:
            return True

        if not blocking:
            with self._lock:
                if self.model is not None:
                    return True
                if not self._is_loading:
                    self._is_loading = True
                    thread = threading.Thread(
                        target=self._load_model_worker,
                        name="AIModelLoadThread",
                        daemon=True
                    )
                    thread.start()
            return False

        # If blocking requested (e.g. in offline tests or explicitly)
        return self._load_model_worker()

    def _load_model_worker(self):
        with self._lock:
            if self.model is not None:
                self._is_loading = False
                return True
            try:
                import torch
                # Restrict PyTorch intra-op and inter-op threads to 1
                torch.set_num_threads(1)
                try:
                    torch.set_num_interop_threads(1)
                except Exception:
                    pass
                self._torch = torch

                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading AI Model '{self._model_name}' on CPU (single-thread mode)...")
                self.model = SentenceTransformer(self._model_name, device='cpu')
                # Set evaluation mode to disable autograd and training hooks
                self.model.eval()
                logger.info(f"AI Model '{self._model_name}' successfully loaded into memory.")
                self._is_loading = False
                # Reclaim deserialization memory
                gc.collect()
                return True
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model: {e}")
                self._is_loading = False
                return False

    def is_available(self) -> bool:
        return self._is_available

    def is_ready(self) -> bool:
        """Check if AI model is in-memory and ready for immediate vector inference without blocking."""
        return bool(self._is_available and self.model is not None)

    def get_embedding(self, text: str):
        """
        Generate a normalized 384-dimensional vector embedding for the given text.
        Uses a bounded OrderedDict LRU cache (MAX_CACHE_SIZE=500).
        """
        if not self.is_available() or not text or not text.strip():
            return None
        
        clean_text = text.strip()
        if clean_text in self._cache:
            self._cache.move_to_end(clean_text)
            return self._cache[clean_text]

        if not self.is_ready():
            # Trigger background load without stalling current request
            self._ensure_model_loaded(blocking=False)
            return None

        try:
            torch_module = self._torch
            if torch_module is not None and hasattr(torch_module, 'inference_mode'):
                ctx = torch_module.inference_mode()
            elif torch_module is not None and hasattr(torch_module, 'no_grad'):
                ctx = torch_module.no_grad()
            else:
                from contextlib import nullcontext
                ctx = nullcontext()

            with ctx:
                embedding = self.model.encode(clean_text, convert_to_numpy=True, normalize_embeddings=True)

            # Evict oldest entry if cache capacity reached
            while len(self._cache) >= self.MAX_CACHE_SIZE:
                self._cache.popitem(last=False)
            self._cache[clean_text] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            return None

    def get_embeddings_batch(self, texts: list) -> list:
        """
        Generate normalized 384-dimensional vector embeddings for a list of texts in a single batch pass.
        Uses batch_size=16 and inference_mode to minimize peak memory allocation on CPU.
        """
        if not self.is_available() or not texts:
            return [None] * len(texts)
        if not self.is_ready():
            self._ensure_model_loaded(blocking=False)
            return [None] * len(texts)

        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []

        for idx, text in enumerate(texts):
            clean = text.strip() if text else ""
            if not clean:
                continue
            if clean in self._cache:
                self._cache.move_to_end(clean)
                results[idx] = self._cache[clean]
            else:
                uncached_indices.append(idx)
                uncached_texts.append(clean)

        if uncached_texts:
            try:
                torch_module = self._torch
                if torch_module is not None and hasattr(torch_module, 'inference_mode'):
                    ctx = torch_module.inference_mode()
                elif torch_module is not None and hasattr(torch_module, 'no_grad'):
                    ctx = torch_module.no_grad()
                else:
                    from contextlib import nullcontext
                    ctx = nullcontext()

                with ctx:
                    batch_embs = self.model.encode(
                        uncached_texts,
                        batch_size=16,
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                        show_progress_bar=False
                    )
                for idx, emb in zip(uncached_indices, batch_embs):
                    results[idx] = emb
                    while len(self._cache) >= self.MAX_CACHE_SIZE:
                        self._cache.popitem(last=False)
                    self._cache[texts[idx].strip()] = emb
            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
            finally:
                gc.collect()

        return results

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
