from typing import Dict, Any

def get_translations(language: str) -> Dict[str, str]:
    """Get translations for the specified language"""
    
    translations = {
        'en': {
            'selected_language': 'Selected Language',
            'welcome_message': 'Welcome to GraviLog Risk Assessment',
            'assessment_intro': 'I will ask you a few questions to assess your current health status during pregnancy. Please answer honestly and in detail.',
            'question': 'Question',
            'your_response': 'Your Response:',
            'next': 'Next',
            'complete_assessment': 'Complete Assessment',
            'previous_responses': 'Previous Questions & Responses',
            'analyzing': 'Analyzing your responses...',
            'risk_assessment_results': 'Risk Assessment Results',
            'risk_level': 'Risk Level',
            'explanation': 'Explanation',
            'recommendations': 'Recommendations',
            'urgent_care_warning': '⚠️ URGENT: Based on your responses, you should seek immediate medical attention. Please contact your healthcare provider or go to the emergency room.',
            'download_report': 'Download Your Report',
            'generate_report': 'Generate EMR Report',
            'generating_report': 'Generating your medical report...',
            'download_pdf': 'Download PDF Report',
            'new_assessment': 'Start New Assessment',
            'question_name': 'What is your name?',
            'question_age': 'What is your age?',
            'question_pregnancy_week': 'What week of pregnancy are you in?',
            'age_error': 'Please enter a valid age between 12 and 60',
            'age_format_error': 'Please enter your age as a number',
            'week_error': 'Please enter a valid pregnancy week between 1 and 42',
            'week_format_error': 'Please enter the pregnancy week as a number',
            'patient_info_title': 'Patient Information',
            'medical_questions_title': 'Medical Assessment',
            'question_headaches': 'Have you experienced headaches or blurry vision this week?',
            'question_fetal_movement': 'Do you feel your baby has been moving normally today?',
            'question_swelling': 'Have you noticed any unusual swelling in your hands, feet, or face?',
            'question_bleeding': 'Have you experienced any vaginal bleeding or unusual discharge?',
            'question_blood_pressure': 'Do you know your most recent blood pressure reading? If so, what was it?',
            'question_nausea': 'Are you experiencing any nausea or vomiting?',
            'question_fatigue': 'How would you describe your energy levels?',
            'question_pain': 'Are you experiencing any pain or discomfort?',
            'question_appetite': 'Have you noticed any changes in your appetite?',
            'question_sleep': 'How has your sleep pattern been?',
            'question_urination': 'Have you experienced any changes in urination frequency?',
            'question_contractions': 'Have you felt any contractions or tightening?'
        },
        'ar': {
            'selected_language': 'اللغة المختارة',
            'welcome_message': 'مرحباً بكِ في تقييم المخاطر GraviLog',
            'assessment_intro': 'سأطرح عليكِ بعض الأسئلة لتقييم حالتكِ الصحية الحالية أثناء الحمل. يرجى الإجابة بصدق وبالتفصيل.',
            'question': 'سؤال',
            'your_response': 'إجابتكِ:',
            'next': 'التالي',
            'complete_assessment': 'إكمال التقييم',
            'previous_responses': 'الأسئلة والإجابات السابقة',
            'analyzing': 'جاري تحليل إجاباتكِ...',
            'risk_assessment_results': 'نتائج تقييم المخاطر',
            'risk_level': 'مستوى الخطورة',
            'explanation': 'التفسير',
            'recommendations': 'التوصيات',
            'urgent_care_warning': '⚠️ عاجل: بناءً على إجاباتكِ، يجب أن تطلبي العناية الطبية الفورية. يرجى الاتصال بمقدم الرعاية الصحية أو الذهاب إلى غرفة الطوارئ.',
            'download_report': 'تحميل التقرير الخاص بكِ',
            'generate_report': 'إنشاء تقرير EMR',
            'generating_report': 'جاري إنشاء التقرير الطبي...',
            'download_pdf': 'تحميل تقرير PDF',
            'new_assessment': 'بدء تقييم جديد',
            'question_name': 'ما اسمك؟',
            'question_age': 'كم عمرك؟',
            'question_pregnancy_week': 'في أي أسبوع من الحمل أنت؟',
            'age_error': 'يرجى إدخال عمر صحيح بين 12 و 60 سنة',
            'age_format_error': 'يرجى إدخال عمرك كرقم',
            'week_error': 'يرجى إدخال أسبوع حمل صحيح بين 1 و 42',
            'week_format_error': 'يرجى إدخال أسبوع الحمل كرقم',
            'patient_info_title': 'معلومات المريضة',
            'medical_questions_title': 'التقييم الطبي',
            'question_headaches': 'هل عانيتِ من صداع أو رؤية ضبابية هذا الأسبوع؟',
            'question_fetal_movement': 'هل شعرتِ بأن حركة الجنين طبيعية اليوم؟',
            'question_swelling': 'هل لاحظتِ تورماً غير طبيعي في يديكِ أو قدميكِ أو وجهكِ؟',
            'question_bleeding': 'هل عانيتِ من نزيف مهبلي أو إفرازات غير طبيعية؟',
            'question_blood_pressure': 'هل تعرفين قراءة ضغط الدم الأخيرة لديكِ؟ إذا كان الأمر كذلك، ما هي؟',
            'question_nausea': 'هل تعانين من غثيان أو قيء؟',
            'question_fatigue': 'كيف تصفين مستوى طاقتك؟',
            'question_pain': 'هل تعانين من أي ألم أو عدم راحة؟',
            'question_appetite': 'هل لاحظتِ أي تغييرات في شهيتك؟',
            'question_sleep': 'كيف كان نمط نومك؟',
            'question_urination': 'هل واجهتِ أي تغييرات في تكرار التبول؟',
            'question_contractions': 'هل شعرتِ بأي انقباضات أو شد؟'
        }
    }
    
    return translations.get(language, translations['en'])

