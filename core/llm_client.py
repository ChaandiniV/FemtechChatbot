"""
LlamaIndex + Google Gemini client for medical question generation and risk assessment
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types
# Simplified imports - no complex LlamaIndex dependencies needed

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    """Google Gemini client for medical AI processing"""
    
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = "gemini-2.5-flash"
        
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate content using Gemini"""
        try:
            config = types.GenerateContentConfig()
            if system_instruction:
                config.system_instruction = system_instruction
                
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return ""

class SimpleRAGRetriever:
    """Simple retrieval system without complex embeddings"""
    
    def __init__(self, knowledge_base: List[Dict]):
        self.knowledge = knowledge_base
        
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Simple keyword-based retrieval"""
        query_lower = query.lower()
        scored_items = []
        
        for item in self.knowledge:
            score = 0
            # Check symptoms
            for symptom in item.get('symptoms', []):
                if symptom.lower() in query_lower:
                    score += 3
            
            # Check category and description
            if item.get('category', '').lower() in query_lower:
                score += 2
            if any(word in query_lower for word in item.get('description', '').lower().split()):
                score += 1
                
            if score > 0:
                scored_items.append((score, item))
        
        # Sort by score and return top results
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_items[:top_k]]

class MedicalRAGSystem:
    """LlamaIndex-based RAG system for medical knowledge"""
    
    def __init__(self, medical_knowledge: List[Dict]):
        self.gemini_client = GeminiClient()
        self.knowledge = medical_knowledge
        self.index = None
        self.query_engine = None
        self._setup_index()
        
    def _setup_index(self):
        """Setup simple RAG system with medical knowledge"""
        try:
            # Use simple keyword-based retrieval instead of complex embeddings
            self.retriever = SimpleRAGRetriever(self.knowledge)
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up RAG system: {e}")
            self.retriever = None
    
    def retrieve_context(self, query: str) -> str:
        """Retrieve relevant medical context"""
        if not self.retriever:
            return "Medical knowledge base not available"
            
        try:
            # Use simple retriever to get relevant knowledge
            items = self.retriever.retrieve(query)
            if items:
                context_parts = []
                for item in items:
                    context = f"Category: {item.get('category', '')}\n"
                    context += f"Risk Level: {item.get('risk_level', '')}\n"
                    context += f"Symptoms: {', '.join(item.get('symptoms', []))}\n"
                    context += f"Description: {item.get('description', '')}"
                    context_parts.append(context)
                return "\n\n".join(context_parts)
            return "No relevant medical context found"
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return "Error retrieving medical context"
    
    def generate_questions(self, user_responses: List[Dict], language: str = "en") -> List[str]:
        """Generate contextual medical questions using RAG + Gemini"""
        
        # Create context from user responses
        response_context = ""
        for resp in user_responses[-3:]:  # Last 3 responses
            response_context += f"Q: {resp.get('question', '')}\nA: {resp.get('answer', '')}\n"
        
        # Retrieve relevant medical knowledge
        medical_context = self.retrieve_context(response_context)
        
        # Language-specific prompts
        if language == "ar":
            system_instruction = """أنت طبيب متخصص في صحة الحمل. قم بتوليد 3-5 أسئلة طبية مهمة باللغة العربية بناءً على إجابات المريضة السابقة والمعرفة الطبية المقدمة. الأسئلة يجب أن تكون:
1. واضحة ومباشرة
2. مهمة طبياً لتقييم المخاطر
3. مناسبة ثقافياً
4. تركز على الأعراض والمخاطر المحتملة"""
            
            prompt = f"""السياق الطبي: {medical_context}

إجابات المريضة السابقة:
{response_context}

قم بتوليد 3-5 أسئلة طبية مهمة باللغة العربية فقط. كل سؤال في سطر منفصل بدون ترقيم."""

        else:
            system_instruction = """You are a pregnancy health specialist. Generate 3-5 important medical questions in English based on the patient's previous responses and the provided medical knowledge. Questions should be:
1. Clear and direct
2. Medically important for risk assessment
3. Culturally appropriate
4. Focus on symptoms and potential risks"""
            
            prompt = f"""Medical Context: {medical_context}

Patient's Previous Responses:
{response_context}

