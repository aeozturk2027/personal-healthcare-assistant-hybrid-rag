"""
Veri yükleme ve işleme modülü

MedQuad Dataset:
- Kaynak: https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research
- 16,461 medical question-answer pairs
- Original sources: NIH, Mayo Clinic, MPlusHealthTopics
"""
import pandas as pd
from typing import List, Dict

class DataProcessor:
    """MedQuad veri setini yükler ve işler"""
    
    def __init__(self, data_path: str = "data/medquad.csv"):
        self.data_path = data_path
        self.data = None
        
    def load_data(self) -> pd.DataFrame:
        """CSV dosyasını yükler"""
        print("Veri seti yükleniyor...")
        self.data = pd.read_csv(self.data_path)
        print(f"✓ {len(self.data)} adet kayıt yüklendi")
        return self.data
    
    def prepare_documents(self) -> List[Dict[str, str]]:
        """Veriyi doküman formatına çevirir"""
        if self.data is None:
            self.load_data()
        
        documents = []
        for idx, row in self.data.iterrows():
            doc = {
                'id': idx,
                'question': str(row['question']),
                'answer': str(row['answer']),
                'source': str(row['source']),
                'focus_area': str(row['focus_area']),
                'text': f"Question: {row['question']}\nAnswer: {row['answer']}"
            }
            documents.append(doc)
        
        print(f"✓ {len(documents)} doküman hazırlandı")
        return documents

