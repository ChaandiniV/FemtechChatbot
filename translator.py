import requests
from typing import Dict, Any, Optional

class Translator:
    """Simple translation service for Arabic to English and vice versa"""
    
    def __init__(self):
        # We'll use a simple translation service or fallback to basic patterns
        self.translation_cache = {}
    
    def translate_arabic_to_english(self, arabic_text: str) -> str:
        """Translate Arabic text to English for risk assessment"""
        
        # Comprehensive Arabic medical terms to English mapping
        arabic_to_english = {
            # Questions translation
            'هل تعاني من': 'Do you experience',
            'هل تشعر بـ': 'Do you feel',
            'هل لاحظت': 'Have you noticed',
            'متى بدأت': 'When did it start',
            'كم مرة': 'How often',
            'ما مدى شدة': 'How severe is',
            'هل يوجد': 'Is there',
            'هل تعانين من': 'Do you experience',
            'هل تشعرين بـ': 'Do you feel',
            'هل لاحظت أي': 'Have you noticed any',
            'خلال فترة الحمل': 'during pregnancy',
            'في الآونة الأخيرة': 'recently',
            'في الأسابيع الماضية': 'in recent weeks',
            'منذ بداية الحمل': 'since pregnancy began',
            
            # High-risk symptoms
            'نزيف': 'bleeding',
            'نزيف شديد': 'severe bleeding',
            'نزيف مهبلي': 'vaginal bleeding',
            'نزيف غزير': 'heavy bleeding',
            'نزيفًا مهبليًا غزيرًا': 'heavy vaginal bleeding',
            'ألم شديد': 'severe pain',
            'ألم في البطن': 'abdominal pain',
            'ألم أسفل البطن': 'lower abdominal pain',
            'تقلصات شديدة': 'severe contractions',
            'تقلصات شديدة أسفل البطن': 'severe lower abdominal contractions',
            'لم أشعر بأي حركة': 'no movement felt',
            'لم أشعر بأي حركة للجنين': 'no fetal movement felt',
            'لا حركة': 'no movement',
            'لا حركة للجنين': 'no fetal movement',
            'حركة الجنين': 'fetal movement',
            'رؤية ضبابية': 'blurry vision',
            'تصبح الرؤية ضبابية': 'vision becomes blurry',
            'مشاكل في البصر': 'vision problems',
            'صداع شديد': 'severe headache',
            'صداع مستمر': 'persistent headache',
            'صداع لا يزول': 'headache that won\'t go away',
            'أعاني من صداع مستمر لا يزول': 'I suffer from persistent headache that won\'t go away',
            'تورم مفاجئ': 'sudden swelling',
            'تورم شديد': 'severe swelling',
            'تورمًا مفاجئًا وشديدًا': 'sudden and severe swelling',
            'لاحظت تورماً مفاجئاً وشديداً': 'I noticed sudden and severe swelling',
            'تورم في الوجه': 'facial swelling',
            'تورم في اليدين': 'hand swelling',
            'تورم في القدمين': 'foot swelling',
            'ضغط الدم': 'blood pressure',
            'ضغط دم عالي': 'high blood pressure',
            '160/100': 'high blood pressure 160/100',
            'دوخة شديدة': 'severe dizziness',
            'إغماء': 'fainting',
            'فقدان الوعي': 'loss of consciousness',
            'ضيق في التنفس': 'shortness of breath',
            'صعوبة في التنفس': 'difficulty breathing',
            'حمى': 'fever',
            'حرارة عالية': 'high fever',
            'بدأ بشكل مفاجئ': 'started suddenly',
            'منذ البارحة': 'since yesterday',
            'منذ عدة ساعات': 'since several hours',
            'مع المسكنات': 'with painkillers',
            'مصحوبًا': 'accompanied by',
            
            # Medium-risk symptoms
            'صداع': 'headache',
            'تورم': 'swelling',
            'غثيان': 'nausea',
            'قيء': 'vomiting',
            'تعب': 'fatigue',
            'إرهاق': 'exhaustion',
            'ألم': 'pain',
            'دوخة': 'dizziness',
            'دوار': 'vertigo',
            'حرقة المعدة': 'heartburn',
            'عسر الهضم': 'indigestion',
            'إمساك': 'constipation',
            'إسهال': 'diarrhea',
            'آلام الظهر': 'back pain',
            'تشنجات': 'cramps',
            
            # Normal pregnancy symptoms
            'غثيان الصباح': 'morning sickness',
            'تعب خفيف': 'mild fatigue',
            'تورم طفيف': 'mild swelling',
            'آلام خفيفة': 'mild pain',
            
            # Common responses
            'نعم': 'yes',
            'لا': 'no',
            'أعاني': 'I suffer from',
            'أعاني من': 'I suffer from',
            'أشعر': 'I feel',
            'أشعر بـ': 'I feel',
            'لاحظت': 'I noticed',
            'شعرت': 'I felt',
            'عندي': 'I have',
            'يوجد': 'there is',
            'موجود': 'present',
            'طبيعي': 'normal',
            'عادي': 'normal',
            'طفيف': 'mild',
            'متوسط': 'moderate',
            'شديد': 'severe',
            'أحياناً': 'sometimes',
            'دائماً': 'always',
            'أبداً': 'never',
            'كثيراً': 'frequently',
            'قليلاً': 'rarely',
            
            # Time indicators
            'اليوم': 'today',
            'أمس': 'yesterday',
            'هذا الأسبوع': 'this week',
            'الأسبوع الماضي': 'last week',
            'منذ أسبوع': 'since a week ago',
            'منذ يومين': 'since two days ago',
            'صباحاً': 'in the morning',
            'مساءً': 'in the evening',
            'ليلاً': 'at night'
        }
        
        # Translate the text by replacing Arabic phrases with English equivalents
        translated_text = arabic_text.lower()
        
        # Sort by length (longest first) to avoid partial replacements
        for arabic_phrase, english_phrase in sorted(arabic_to_english.items(), key=lambda x: len(x[0]), reverse=True):
            if arabic_phrase in translated_text:
                translated_text = translated_text.replace(arabic_phrase, english_phrase)
        
        return translated_text
    
    def translate_english_to_arabic(self, english_text: str) -> str:
        """Translate English medical terms back to Arabic for EMR reports"""
        
        english_to_arabic = {
            # Risk levels
            'high': 'عالي',
            'medium': 'متوسط',
            'low': 'منخفض',
            'High': 'عالي',
            'Medium': 'متوسط',
            'Low': 'منخفض',
            
            # Medical terms
            'bleeding': 'نزيف',
            'severe bleeding': 'نزيف شديد',
            'vaginal bleeding': 'نزيف مهبلي',
            'heavy bleeding': 'نزيف غزير',
            'severe pain': 'ألم شديد',
            'abdominal pain': 'ألم في البطن',
            'severe contractions': 'تقلصات شديدة',
            'no fetal movement': 'لا حركة للجنين',
            'blurry vision': 'رؤية ضبابية',
            'severe headache': 'صداع شديد',
            'persistent headache': 'صداع مستمر',
            'sudden swelling': 'تورم مفاجئ',
            'severe swelling': 'تورم شديد',
            'high blood pressure': 'ضغط دم عالي',
            'severe dizziness': 'دوخة شديدة',
            
            # Recommendations
            'immediate medical attention': 'عناية طبية فورية',
            'contact your doctor': 'اتصلي بطبيبك',
            'go to hospital': 'اذهبي إلى المستشفى',
            'urgent care needed': 'رعاية عاجلة مطلوبة',
            'continue regular follow-up': 'استمري في المتابعة المنتظمة',
            'stable condition': 'حالة مستقرة'
        }
        
        translated_text = english_text
        
        # Sort by length (longest first) to avoid partial replacements
        for english_phrase, arabic_phrase in sorted(english_to_arabic.items(), key=lambda x: len(x[0]), reverse=True):
            if english_phrase in translated_text:
                translated_text = translated_text.replace(english_phrase, arabic_phrase)
        
        return translated_text

    def translate_responses_for_assessment(self, responses: list, language: str) -> list:
        """Translate Arabic responses to English for risk assessment"""
        if language != 'ar':
            return responses
        
        translated_responses = []
        for response in responses:
            translated = self.translate_arabic_to_english(response)
            translated_responses.append(translated)
            print(f"Translated '{response}' -> '{translated}'")
        
        return translated_responses

# Global translator instance
translator = Translator()