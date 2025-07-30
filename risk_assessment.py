"""
Rule-based risk assessment for pregnancy health
Fallback when AI systems are unavailable
"""
import logging
from typing import Dict, List, Any
from medical_knowledge import get_risk_keywords

logger = logging.getLogger(__name__)

class RiskAssessment:
    """Rule-based risk assessment using keyword matching"""
    
    def __init__(self):
        self.risk_keywords = get_risk_keywords()
        
    def assess_risk(self, responses: List[Dict], language: str = "en") -> Dict[str, Any]:
        """Assess pregnancy risk based on responses using rule-based logic"""
        
        risk_score = 0
        risk_factors = []
        detected_conditions = []
        
        # Combine all responses for analysis
        combined_text = ""
        for response in responses:
            answer = response.get("answer", "").lower()
            combined_text += " " + answer
        
        # Check for high-risk keywords
        for keyword in self.risk_keywords["high"]:
            if keyword.lower() in combined_text:
                risk_score += 3
                if language == "ar":
                    risk_factors.append(f"عرض عالي الخطورة: {keyword}")
                else:
                    risk_factors.append(f"High-risk symptom: {keyword}")
        
        # Check for medium-risk keywords
        for keyword in self.risk_keywords["medium"]:
            if keyword.lower() in combined_text:
                risk_score += 2
                if language == "ar":
                    risk_factors.append(f"عرض متوسط الخطورة: {keyword}")
                else:
                    risk_factors.append(f"Medium-risk symptom: {keyword}")
        
        # Check for low-risk keywords
        for keyword in self.risk_keywords["low"]:
            if keyword.lower() in combined_text:
                risk_score += 1
                if language == "ar":
                    risk_factors.append(f"عرض منخفض الخطورة: {keyword}")
                else:
                    risk_factors.append(f"Low-risk symptom: {keyword}")
        
        # Determine risk level
        if risk_score >= 6:
            risk_level = "عالي" if language == "ar" else "High"
            if language == "ar":
                recommendations = ["استشر طبيبك فوراً", "اذهب إلى المستشفى"]
            else:
                recommendations = ["Consult your doctor immediately", "Go to hospital"]
        elif risk_score >= 3:
            risk_level = "متوسط" if language == "ar" else "Medium"
            if language == "ar":
                recommendations = ["اتصل بطبيبك", "راقب الأعراض"]
            else:
                recommendations = ["Contact your doctor", "Monitor symptoms"]
        else:
            risk_level = "منخفض" if language == "ar" else "Low"
            if language == "ar":
                recommendations = ["متابعة روتينية", "حافظ على العادات الصحية"]
            else:
                recommendations = ["Routine follow-up", "Maintain healthy habits"]
        
        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 10),  # Cap at 10
            "reasons": risk_factors[:3],  # Max 3 reasons
            "recommendations": recommendations
        }