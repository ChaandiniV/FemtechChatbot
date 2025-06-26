import json
import requests
from typing import List, Dict, Any, Optional
from translations import get_translations

class HuggingFaceClient:
    """Client for interacting with Hugging Face models"""
    
    def __init__(self):
        # Using Hugging Face Inference API (free tier)
        self.api_url = "https://api-inference.huggingface.co/models/"
        self.headers = {
            "Content-Type": "application/json",
        }
        
        # Models to use
        self.text_generation_model = "microsoft/DialoGPT-medium"
        self.classification_model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    async def generate_questions(self, language: str, context: str, previous_responses: Optional[List[str]] = None) -> List[str]:
        """Generate contextual medical questions using Hugging Face"""
        try:
            # Create prompt for question generation
            prev_responses_text = ' '.join(previous_responses) if previous_responses else ''
            
            if language == 'ar':
                prompt = f"""بناءً على المعرفة الطبية التالية والإجابات السابقة، اطرح 3 أسئلة طبية مهمة لتقييم مخاطر الحمل:

المعرفة الطبية: {context}

الإجابات السابقة: {prev_responses_text if prev_responses_text else 'لا توجد إجابات سابقة'}

أسئلة طبية مهمة:
1."""
            else:
                prompt = f"""Based on the following medical knowledge and previous responses, generate 3 important medical questions for pregnancy risk assessment:

Medical Knowledge: {context}

Previous Responses: {prev_responses_text if prev_responses_text else 'No previous responses'}

Important medical questions:
1."""
            
            # Try to generate using Hugging Face API
            response = await self._make_api_request("text-generation", prompt)
            
            if response and "generated_text" in response[0]:
                generated_text = response[0]["generated_text"]
                questions = self._extract_questions_from_text(generated_text, language)
                if questions:
                    return questions
            
        except Exception as e:
            print(f"Error generating questions with HuggingFace: {e}")
        
        # Fallback to template-based questions
        return self._get_template_questions(language, context, previous_responses or [])
    
    async def analyze_risk(self, responses: List[str], context: str, language: str) -> Dict[str, Any]:
        """Analyze pregnancy risk using Hugging Face models"""
        try:
            # Create risk analysis prompt
            responses_text = " ".join(responses)
            
            if language == 'ar':
                prompt = f"""قم بتحليل الإجابات التالية لتقييم مخاطر الحمل:

المعرفة الطبية: {context}

إجابات المريضة: {responses_text}

قم بتصنيف مستوى الخطر (منخفض، متوسط، عالي) وقدم تفسيراً وتوصيات."""
            else:
                prompt = f"""Analyze the following responses for pregnancy risk assessment:

Medical Knowledge: {context}

Patient Responses: {responses_text}

Classify risk level (Low, Medium, High) and provide explanation and recommendations."""
            
            # Try to analyze using Hugging Face API
            response = await self._make_api_request("text-generation", prompt)
            
            if response and "generated_text" in response[0]:
                generated_text = response[0]["generated_text"]
                risk_analysis = self._extract_risk_analysis(generated_text, language)
                if risk_analysis:
                    return risk_analysis
            
        except Exception as e:
            print(f"Error analyzing risk with HuggingFace: {e}")
        
        # Fallback to rule-based analysis
        return self._rule_based_risk_analysis(responses, language)
    
    async def _make_api_request(self, task: str, prompt: str) -> Optional[Dict]:
        """Make request to Hugging Face Inference API"""
        try:
            if task == "text-generation":
                url = f"{self.api_url}{self.text_generation_model}"
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 150,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }
            else:
                return None
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HuggingFace API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API request error: {e}")
            return None
    
    def _extract_questions_from_text(self, text: str, language: str) -> List[str]:
        """Extract questions from generated text"""
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or (language == 'ar' and '؟' in line)):
                # Clean up the question
                if line.startswith(('1.', '2.', '3.', '-', '*')):
                    line = line[2:].strip()
                questions.append(line)
        
        return questions[:3]  # Return max 3 questions
    
    def _extract_risk_analysis(self, text: str, language: str) -> Dict[str, Any]:
        """Extract risk analysis from generated text"""
        # Simple extraction based on keywords
        text_lower = text.lower()
        
        # Determine risk level
        if any(word in text_lower for word in ['high', 'severe', 'emergency', 'urgent', 'عالي', 'شديد', 'طارئ']):
            risk_level = 'High'
        elif any(word in text_lower for word in ['medium', 'moderate', 'concerning', 'متوسط', 'معتدل']):
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Extract explanation (first paragraph)
        paragraphs = text.split('\n\n')
        explanation = paragraphs[0] if paragraphs else text[:200]
        
        # Generate recommendations based on risk level
        if language == 'ar':
            if risk_level == 'High':
                recommendations = "اطلبي الرعاية الطبية الفورية. اتصلي بطبيب النساء أو اذهبي إلى غرفة الطوارئ."
            elif risk_level == 'Medium':
                recommendations = "اتصلي بمقدم الرعاية الصحية خلال 24 ساعة لمناقشة هذه الأعراض."
            else:
                recommendations = "استمري في المتابعة الدورية للحمل واحرصي على نمط حياة صحي."
        else:
            if risk_level == 'High':
                recommendations = "Seek immediate medical care. Contact your OB/GYN or go to the emergency room."
            elif risk_level == 'Medium':
                recommendations = "Contact your healthcare provider within 24 hours to discuss these symptoms."
            else:
                recommendations = "Continue routine prenatal care and maintain a healthy lifestyle."
        
        return {
            'risk_level': risk_level,
            'explanation': explanation,
            'recommendations': recommendations,
            'urgent_care_needed': risk_level == 'High'
        }
    
    def _get_template_questions(self, language: str, context: str, previous_responses: List[str]) -> List[str]:
        """Generate template-based questions when AI generation fails"""
        translations = get_translations(language)
        
        # Analyze context and previous responses to select relevant questions
        context_lower = context.lower() if context else ""
        responses_text = " ".join(previous_responses).lower()
        
        question_pool = [
            translations["question_headaches"],
            translations["question_fetal_movement"],
            translations["question_swelling"],
            translations["question_bleeding"],
            translations["question_blood_pressure"]
        ]
        
        # Add contextual questions based on symptoms mentioned
        if language == 'ar':
            contextual_questions = {
                'headache': "هل الصداع مصحوب بغثيان أو تغيرات في الرؤية؟",
                'swelling': "هل التورم في الوجه أم فقط في الأطراف؟",
                'bleeding': "هل النزيف مصحوب بألم أو تقلصات؟",
                'movement': "كم مرة تشعرين بحركة الجنين في الساعة؟",
                'pressure': "هل تعرفين قراءات ضغط الدم الأخيرة؟"
            }
        else:
            contextual_questions = {
                'headache': "Is the headache accompanied by nausea or vision changes?",
                'swelling': "Is the swelling in your face or just in your extremities?",
                'bleeding': "Is the bleeding accompanied by pain or cramping?",
                'movement': "How many times do you feel fetal movement per hour?",
                'pressure': "Do you know your recent blood pressure readings?"
            }
        
        # Select questions based on context
        selected_questions = question_pool[:3]  # Default first 3
        
        for keyword, question in contextual_questions.items():
            if keyword in context_lower or keyword in responses_text:
                if question not in selected_questions:
                    selected_questions.append(question)
        
        return selected_questions[:3]
    
    def _rule_based_risk_analysis(self, responses: List[str], language: str) -> Dict[str, Any]:
        """Fallback rule-based risk analysis"""
        responses_text = " ".join(responses).lower()
        
        # High-risk keywords
        high_risk_keywords = [
            'heavy bleeding', 'severe pain', 'no movement', 'blurry vision',
            'severe headache', 'fever', 'difficulty breathing', 'chest pain'
        ]
        
        # Medium-risk keywords  
        medium_risk_keywords = [
            'vomiting', 'blood pressure', 'swelling', 'headache',
            'bleeding', 'decreased movement', 'pain'
        ]
        
        risk_score = 0
        
        for keyword in high_risk_keywords:
            if keyword in responses_text:
                risk_score += 3
        
        for keyword in medium_risk_keywords:
            if keyword in responses_text:
                risk_score += 2
        
        if risk_score >= 6:
            risk_level = 'High'
        elif risk_score >= 3:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Generate explanation and recommendations
        if language == 'ar':
            explanations = {
                'High': 'تشير الأعراض لديكِ إلى حالة خطيرة محتملة تتطلب اهتماماً فورياً.',
                'Medium': 'بعض الأعراض تتطلب متابعة وقد تحتاج إلى عناية طبية.',
                'Low': 'تبدو الأعراض لديكِ طبيعية ومرتبطة بالحمل.'
            }
            recommendations = {
                'High': 'اطلبي الرعاية الطبية الفورية. اتصلي بطبيب النساء أو اذهبي إلى غرفة الطوارئ.',
                'Medium': 'اتصلي بمقدم الرعاية الصحية خلال 24 ساعة لمناقشة هذه الأعراض.',
                'Low': 'استمري في المتابعة الدورية للحمل واحرصي على نمط حياة صحي.'
            }
        else:
            explanations = {
                'High': 'Your symptoms indicate a potentially serious condition requiring immediate attention.',
                'Medium': 'Some symptoms require monitoring and may need medical attention.',
                'Low': 'Your symptoms appear to be normal pregnancy-related changes.'
            }
            recommendations = {
                'High': 'Seek immediate medical care. Contact your OB/GYN or go to the emergency room.',
                'Medium': 'Contact your healthcare provider within 24 hours to discuss these symptoms.',
                'Low': 'Continue routine prenatal care and maintain a healthy lifestyle.'
            }
        
        return {
            'risk_level': risk_level,
            'explanation': explanations[risk_level],
            'recommendations': recommendations[risk_level],
            'urgent_care_needed': risk_level == 'High'
        }