"""
HuggingFace embedding modülü
"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingModel:
    """HuggingFace SentenceTransformer ile embedding oluşturur"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        print(f"Embedding modeli yükleniyor: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("✓ Model yüklendi")
        
    def encode(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """Metinleri vektörlere çevirir"""
        embeddings = self.model.encode(
            texts,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        """Tek bir metni vektöre çevirir"""
        return self.model.encode([text], convert_to_numpy=True)[0]
    
    def get_dimension(self) -> int:
        """Embedding boyutunu döndürür"""
        return self.model.get_sentence_embedding_dimension()

