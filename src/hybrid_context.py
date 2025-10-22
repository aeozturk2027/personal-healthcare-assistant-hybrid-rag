"""
Hybrid Context Builder - Neo4j + FAISS birleştirir
"""
from typing import Dict, List, Optional
from src.neo4j_client import Neo4jClient
from src.intent_classifier import IntentClassifier
from src.date_tools import DateTools
from src.vector_store import VectorStore
from src.embeddings import EmbeddingModel

class HybridContextBuilder:
    """Neo4j personal data + FAISS knowledge birleştirir"""
    
    def __init__(
        self,
        neo4j_client: Neo4jClient,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel
    ):
        self.neo4j = neo4j_client
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.intent_classifier = IntentClassifier()
        self.date_tools = DateTools()
    
    def build_context(self, user_id: str, question: str, k_docs: int = 3) -> Dict:
        """Hybrid context oluştur"""
        
        # LLM-based intent classification + required data detection
        classification = self.intent_classifier.classify_with_data(question)
        intent = classification['intent']
        required_data = classification['required_data']
        
        context = {
            'intent': intent,
            'personal_data': {},
            'knowledge': [],
            'required_data': required_data,  # Store for debugging/trace
            'metadata': {
                'current_date': self.date_tools.get_current_date(),
                'current_time': self.date_tools.get_current_time()
            }
        }
        
        # Intent-based data retrieval
        if intent == "PERSONAL":
            # PERSONAL: Sadece Neo4j graph data (sadece gerekli olanlar)
            context['personal_data'] = self._get_personal_data(user_id, question, required_data)
            context['knowledge'] = []
            
        elif intent == "GENERIC":
            # GENERIC: Sadece FAISS RAG
            context['knowledge'] = self._get_knowledge(question, k_docs)
            
        elif intent == "HYBRID":
            # HYBRID: Hem graph hem RAG (sadece gerekli olanlar)
            context['personal_data'] = self._get_personal_data(user_id, question, required_data)
            
            # HYBRID için enriched query oluştur
            enriched_query = self._enrich_query_with_personal_data(question, context['personal_data'])
            context['knowledge'] = self._get_knowledge(enriched_query, k_docs)
            context['original_question'] = question  # Original'i sakla
            context['enriched_query'] = enriched_query  # Enriched'i sakla (debug için)
        
        return context
    
    def _get_personal_data(self, user_id: str, question: str, required_data: Dict[str, bool]) -> Dict:
        """
        Neo4j'den SADECE GEREKLİ personal data'yı çek
        
        LLM hangi dataların gerekli olduğunu belirledi,
        sadece onları çek -> daha küçük prompt, daha hızlı.
        
        FALLBACK: Eğer hiçbir data gerekli değilse (LLM belirsizse),
        güvenli tarafta kal ve tüm dataları çek.
        
        Args:
            user_id: Kullanıcı ID
            question: Kullanıcı sorusu (tarih parsing için)
            required_data: LLM'den gelen gerekli data listesi
        """
        personal_data = {}
        
        try:
            # User info (her zaman çek - küçük data)
            user = self.neo4j.get_user(user_id)
            if user:
                personal_data['user'] = user
            
            # Relative date parsing (soruda tarih varsa)
            date_filter = self.date_tools.parse_relative_date(question)
            
            # FALLBACK: Eğer hiçbir data field gerekli değilse, hepsini çek
            if not any(required_data.values()):
                print(f"⚠️ LLM hiçbir data field belirtmedi, tüm dataları çekiyorum (fallback)")
                required_data = {
                    'appointments': True,
                    'medications': True,
                    'conditions': True,
                    'test_results': True
                }
            
            # Sadece gerekli dataları çek
            if required_data.get('appointments', False):
                appointments = self.neo4j.get_user_appointments(user_id, date_filter)
                if appointments:
                    personal_data['appointments'] = appointments
            
            if required_data.get('medications', False):
                medications = self.neo4j.get_user_medications(user_id)
                if medications:
                    personal_data['medications'] = medications
            
            if required_data.get('conditions', False):
                conditions = self.neo4j.get_user_conditions(user_id)
                if conditions:
                    personal_data['conditions'] = conditions
            
            if required_data.get('test_results', False):
                test_results = self.neo4j.get_user_test_results(user_id)
                if test_results:
                    personal_data['test_results'] = test_results
        
        except Exception as e:
            print(f"⚠️ Neo4j veri çekme hatası: {e}")
        
        return personal_data
    
    def _enrich_query_with_personal_data(self, question: str, personal_data: Dict) -> str:
        """
        HYBRID sorular için query'yi personal data ile zenginleştir
        
        Örnek:
        - Original: "What foods should I avoid with my current medications?"
        - Personal: medications = [Lisinopril, Metformin]
        - Enriched: "What foods should I avoid with Lisinopril and Metformin?"
        """
        enriched_parts = [question]
        
        # Medications (en önemli)
        if personal_data.get('medications'):
            med_names = [med['name'] for med in personal_data['medications']]
            if med_names:
                med_context = f" (Current medications: {', '.join(med_names)})"
                enriched_parts.append(med_context)
        
        # Conditions (hastalıklar)
        if personal_data.get('conditions'):
            cond_names = [cond['name'] for cond in personal_data['conditions']]
            if cond_names:
                cond_context = f" (Health conditions: {', '.join(cond_names)})"
                enriched_parts.append(cond_context)
        
        # Test Results (sadece anormal olanlar)
        if personal_data.get('test_results'):
            abnormal_tests = []
            for test in personal_data['test_results']:
                if test.get('status') and test['status'] != 'Normal':
                    abnormal_tests.append(f"{test.get('test_name', 'Unknown')}: {test.get('value', 'N/A')}")
            if abnormal_tests and len(abnormal_tests) <= 2:  # Max 2 tane göster
                test_context = f" (Recent test results: {', '.join(abnormal_tests)})"
                enriched_parts.append(test_context)
        
        enriched_query = ''.join(enriched_parts)
        
        # Log for debugging
        if enriched_query != question:
            print(f"🔍 Enriched query: {enriched_query[:150]}...")
        
        return enriched_query
    
    def _get_knowledge(self, question: str, k: int) -> List[Dict]:
        """FAISS'ten knowledge çek"""
        try:
            query_embedding = self.embedding_model.encode_single(question)
            similar_docs = self.vector_store.search(query_embedding, k=k)
            return similar_docs
        except Exception as e:
            print(f"⚠️ FAISS arama hatası: {e}")
            return []
    
    def format_for_gpt(self, context: Dict) -> str:
        """Context'i GPT için string formatına çevir"""
        parts = []
        
        # Metadata
        parts.append(f"Current Date: {context['metadata']['current_date']}")
        parts.append(f"Current Time: {context['metadata']['current_time']}")
        parts.append("")
        
        # Personal Data
        personal = context.get('personal_data', {})
        
        if personal.get('user'):
            user = personal['user']
            parts.append("=== USER INFORMATION ===")
            parts.append(f"Name: {user.get('name', 'N/A')}")
            if user.get('age'):
                parts.append(f"Age: {user['age']}")
            parts.append("")
        
        if personal.get('appointments'):
            parts.append("=== USER APPOINTMENTS ===")
            for apt in personal['appointments']:
                date_str = self.date_tools.format_date_friendly(str(apt['date']))
                parts.append(f"- {date_str} at {apt.get('time', 'N/A')}")
                parts.append(f"  Doctor: {apt.get('doctor', 'N/A')}")
                if apt.get('specialty'):
                    parts.append(f"  Specialty: {apt['specialty']}")
                if apt.get('location'):
                    parts.append(f"  Location: {apt['location']}")
            parts.append("")
        
        if personal.get('medications'):
            parts.append("=== USER MEDICATIONS ===")
            for med in personal['medications']:
                parts.append(f"- {med['name']}")
                if med.get('dosage'):
                    parts.append(f"  Dosage: {med['dosage']}")
                if med.get('frequency'):
                    parts.append(f"  Frequency: {med['frequency']}")
            parts.append("")
        
        if personal.get('conditions'):
            parts.append("=== USER HEALTH CONDITIONS ===")
            for cond in personal['conditions']:
                parts.append(f"- {cond['name']}")
                if cond.get('diagnosed_date'):
                    parts.append(f"  Diagnosed: {cond['diagnosed_date']}")
                if cond.get('severity'):
                    parts.append(f"  Severity: {cond['severity']}")
            parts.append("")
        
        if personal.get('test_results'):
            parts.append("=== USER TEST RESULTS ===")
            for test in personal['test_results']:
                parts.append(f"- {test['test_name']}")
                parts.append(f"  Date: {test.get('test_date', 'N/A')}")
                parts.append(f"  Result: {test.get('result', 'N/A')} {test.get('unit', '')}")
                if test.get('normal_range'):
                    parts.append(f"  Normal Range: {test['normal_range']}")
                if test.get('status'):
                    status_icon = "🔴" if test['status'] == 'high' else "🟡" if test['status'] == 'borderline' else "🟢"
                    parts.append(f"  Status: {status_icon} {test['status'].upper()}")
            parts.append("")
        
        # Medical Knowledge
        knowledge = context.get('knowledge', [])
        if knowledge:
            parts.append("=== MEDICAL KNOWLEDGE BASE ===")
            for i, doc in enumerate(knowledge, 1):
                parts.append(f"\nDocument {i}:")
                parts.append(f"Source: {doc.get('source', 'N/A')}")
                parts.append(f"Topic: {doc.get('focus_area', 'N/A')}")
                parts.append(f"Q: {doc.get('question', 'N/A')}")
                parts.append(f"A: {doc.get('answer', 'N/A')}")
                if doc.get('similarity_score'):
                    parts.append(f"Relevance: {doc['similarity_score']:.3f}")
                parts.append("---")
        
        return "\n".join(parts)

