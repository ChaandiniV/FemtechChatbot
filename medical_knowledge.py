"""
Medical knowledge base for pregnancy health risk assessment
LlamaIndex-compatible knowledge structure
"""
from typing import List, Dict, Any

def get_medical_knowledge() -> List[Dict[str, Any]]:
    """Return structured medical knowledge for LlamaIndex"""
    return [
        # High-risk emergency conditions
        {
            "category": "Emergency Symptoms",
            "risk_level": "High", 
            "symptoms": ["bleeding", "نزيف", "severe pain", "ألم شديد", "cramping", "تقلصات"],
            "description": "Vaginal bleeding or severe abdominal pain requiring immediate medical attention",
            "action": "Seek emergency care",
            "score": 3
        },
        {
            "category": "Preeclampsia Signs",
            "risk_level": "High",
            "symptoms": ["vision changes", "تغيرات في الرؤية", "severe headache", "صداع شديد", "swelling face", "تورم الوجه"],
            "description": "High blood pressure disorder that can be life-threatening",
            "action": "Immediate medical evaluation required",
            "score": 3
        },
        {
            "category": "Fetal Distress",  
            "risk_level": "High",
            "symptoms": ["decreased movement", "انخفاض حركة الجنين", "no movement", "لا حركة للجنين"],
            "description": "Reduced or absent fetal movement may indicate fetal distress",
            "action": "Immediate medical evaluation",
            "score": 3
        },
        {
            "category": "Premature Labor",
            "risk_level": "High", 
            "symptoms": ["regular contractions", "تقلصات منتظمة", "water breaking", "نزول المياه", "pressure", "ضغط"],
            "description": "Signs of preterm labor before 37 weeks",
            "action": "Emergency medical care",
            "score": 3
        },
        
        # Medium-risk conditions
        {
            "category": "Severe Morning Sickness",
            "risk_level": "Medium",
            "symptoms": ["severe nausea", "غثيان شديد", "vomiting", "قيء", "dehydration", "جفاف"],
            "description": "Hyperemesis gravidarum - severe nausea preventing nutrition",
            "action": "Medical consultation needed",
            "score": 2
        },
        {
            "category": "Infection Signs",
            "risk_level": "Medium", 
            "symptoms": ["fever", "حمى", "burning urination", "حرقة عند التبول", "discharge", "إفرازات"],
            "description": "Potential infections that need treatment during pregnancy",
            "action": "Contact healthcare provider",
            "score": 2
        },
        {
            "category": "Blood Pressure Issues", 
            "risk_level": "Medium",
            "symptoms": ["dizziness", "دوخة", "headaches", "صداع", "chest pain", "ألم في الصدر"],
            "description": "Signs that may indicate blood pressure problems",
            "action": "Monitor and consult doctor",
            "score": 2
        },
        {
            "category": "Gestational Diabetes Signs",
            "risk_level": "Medium",
            "symptoms": ["excessive thirst", "عطش مفرط", "frequent urination", "كثرة التبول", "fatigue", "تعب"],
            "description": "High blood sugar during pregnancy requiring management",
            "action": "Glucose testing recommended", 
            "score": 2
        },
        
        # Low-risk normal symptoms
        {
            "category": "Normal Early Pregnancy",
            "risk_level": "Low",
            "symptoms": ["mild nausea", "غثيان خفيف", "tiredness", "تعب", "breast tenderness", "حساسية الثدي"],
            "description": "Common early pregnancy symptoms that are typically normal",
            "action": "Monitor and maintain healthy habits",
            "score": 1
        },
        {
            "category": "Normal Later Pregnancy", 
            "risk_level": "Low",
            "symptoms": ["heartburn", "حرقة المعدة", "back pain", "ألم الظهر", "mild swelling", "تورم خفيف"],
            "description": "Common later pregnancy discomforts",
            "action": "Normal pregnancy changes - comfort measures",
            "score": 1
        },
        {
            "category": "Normal Digestive Changes",
            "risk_level": "Low", 
            "symptoms": ["food aversions", "نفور من الطعام", "constipation", "إمساك", "gas", "غازات"],
            "description": "Normal digestive system changes during pregnancy",
            "action": "Dietary modifications may help",
            "score": 1
        }
    ]

def get_fallback_questions() -> Dict[str, List[str]]:
    """Fallback questions when AI generation fails"""
    return {
        "en": [
            "Are you experiencing any vaginal bleeding or spotting?",
            "Do you have severe abdominal or pelvic pain?", 
            "Have you noticed any changes in your baby's movement?",
            "Are you having regular contractions or cramping?",
            "Do you have severe headaches or vision changes?",
            "Are you experiencing persistent nausea or vomiting?",
            "Do you have any swelling in your face, hands, or feet?",
            "Are you having any difficulty breathing or chest pain?",
            "Do you have fever or signs of infection?",
            "How are you feeling overall about your pregnancy?"
        ],
        "ar": [
            "هل تعانين من نزيف مهبلي أو بقع دم؟",
            "هل لديك ألم شديد في البطن أو الحوض؟",
            "هل لاحظت أي تغيرات في حركة طفلك؟", 
            "هل تعانين من تقلصات أو انقباضات منتظمة؟",
            "هل لديك صداع شديد أو تغيرات في الرؤية؟",
            "هل تعانين من غثيان أو قيء مستمر؟",
            "هل لديك تورم في الوجه أو اليدين أو القدمين؟",
            "هل تعانين من صعوبة في التنفس أو ألم في الصدر؟",
            "هل لديك حمى أو علامات عدوى؟",
            "كيف تشعرين بشكل عام حول حملك؟"
        ]
    }

def get_risk_keywords() -> Dict[str, List[str]]:
    """Keywords for rule-based risk assessment fallback"""
    return {
        "high": [
            "bleeding", "نزيف", "blood", "دم", 
            "severe pain", "ألم شديد", "cramping", "تقلصات",
            "vision", "رؤية", "headache", "صداع",
            "contractions", "انقباضات", "water broke", "نزول المياه"
        ],
        "medium": [
            "nausea", "غثيان", "vomiting", "قيء",
            "fever", "حمى", "infection", "عدوى", 
            "dizziness", "دوخة", "swelling", "تورم",
            "chest pain", "ألم الصدر"
        ],
        "low": [
            "tired", "متعبة", "fatigue", "تعب",
            "heartburn", "حرقة", "back pain", "ألم الظهر",
            "constipation", "إمساك", "gas", "غازات"
        ]
    }