import json
import re
from typing import Dict, List, Any
from medical_knowledge import MedicalKnowledgeBase

class RiskAssessment:
    def __init__(self, knowledge_base: MedicalKnowledgeBase):
        self.kb = knowledge_base
        
    def assess_risk(self, responses: List[str], language: str = 'en') -> Dict[str, Any]:
        """Assess risk based on user responses using rule-based logic as fallback"""
        
        # Combine all responses into a single text for analysis
        combined_text = ' '.join(responses).lower()
        
        # Debug: Print combined text for Arabic debugging
        if language == 'ar':
            print(f"=== ARABIC RISK ASSESSMENT DEBUG ===")
            print(f"Combined text: {combined_text}")
            print(f"Number of responses: {len(responses)}")
            print(f"Responses: {responses}")
            print(f"Language: {language}")
        
        # Initialize risk score
        risk_score = 0
        risk_factors = []
        
        # Define bilingual keywords for risk assessment
        if language == 'ar':
            # High-risk indicators in Arabic (score +3 each) - Based on actual user responses
            high_risk_keywords = [
                'نزيف شديد', 'نزيف مهبلي', 'نزيف غزير', 'نزيفًا', 'نزيف',
                'نزيفًا مهبليًا غزيرًا', 'نزيف مهبلي غزير', 'نزيفا مهبليا غزيرا',
                'ألم شديد', 'ألم في البطن', 'تقلصات شديدة', 'تقلصات شديدة أسفل البطن',
                'لا حركة', 'لم أشعر بحركة', 'لم أشعر بأي حركة', 'لم أشعر بأي حركة للجنين',
                'رؤية ضبابية', 'رؤية مشوشة', 'تصبح الرؤية ضبابية', 'أحيانًا تصبح الرؤية ضبابية',
                'صداع شديد', 'صداع مستمر', 'صداع لا يزول', 'أعاني من صداع مستمر لا يزول',
                'حمى', 'صعوبة في التنفس', 'ألم في الصدر',
                'فقدان الوعي', 'دوخة شديدة', 'ضغط الدم', '160/100',
                'تورم مفاجئ', 'تورم شديد', 'تورمًا مفاجئًا وشديدًا', 'لاحظت تورماً مفاجئاً وشديداً',
                'بدأ بشكل مفاجئ', 'منذ البارحة', 'منذ عدة ساعات'
            ]
            
            # Medium-risk indicators in Arabic (score +2 each)
            medium_risk_keywords = [
                'قيء', 'تورم', 'صداع', 'حركة قليلة', 'ألم', 'إفرازات', 'غثيان', 
                'دوخة', 'تعب شديد', 'نعم', 'أعاني', 'أشعر', 'لاحظت', 'عندي', 
                'موجود', 'يوجد', 'احس', 'اشعر', 'اعاني', 'لاحظت', 'شعرت',
                'مصحوبًا', 'بدأ بشكل مفاجئ', 'ضغط في الرأس', 'مع المسكنات'
            ]
            
            # Low-risk indicators in Arabic (score +1 each)
            low_risk_keywords = [
                'غثيان خفيف', 'تعب', 'ألم في الظهر', 'إمساك',
                'حساسية الثدي', 'تبول متكرر', 'طبيعي', 'عادي'
            ]
        else:
            # High-risk indicators in English (score +3 each)
            high_risk_keywords = [
                'heavy bleeding', 'severe pain', 'no movement', 'blurry vision',
                'severe headache', 'fever', 'difficulty breathing', 'chest pain',
                'severe abdominal pain', 'heavy vaginal bleeding', 'unconscious',
                'yes bleeding', 'yes pain', 'yes headache', 'yes fever'
            ]
            
            # Medium-risk indicators in English (score +2 each)
            medium_risk_keywords = [
                'vomiting', 'blood pressure', 'swelling', 'headache',
                'bleeding', 'decreased movement', 'pain', 'discharge',
                'nausea', 'dizziness', 'severe fatigue', 'yes', 'experiencing'
            ]
            
            # Low-risk indicators in English (score +1 each)
            low_risk_keywords = [
                'mild nausea', 'fatigue', 'back pain', 'constipation',
                'breast tenderness', 'frequent urination', 'normal', 'fine'
            ]
        
        for keyword in high_risk_keywords:
            if keyword in combined_text:
                risk_score += 3
                risk_factors.append(keyword)
                if language == 'ar':
                    print(f"Found high-risk Arabic keyword: {keyword}")
        
        for keyword in medium_risk_keywords:
            if keyword in combined_text and keyword not in ' '.join(risk_factors):
                risk_score += 2
                risk_factors.append(keyword)
                if language == 'ar':
                    print(f"Found medium-risk Arabic keyword: {keyword}")
        
        for keyword in low_risk_keywords:
            if keyword in combined_text and keyword not in ' '.join(risk_factors):
                risk_score += 1
                risk_factors.append(keyword)
        
        # Debug: Print final risk calculation
        if language == 'ar':
            print(f"Final risk score: {risk_score}")
            print(f"Risk factors found: {risk_factors}")
            print(f"=== END DEBUG ===")
        
        # Determine risk level based on score
        if risk_score >= 6:
            risk_level = 'High'
        elif risk_score >= 3:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Get recommendations from knowledge base
        recommendations = self.kb.get_recommendations(risk_level, language)
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'explanation': recommendations['explanation'],
            'recommendations': recommendations['recommendations'],
            'urgent_care_needed': recommendations['urgent_care_needed']
        }
    
    def check_emergency_symptoms(self, responses: List[str]) -> bool:
        """Check if responses contain emergency symptoms requiring immediate care"""
        
        emergency_keywords = [
            'heavy bleeding', 'severe pain', 'no fetal movement', 'seizure',
            'loss of consciousness', 'difficulty breathing', 'chest pain',
            'severe headache with vision changes'
        ]
        
        combined_text = ' '.join(responses).lower()
        
        return any(keyword in combined_text for keyword in emergency_keywords)
    
    def analyze_symptom_patterns(self, responses: List[str]) -> Dict[str, Any]:
        """Analyze symptom patterns for detailed assessment"""
        
        patterns = {
            'preeclampsia_indicators': 0,
            'preterm_labor_indicators': 0,
            'gestational_diabetes_indicators': 0,
            'infection_indicators': 0
        }
        
        combined_text = ' '.join(responses).lower()
        
        # Preeclampsia pattern
        preeclampsia_keywords = ['headache', 'vision', 'swelling', 'blood pressure']
        patterns['preeclampsia_indicators'] = sum(1 for keyword in preeclampsia_keywords if keyword in combined_text)
        
        # Preterm labor pattern
        preterm_keywords = ['contractions', 'pressure', 'cramping', 'back pain']
        patterns['preterm_labor_indicators'] = sum(1 for keyword in preterm_keywords if keyword in combined_text)
        
        # Gestational diabetes pattern
        diabetes_keywords = ['thirst', 'fatigue', 'urination', 'blurred vision']
        patterns['gestational_diabetes_indicators'] = sum(1 for keyword in diabetes_keywords if keyword in combined_text)
        
        # Infection pattern
        infection_keywords = ['fever', 'discharge', 'burning', 'odor']
        patterns['infection_indicators'] = sum(1 for keyword in infection_keywords if keyword in combined_text)
        
        return patterns
    
    def get_detailed_assessment(self, responses: List[str], language: str = 'en') -> Dict[str, Any]:
        """Provide detailed risk assessment with pattern analysis"""
        
        basic_assessment = self.assess_risk(responses, language)
        patterns = self.analyze_symptom_patterns(responses)
        emergency_check = self.check_emergency_symptoms(responses)
        
        # Enhance assessment with pattern analysis
        detailed_assessment = basic_assessment.copy()
        detailed_assessment['symptom_patterns'] = patterns
        detailed_assessment['emergency_symptoms_detected'] = emergency_check
        
        # Adjust risk level if emergency symptoms detected
        if emergency_check:
            detailed_assessment['risk_level'] = 'High'
            detailed_assessment['urgent_care_needed'] = True
        
        return detailed_assessment
