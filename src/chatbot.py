"""
GPT API entegrasyon modülü - Personalized Healthcare Assistant
"""
from openai import OpenAI
from typing import List, Dict, Optional
import os

class HealthcareChatbot:
    """GPT-4 tabanlı personalized healthcare chatbot"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        print(f"✓ Chatbot model: {model}")
    
    def generate_personalized_response(
        self, 
        user_query: str, 
        formatted_context: str,
        intent: str = "GENERIC"
    ) -> Dict[str, any]:
        """Personalized yanıt üret (hybrid context ile)"""
        
        # Intent-based system prompts
        if intent == "PERSONAL":
            system_prompt = """You are a personal healthcare assistant with access to the user's health records.

IMPORTANT RULES:
1. Use ONLY the user's personal health data from their records
2. Provide specific, personalized answers based on their conditions, medications, and appointments
3. Doctor information is stored in appointments (doctor name, specialty)
4. If asked about "who is my [specialty] doctor", look in appointments for doctor with that specialty
5. Be empathetic and supportive
6. If answering about appointments or medications, be specific and use their actual data
7. Always remind them to consult their doctor for medical decisions
8. Use clear, professional language

You have access to:
- User's health conditions
- Current medications
- Upcoming appointments (includes doctor names and specialties)
- Test results"""
        
        elif intent == "GENERIC":
            system_prompt = """You are an expert healthcare assistant providing general medical information.

IMPORTANT RULES:
1. Only use the information provided in the medical knowledge base
2. Provide accurate, evidence-based information
3. Do not give personalized medical advice
4. Always recommend consulting a healthcare professional
5. Use clear, professional language"""
        
        elif intent == "HYBRID":
            system_prompt = """You are an intelligent healthcare assistant with access to BOTH:
1. User's personal health records (Neo4j Graph)
2. General medical knowledge base (FAISS RAG)

IMPORTANT RULES:
1. Combine the user's personal data with general medical knowledge
2. Provide personalized, evidence-based answers
3. Reference their specific conditions/medications when relevant
4. Doctor information is stored in appointments (doctor name, specialty)
5. Use medical knowledge to explain concepts related to their health
6. Be empathetic but professional
7. Always recommend consulting their doctor for medical decisions

You have access to:
- User's health conditions, medications, appointments (with doctor info), test results
- General medical knowledge about diseases, treatments, symptoms"""
        
        user_prompt = f"""Context:\n{formatted_context}\n\nUser Question: {user_query}\n\nPlease answer this question using the context provided above."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "intent": intent,
                "success": True
            }
            
        except Exception as e:
            return {
                "answer": f"Sorry, an error occurred: {str(e)}",
                "intent": intent,
                "success": False
            }
        
    def generate_response_legacy(self, user_query: str, context_docs: List[Dict]) -> Dict[str, any]:
        """Kullanıcı sorusu ve context dokümanları ile yanıt üretir"""
        
        # Context oluştur
        context = self._build_context(context_docs)
        
        # Prompt oluştur
        system_prompt = """You are an expert healthcare assistant. You provide informative and accurate answers about health questions.

        IMPORTANT RULES:
        1. Only use the information provided in the context
        2. If the answer is not in the context, tell the user
        3. Don't give medical advice, only provide information
        4. Use professional and clear language

        Context information is provided below."""

        user_prompt = f"""Context:\n{context}\n\nUser Question: {user_query}\n\nPlease answer this question using the context information provided."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            answer = response.choices[0].message.content
            
            # Detaylı kaynak bilgileri
            source_details = []
            for doc in context_docs:
                source_details.append({
                    'source': doc['source'],
                    'focus_area': doc['focus_area'],
                    'question': doc['question'],
                    'answer': doc['answer'],
                    'similarity_score': doc.get('similarity_score', 0)
                })
            
            return {
                "answer": answer,
                "source_details": source_details,
                "focus_areas": list(set([doc['focus_area'] for doc in context_docs]))
            }
            
        except Exception as e:
            return {
                "answer": f"Sorry, an error occurred: {str(e)}",
                "source_details": [],
                "focus_areas": []
            }
    
    def _build_context(self, docs: List[Dict]) -> str:
        """Dokümanlardan context metni oluşturur"""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"""
                Document {i}:
                Source: {doc['source']}
                Focus Area: {doc['focus_area']}
                Question: {doc['question']}
                Answer: {doc['answer']}
                ---""")
        return "\n".join(context_parts)

