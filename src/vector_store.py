"""
FAISS vector store modülü
"""
import faiss
import numpy as np
import pickle
from typing import List, Dict, Tuple
import os

class VectorStore:
    """FAISS ile vektör veritabanı yönetimi"""
    
    def __init__(self, dimension: int, use_cosine: bool = True):
        self.dimension = dimension
        self.use_cosine = use_cosine
        
        if use_cosine:
            # Cosine similarity için Inner Product kullan
            # Yüksek değer = daha benzer (1'e yakın = çok benzer)
            self.index = faiss.IndexFlatIP(dimension)
        else:
            # L2 distance kullan
            # Düşük değer = daha benzer (0'a yakın = çok benzer)
            self.index = faiss.IndexFlatL2(dimension)
        
        self.documents = []
        
    def add_documents(self, embeddings: np.ndarray, documents: List[Dict]):
        """Dokümanları ve embedding'lerini ekler"""
        print(f"Vector store'a {len(documents)} doküman ekleniyor...")
        
        embeddings_float = embeddings.astype('float32')
        
        # Cosine similarity için embeddings'leri normalize et
        if self.use_cosine:
            # L2 normalization (her vektörün uzunluğu 1 olacak)
            norms = np.linalg.norm(embeddings_float, axis=1, keepdims=True)
            embeddings_float = embeddings_float / norms
        
        self.index.add(embeddings_float)
        self.documents = documents
        print(f"✓ Toplam {self.index.ntotal} doküman eklendi")
        
    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[Dict]:
        """En benzer K dokümanı bulur"""
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Cosine similarity için query'yi de normalize et
        if self.use_cosine:
            norm = np.linalg.norm(query_embedding)
            query_embedding = query_embedding / norm
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                
                if self.use_cosine:
                    # Cosine similarity: 1 = aynı, 0 = farklı, -1 = tam zıt
                    # Clip to [-1, 1] range (numerical precision hatalarını düzelt)
                    score = np.clip(float(distance), -1.0, 1.0)
                    doc['similarity_score'] = score
                else:
                    # L2 distance: 0 = aynı, yüksek = farklı
                    doc['similarity_score'] = float(distance)
                
                results.append(doc)
        
        return results
    
    def save(self, index_path: str = "faiss_index.bin", docs_path: str = "documents.pkl"):
        """Index ve dokümanları kaydeder"""
        print("Vector store kaydediliyor...")
        faiss.write_index(self.index, index_path)
        
        # Metadata da kaydet (hangi similarity kullanıldığını sakla)
        metadata = {
            'use_cosine': self.use_cosine,
            'dimension': self.dimension
        }
        
        with open(docs_path, 'wb') as f:
            pickle.dump({'documents': self.documents, 'metadata': metadata}, f)
        print(f"✓ Index kaydedildi: {index_path}")
        
    def load(self, index_path: str = "faiss_index.bin", docs_path: str = "documents.pkl"):
        """Kaydedilmiş index'i yükler"""
        if os.path.exists(index_path) and os.path.exists(docs_path):
            print("Kaydedilmiş index yükleniyor...")
            
            with open(docs_path, 'rb') as f:
                data = pickle.load(f)
            
            # Yeni format (metadata ile)
            if isinstance(data, dict) and 'documents' in data:
                self.documents = data['documents']
            else:
                # Eski format - direkt liste
                self.documents = data
            
            self.index = faiss.read_index(index_path)
            print(f"✓ {len(self.documents)} doküman yüklendi")
            return True
        return False

