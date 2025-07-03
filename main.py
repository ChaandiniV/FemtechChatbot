from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from medical_knowledge import MedicalKnowledgeBase
from risk_assessment import RiskAssessment
from report_generator import ReportGenerator
from translations import get_translations, get_language_name
from rag_system import RAGSystem
from huggingface_client import HuggingFaceClient
from translator import translator

# Initialize FastAPI app
app = FastAPI(title="GraviLog - Smart Risk Analysis Agent", version="1.0.0")

# Add CORS middleware for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files
templates = Jinja2Templates(directory="templates")

# Initialize components
knowledge_base = MedicalKnowledgeBase()
risk_assessor = RiskAssessment(knowledge_base)
report_generator = ReportGenerator()
rag_system = RAGSystem(knowledge_base)
hf_client = HuggingFaceClient()

# In-memory session storage (in production, use Redis or database)
sessions = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with language selection"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/assessment", response_class=HTMLResponse)
async def assessment_page(request: Request, session_id: str):
    """Assessment page"""
    if session_id not in sessions:
        # Redirect to home if session doesn't exist
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/")
    
    session = sessions[session_id]
    language = session.get('language', 'en')
    translations_data = get_translations(language)
    
    return templates.TemplateResponse("chat_assessment.html", {
        "request": request,
        "session_id": session_id,
        "language": language,
        "translations": translations_data
    })

@app.post("/start-session")
async def start_session(language: str = Form(...)):
    """Start a new assessment session"""
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    sessions[session_id] = {
        "session_id": session_id,
        "language": language,
        "phase": "patient_info",  # patient_info -> medical_questions -> completed
        "patient_info": {
            "name": None,
            "age": None,
            "pregnancy_week": None
        },
        "questions_asked": [],
        "user_responses": [],
        "current_question_index": 0,
        "current_patient_info_step": 0,  # 0=name, 1=age, 2=pregnancy_week
        "risk_assessment": None,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    
    return {"session_id": session_id, "phase": "patient_info"}

@app.post("/patient-info/{session_id}")
async def submit_patient_info(session_id: str, info_value: str = Form(...)):
    """Submit patient information (name, age, or pregnancy week)"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if session["phase"] != "patient_info":
        raise HTTPException(status_code=400, detail="Not in patient info collection phase")
    
    current_step = session["current_patient_info_step"]
    translations = get_translations(session["language"])
    
    # Store the information based on current step
    if current_step == 0:  # Name
        session["patient_info"]["name"] = info_value.strip()
        session["current_patient_info_step"] = 1
        return {
            "message": translations.get("question_age", "What is your age?"),
            "next_step": "patient_info",
            "step": 1
        }
    elif current_step == 1:  # Age
        try:
            age = int(info_value.strip())
            if age < 12 or age > 60:
                return {"error": translations.get("age_error", "Please enter a valid age between 12 and 60")}
            session["patient_info"]["age"] = age
            session["current_patient_info_step"] = 2
            return {
                "message": translations.get("question_pregnancy_week", "What week of pregnancy are you in?"),
                "next_step": "patient_info",
                "step": 2
            }
        except ValueError:
            return {"error": translations.get("age_format_error", "Please enter your age as a number")}
    elif current_step == 2:  # Pregnancy week
        try:
            week = int(info_value.strip())
            if week < 1 or week > 42:
                return {"error": translations.get("week_error", "Please enter a valid pregnancy week between 1 and 42")}
            session["patient_info"]["pregnancy_week"] = week
            
            # Move to medical questions phase
            session["phase"] = "medical_questions"
            session["current_patient_info_step"] = 0
            
            # Generate initial medical questions using patient context
            patient_context = f"Patient: {session['patient_info']['name']}, Age: {session['patient_info']['age']}, Pregnancy Week: {session['patient_info']['pregnancy_week']}"
            initial_questions = await generate_contextual_questions(session["language"], [patient_context])
            session["questions_asked"] = initial_questions[:3]
            
            return {
                "message": translations.get("questions_intro", "Great! Now I'll ask you some medical questions."),
                "next_step": "questions"
            }
        except ValueError:
            return {"error": translations.get("week_format_error", "Please enter the pregnancy week as a number")}

@app.get("/question/{session_id}")
async def get_current_question(session_id: str):
    """Get current question for the session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    translations = get_translations(session["language"])
    
    # Check if assessment is already completed
    if session["phase"] == "completed" or session.get("completed", False):
        return {"completed": True, "message": "Assessment completed"}
    
    # Handle patient info phase
    if session["phase"] == "patient_info":
        current_step = session["current_patient_info_step"]
        
        if current_step == 0:
            return {
                "phase": "patient_info",
                "question": translations.get("question_name", "What is your name?"),
                "step": 0,
                "field": "name",
                "translations": translations
            }
        elif current_step == 1:
            return {
                "phase": "patient_info", 
                "question": translations.get("question_age", "What is your age?"),
                "step": 1,
                "field": "age",
                "translations": translations
            }
        elif current_step == 2:
            return {
                "phase": "patient_info",
                "question": translations.get("question_pregnancy_week", "What week of pregnancy are you in?"),
                "step": 2,
                "field": "pregnancy_week",
                "translations": translations
            }
    
    # Handle medical questions phase
    elif session["phase"] == "medical_questions":
        current_idx = session["current_question_index"]
        
        if current_idx >= len(session["questions_asked"]):
            return {"completed": True, "message": "Assessment completed"}
        
        return {
            "phase": "medical_questions",
            "session_id": session_id,
            "question_number": current_idx + 1,
            "total_questions": len(session["questions_asked"]),
            "question": session["questions_asked"][current_idx],
            "language": session["language"],
            "patient_info": session["patient_info"],
            "translations": translations
        }
    
    return {"error": "Invalid session phase"}

@app.post("/submit-answer/{session_id}")
async def submit_answer(session_id: str, answer: str = Form(...)):
    """Submit answer for current medical question"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Only handle medical questions phase
    if session["phase"] != "medical_questions":
        raise HTTPException(status_code=400, detail="Not in medical questions phase")
    
    # Store the answer
    session["user_responses"].append(answer.strip())
    session["current_question_index"] += 1
    
    # Check if we need more questions based on responses
    if len(session["user_responses"]) >= 3 and len(session["questions_asked"]) < 6:
        # Generate follow-up questions using RAG with patient context
        patient_context = f"Patient: {session['patient_info']['name']}, Age: {session['patient_info']['age']}, Pregnancy Week: {session['patient_info']['pregnancy_week']}"
        follow_up_questions = await generate_contextual_questions(
            session["language"], 
            [patient_context] + session["user_responses"],
            session["questions_asked"]  # Pass existing questions to avoid repetition
        )
        # Only add questions that are not already asked to prevent repetition
        for question in follow_up_questions:
            if question not in session["questions_asked"] and len(session["questions_asked"]) < 6:
                session["questions_asked"].append(question)
    
    # Check if assessment is complete
    if session["current_question_index"] >= len(session["questions_asked"]) or len(session["user_responses"]) >= 6:
        session["completed"] = True
        session["phase"] = "completed"
        
        # Translate Arabic responses to English for accurate risk assessment
        translated_responses = translator.translate_responses_for_assessment(
            session["user_responses"], 
            session["language"]
        )
        
        # Perform risk assessment using RAG + HuggingFace with patient context
        patient_context = f"Patient: {session['patient_info']['name']}, Age: {session['patient_info']['age']}, Pregnancy Week: {session['patient_info']['pregnancy_week']}"
        risk_assessment = await analyze_risk_with_rag(
            [patient_context] + translated_responses,
            'en'  # Always use English for risk assessment
        )
        # Add pregnancy week-specific risk factors
        risk_assessment = enhance_risk_assessment_with_pregnancy_week(
            risk_assessment, 
            session['patient_info']['pregnancy_week']
        )
        session["risk_assessment"] = risk_assessment
        
        translations = get_translations(session["language"])
        return {
            "status": "complete",
            "message": translations.get("assessment_complete", "Assessment complete! Let me analyze your responses.")
        }
    
    # Continue with next question
    translations = get_translations(session["language"]) 
    return {
        "status": "continue",
        "message": translations.get("answer_received", "Thank you for your answer.")
    }

@app.get("/results/{session_id}")
async def get_results(request: Request, session_id: str):
    """Get assessment results"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if not session["completed"] or not session["risk_assessment"]:
        raise HTTPException(status_code=400, detail="Assessment not completed")
    
    translations = get_translations(session["language"])
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "session": session,
        "translations": translations,
        "language_name": get_language_name(session["language"])
    })

