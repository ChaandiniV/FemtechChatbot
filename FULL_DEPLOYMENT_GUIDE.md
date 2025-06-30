# Full GraviLog Deployment Guide

## Deployment Options for Full FastAPI Application

### Option 1: Replit Deployment (Recommended - Easiest)
**Best for: Quick deployment with minimal setup**

1. **In your Replit project:**
   - Click the "Deploy" button in the top right
   - Choose "Autoscale Deployment"
   - Your app will be available at `https://your-repl-name.replit.app`

2. **Benefits:**
   - ✅ Zero configuration needed
   - ✅ Automatic scaling
   - ✅ Built-in domain and SSL
   - ✅ All features work (AI, PDF, database)

### Option 2: Railway Deployment
**Best for: Production deployment with custom domain**

1. **Setup:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

2. **Add environment variables in Railway dashboard:**
   - `OPENAI_API_KEY` (if using OpenAI features)
   - `PORT=5000`

### Option 3: Render Deployment  
**Best for: Free tier with good performance**

1. **Create these files:**

**requirements.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
jinja2==3.1.2
python-multipart==0.0.6
reportlab==4.0.4
scikit-learn==1.3.0
numpy==1.24.3
requests==2.31.0
```

**render.yaml:**
```yaml
services:
  - type: web
    name: gravilog
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PORT
        value: 10000
```

### Option 4: Heroku Deployment
**Best for: Established platform with addons**

1. **Create Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. **Create runtime.txt:**
```
python-3.11.6
```

3. **Deploy:**
```bash
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
```

## Required Files for Production Deployment

### ✅ Already Created:
- `main.py` - FastAPI application
- `requirements.txt` - Python dependencies (in pyproject.toml)
- All medical knowledge files
- Risk assessment system
- Translation system

### 🔧 Production Optimizations:

**For better performance, update main.py:**
```python
# Add at the top of main.py
import os
from fastapi.middleware.cors import CORSMiddleware

# Add after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Update port binding
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
```

## Environment Variables Needed

### Required:
- `PORT` - Usually auto-set by deployment platform

### Optional (for enhanced features):
- `OPENAI_API_KEY` - For AI-powered question generation
- `HUGGINGFACE_API_KEY` - For enhanced model access

## Features Available in Full Deployment

✅ **AI-Powered Risk Assessment** - Advanced analysis using Hugging Face models  
✅ **PDF Report Generation** - Professional EMR reports in English  
✅ **Session Management** - Persistent user sessions  
✅ **Bilingual Support** - Complete English/Arabic interface  
✅ **RAG System** - Retrieval-Augmented Generation for medical context  
✅ **Enhanced Translation** - Medical terminology translation  
✅ **Scalable Architecture** - FastAPI with async support  

## Recommended Deployment Steps

1. **Replit Deploy (Fastest):**
   - Click "Deploy" → "Autoscale Deployment"
   - Done! Your app is live

2. **For Custom Domain:**
   - Use Railway or Render
   - Connect custom domain in platform settings

3. **For Enterprise:**
   - Use AWS/GCP with Docker containerization
   - Set up load balancing and database

## Testing Your Deployment

After deployment, test these features:
- [ ] Language selection (English/Arabic)
- [ ] Patient information collection
- [ ] Medical questionnaire (5 questions)
- [ ] Risk assessment results
- [ ] PDF report generation
- [ ] Arabic translation accuracy

## Support

For deployment issues:
- Replit: Use Replit community forums
- Railway: Check Railway docs
- Render: Use Render support
- Heroku: Check Heroku dev center