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
        "language": language,
        "questions_asked": [],
        "user_responses": [],
        "current_question_index": 0,
        "risk_assessment": None,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    
    # Generate initial questions using RAG + HuggingFace
    initial_questions = await generate_contextual_questions(language, [])
    sessions[session_id]["questions_asked"] = initial_questions[:3]
    
    return {"session_id": session_id, "first_question": initial_questions[0] if initial_questions else None}

@app.get("/question/{session_id}")
async def get_current_question(session_id: str):
    """Get current question for the session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    current_idx = session["current_question_index"]
    
    if current_idx >= len(session["questions_asked"]):
        return {"completed": True, "message": "Assessment completed"}
    
    translations = get_translations(session["language"])
    
    return {
        "session_id": session_id,
        "question_number": current_idx + 1,
        "total_questions": len(session["questions_asked"]),
        "question": session["questions_asked"][current_idx],
        "language": session["language"],
        "translations": translations
    }

@app.post("/answer/{session_id}")
async def submit_answer(session_id: str, answer: str = Form(...)):
    """Submit answer for current question"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Store the answer
    session["user_responses"].append(answer.strip())
    session["current_question_index"] += 1
    
    # Check if we need more questions based on responses
    if len(session["user_responses"]) >= 3 and len(session["questions_asked"]) < 5:
        # Generate follow-up questions using RAG
        follow_up_questions = await generate_contextual_questions(
            session["language"], 
            session["user_responses"]
        )
        session["questions_asked"].extend(follow_up_questions[:2])
    
    # Check if assessment is complete
    if session["current_question_index"] >= len(session["questions_asked"]) or len(session["user_responses"]) >= 5:
        session["completed"] = True
        
        # Perform risk assessment using RAG + HuggingFace
        risk_assessment = await analyze_risk_with_rag(
            session["user_responses"],
            session["language"]
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
    
    report_data = {
        'language': session['language'],
        'timestamp': datetime.now().isoformat(),
        'questions': session['questions_asked'],
        'responses': session['user_responses'],
        'risk_assessment': session['risk_assessment']
    }
    
    pdf_buffer = report_generator.generate_pdf_report(report_data)
    
    from fastapi.responses import Response
    return Response(
        content=pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=pregnancy_risk_report_{session_id}.pdf"}
    )

async def generate_contextual_questions(language: str, previous_responses: Optional[List[str]] = None) -> List[str]:
    """Generate contextual medical questions using RAG + HuggingFace"""
    try:
        # Use RAG to get relevant medical context
        context = rag_system.get_relevant_context(previous_responses or [], language)
        
        # Generate questions using HuggingFace
        questions = await hf_client.generate_questions(language, context, previous_responses or [])
        
        if questions and len(questions) > 0:
            return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
    
    # Fallback to predefined questions
    return get_fallback_questions(language)

def get_fallback_questions(language: str) -> List[str]:
    """Fallback questions if AI generation fails"""
    translations = get_translations(language)
    return [
        translations["question_headaches"],
        translations["question_fetal_movement"], 
        translations["question_swelling"],
        translations["question_bleeding"],
        translations["question_blood_pressure"]
    ]

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)