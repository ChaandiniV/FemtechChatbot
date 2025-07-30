"""
GraviLog - Smart Risk Analysis Agent for Pregnancy Health
FastAPI backend with LlamaIndex + Google Gemini
"""
import logging
import os
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

# Import our new modules
from core.llm_client import MedicalRAGSystem
from medical_knowledge import get_medical_knowledge, get_fallback_questions
from report_generator import ReportGenerator
from risk_assessment import RiskAssessment
from translations import get_translations

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="GraviLog - Smart Risk Analysis Agent", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize systems
try:
    medical_knowledge = get_medical_knowledge()
    rag_system = MedicalRAGSystem(medical_knowledge)
    risk_assessor = RiskAssessment()
    report_generator = ReportGenerator()
    logger.info("All systems initialized successfully with LlamaIndex + Gemini")
except Exception as e:
    logger.error(f"System initialization error: {e}")
    rag_system = None
    risk_assessor = RiskAssessment()  # This should always work as it's rule-based
    report_generator = ReportGenerator()

# Session storage (in production, use Redis or database)
sessions: Dict[str, Dict] = {}

def get_session(session_id: str) -> Dict:
    """Get or create session"""
    if session_id not in sessions:
        sessions[session_id] = {
            "id": session_id,
            "language": "en",
            "patient_info": {},
            "responses": [],
            "current_question_index": 0,
            "questions": [],
            "risk_assessment": None,
            "created_at": datetime.now()
        }
    return sessions[session_id]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with language selection"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start-session")
async def start_session(language: str = Form(...)):
    """Start a new assessment session"""
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session = get_session(session_id)
    session["language"] = language

    logger.info(f"Started new session: {session_id} (Language: {language})")
    return {"session_id": session_id, "redirect": f"/assessment?session_id={session_id}"}

@app.get("/assessment", response_class=HTMLResponse)
async def assessment_page(request: Request, session_id: str):
    """Assessment page"""
    session = get_session(session_id)
    translations = get_translations(session["language"])

    return templates.TemplateResponse("assessment.html", {
        "request": request,
        "session_id": session_id,
        "language": session["language"],
        "translations": translations
    })

@app.post("/patient-info/{session_id}")
async def collect_patient_info(
    session_id: str,
    name: str = Form(...),
    age: int = Form(...),
    gestational_week: int = Form(...)
):
    """Collect basic patient information"""
    session = get_session(session_id)
    session["patient_info"] = {
        "name": name,
        "age": age,
        "gestational_week": gestational_week
    }

    logger.info(f"Patient info collected for session {session_id}")
    return {"status": "success", "message": "Patient information saved"}

@app.get("/question/{session_id}")
async def get_question(session_id: str):
    """Get next question for the session using LlamaIndex + Gemini"""
    session = get_session(session_id)
    language = session["language"]
    responses = session["responses"]

    # Generate questions if needed
    if not session["questions"] or len(responses) >= len(session["questions"]):
        try:
            # Try AI-powered question generation with LlamaIndex + Gemini
            if rag_system:
                new_questions = rag_system.generate_questions(responses, language)
                if new_questions:
                    session["questions"].extend(new_questions)
                    logger.info(f"Generated {len(new_questions)} Gemini questions for session {session_id}")

            # Fallback to template questions if AI fails
            if not session["questions"] or len(responses) >= len(session["questions"]):
                fallback_questions = get_fallback_questions()[language]
                session["questions"].extend(fallback_questions[len(responses):len(responses)+3])
                logger.info(f"Using fallback questions for session {session_id}")

        except Exception as e:
            logger.error(f"Question generation error: {e}")
            # Use fallback questions
            fallback_questions = get_fallback_questions()[language]
            session["questions"].extend(fallback_questions[len(responses):len(responses)+3])

    # Check if we have more questions
    current_index = len(responses)
    if current_index < len(session["questions"]) and current_index < 10:  # Cap at 10 questions
        question = session["questions"][current_index]
        return {
            "question": question,
            "question_number": current_index + 1,
            "total_questions": min(len(session["questions"]), 10),
            "has_more": current_index + 1 < min(len(session["questions"]), 10)
        }
    else:
        # No more questions, proceed to assessment
        return {"question": None, "has_more": False, "assessment_ready": True}

@app.post("/submit-answer/{session_id}")
async def submit_answer(session_id: str, answer: str = Form(...)):
    """Submit answer for current question"""
    session = get_session(session_id)
    current_index = len(session["responses"])

    if current_index < len(session["questions"]):
        question = session["questions"][current_index]
        session["responses"].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Answer submitted for session {session_id}, question {current_index + 1}")
        return {"status": "success", "message": "Answer recorded"}
    else:
        return {"status": "error", "message": "No active question"}

@app.get("/assess-risk/{session_id}")
async def assess_risk(session_id: str):
    """Perform risk assessment using LlamaIndex + Gemini"""
    session = get_session(session_id)
    responses = session["responses"]
    language = session["language"]

    if not responses:
        raise HTTPException(status_code=400, detail="No responses found")

    try:
        # Try AI-powered risk assessment with Gemini
        if rag_system:
            try:
                risk_result = rag_system.assess_risk(responses, language)
                if risk_result:
                    session["risk_assessment"] = risk_result
                    logger.info(f"Gemini risk assessment completed for session {session_id}")
                    return risk_result
            except Exception as e:
                logger.error(f"Gemini risk assessment failed: {e}")

        # Fallback to rule-based assessment
        risk_result = risk_assessor.assess_risk(responses, language)
        session["risk_assessment"] = risk_result
        logger.info(f"Rule-based risk assessment completed for session {session_id}")
        return risk_result

    except Exception as e:
        logger.error(f"Risk assessment error: {e}")
        raise HTTPException(status_code=500, detail="Risk assessment failed")

@app.get("/results/{session_id}", response_class=HTMLResponse)
async def results_page(request: Request, session_id: str):
    """Results page showing risk assessment"""
    session = get_session(session_id)

    if not session.get("risk_assessment"):
        # Perform assessment if not done
        if rag_system:
            risk_result = rag_system.assess_risk(session["responses"], session["language"])
        else:
            risk_result = risk_assessor.assess_risk(session["responses"], session["language"])
        session["risk_assessment"] = risk_result

    translations = get_translations(session["language"])

    return templates.TemplateResponse("results.html", {
        "request": request,
        "session": session,
        "translations": translations
    })

@app.get("/generate-report/{session_id}")
async def generate_report(session_id: str):
    """Generate PDF report"""
    session = get_session(session_id)

    if not session.get("risk_assessment"):
        raise HTTPException(status_code=400, detail="Risk assessment not completed")

    try:
        # Generate PDF report
        pdf_path = report_generator.generate_report(
            patient_info=session["patient_info"],
            responses=session["responses"],
            risk_assessment=session["risk_assessment"],
            language=session["language"]
        )

        logger.info(f"PDF report generated for session {session_id}")
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"pregnancy_assessment_{session_id}.pdf"
        )

    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "systems": {
            "llamaindex_gemini": rag_system is not None,
            "risk_assessment": risk_assessor is not None,
            "report_generator": report_generator is not None,
            "gemini_api_key": bool(os.environ.get("GEMINI_API_KEY"))
        }
    }

if __name__ == "__main__":
    import uvicorn

    print("Starting GraviLog FastAPI server with LlamaIndex + Gemini...")
    print("Server will run on: http://0.0.0.0:8000")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