Generate 3-5 important medical questions in English only. Each question on a separate line without numbering."""
        
        # Generate questions using Gemini
        response = self.gemini_client.generate_content(prompt, system_instruction)
        
        if response:
            questions = [q.strip() for q in response.split('\n') if q.strip()]
            return questions[:5]  # Max 5 questions
        
        # Fallback questions
        return self._get_fallback_questions(language)
    
    def _get_fallback_questions(self, language: str) -> List[str]:
        """Fallback questions if AI generation fails"""
        if language == "ar":
            return [
                "هل تشعرين بأي آلام في البطن أو الظهر؟",
                "هل لاحظت أي تغيرات في حركة الجنين؟",
                "هل تعانين من غثيان أو قيء شديد؟"
            ]
        else:
            return [
                "Are you experiencing any abdominal or back pain?",
                "Have you noticed any changes in fetal movement?",
                "Are you experiencing severe nausea or vomiting?"
            ]
    
    def assess_risk(self, responses: List[Dict], language: str = "en") -> Dict[str, Any]:
        """AI-powered risk assessment using Gemini + medical knowledge"""
        
        # Prepare response context
        response_text = ""
        for resp in responses:
            response_text += f"Q: {resp.get('question', '')}\nA: {resp.get('answer', '')}\n"
        
        # Get relevant medical context
        medical_context = self.retrieve_context(response_text)
        
        # Risk assessment prompt
        if language == "ar":
            system_instruction = """أنت طبيب متخصص في صحة الحمل. قم بتحليل إجابات المريضة وتقييم مستوى المخاطر. يجب أن يكون التقييم دقيقاً ومبنياً على الأدلة الطبية.

أعط النتيجة بصيغة JSON فقط:
{
  "risk_level": "منخفض" أو "متوسط" أو "عالي",
  "risk_score": رقم من 1 إلى 10,
  "reasons": ["سبب 1", "سبب 2"],
  "recommendations": ["توصية 1", "توصية 2"]
}"""
        else:
            system_instruction = """You are a pregnancy health specialist. Analyze the patient's responses and assess risk level. Assessment must be accurate and evidence-based.

Provide result in JSON format only:
{
  "risk_level": "Low" or "Medium" or "High",
  "risk_score": number from 1 to 10,
  "reasons": ["reason 1", "reason 2"],
  "recommendations": ["recommendation 1", "recommendation 2"]
}"""
        
        prompt = f"""Medical Knowledge: {medical_context}

Patient Responses:
{response_text}

Analyze and provide risk assessment in JSON format."""
        
        try:
            # Generate assessment
            response = self.gemini_client.generate_content(prompt, system_instruction)
            
            if response:
                # Try to parse JSON
                result = json.loads(response)
                return result
                
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
        
        # Fallback to rule-based assessment
        return self._fallback_risk_assessment(responses, language)
    
    def _fallback_risk_assessment(self, responses: List[Dict], language: str) -> Dict[str, Any]:
        """Fallback rule-based risk assessment"""
        risk_score = 0
        reasons = []
        
        # Simple keyword-based risk detection
        high_risk_keywords = ["bleeding", "pain", "cramping", "نزيف", "ألم", "تقلصات"]
        medium_risk_keywords = ["nausea", "headache", "tired", "غثيان", "صداع", "تعب"]
        
        for resp in responses:
            answer = resp.get('answer', '').lower()
            for keyword in high_risk_keywords:
                if keyword in answer:
                    risk_score += 3
                    if language == "ar":
                        reasons.append(f"ذكر أعراض عالية الخطورة: {keyword}")
                    else:
                        reasons.append(f"High-risk symptom mentioned: {keyword}")
            
            for keyword in medium_risk_keywords:
                if keyword in answer:
                    risk_score += 1
                    if language == "ar":
                        reasons.append(f"ذكر أعراض متوسطة الخطورة: {keyword}")
                    else:
                        reasons.append(f"Medium-risk symptom mentioned: {keyword}")
        
        # Determine risk level
        if risk_score >= 6:
            risk_level = "عالي" if language == "ar" else "High"
        elif risk_score >= 3:
            risk_level = "متوسط" if language == "ar" else "Medium"
        else:
            risk_level = "منخفض" if language == "ar" else "Low"
        
        # Generate recommendations
        if language == "ar":
            recommendations = ["استشر طبيبك فوراً", "راقب الأعراض بعناية"]
        else:
            recommendations = ["Consult your doctor immediately", "Monitor symptoms carefully"]
        
        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 10),
            "reasons": reasons[:3],  # Max 3 reasons
            "recommendations": recommendations
        }