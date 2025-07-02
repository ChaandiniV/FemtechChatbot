# Render Deployment Fix for Bad Gateway Error

## Problem Identified
Render was trying to install packages from `pyproject.toml` instead of `render-requirements.txt`, causing conflicts with Streamlit and other unnecessary dependencies.

## Solution Applied
Updated `render.yaml` to:
1. Temporarily move `pyproject.toml` during build
2. Install only essential packages from `render-requirements.txt`
3. Use simplified package versions without conflicts

## What to Do Now

### Step 1: Commit the Fixes
```bash
git add .
git commit -m "Fix Render deployment - remove pyproject.toml conflicts"
git push origin main
```

### Step 2: Redeploy in Render
1. Go to your Render dashboard
2. Find your GraviLog service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Watch the build logs - should complete successfully now

### Step 3: Test Your App
After successful deployment, test:
- Language selection
- Patient information form
- Medical questionnaire
- Risk assessment results

## Alternative: Manual Settings in Render Dashboard

If the yaml file still causes issues, manually configure in Render:

**Build Command:**
```bash
pip install fastapi uvicorn jinja2 python-multipart reportlab scikit-learn numpy requests
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Expected Result
- Build should complete in 2-3 minutes
- App should start successfully
- All medical assessment features should work
- No more "Bad Gateway" errors

The fixed configuration removes Streamlit and other conflicting packages that aren't needed for your FastAPI application.