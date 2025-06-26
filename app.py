import streamlit as st
import json
import os
from datetime import datetime
from medical_knowledge import MedicalKnowledgeBase
from risk_assessment import RiskAssessment
from report_generator import ReportGenerator
from translations import get_translations, get_language_name
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-placeholder-key")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Page configuration
st.set_page_config(
    page_title="GraviLog - Smart Risk Analysis Agent",
    page_icon="🤱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False
if 'language' not in st.session_state:
    st.session_state.language = None
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = []
if 'user_responses' not in st.session_state:
    st.session_state.user_responses = []
if 'risk_assessment' not in st.session_state:
    st.session_state.risk_assessment = None
if 'conversation_complete' not in st.session_state:
    st.session_state.conversation_complete = False

# Initialize components
@st.cache_resource
def init_components():
    kb = MedicalKnowledgeBase()
    risk_assessor = RiskAssessment(kb)
    report_gen = ReportGenerator()
    return kb, risk_assessor, report_gen

knowledge_base, risk_assessor, report_generator = init_components()

def get_ai_questions(language, previous_responses=None):
    """Generate contextual medical questions using OpenAI based on medical knowledge base"""
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    
    system_prompt = f"""You are a medical AI assistant specialized in pregnancy risk assessment. 
    Generate 3-5 empathetic, medically relevant questions in {language} to assess pregnancy-related health risks.
    
    Base your questions on these medical knowledge areas:
    - Preeclampsia symptoms (headaches, vision changes, swelling)
    - Gestational diabetes indicators
    - Preterm labor signs  
    - Fetal movement patterns
    - Bleeding or discharge abnormalities
    - General pregnancy symptoms by trimester
    
    Questions should be:
    1. Empathetic and conversational
    2. Medically relevant for risk assessment
    3. Clear and easy to understand
    4. Appropriate for pregnant women
    
    Return your response as JSON with this format:
    {{"questions": ["question1", "question2", "question3"]}}
    """
    
    user_prompt = "Generate 3-5 pregnancy risk assessment questions"
    if previous_responses:
        user_prompt += f" considering these previous responses: {previous_responses}"
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("questions", [])
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        # Fallback to predefined questions
        return get_fallback_questions(language)

def get_fallback_questions(language):
    """Fallback questions if OpenAI is unavailable"""
    translations = get_translations(language)
    return [
        translations["question_headaches"],
        translations["question_fetal_movement"], 
        translations["question_swelling"],
        translations["question_bleeding"],
        translations["question_blood_pressure"]
    ]

def analyze_risk_with_ai(responses, language):
    """Use AI to analyze responses and determine risk level"""
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    
    system_prompt = f"""You are a medical AI specialized in pregnancy risk assessment. 
    Analyze the user's responses and assign a risk level (Low, Medium, High) based on established medical guidelines.
    
    Use this medical knowledge for assessment:
    
    HIGH RISK indicators:
    - Heavy vaginal bleeding with cramping
    - Severe headaches with vision changes and swelling (preeclampsia triad)
    - Severe abdominal pain
    - No fetal movement for extended periods
    - Fever >38.5°C with other symptoms
    - Signs of preterm labor before 37 weeks
    
    MEDIUM RISK indicators:
    - Persistent vomiting >3x/day
    - Elevated blood pressure (≥140/90)
    - Mild bleeding in 2nd/3rd trimester
    - Decreased fetal movement
    - Persistent headaches
    - Mild to moderate swelling
    
    LOW RISK indicators:
    - Normal pregnancy symptoms (mild nausea, fatigue, mild back pain)
    - Light spotting in early pregnancy
    - Normal fetal movement patterns
    
    Respond in {language} with this JSON format:
    {{
        "risk_level": "Low|Medium|High",
        "explanation": "Brief explanation of the risk assessment",
        "recommendations": "Next steps and recommendations",
        "urgent_care_needed": true/false
    }}
    """
    
    user_prompt = f"Analyze these pregnancy symptom responses: {responses}"
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        st.error(f"Error analyzing risk: {e}")
        # Fallback to rule-based assessment
        return risk_assessor.assess_risk(responses, language)

def main():
    translations = get_translations(st.session_state.language) if st.session_state.language else {}
    
    # Header
    st.title("🤱 GraviLog - Smart Risk Analysis Agent")
    
    # Language selection
    if not st.session_state.conversation_started:
        st.markdown("---")
        
        # Display language selection in both languages
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h3>Hello! Before we begin, would you like to continue in English or Arabic?</h3>
            <h3 style='direction: rtl;'>مرحبًا! قبل أن نبدأ، هل ترغبين في المتابعة باللغة الإنجليزية أم العربية؟</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("English", key="lang_en", use_container_width=True):
                st.session_state.language = "en"
                st.session_state.conversation_started = True
                st.rerun()
        
        with col3:
            if st.button("العربية", key="lang_ar", use_container_width=True):
                st.session_state.language = "ar"
                st.session_state.conversation_started = True
                st.rerun()
        
        return
    
    # Main conversation flow
    if st.session_state.conversation_started and not st.session_state.conversation_complete:
        st.markdown(f"**{translations['selected_language']}**: {get_language_name(st.session_state.language)}")
        
        # Welcome message
        if not st.session_state.questions_asked:
            st.markdown(f"### {translations['welcome_message']}")
            st.info(translations['assessment_intro'])
        
        # Generate and display questions
        if len(st.session_state.questions_asked) < 5:
            if not st.session_state.questions_asked:
                # Generate initial questions
                questions = get_ai_questions(st.session_state.language)
                st.session_state.questions_asked = questions[:3]  # Start with 3 questions
            
            # Display current question
            current_q_idx = len(st.session_state.user_responses)
            if current_q_idx < len(st.session_state.questions_asked):
                st.markdown(f"**{translations['question']} {current_q_idx + 1}:**")
                st.markdown(st.session_state.questions_asked[current_q_idx])
                
                # Response input
                response = st.text_area(
                    translations['your_response'],
                    key=f"response_{current_q_idx}",
                    height=100
                )
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(translations['next'], disabled=not response.strip()):
                        st.session_state.user_responses.append(response.strip())
                        st.rerun()
            
            # Check if we need more questions
            elif len(st.session_state.user_responses) >= 3:
                # Generate follow-up questions if needed
                if len(st.session_state.questions_asked) < 5:
                    follow_up_questions = get_ai_questions(
                        st.session_state.language, 
                        st.session_state.user_responses
                    )
                    st.session_state.questions_asked.extend(follow_up_questions[:2])
                    st.rerun()
                else:
                    # Proceed to assessment
                    if st.button(translations['complete_assessment']):
                        st.session_state.conversation_complete = True
                        st.rerun()
        
        # Display previous Q&A
        if st.session_state.user_responses:
            with st.expander(translations['previous_responses']):
                for i, (q, a) in enumerate(zip(st.session_state.questions_asked, st.session_state.user_responses)):
                    st.markdown(f"**Q{i+1}:** {q}")
                    st.markdown(f"**A:** {a}")
                    st.markdown("---")
    
    # Risk Assessment Results
    if st.session_state.conversation_complete:
        if not st.session_state.risk_assessment:
            with st.spinner(translations['analyzing']):
                assessment = analyze_risk_with_ai(
                    st.session_state.user_responses,
                    st.session_state.language
                )
                st.session_state.risk_assessment = assessment
                st.rerun()
        
        # Display risk assessment
        assessment = st.session_state.risk_assessment
        
        st.markdown(f"## {translations['risk_assessment_results']}")
        
        # Risk level with color coding
        risk_level = assessment['risk_level']
        risk_colors = {
            'Low': '#28a745',
            'Medium': '#ffc107', 
            'High': '#dc3545'
        }
        
        st.markdown(f"""
        <div style='padding: 20px; border-radius: 10px; background-color: {risk_colors.get(risk_level, '#6c757d')}20; border-left: 5px solid {risk_colors.get(risk_level, '#6c757d')};'>
            <h3 style='color: {risk_colors.get(risk_level, '#6c757d')}'>{translations['risk_level']}: {risk_level}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Explanation and recommendations
        st.markdown(f"### {translations['explanation']}")
        st.write(assessment['explanation'])
        
        st.markdown(f"### {translations['recommendations']}")
        st.write(assessment['recommendations'])
        
        # Urgent care warning
        if assessment.get('urgent_care_needed', False):
            st.error(translations['urgent_care_warning'])
        
        # Generate and download report
        st.markdown(f"### {translations['download_report']}")
        
        if st.button(translations['generate_report']):
            with st.spinner(translations['generating_report']):
                report_data = {
                    'language': st.session_state.language,
                    'timestamp': datetime.now().isoformat(),
                    'questions': st.session_state.questions_asked,
                    'responses': st.session_state.user_responses,
                    'risk_assessment': assessment
                }
                
                pdf_buffer = report_generator.generate_pdf_report(report_data)
                
                st.download_button(
                    label=translations['download_pdf'],
                    data=pdf_buffer,
                    file_name=f"pregnancy_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        
        # Start new assessment
        st.markdown("---")
        if st.button(translations['new_assessment']):
            # Reset session state
            for key in ['conversation_started', 'language', 'questions_asked', 
                       'user_responses', 'risk_assessment', 'conversation_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
