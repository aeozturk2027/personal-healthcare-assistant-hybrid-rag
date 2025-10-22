"""
Intent classification - LLM-based classifier (GPT-4o-mini)
3 Intent Types: PERSONAL, GENERIC, HYBRID
+ Required data detection
"""
from typing import Literal, Dict, Any
from openai import OpenAI
import os
import json

IntentType = Literal["PERSONAL", "GENERIC", "HYBRID"]

class IntentClassifier:
    """LLM-based intent classifier with 3-way classification"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        LLM-based intent classifier
        
        Args:
            api_key: OpenAI API key (None ise .env'den alır)
            model: OpenAI model (default: gpt-4o-mini - ucuz ve hızlı)
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # System prompt for classification
        self.system_prompt = """You are an intent classifier for a healthcare chatbot with access to:
1. User's personal health records (Neo4j Graph): appointments, medications, conditions, test_results
2. General medical knowledge base (FAISS RAG): 16,000+ medical Q&A pairs

Your job: Classify the question AND specify which data is needed.

**PERSONAL**: Questions ONLY about the user's own data
Examples:
- "Do I have any appointments today?" → needs appointments
- "When is my next appointment?" → needs appointments
- "Who is my cardiologist?" → needs appointments (doctors are linked to appointments)
- "What medications am I taking?" → needs medications
- "Which medication am I taking for diabetes?" → needs medications, conditions
- "Show me my test results" → needs test_results
- "What are my health conditions?" → needs conditions

**GENERIC**: General medical questions (no personal data needed)
Examples:
- "What is high blood pressure?" → no personal data
- "How does metformin work?" → no personal data

**HYBRID**: Questions that need BOTH personal data AND general medical knowledge
Examples:
- "Should I be concerned about my BP given my hypertension?" → needs test_results, conditions + RAG
- "Is my medication effective for my condition?" → needs medications, conditions + RAG

Respond with ONLY valid JSON (no markdown, no extra text):
{
  "intent": "PERSONAL" | "GENERIC" | "HYBRID",
  "required_data": {
    "appointments": true/false,
    "medications": true/false,
    "conditions": true/false,
    "test_results": true/false
  }
}"""

    def classify_with_data(self, question: str) -> Dict[str, Any]:
        """
        LLM ile soruyu sınıflandır + hangi dataların gerekli olduğunu belirle
        
        Args:
            question: Kullanıcı sorusu
            
        Returns:
            {
                "intent": "PERSONAL" | "GENERIC" | "HYBRID",
                "required_data": {
                    "appointments": bool,
                    "medications": bool,
                    "conditions": bool,
                    "test_results": bool
                }
            }
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Question: {question}"}
                ],
                temperature=0.0,  # Deterministic
                max_tokens=100,   # Enough for JSON response
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            # Validate
            intent = result.get("intent", "").upper()
            if intent not in ["PERSONAL", "GENERIC", "HYBRID"]:
                print(f"⚠️ LLM returned invalid intent: {intent}, using fallback")
                return self._fallback_classify_with_data(question)
            
            # Ensure required_data exists
            if "required_data" not in result:
                result["required_data"] = {
                    "appointments": False,
                    "medications": False,
                    "conditions": False,
                    "test_results": False
                }
            
            return {
                "intent": intent,
                "required_data": result["required_data"]
            }
                
        except Exception as e:
            print(f"⚠️ LLM classification error: {e}, using fallback")
            return self._fallback_classify_with_data(question)
    
    def classify(self, question: str) -> IntentType:
        """
        Backward compatibility: sadece intent döner
        
        Args:
            question: Kullanıcı sorusu
            
        Returns:
            "PERSONAL", "GENERIC", veya "HYBRID"
        """
        result = self.classify_with_data(question)
        return result["intent"]
    
    def _fallback_classify_with_data(self, question: str) -> Dict[str, Any]:
        """Fallback keyword-based classifier (eğer LLM başarısız olursa)"""
        question_lower = question.lower()
        
        # HYBRID indicators
        hybrid_keywords = [
            "given my", "with my", "for my", "considering my",
            "should i", "is it safe for me", "can i"
        ]
        
        personal_keywords = ["my ", "i have", "do i", "am i"]
        
        has_personal = any(kw in question_lower for kw in personal_keywords)
        has_hybrid_indicator = any(kw in question_lower for kw in hybrid_keywords)
        
        # Determine intent
        if has_hybrid_indicator and has_personal:
            intent = "HYBRID"
        elif has_personal:
            intent = "PERSONAL"
        else:
            intent = "GENERIC"
        
        # Determine required data (basic keyword matching)
        required_data = {
            "appointments": any(kw in question_lower for kw in ["appointment", "doctor", "visit"]),
            "medications": any(kw in question_lower for kw in ["medication", "medicine", "drug", "pill"]),
            "conditions": any(kw in question_lower for kw in ["condition", "disease", "diagnosis"]),
            "test_results": any(kw in question_lower for kw in ["test", "result", "lab", "blood pressure reading"])
        }
        
        # If personal/hybrid but no specific data matched, get all
        if intent in ["PERSONAL", "HYBRID"] and not any(required_data.values()):
            required_data = {
                "appointments": True,
                "medications": True,
                "conditions": True,
                "test_results": True
            }
        
        return {
            "intent": intent,
            "required_data": required_data
        }
    
    def _fallback_classify(self, question: str) -> IntentType:
        """Fallback: sadece intent döner"""
        result = self._fallback_classify_with_data(question)
        return result["intent"]
    
    def is_personal(self, question: str) -> bool:
        """Personal soru mu?"""
        return self.classify(question) == "PERSONAL"
    
    def is_generic(self, question: str) -> bool:
        """Generic soru mu?"""
        return self.classify(question) == "GENERIC"
    
    def is_hybrid(self, question: str) -> bool:
        """Hybrid soru mu?"""
        return self.classify(question) == "HYBRID"

