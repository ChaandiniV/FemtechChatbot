import json
import re
from typing import Dict, List, Any

class MedicalKnowledgeBase:
    def __init__(self):
        self.knowledge = self._load_knowledge_base()
        self.risk_indicators = self._extract_risk_indicators()
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load and parse the medical knowledge base from the provided files"""
        
        # Pregnancy knowledge base content
        pregnancy_knowledge = """
        PREGNANCY RISK MANAGEMENT KNOWLEDGE BASE
        
        SYMPTOM CATEGORIZATION BY SEVERITY AND CONTEXT
        
        NORMAL (LOW RISK) SYMPTOMS:
        - Mild Nausea: Common in the 1st trimester due to hCG hormone changes
        - Light Spotting: Possible during implantation (first 4-6 weeks of pregnancy)
        - Mild Back Pain: Due to ligament stretching as uterus expands
        - Constipation & Gas: Related to progesterone hormone slowing digestion
        - Mild Fatigue: Normal during first and third trimesters
        - Breast Tenderness: Common early pregnancy symptom
        - Frequent Urination: Normal due to increased blood volume and uterine pressure
        
        MEDIUM RISK INDICATORS:
        - Persistent Vomiting >3x/day: Could suggest hyperemesis gravidarum requiring medical attention
        - Elevated Blood Pressure (≥140/90): Must monitor for preeclampsia development
        - Gestational Diabetes Symptoms: Excessive thirst, fatigue, frequent urination beyond normal
        - Mild Vaginal Bleeding in 2nd/3rd Trimester: Needs immediate OB evaluation
        - Severe Heartburn: May indicate GERD requiring treatment
        - Swollen Hands/Feet: Monitor for preeclampsia if sudden or severe
        - Decreased Fetal Movement: After 28 weeks, reduced movement patterns need evaluation
        
        HIGH RISK / EMERGENCY SYMPTOMS:
        - Heavy Vaginal Bleeding + Cramping: Indicates possible miscarriage or placental abruption
        - Severe Abdominal Pain (localized): Possible ectopic pregnancy if early, other complications if later
        - Blurry Vision + Headache + Swelling: Classic triad of preeclampsia requiring immediate care
        - Fever >38.5°C with chills: Suspected intrauterine infection
        - Reduced or No Fetal Movement: Fetal distress, hypoxia, or demise requiring emergency assessment
        - Severe Chest Pain: Possible pulmonary embolism or cardiac issues
        - Difficulty Breathing: May indicate pulmonary edema or embolism
        - Persistent Severe Headaches: Possible preeclampsia or hypertensive crisis
        """
        
        # Pregnancy guidelines content
        pregnancy_guidelines = """
        PREGNANCY RISK ASSESSMENT KNOWLEDGE BASE
        
        RED FLAG SYMPTOM COMBINATIONS
        
        CRITICAL COMBINATIONS REQUIRING IMMEDIATE CARE:
        1. Severe headache + vision changes + swelling = Preeclampsia (HIGH RISK)
        2. Bleeding + sharp abdominal pain + low blood pressure = Ectopic Pregnancy (HIGH RISK)
        3. Fever + vaginal discharge + abdominal tenderness = Chorioamnionitis/Infection (HIGH RISK)
        4. No fetal movement after 28 weeks = Fetal demise or distress (HIGH RISK)
        5. Contractions <37 weeks + cervical changes = Preterm labor (MEDIUM-HIGH RISK)
        
        EMERGENCY CONTACT CRITERIA
        
        CALL 911 IMMEDIATELY FOR:
        - Heavy bleeding with clots
        - Severe abdominal pain
        - Loss of consciousness
        - Difficulty breathing
        - Chest pain
        - Seizures
        - Signs of stroke
        
        CONTACT OB/GYN URGENTLY FOR:
        - Persistent vomiting
        - High fever
        - Severe headache
        - Vision changes
        - Decreased fetal movement
        - Leaking fluid
        - Regular contractions before 37 weeks
        """
        
        return {
            'pregnancy_knowledge': pregnancy_knowledge,
            'pregnancy_guidelines': pregnancy_guidelines
        }
    
    def _extract_risk_indicators(self) -> Dict[str, List[str]]:
        """Extract risk indicators from knowledge base"""
        
        risk_indicators = {
            'low_risk': [
                'mild nausea', 'light spotting', 'mild back pain', 'constipation',
                'mild fatigue', 'breast tenderness', 'frequent urination'
            ],
            'medium_risk': [
                'persistent vomiting', 'elevated blood pressure', 'gestational diabetes',
                'mild vaginal bleeding', 'severe heartburn', 'swollen hands',
                'swollen feet', 'decreased fetal movement'
            ],
            'high_risk': [
                'heavy vaginal bleeding', 'severe abdominal pain', 'blurry vision',
                'headache with swelling', 'fever with chills', 'no fetal movement',
                'severe chest pain', 'difficulty breathing', 'persistent severe headaches'
            ],
            'emergency_combinations': [
                'severe headache + vision changes + swelling',
                'bleeding + sharp abdominal pain',
                'fever + vaginal discharge + abdominal tenderness',
                'no fetal movement after 28 weeks',
                'contractions before 37 weeks'
            ]
        }
        
        return risk_indicators
    
    def get_symptom_risk_level(self, symptoms: List[str]) -> str:
        """Determine risk level based on reported symptoms"""
        symptoms_lower = [s.lower() for s in symptoms]
        
        # Check for high-risk indicators
        for symptom in symptoms_lower:
            for high_risk in self.risk_indicators['high_risk']:
                if high_risk in symptom:
                    return 'High'
        
        # Check for emergency combinations
        symptom_text = ' '.join(symptoms_lower)
        for combination in self.risk_indicators['emergency_combinations']:
            if self._check_symptom_combination(symptom_text, combination):
                return 'High'
        
        # Check for medium-risk indicators
        for symptom in symptoms_lower:
            for medium_risk in self.risk_indicators['medium_risk']:
                if medium_risk in symptom:
                    return 'Medium'
        
        return 'Low'
    
    def _check_symptom_combination(self, symptom_text: str, combination: str) -> bool:
        """Check if symptom combination is present in text"""
        parts = combination.split(' + ')
        return all(part.strip() in symptom_text for part in parts)
    
    def get_recommendations(self, risk_level: str, language: str = 'en') -> Dict[str, str]:
        """Get recommendations based on risk level"""
        
        recommendations = {
            'en': {
                'Low': {
                    'explanation': 'These are common pregnancy symptoms due to hormonal changes and ligament stretching.',
                    'recommendations': '🟢 Low Risk - Monitor at home; routine prenatal care is sufficient.',
                    'urgent_care_needed': False
                },
                'Medium': {
                    'explanation': 'These symptoms suggest possible complications that may require medical attention.',
                    'recommendations': '🟡 Medium Risk - Recommend contacting a doctor within 24 hours.',
                    'urgent_care_needed': False
                },
                'High': {
                    'explanation': 'These symptoms indicate serious pregnancy complications requiring immediate care.',
                    'recommendations': '🔴 High Risk - Immediate visit to the ER or OB emergency care required.',
                    'urgent_care_needed': True
                }
            },
            'ar': {
                'Low': {
                    'explanation': 'هذه أعراض شائعة في الحمل بسبب التغيرات الهرمونية وتمدد الأربطة.',
                    'recommendations': '🟢 مخاطر منخفضة - راقبي في المنزل؛ الرعاية الدورية للحمل كافية.',
                    'urgent_care_needed': False
                },
                'Medium': {
                    'explanation': 'تشير هذه الأعراض إلى مضاعفات محتملة قد تتطلب رعاية طبية.',
                    'recommendations': '🟡 مخاطر متوسطة - يُنصح بالاتصال بالطبيب خلال 24 ساعة.',
                    'urgent_care_needed': False
                },
                'High': {
                    'explanation': 'تشير هذه الأعراض إلى مضاعفات خطيرة في الحمل تتطلب رعاية فورية.',
                    'recommendations': '🔴 مخاطر عالية - مطلوب زيارة فورية لغرفة الطوارئ أو طوارئ النساء والولادة.',
                    'urgent_care_needed': True
                }
            }
        }
        
        return recommendations[language][risk_level]
    
    def get_questions_by_category(self, category: str, language: str = 'en') -> List[str]:
        """Get medical questions by category"""
        
        questions = {
            'en': {
                'general': [
                    "Have you experienced any unusual bleeding or discharge?",
                    "How would you describe your baby's movements today compared to yesterday?",
                    "Have you had any headaches that won't go away or that affect your vision?",
                    "Do you feel any pressure or pain in your pelvis or lower back?",
                    "Have you noticed any swelling in your hands, face, or feet?"
                ],
                'preeclampsia': [
                    "Have you experienced severe headaches recently?",
                    "Have you noticed any changes in your vision, such as blurriness or seeing spots?",
                    "Have you had any sudden swelling in your hands, face, or feet?",
                    "Do you know your most recent blood pressure reading?"
                ],
                'fetal_movement': [
                    "When did you last feel your baby move?",
                    "How many times did you feel your baby move in the last hour?",
                    "Have you noticed any changes in your baby's movement patterns?"
                ]
            },
            'ar': {
                'general': [
                    "هل عانيتِ من نزيف غير طبيعي أو إفرازات؟",
                    "كيف تصفين حركة الجنين اليوم مقارنة بالأمس؟",
                    "هل عانيتِ من صداع لا يزول أو يؤثر على رؤيتكِ؟",
                    "هل تشعرين بضغط أو ألم في الحوض أو أسفل الظهر؟",
                    "هل لاحظتِ أي تورم في يديكِ أو وجهكِ أو قدميكِ؟"
                ],
                'preeclampsia': [
                    "هل عانيتِ من صداع شديد مؤخراً؟",
                    "هل لاحظتِ أي تغييرات في رؤيتكِ، مثل عدم وضوح الرؤية أو رؤية بقع؟",
                    "هل عانيتِ من تورم مفاجئ في يديكِ أو وجهكِ أو قدميكِ؟",
                    "هل تعرفين قراءة ضغط الدم الأخيرة لديكِ؟"
                ],
                'fetal_movement': [
                    "متى آخر مرة شعرتِ بحركة الجنين؟",
                    "كم مرة شعرتِ بحركة الجنين في الساعة الماضية؟",
                    "هل لاحظتِ أي تغييرات في أنماط حركة الجنين؟"
                ]
            }
        }
        
        return questions[language].get(category, questions[language]['general'])
    
    def get_bilingual_medical_guidelines(self, language: str = 'en') -> Dict[str, str]:
        """Get comprehensive bilingual medical guidelines for pregnancy"""
        guidelines = {
            'emergency_symptoms': {
                'en': "Emergency symptoms requiring immediate attention: severe bleeding, no fetal movement, severe headaches with vision changes, severe abdominal pain, high blood pressure readings (>160/100).",
                'ar': "الأعراض الطارئة التي تتطلب عناية فورية: نزيف شديد، عدم حركة الجنين، صداع شديد مع تغيرات في الرؤية، ألم شديد في البطن، قراءات ضغط دم عالية (>160/100)."
            },
            'moderate_symptoms': {
                'en': "Moderate symptoms requiring medical consultation: mild recurring headaches, reduced fetal movement, mild swelling, elevated blood pressure (130-160/80-100), unusual discharge.",
                'ar': "أعراض متوسطة تتطلب استشارة طبية: صداع خفيف متكرر، قلة حركة الجنين، تورم خفيف، ارتفاع ضغط الدم (130-160/80-100)، إفرازات غير عادية."
            },
            'normal_symptoms': {
                'en': "Normal pregnancy symptoms: mild fatigue, occasional nausea, mild back pain, mild swelling that improves with rest, normal fetal movement patterns.",
                'ar': "أعراض الحمل الطبيعية: تعب خفيف، غثيان عرضي، ألم خفيف في الظهر، تورم خفيف يتحسن مع الراحة، أنماط حركة جنين طبيعية."
            },
            'when_to_call': {
                'en': "Call your healthcare provider immediately for: bleeding, severe pain, no fetal movement for 12+ hours, severe headaches, vision changes, high blood pressure symptoms.",
                'ar': "اتصلي بمقدم الرعاية الصحية فوراً في حالة: النزيف، الألم الشديد، عدم حركة الجنين لأكثر من 12 ساعة، الصداع الشديد، تغيرات الرؤية، أعراض ضغط الدم العالي."
            }
        }
        
        return {key: value[language] for key, value in guidelines.items()}
    
    def get_arabic_medical_assessment_context(self) -> Dict[str, Any]:
        """Get comprehensive Arabic medical context for better risk assessment"""
        return {
            'high_risk_patterns': {
                'bleeding': ['نزيف شديد', 'نزيف غزير', 'دم كثير'],
                'neurological': ['صداع شديد مع تغيرات في الرؤية', 'رؤية ضبابية', 'دوخة شديدة', 'إغماء'],
                'fetal_concerns': ['عدم حركة الجنين', 'لا حركة للجنين منذ', 'توقف حركة الجنين'],
                'hypertension': ['ضغط دم عالي جداً', '160', '170', '180', '100', '110'],
                'respiratory': ['صعوبة في التنفس', 'ضيق تنفس شديد', 'ألم في الصدر']
            },
            'medium_risk_patterns': {
                'mild_headaches': ['صداع خفيف متكرر', 'صداع عدة مرات', 'صداع في المساء'],
                'reduced_movement': ['حركة أقل من المعتاد', 'قلة حركة الجنين', 'تحسنت بعد الأكل'],
                'mild_swelling': ['تورم خفيف', 'تورم في نهاية اليوم', 'يتحسن مع الراحة'],
                'mild_bleeding': ['إفرازات وردية', 'كمية صغيرة', 'استمرت ساعات قليلة'],
                'borderline_bp': ['138', '140', '145', '88', '90', 'قريب من الحد الأعلى']
            },
            'normal_patterns': {
                'typical_symptoms': ['غثيان خفيف', 'تعب بسيط', 'ألم ظهر خفيف'],
                'reassuring_signs': ['طبيعي', 'عادي', 'حالة جيدة', 'يزول مع الراحة']
            }
        }