@app.post("/generate-report/{session_id}")
async def generate_report(session_id: str):
    """Generate and download PDF report"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if not session["completed"]:
        raise HTTPException(status_code=400, detail="Assessment not completed")
    
    # Always generate EMR reports in English for medical professionals
    from translator import translator
    
    # Translate responses and get proper English equivalents of the questions asked
    if session['language'] == 'ar':
        translated_responses = [translator.translate_arabic_to_english(response) for response in session['user_responses']]
        # Get the English versions of the exact same questions that were asked in Arabic
        english_translations = get_translations('en')
        arabic_translations = get_translations('ar')
        
        # Create mapping from Arabic questions to English questions
        arabic_to_english_map = {
            arabic_translations["question_headaches"]: english_translations["question_headaches"],
            arabic_translations["question_fetal_movement"]: english_translations["question_fetal_movement"],
            arabic_translations["question_swelling"]: english_translations["question_swelling"],
            arabic_translations["question_bleeding"]: english_translations["question_bleeding"],
            arabic_translations["question_blood_pressure"]: english_translations["question_blood_pressure"]
        }
        
        # Translate the actual questions that were asked
        english_questions = []
        for arabic_q in session['questions_asked']:
            english_q = arabic_to_english_map.get(arabic_q, arabic_q)  # fallback to original if not found
            english_questions.append(english_q)
    else:
        translated_responses = session['user_responses']
        english_questions = session['questions_asked']
    
    report_data = {
        'language': 'en',  # Always English for EMR
        'timestamp': datetime.now().isoformat(),
        'patient_info': session['patient_info'],
        'questions': english_questions,
        'responses': translated_responses,
        'risk_assessment': session['risk_assessment']
    }
    
    pdf_buffer = report_generator.generate_pdf_report(report_data)
    
    from fastapi.responses import Response
    return Response(
        content=pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=pregnancy_risk_report_{session_id}.pdf"}
    )

async def generate_contextual_questions(language: str, previous_responses: Optional[List[str]] = None, existing_questions: Optional[List[str]] = None) -> List[str]:
    """Generate contextual medical questions - Always use standardized questions for consistency"""
    # Always use standardized questions to ensure consistency between languages
    # This prevents the issues with AI-generated questions being different each time
    return get_fallback_questions(language, existing_questions or [])

def get_fallback_questions(language: str, existing_questions: Optional[List[str]] = None) -> List[str]:
    """Standard medical questions - returns unique questions avoiding repetition"""
    translations = get_translations(language)
    
    # Complete pool of medical questions - expanded to prevent repetition
    all_questions = [
        translations["question_headaches"],
        translations["question_fetal_movement"], 
        translations["question_swelling"],
        translations["question_bleeding"],
        translations["question_blood_pressure"],
        translations["question_other_symptoms"],  # 6th question added
        translations["question_nausea"],
        translations["question_fatigue"],
        translations["question_pain"],
        translations["question_appetite"],
        translations["question_sleep"],
        translations["question_urination"],
        translations["question_contractions"]
    ]
    
    # If no existing questions, return first 6 (including the new "other symptoms" question)
    if not existing_questions:
        return all_questions[:6]
    
    # Filter out already asked questions to avoid repetition
    new_questions = []
    for question in all_questions:
        if question not in existing_questions and len(new_questions) < 3:
            new_questions.append(question)
    
    return new_questions

async def analyze_risk_with_rag(responses: List[str], language: str) -> Dict[str, Any]:
    """Analyze risk using rule-based assessment (HuggingFace disabled due to inaccurate results)"""
    print(f"=== ANALYZE_RISK_WITH_RAG DEBUG ===")
    print(f"Responses received: {responses}")
    print(f"Language: {language}")
    
    # Force use of rule-based assessment for medical accuracy
    # HuggingFace API was giving incorrect LOW risk for ectopic pregnancy symptoms
    print(f"Using rule-based assessment for medical accuracy...")
    result = risk_assessor.assess_risk(responses, language)
    print(f"Rule-based result: {result}")
    return result

def enhance_risk_assessment_with_pregnancy_week(risk_assessment: Dict[str, Any], pregnancy_week: int) -> Dict[str, Any]:
    """Enhance risk assessment based on pregnancy week"""
    enhanced_assessment = risk_assessment.copy()
    
    # Add pregnancy week-specific risk factors
    week_specific_risks = []
    
    if pregnancy_week <= 12:  # First trimester
        week_specific_risks.append("First trimester - Critical organ development period")
        if risk_assessment.get('risk_level') == 'High':
            week_specific_risks.append("Extra caution needed during first trimester")
    elif pregnancy_week <= 28:  # Second trimester
        week_specific_risks.append("Second trimester - Monitor for gestational diabetes")
        if pregnancy_week >= 20:
            week_specific_risks.append("Anatomy scan period - Monitor fetal development")
    else:  # Third trimester
        week_specific_risks.append("Third trimester - Monitor for preeclampsia and preterm labor")
        if pregnancy_week >= 37:
            week_specific_risks.append("Full term - Prepare for delivery")
        elif pregnancy_week >= 34:
            week_specific_risks.append("Late preterm period - Monitor closely")
    
    # Adjust risk level based on pregnancy week and symptoms
    if pregnancy_week < 20 and 'bleeding' in ' '.join(risk_assessment.get('symptoms', [])).lower():
        enhanced_assessment['risk_level'] = 'High'
        week_specific_risks.append("Bleeding in early pregnancy requires immediate evaluation")
    
    enhanced_assessment['pregnancy_week_risks'] = week_specific_risks
    enhanced_assessment['pregnancy_week'] = pregnancy_week
    
    return enhanced_assessment

def generate_english_medical_questions(num_questions: int) -> List[str]:
    """Generate proper English medical questions for EMR documentation"""
    standard_questions = [
        "How have you been feeling about fetal movement recently?",
        "Have you noticed any unusual swelling in your face, hands, or feet?",
        "Have you experienced any vaginal bleeding or spotting?",
        "Have you had any blood pressure readings or related symptoms?",
        "Have you experienced any severe headaches or vision changes?",
        "Are you having any abdominal pain or unusual contractions?",
        "Have you noticed any changes in your usual pregnancy symptoms?",
        "Do you have any other symptoms or concerns you'd like to discuss?"
    ]
    
    return standard_questions[:num_questions]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("Starting GraviLog FastAPI server...")
    try:
        # Get port from environment variable for production deployment
        # Use 8000 for Replit, allow PORT override for Render
        port = int(os.environ.get("PORT", 8000))
        print(f"Server will run on: http://0.0.0.0:{port}")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()