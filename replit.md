# GraviLog - Smart Risk Analysis Agent

## Overview

GraviLog is a bilingual (English/Arabic) pregnancy health risk assessment application built with FastAPI and Hugging Face models. The system uses conversational AI with Retrieval-Augmented Generation (RAG) to conduct medical interviews with pregnant users, assess their health risks based on symptoms and responses, and generate comprehensive medical reports. The application integrates Hugging Face models for intelligent question generation and provides rule-based fallback risk assessment.

## System Architecture

### Frontend Architecture
- **Framework**: FastAPI with Jinja2 templates for server-side rendering
- **UI Components**: Modern responsive web interface with progressive enhancement
- **Styling**: Custom CSS with healthcare-focused color scheme and RTL support
- **Deployment**: Configured for Replit autoscale deployment on port 5000

### Backend Architecture
- **Core Framework**: Python 3.11 with FastAPI for high-performance API endpoints
- **AI Integration**: Hugging Face models for contextual medical question generation
- **RAG System**: TF-IDF based retrieval system for medical knowledge augmentation
- **Risk Assessment**: Hybrid approach combining AI-driven analysis with rule-based fallback
- **Report Generation**: PDF report creation using ReportLab library
- **Internationalization**: Full bilingual support (English/Arabic) with RTL text handling

## Key Components

### 1. Medical Knowledge Base (`medical_knowledge.py`)
- **Purpose**: Centralized repository of pregnancy-related medical knowledge
- **Content**: Symptom categorization (normal, medium risk, high risk/emergency)
- **Risk Indicators**: Structured data for conditions like preeclampsia, gestational diabetes
- **Implementation**: Rule-based knowledge extraction and parsing

### 2. Risk Assessment Engine (`risk_assessment.py`)
- **Algorithm**: Weighted scoring system based on symptom severity
- **Scoring Logic**: 
  - High-risk symptoms: +3 points each
  - Medium-risk symptoms: +2 points each  
  - Low-risk symptoms: +1 point each
- **Fallback Mechanism**: Rule-based assessment when AI services are unavailable
- **Output**: Risk level classification with explanations and recommendations

### 3. RAG System (`rag_system.py`)
- **Retrieval**: TF-IDF vectorization of medical knowledge base for context retrieval
- **Augmentation**: Contextual medical information retrieval based on user responses
- **Knowledge Base**: Structured pregnancy symptom categorization and risk indicators
- **Language Support**: Bilingual context retrieval with cultural sensitivity

### 4. Hugging Face Client (`huggingface_client.py`)
- **Models**: Hugging Face Inference API for text generation and analysis
- **Approach**: Dynamic question generation based on retrieved medical context
- **Fallback**: Template-based question generation when API is unavailable
- **Risk Analysis**: AI-powered risk assessment with rule-based fallback

### 5. Report Generator (`report_generator.py`)
- **Format**: Professional PDF medical reports
- **Library**: ReportLab for document creation
- **Styling**: Healthcare-appropriate formatting with risk level color coding
- **Content**: Comprehensive assessment results, recommendations, and next steps

### 6. Translation System (`translations.py`)
- **Languages**: English and Arabic with full RTL support
- **Coverage**: Complete UI translations including medical terminology
- **Implementation**: Dictionary-based translation system with language detection

## Data Flow

1. **Language Selection**: User chooses preferred language (English/Arabic) via FastAPI web interface
2. **Session Management**: FastAPI creates session with unique ID for conversation tracking
3. **RAG-Enhanced Question Generation**: System retrieves relevant medical context and generates 3-5 contextual questions
4. **Response Collection**: User responses processed through FastAPI endpoints with real-time validation
5. **AI-Powered Risk Analysis**: Hugging Face models analyze responses using retrieved medical context
6. **Report Generation**: PDF report creation with comprehensive assessment results
7. **Action Recommendations**: Immediate care suggestions based on risk classification

## External Dependencies

### Core Libraries
- **FastAPI**: High-performance web framework for API endpoints
- **Hugging Face Transformers**: AI models for text generation and analysis
- **Scikit-learn**: TF-IDF vectorization for RAG implementation
- **ReportLab**: PDF generation for medical reports
- **Jinja2**: Template engine for server-side rendering

### AI Services
- **Hugging Face Inference API**: Primary service for conversational AI and medical analysis
- **Models**: DialoGPT-medium for text generation, RoBERTa for classification
- **Fallback**: Template-based question generation and rule-based assessment when API unavailable

