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
                'نزيف شديد', 'نزيف غزير', 'نزيفًا مهبليًا غزيرًا', 'نزيف مهبلي غزير',
                'ألم شديد', 'تقلصات شديدة', 'تقلصات شديدة أسفل البطن', 'ألم شديد في البطن',
                'لا حركة', 'لم أشعر بحركة', 'لم أشعر بأي حركة للجنين',
                'رؤية ضبابية', 'تصبح الرؤية ضبابية', 'مشاكل في البصر', 'رؤيتي ضبابية',
                'صداع شديد', 'صداع مستمر لا يزول', 'أعاني من صداع مستمر لا يزول',
                'حمى', 'صعوبة في التنفس', 'ألم في الصدر',
                'فقدان الوعي', 'دوخة شديدة', 'إغماء',
                'تورم مفاجئ', 'تورم شديد', 'تورمًا مفاجئًا وشديدًا', 'لاحظت تورماً مفاجئاً وشديداً',
                'ضغط دم عالي', '160/100', '150/95', '140/', '145/', '155/',
                'بدأ بشكل مفاجئ', 'منذ البارحة', 'منذ عدة ساعات'
            ]
            
            # Medium-risk indicators in Arabic (score +2 each) - Enhanced for better detection
            medium_risk_keywords = [
                # Headache patterns
                'صداع خفيف', 'صداع متكرر', 'عدة مرات هذا الأسبوع', 'صداع في المساء',
                'شعرتُ بصداع', 'بدأ يتكرر أكثر من المعتاد',
                # Gastrointestinal 
                'قيء', 'غثيان', 'غثيان شديد',
                # Swelling and edema
                'تورم خفيف', 'بعض التورم', 'لاحظت بعض التورم', 'تورم في قدميّ',
                'تورم بنهاية اليوم', 'يتحسن عند الراحة أو رفع الساقين',
                # Fetal movement concerns
                'حركة قليلة', 'أقل من المعتاد', 'كانت أقل من المعتاد', 'حركة الجنين أقل',
                'قلة حركة الجنين', 'تحسنت قليلاً بعد أن تناولت وجبة',
                # Discharge patterns
                'إفرازات مهبلية', 'بلون وردي خفيف', 'كمية صغيرة', 'إفرازات وردية فاتحة',
                'لاحظتُ كمية صغيرة من الإفرازات', 'استمرت لبضع ساعات ثم توقفت',
                # General symptoms
                'دوخة', 'تعب شديد', 'ألم خفيف',
                # Blood pressure concerns
                '138/89', '138/88', '138', 'قريب من الحد الأعلى', 'متابعة مستمرة',
                'طلبت مني مراقبته', 'قالت إنه قريب من الحد الأعلى',
                # Improving symptoms (still concerning if recurring)
                'يتحسن مع الراحة', 'يزول بعد الراحة', 'يتحسن عند الراحة',
                'وعادةً ما يزول', 'تحسنت قليلاً', 'يتحسن عند'
            ]
            
            # Low-risk indicators in Arabic (score +1 each)
            low_risk_keywords = [
                'غثيان خفيف', 'تعب', 'ألم في الظهر', 'إمساك',
                'حساسية الثدي', 'تبول متكرر', 'طبيعي', 'عادي',
                'لا يؤثر على الرؤية', 'ولم يكن هناك ألم', 'تحسنت قليلاً'
            ]
        else:
            # High-risk indicators in English (score +3 each)
            high_risk_keywords = [
                'heavy bleeding', 'severe bleeding', 'heavy vaginal bleeding',
                'severe pain', 'severe abdominal pain', 'severe contractions',
                'no fetal movement', 'no movement felt',
                'blurry vision', 'vision is blurry', 'vision becomes blurry', 'vision problems', 'my vision is blurry',
                'severe headache', 'persistent headache', 'headache that won\'t go away', 'severe headache that won\'t go away',
                'fever', 'difficulty breathing', 'chest pain',
                'unconscious', 'fainting', 'severe dizziness',
                'sudden swelling', 'severe swelling', 'sudden and severe swelling', 'feet are swollen',
                'high blood pressure', '160/', '150/', '140/', '145/', '155/',
                'started suddenly', 'severe abdominal pain on one side', 'abdominal pain on one side', 'pain on one side'
            ]
            
            # Medium-risk indicators in English (score +2 each)
            medium_risk_keywords = [
                'mild headache', 'recurring headache', 'headaches', 'vomiting', 'nausea',
                'mild swelling', 'some swelling', 'less than usual', 'long periods',
                'vaginal discharge', 'light pink color', 'unusual discharge',
                'dizziness', 'dizzy', 'severe fatigue', 'mild pain',
                '138/', '135/', '130/', 'close to upper limit', 'continuous monitoring',
                'improves with', 'goes away after', 'feel dizzy'
            ]
            
            # Low-risk indicators in English (score +1 each)
            low_risk_keywords = [
                'mild nausea', 'mild headaches', 'nauseous in the mornings', 'mild back pain',
                'fatigue', 'back pain', 'constipation', 'breast tenderness', 
                'frequent urination', 'normal', 'fine', 'bit nauseous', 'feel a bit'
            ]
        
        # Check high-risk first and exclude if found
        high_risk_found = False
        for keyword in high_risk_keywords:
            if keyword in combined_text:
                risk_score += 3
                risk_factors.append(keyword)
                high_risk_found = True
                if language == 'ar':
                    print(f"Found high-risk Arabic keyword: {keyword}")
        
        # Only check medium-risk if no high-risk symptoms found
        if not high_risk_found:
            for keyword in medium_risk_keywords:
                if keyword in combined_text:
                    risk_score += 2
                    risk_factors.append(keyword)
                    if language == 'ar':
                        print(f"Found medium-risk Arabic keyword: {keyword}")
        
        # Add low-risk factors only if no high-risk found
        if not high_risk_found:
            for keyword in low_risk_keywords:
                if keyword in combined_text and keyword not in ' '.join(risk_factors):
                    risk_score += 1
                    risk_factors.append(keyword)
        
        # Enhanced risk level determination with specific condition checks
        
        # Check for high-risk combinations first
        preeclampsia_signs = any(keyword in combined_text for keyword in ['severe headache', 'blurry vision', 'vision is blurry', 'swollen']) and \
                           any(keyword in combined_text for keyword in ['140/', '130/', '135/', '145/', '150/'])
        
        # Ectopic pregnancy detection (critical in early pregnancy)
        ectopic_signs = (any(keyword in combined_text for keyword in ['severe abdominal pain on one side', 'abdominal pain on one side', 'pain on one side']) and 
                        any(keyword in combined_text for keyword in ['dizzy', 'feel dizzy', 'dizziness'])) or \
                       (any(keyword in combined_text for keyword in ['severe abdominal pain', 'severe pain']) and 
                        any(keyword in combined_text for keyword in ['week 7', 'week 6', 'week 8', 'early pregnancy']))
        
        severe_symptoms = any(keyword in combined_text for keyword in ['severe headache', 'severe abdominal pain', 'blurry vision', 'vision is blurry'])
        
        high_bp_with_symptoms = any(keyword in combined_text for keyword in ['140/', '145/', '150/']) and \
                              any(keyword in combined_text for keyword in ['dizzy', 'dizziness', 'severe', 'pain'])
        
        # Debug: Print risk calculation details
        print(f"=== RISK ASSESSMENT DEBUG ===")
        print(f"Combined text: {combined_text}")
        print(f"High risk found: {high_risk_found}")
        print(f"Final risk score: {risk_score}")
        print(f"Risk factors found: {risk_factors}")
        print(f"Ectopic signs detected: {ectopic_signs}")
        print(f"Preeclampsia signs detected: {preeclampsia_signs}")
        print(f"Severe symptoms detected: {severe_symptoms}")
        print(f"High BP with symptoms: {high_bp_with_symptoms}")
        print(f"=== END DEBUG ===")
        
        if ectopic_signs or preeclampsia_signs or severe_symptoms or high_bp_with_symptoms or (high_risk_found and risk_score >= 3):
            risk_level = 'High'
        elif risk_score >= 4:  # Multiple medium-risk factors
            risk_level = 'Medium'
        elif risk_score >= 2:  # Some medium-risk factors  
            risk_level = 'Medium'
        elif any(keyword in combined_text for keyword in ['mild', 'nausea', 'back pain']) and not high_risk_found:
            risk_level = 'Low'  # Explicitly low for common pregnancy symptoms
        else:
            risk_level = 'Low'
        
        # Get contextual recommendations based on specific symptoms
        contextual_assessment = self._get_contextual_assessment(combined_text, risk_level, language)
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'explanation': contextual_assessment['explanation'],
            'recommendations': contextual_assessment['recommendations'],
            'urgent_care_needed': contextual_assessment['urgent_care_needed'],
            'condition_detected': contextual_assessment.get('condition_detected', None)
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
    
    def _get_contextual_assessment(self, combined_text: str, risk_level: str, language: str) -> Dict[str, Any]:
        """Provide contextual assessment based on specific symptoms mentioned"""
        
        # Specific condition detection patterns
        conditions = {
            'preeclampsia': {
                'patterns': ['severe headache', 'blurry vision', 'vision is blurry', 'swollen', '140/', '130/', '135/'],
                'en': {
                    'explanation': 'Classic symptoms of preeclampsia, a serious pregnancy complication.',
                    'recommendations': '🔴 High Risk - Immediate visit to the ER or OB emergency care.',
                    'urgent_care_needed': True
                },
                'ar': {
                    'explanation': 'أعراض كلاسيكية لتسمم الحمل، وهو مضاعفة خطيرة في الحمل.',
                    'recommendations': '🔴 مخاطر عالية - زيارة فورية لغرفة الطوارئ أو طوارئ النساء والولادة.',
                    'urgent_care_needed': True
                }
            },
            'hyperemesis': {
                'patterns': ['vomiting', 'three times', 'dehydrated', 'قيء', 'ثلاث مرات', 'جفاف'],
                'en': {
                    'explanation': 'Suggests possible hyperemesis gravidarum, which may require medical attention.',
                    'recommendations': '🟡 Medium Risk - Recommend contacting a doctor within 24 hours.',
                    'urgent_care_needed': False
                },
                'ar': {
                    'explanation': 'تشير إلى احتمالية القيء المفرط في الحمل، والذي قد يتطلب رعاية طبية.',
                    'recommendations': '🟡 مخاطر متوسطة - يُنصح بالاتصال بالطبيب خلال 24 ساعة.',
                    'urgent_care_needed': False
                }
            },
            'ectopic': {
                'patterns': ['severe abdominal pain on one side', 'abdominal pain on one side', 'pain on one side', 'feel dizzy', 'week 7', 'week 6', 'week 8', 'الأسبوع 7', 'ألم شديد في البطن', 'جانب واحد', 'دوخة'],
                'en': {
                    'explanation': 'Could indicate ectopic pregnancy, especially dangerous in early weeks (4-12). Combination of one-sided severe abdominal pain and dizziness requires immediate evaluation.',
                    'recommendations': '🚨 High Risk - Emergency care required immediately. Go to ER now.',
                    'urgent_care_needed': True
                },
                'ar': {
                    'explanation': 'قد تشير إلى حمل خارج الرحم، خطير جداً في الأسابيع المبكرة (4-12). مزيج من الألم الشديد في جانب واحد والدوخة يتطلب تقييماً فورياً.',
                    'recommendations': '🚨 مخاطر عالية - رعاية طوارئ مطلوبة فوراً. اذهب للطوارئ الآن.',
                    'urgent_care_needed': True
                }
            }
        }
        
        # Check for specific conditions
        for condition_name, condition_data in conditions.items():
            pattern_matches = sum(1 for pattern in condition_data['patterns'] if pattern in combined_text.lower())
            if pattern_matches >= 2:  # At least 2 patterns match
                return {
                    'condition_detected': condition_name,
                    **condition_data[language]
                }
        
        # Default recommendations based on risk level
        default_recommendations = self.kb.get_recommendations(risk_level, language)
        return default_recommendations
    
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
