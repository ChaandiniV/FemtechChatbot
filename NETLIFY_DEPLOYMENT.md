# Netlify Deployment Guide for GraviLog

## Quick Deployment Steps

### Option 1: Direct File Upload
1. Download these files from your Replit project:
   - `index.html` (main application file)
   - `netlify.toml` (configuration file) 
   - `_redirects` (routing configuration)

2. Go to [Netlify](https://www.netlify.com)
3. Drag and drop the folder containing these files onto Netlify
4. Your site will be deployed instantly!

### Option 2: Git Deployment
1. Push these files to a GitHub repository
2. Connect your GitHub repo to Netlify
3. Set build command: `# No build needed`
4. Set publish directory: `./`

## Files Required for Deployment

### ✅ index.html
- Main application file with full bilingual pregnancy risk assessment
- Contains all CSS, JavaScript, and HTML in a single file
- No external dependencies required

### ✅ netlify.toml
- Netlify configuration file
- Handles routing and security headers
- Redirects all paths to index.html

### ✅ _redirects
- Backup routing configuration
- Ensures all URLs serve the main application

## Static Version Features

✅ **Language Support**: Full English and Arabic interface  
✅ **Risk Assessment**: Rule-based pregnancy risk evaluation  
✅ **Medical Questions**: 5 standardized medical assessment questions  
✅ **Risk Classification**: Low, Medium, High risk categories  
✅ **Bilingual UI**: Complete RTL support for Arabic  
✅ **Responsive Design**: Works on mobile and desktop  
✅ **Offline Ready**: No server dependencies  

## Limitations of Static Version

❌ **No AI Features**: Uses rule-based assessment instead of AI  
❌ **No PDF Reports**: Cannot generate downloadable medical reports  
❌ **No Session Storage**: Data not persisted between visits  
❌ **Basic Translation**: Simple keyword-based Arabic translations  

## Troubleshooting

### "Page Not Found" Error
- Ensure `index.html` exists in the root directory
- Check that `_redirects` or `netlify.toml` is configured correctly

### Blank Page
- Check browser console for JavaScript errors
- Ensure all files uploaded correctly

### Deployment URL
Your site will be available at: `https://your-site-name.netlify.app`

## Full-Featured Version
For AI-powered assessment and PDF reports, use the Replit deployment:
`https://your-replit-name.replit.app`