# GraviLog Deployment Guide

## Option 1: Replit Deployment (Recommended - Full Features)

### Features:
- Full AI-powered risk assessment
- RAG system with medical knowledge base
- HuggingFace integration
- PDF report generation
- Complete bilingual support
- Session management

### Steps:
1. Click the "Deploy" button in Replit
2. Your app will be available at `https://yourapp.replit.app`
3. Handles scaling and server management automatically

### Requirements:
- Replit account
- Optional: HuggingFace API key for enhanced AI features

---

## Option 2: Netlify Static Deployment (Basic Features)

### Features:
- Bilingual interface (English/Arabic)
- Patient information collection
- Medical questionnaire
- Basic rule-based risk assessment
- Arabic symptom processing

### Limitations:
- No AI-powered features
- No PDF generation
- No advanced medical knowledge integration
- Rule-based assessment only

### Steps:
1. Download `netlify_version.html`
2. Rename to `index.html`
3. Deploy to Netlify:
   - Option A: Drag & drop to netlify.com
   - Option B: Connect GitHub repository
   - Option C: Use Netlify CLI

### File Structure for Netlify:
```
your-project/
├── index.html (renamed from netlify_version.html)
└── README.md (optional)
```

---

## Option 3: Other Hosting Platforms

### For Full FastAPI Version:
- **Vercel**: Supports Python/FastAPI
- **Railway**: Backend-friendly platform
- **Heroku**: Traditional cloud platform
- **DigitalOcean App Platform**: Scalable hosting

### For Static Version:
- **GitHub Pages**: Free static hosting
- **Vercel**: Also supports static files
- **Surge**: Simple static deployment

---

## Comparison

| Feature | Replit | Netlify Static | Other Platforms |
|---------|--------|----------------|-----------------|
| AI Assessment | ✅ | ❌ | ✅ (FastAPI) |
| PDF Reports | ✅ | ❌ | ✅ (FastAPI) |
| Bilingual UI | ✅ | ✅ | ✅ |
| Setup Difficulty | Easy | Very Easy | Medium |
| Cost | Free tier | Free | Varies |
| Scalability | Auto | Static only | Manual |

---

## Recommended Approach

1. **Development/Testing**: Use current Replit environment
2. **Production**: Deploy on Replit for full features
3. **Demo/Portfolio**: Use Netlify static version for simple showcase

Both versions include proper Arabic language support and risk assessment functionality.