### Infrastructure
- **Deployment**: Replit autoscale deployment
- **Environment**: Python 3.11 with Nix package management
- **Port Configuration**: Application runs on port 5000

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with stable Nix channel
- **Packages**: FastAPI, Uvicorn, Hugging Face Transformers, Scikit-learn, ReportLab
- **Deployment Target**: Autoscale for handling variable user loads
- **Run Command**: `python main.py` (FastAPI with Uvicorn)

### Environment Setup
- **API Keys**: Optional Hugging Face API key for enhanced model access
- **Configuration**: FastAPI server configuration for production deployment
- **Workflows**: Single FastAPI server workflow for optimal performance

### Scalability Considerations
- **Session Management**: In-memory session storage with unique session IDs
- **Caching**: TF-IDF vectorization caching for knowledge base retrieval
- **Error Handling**: Graceful fallback to template-based questions and rule-based assessment
- **Performance**: Asynchronous FastAPI endpoints for optimal response times

## Deployment Options

### Production Deployment (Recommended)
- **Platform**: Replit Autoscale Deployment
- **Features**: Full AI-powered risk assessment, PDF generation, bilingual support
- **Setup**: Click "Deploy" button in Replit interface
- **URL**: Will be provided as `https://yourapp.replit.app`

### Static Deployment Alternative
- **Platform**: Netlify/GitHub Pages compatible
- **File**: `netlify_version.html` (standalone HTML)
- **Features**: Basic rule-based assessment, bilingual UI
- **Limitations**: No AI features, no PDF generation

## Recent Fixes (July 2, 2025)

### Netlify Full App Deployment (Latest)
- ✅ Created complete FastAPI serverless function deployment for Netlify
- ✅ Built comprehensive single-page application (index.html) with full UI
- ✅ Configured Mangum adapter for AWS Lambda/Netlify Functions compatibility
- ✅ Set up proper routing with netlify.toml and _redirects configurations
- ✅ Created netlify-requirements.txt with all Python dependencies
- ✅ Built bilingual interface with API fallback for static hosting
- ✅ Added comprehensive deployment guide (NETLIFY_FULL_DEPLOYMENT.md)

### Netlify Deployment Fix (Previous)
- ✅ Created proper index.html file for Netlify deployment
- ✅ Added netlify.toml configuration with routing and security headers
- ✅ Added _redirects file for proper SPA routing
- ✅ Enhanced static version with meta tags and SEO optimization
- ✅ Created comprehensive deployment guide (NETLIFY_DEPLOYMENT.md)

### EMR Report & Question Fixes
- ✅ Fixed question/answer mismatch in Arabic EMR reports with proper translation mapping  
- ✅ Enhanced Arabic medical keywords for better medium-risk detection
- ✅ Fixed inconsistent questions between Arabic and English versions
- ✅ Disabled AI question generation to ensure standardized medical questions
- ✅ Questions now perfectly match between Arabic and English interfaces

### Risk Assessment Enhancement  
- ✅ Fixed Arabic risk scoring system with hierarchical risk checking
- ✅ Improved scoring thresholds to properly classify Medium vs High risk
- ✅ Enhanced translation system with comprehensive medical phrases
- ✅ Added prevention of risk over-scoring from multiple keyword matches

### EMR Report English Translation
- ✅ EMR reports now always generate in English for medical professionals
- ✅ Enhanced Arabic-to-English translation for medical documentation
- ✅ Comprehensive medical terminology translation dictionary
- ✅ Clean translation output removing mixed Arabic-English text
- ✅ User interface remains in chosen language while EMR is English-only

### Arabic Language Support
- ✅ Fixed Arabic risk assessment with bilingual keyword matching
- ✅ Enhanced Arabic UI with proper placeholder translations
- ✅ Improved Arabic text processing for accurate risk detection
- ✅ Added comprehensive Arabic medical terminology

### Question System Improvements
- ✅ Resolved question repetition issues with proper tracking
- ✅ Enhanced fallback question pool with 12 unique medical questions
- ✅ Improved session management to prevent API error loops

### Deployment Preparation
- ✅ Created static HTML version for Netlify deployment
- ✅ Prepared comprehensive deployment guide
- ✅ Configured both full-featured and basic deployment options

## Changelog

- June 26, 2025: Initial setup with Streamlit and OpenAI integration
- June 26, 2025: Major architecture migration to FastAPI + Hugging Face + RAG system
- June 26, 2025: Fixed Arabic language processing and created deployment options

## User Preferences

Preferred communication style: Simple, everyday language.