def get_language_name(language_code: str) -> str:
    """Get the display name for a language code"""
    
    language_names = {
        'en': 'English',
        'ar': 'العربية'
    }
    
    return language_names.get(language_code, 'English')

def get_medical_terms(language: str) -> Dict[str, str]:
    """Get medical terms translations"""
    
    medical_terms = {
        'en': {
            'preeclampsia': 'Preeclampsia',
            'gestational_diabetes': 'Gestational Diabetes',
            'preterm_labor': 'Preterm Labor',
            'miscarriage': 'Miscarriage',
            'ectopic_pregnancy': 'Ectopic Pregnancy',
            'placenta_previa': 'Placenta Previa',
            'hyperemesis_gravidarum': 'Hyperemesis Gravidarum',
            'fetal_distress': 'Fetal Distress',
            'chorioamnionitis': 'Chorioamnionitis',
            'intrauterine_growth_restriction': 'Intrauterine Growth Restriction'
        },
        'ar': {
            'preeclampsia': 'تسمم الحمل',
            'gestational_diabetes': 'سكري الحمل',
            'preterm_labor': 'الولادة المبكرة',
            'miscarriage': 'الإجهاض',
            'ectopic_pregnancy': 'الحمل خارج الرحم',
            'placenta_previa': 'المشيمة النازلة',
            'hyperemesis_gravidarum': 'القيء المفرط في الحمل',
            'fetal_distress': 'ضائقة جنينية',
            'chorioamnionitis': 'التهاب الأغشية والسائل الأمنيوسي',
            'intrauterine_growth_restriction': 'تقييد النمو داخل الرحم'
        }
    }
    
    return medical_terms.get(language, medical_terms['en'])

def get_risk_level_colors() -> Dict[str, str]:
    """Get color codes for risk levels"""
    
    return {
        'Low': '#28a745',    # Green
        'Medium': '#ffc107', # Yellow/Orange
        'High': '#dc3545'    # Red
    }

def format_rtl_text(text: str, language: str) -> str:
    """Format text for RTL languages if needed"""
    
    if language == 'ar':
        # Add RTL formatting for Arabic text
        return f'<div dir="rtl" style="text-align: right;">{text}</div>'
    
    return text
