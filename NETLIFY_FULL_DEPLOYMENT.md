# Netlify Full App Deployment Guide

## Complete GraviLog Deployment to Netlify

### Overview
This guide walks you through deploying the complete GraviLog FastAPI application to Netlify using serverless functions. Your app will have all features including AI-powered risk assessment, PDF generation, and bilingual support.

### Prerequisites
- GitHub account
- Netlify account (free)
- Your GraviLog code pushed to a GitHub repository

## Step 1: Prepare Your Repository

Ensure your GitHub repository contains these files:

### Required Files ✅
- `index.html` - Frontend single-page application
- `netlify.toml` - Netlify configuration
- `netlify/functions/app.py` - Serverless function handler
- `netlify-requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification
- All your Python modules (`main.py`, `medical_knowledge.py`, etc.)

### File Structure
```
your-repo/
├── index.html                 # Frontend app
├── netlify.toml              # Netlify config
├── netlify-requirements.txt   # Dependencies
├── runtime.txt               # Python version
├── netlify/
│   └── functions/
│       └── app.py            # API handler
├── main.py                   # FastAPI app
├── medical_knowledge.py      # Medical knowledge
├── risk_assessment.py        # Risk logic
├── report_generator.py       # PDF reports
├── translations.py           # Language support
├── rag_system.py            # RAG implementation
├── huggingface_client.py     # AI client
└── [all other Python files]
```

## Step 2: Deploy to Netlify

### Option A: GitHub Integration (Recommended)

1. **Connect Repository**
   - Go to [Netlify](https://netlify.com)
   - Click "New site from Git"
   - Choose "GitHub" and authorize
   - Select your GraviLog repository

2. **Configure Build Settings**
   - Build command: `cp netlify-requirements.txt requirements.txt`
   - Publish directory: `.` (root)
   - Functions directory: `netlify/functions`

3. **Deploy**
   - Click "Deploy site"
   - Wait for build to complete
   - Your app will be live at `https://your-site-name.netlify.app`

### Option B: Manual Upload

1. **Prepare Files**
   - Download all files from your repository
   - Ensure `netlify-requirements.txt` is named exactly that

2. **Upload to Netlify**
   - Go to Netlify dashboard
   - Drag and drop your project folder
   - Netlify will automatically detect the configuration

## Step 3: Configure Environment Variables (Optional)

For enhanced AI features, add these environment variables in Netlify:

1. Go to Site Settings → Environment Variables
2. Add variables:
   - `HUGGINGFACE_API_KEY` - Your Hugging Face API key
   - `OPENAI_API_KEY` - OpenAI key (if using OpenAI features)

## Step 4: Test Your Deployment

After deployment, test these features:

### ✅ Frontend Features
- [ ] Language selection (English/Arabic)
- [ ] Patient information form
- [ ] Medical questionnaire
- [ ] Results display
- [ ] RTL support for Arabic

### ✅ Backend Features (via Serverless Functions)
- [ ] Session creation
- [ ] Question generation
- [ ] Risk assessment
- [ ] PDF report generation
- [ ] API endpoints working

## Step 5: Custom Domain (Optional)

To use your own domain:

1. In Netlify dashboard, go to Site Settings
2. Click "Domain management"
3. Add your custom domain
4. Follow DNS configuration instructions

## Features Available

### ✅ Full Feature Set
- **AI-Powered Assessment** - Hugging Face model integration
- **PDF Reports** - Medical reports in English
- **Session Management** - Persistent user sessions
- **Bilingual Support** - Complete English/Arabic interface
- **RAG System** - Medical knowledge retrieval
- **Risk Classification** - Low/Medium/High risk levels
- **Responsive Design** - Works on all devices

### How It Works

1. **Frontend (index.html)**
   - Single-page application
   - Handles user interface
   - Makes API calls to serverless functions

2. **Backend (netlify/functions/app.py)**
   - Serverless function powered by Mangum
   - Runs your complete FastAPI application
   - Handles all API endpoints

3. **Automatic Scaling**
   - Netlify automatically scales based on usage
   - Pay only for actual function invocations
   - Built-in CDN for fast global access

## Troubleshooting

### Build Errors
- Ensure `netlify-requirements.txt` contains all dependencies
- Check Python version in `runtime.txt` (3.9 recommended)
- Verify all Python files are in the repository

### Function Errors
- Check function logs in Netlify dashboard
- Ensure all imports are available
- Verify file paths in `app.py`

### Frontend Issues
- Check browser console for JavaScript errors
- Verify API calls are going to correct endpoints
- Test fallback mode when functions are unavailable

## Cost Estimation

### Netlify Free Tier Includes:
- 100GB bandwidth per month
- 125,000 function invocations per month
- SSL certificate included
- Custom domain support

### Typical Usage:
- Small to medium usage: **Free**
- High traffic: Approximately $19-99/month

## Support and Maintenance

### Monitoring
- Check Netlify dashboard for function performance
- Monitor error rates and response times
- Use Netlify Analytics for usage insights

### Updates
- Push changes to GitHub repository
- Netlify automatically rebuilds and deploys
- Instant rollback available if needed

## Production Checklist

Before going live:

- [ ] Test all features thoroughly
- [ ] Configure custom domain
- [ ] Set up monitoring and alerts
- [ ] Add analytics tracking
- [ ] Configure proper CORS settings
- [ ] Test Arabic language support
- [ ] Verify PDF generation works
- [ ] Check mobile responsiveness

## Next Steps

1. **Deploy your app** using the steps above
2. **Test thoroughly** with real pregnancy scenarios
3. **Share the URL** with your users
4. **Monitor performance** and user feedback
5. **Iterate and improve** based on usage data

Your GraviLog application will be live and fully functional on Netlify with all AI features, bilingual support, and professional medical reporting capabilities!

## Questions or Issues?

If you encounter any problems:
1. Check the Netlify function logs
2. Verify all files are properly uploaded
3. Test API endpoints individually
4. Contact Netlify support for platform-specific issues

**Deployment URL:** Your app will be available at `https://your-chosen-name.netlify.app`