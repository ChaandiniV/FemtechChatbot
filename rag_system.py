import json
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from medical_knowledge import MedicalKnowledgeBase
from translations import get_translations

class RAGSystem:
    """Retrieval-Augmented Generation system for medical knowledge"""
    
    def __init__(self, knowledge_base: MedicalKnowledgeBase):
        self.kb = knowledge_base
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.knowledge_vectors = None
        self.knowledge_texts = []
        self._build_knowledge_index()
    
    def _build_knowledge_index(self):
        """Build vector index from medical knowledge base"""
        # Extract all knowledge text from the knowledge base
        knowledge_content = []
        
        # Add pregnancy knowledge
        pregnancy_knowledge = self.kb.knowledge.get('pregnancy_knowledge', '')
        knowledge_content.append(pregnancy_knowledge)
        
        # Add pregnancy guidelines
        pregnancy_guidelines = self.kb.knowledge.get('pregnancy_guidelines', '')
        knowledge_content.append(pregnancy_guidelines)
        
        # Add risk indicators as separate documents
        for risk_level, indicators in self.kb.risk_indicators.items():
            for indicator in indicators:
                knowledge_content.append(f"{risk_level}: {indicator}")
        
        # Add symptom categories
        symptom_categories = [
            "Normal pregnancy symptoms: mild nausea, light spotting, mild back pain, constipation, mild fatigue, breast tenderness, frequent urination",
            "Medium risk symptoms: persistent vomiting, elevated blood pressure, gestational diabetes symptoms, mild vaginal bleeding, severe heartburn, swollen hands and feet, decreased fetal movement",
            "High risk emergency symptoms: heavy vaginal bleeding with cramping, severe abdominal pain, blurry vision with headache and swelling, fever with chills, no fetal movement, severe chest pain, difficulty breathing, persistent severe headaches",
            "Preeclampsia indicators: severe headache, vision changes, sudden swelling, protein in urine, high blood pressure",
            "Gestational diabetes signs: excessive thirst, fatigue beyond normal pregnancy, frequent urination, blurred vision",
            "Preterm labor warnings: regular contractions before 37 weeks, lower back pressure, pelvic pressure, watery discharge, cervical changes"
        ]
        knowledge_content.extend(symptom_categories)
        
        self.knowledge_texts = knowledge_content
        
        # Build TF-IDF vectors
        if knowledge_content:
            self.knowledge_vectors = self.vectorizer.fit_transform(knowledge_content)
    
    def get_relevant_context(self, user_responses: List[str], language: str = 'en', top_k: int = 3) -> str:
        """Retrieve relevant medical context based on user responses"""
        if not user_responses or self.knowledge_vectors is None:
            return self._get_default_context(language)
        
        # Combine user responses into query
        query = " ".join(user_responses)
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()
        
        # Get top-k most relevant documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_contexts = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                relevant_contexts.append(self.knowledge_texts[idx])
        
        if not relevant_contexts:
            return self._get_default_context(language)
        
        return "\n\n".join(relevant_contexts)
    
    def _get_default_context(self, language: str) -> str:
        """Get default medical context when no specific context is found"""
        if language == 'ar':
            return """
            المعرفة الطبية الأساسية للحمل:
            - الأعراض الطبيعية: غثيان خفيف، تعب، ألم ظهر خفيف
            - أعراض متوسطة الخطورة: قيء مستمر، ارتفاع ضغط الدم، تورم
            - أعراض عالية الخطورة: نزيف شديد، ألم بطن شديد، صداع مع تغيرات في الرؤية
            - تسمم الحمل: صداع شديد + تغيرات في الرؤية + تورم
            - سكري الحمل: عطش مفرط، تعب، كثرة التبول
            """
        else:
            return """
            Essential pregnancy medical knowledge:
            - Normal symptoms: mild nausea, fatigue, mild back pain
            - Medium risk symptoms: persistent vomiting, elevated blood pressure, swelling
            - High risk symptoms: heavy bleeding, severe abdominal pain, severe headache with vision changes
            - Preeclampsia: severe headache + vision changes + swelling
            - Gestational diabetes: excessive thirst, fatigue, frequent urination
            """
    
    def search_symptoms(self, symptoms: List[str], language: str = 'en') -> Dict[str, Any]:
        """Search for specific symptoms in knowledge base"""
        results = {
            'matched_conditions': [],
            'risk_level': 'Low',
            'recommendations': []
        }
        
        symptoms_text = " ".join(symptoms).lower()
        
        # Check for high-risk combinations
        high_risk_patterns = [
            ['severe headache', 'vision changes', 'swelling'],
            ['heavy bleeding', 'cramping'],
            ['severe abdominal pain'],
            ['no fetal movement'],
            ['difficulty breathing', 'chest pain']
        ]
        
        for pattern in high_risk_patterns:
            if all(symptom in symptoms_text for symptom in pattern):
                results['risk_level'] = 'High'
                results['matched_conditions'].append(' + '.join(pattern))
                break
        
        # Check for medium-risk indicators
        medium_risk_keywords = [
            'persistent vomiting', 'blood pressure', 'swelling',
            'decreased movement', 'bleeding', 'headache'
        ]
        
        if results['risk_level'] == 'Low':
            for keyword in medium_risk_keywords:
                if keyword in symptoms_text:
                    results['risk_level'] = 'Medium'
                    results['matched_conditions'].append(keyword)
        
        return results
    
    def get_contextual_questions(self, responses: List[str], language: str = 'en') -> List[str]:
        """Generate contextual follow-up questions based on previous responses"""
        if not responses:
            return self._get_initial_questions(language)
        
        # Analyze responses to determine focus areas
        responses_text = " ".join(responses).lower()
        
        questions = []
        translations = get_translations(language)
        
        # Follow-up based on concerning symptoms mentioned
        if any(keyword in responses_text for keyword in ['headache', 'head', 'pain']):
            if language == 'ar':
                questions.append("هل الصداع مصحوب بتغيرات في الرؤية أو رؤية بقع؟")
            else:
                questions.append("Is the headache accompanied by vision changes or seeing spots?")
        
        if any(keyword in responses_text for keyword in ['swelling', 'swollen', 'swell']):
            if language == 'ar':
                questions.append("هل التورم مفاجئ أم تدريجي؟ وما هي المناطق المتأثرة؟")
            else:
                questions.append("Is the swelling sudden or gradual? Which areas are affected?")
        
        if any(keyword in responses_text for keyword in ['bleeding', 'blood', 'spotting']):
            if language == 'ar':
                questions.append("ما هو لون الدم وكميته؟ هل مصحوب بألم أو تقلصات؟")
            else:
                questions.append("What is the color and amount of bleeding? Is it accompanied by pain or cramping?")
        
        if any(keyword in responses_text for keyword in ['movement', 'moving', 'kick']):
            if language == 'ar':
                questions.append("في أي أسبوع من الحمل أنتِ؟ متى آخر مرة شعرتِ بحركة قوية؟")
            else:
                questions.append("What week of pregnancy are you in? When did you last feel strong movement?")
        
        # If no specific follow-ups, ask general questions
        if not questions:
            questions = self._get_general_followup_questions(language)
        
        return questions[:2]  # Return max 2 follow-up questions
    
    def _get_initial_questions(self, language: str) -> List[str]:
        """Get initial assessment questions"""
        if language == 'ar':
            return [
                "هل عانيتِ من صداع أو رؤية ضبابية هذا الأسبوع؟",
                "هل شعرتِ بأن حركة الجنين طبيعية اليوم؟",
                "هل لاحظتِ تورماً غير طبيعي في يديكِ أو قدميكِ؟"
            ]
        else:
            return [
                "Have you experienced headaches or blurry vision this week?",
                "Do you feel your baby has been moving normally today?",
                "Have you noticed any unusual swelling in your hands or feet?"
            ]
    
    def _get_general_followup_questions(self, language: str) -> List[str]:
        """Get general follow-up questions"""
        if language == 'ar':
            return [
                "هل تعانين من أي أعراض أخرى لم نناقشها؟",
                "كيف تشعرين بشكل عام مقارنة بالأسبوع الماضي؟"
            ]
        else:
            return [
                "Are you experiencing any other symptoms we haven't discussed?",
                "How are you feeling overall compared to last week?"
            ]