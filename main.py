from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
    
    return templates.TemplateResponse("assessment.html", {
        "request": request,
        "session_id": session_id
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
            "next_question": translations.get("question_age", "What is your age?"),
            "step": 1,
            "field": "age"
        }
    elif current_step == 1:  # Age
        try:
            age = int(info_value.strip())
            if age < 12 or age > 60:
                return {"error": translations.get("age_error", "Please enter a valid age between 12 and 60")}
            session["patient_info"]["age"] = age
            session["current_patient_info_step"] = 2
            return {
                "next_question": translations.get("question_pregnancy_week", "What week of pregnancy are you in?"),
                "step": 2,
                "field": "pregnancy_week"
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
                "patient_info_complete": True,
                "first_medical_question": session["questions_asked"][0] if session["questions_asked"] else None,
                "phase": "medical_questions"
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

@app.post("/answer/{session_id}")
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
    if len(session["user_responses"]) >= 3 and len(session["questions_asked"]) < 5:
        # Generate follow-up questions using RAG with patient context
        patient_context = f"Patient: {session['patient_info']['name']}, Age: {session['patient_info']['age']}, Pregnancy Week: {session['patient_info']['pregnancy_week']}"
        follow_up_questions = await generate_contextual_questions(
            session["language"], 
            [patient_context] + session["user_responses"],
            session["questions_asked"]  # Pass existing questions to avoid repetition
        )
        session["questions_asked"].extend(follow_up_questions[:2])
    
    # Check if assessment is complete
    if session["current_question_index"] >= len(session["questions_asked"]) or len(session["user_responses"]) >= 5:
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
        
        return {"completed": True, "redirect_to_results": True}
    
    return {"completed": False, "next_question_available": True}

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
    
    # Only translate responses to English, generate proper English medical questions for EMR
    if session['language'] == 'ar':
        translated_responses = [translator.translate_arabic_to_english(response) for response in session['user_responses']]
        # Generate proper medical questions in English based on standard pregnancy assessment
        english_questions = generate_english_medical_questions(len(session['questions_asked']))
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
    """Generate contextual medical questions using RAG + HuggingFace"""
    try:
        # Use RAG to get relevant medical context
        context = rag_system.get_relevant_context(previous_responses or [], language)
        
        # Generate questions using HuggingFace
        questions = await hf_client.generate_questions(language, context, previous_responses or [])
        
        if questions and len(questions) > 0:
            # Filter out already asked questions
            if existing_questions:
                existing_set = set(existing_questions)
                questions = [q for q in questions if q not in existing_set]
            
            if questions:
                return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
    
    # Fallback to predefined questions
    return get_fallback_questions(language, existing_questions or [])

def get_fallback_questions(language: str, existing_questions: Optional[List[str]] = None) -> List[str]:
    """Fallback questions if AI generation fails"""
    translations = get_translations(language)
    
    all_questions = [
        translations["question_headaches"],
        translations["question_fetal_movement"], 
        translations["question_swelling"],
        translations["question_bleeding"],
        translations["question_blood_pressure"],
        translations.get("question_nausea", "Are you experiencing any nausea or vomiting?"),
        translations.get("question_fatigue", "How would you describe your energy levels?"),
        translations.get("question_pain", "Are you experiencing any pain or discomfort?"),
        translations.get("question_appetite", "Have you noticed any changes in your appetite?"),
        translations.get("question_sleep", "How has your sleep pattern been?"),
        translations.get("question_urination", "Have you experienced any changes in urination frequency?"),
        translations.get("question_contractions", "Have you felt any contractions or tightening?")
    ]
    
    # Filter out already asked questions
    if existing_questions:
        existing_set = set(existing_questions)
        available_questions = [q for q in all_questions if q not in existing_set]
        return available_questions if available_questions else all_questions[:3]
    
    return all_questions[:5]

async def analyze_risk_with_rag(responses: List[str], language: str) -> Dict[str, Any]:
    """Analyze risk using RAG + HuggingFace"""
    try:
        # Get relevant medical context using RAG
        context = rag_system.get_relevant_context(responses, language)
        
        # Analyze risk using HuggingFace
        risk_analysis = await hf_client.analyze_risk(responses, context, language)
        
        if risk_analysis:
            return risk_analysis
    except Exception as e:
        print(f"Error analyzing risk: {e}")
    
    # Fallback to rule-based assessment
    return risk_assessor.assess_risk(responses, language)

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
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)