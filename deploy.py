#!/usr/bin/env python3
"""
GraviLog Deployment Helper Script
Helps deploy the full FastAPI application to various platforms
"""

import os
import sys
import subprocess

def print_deployment_options():
    print("🚀 GraviLog Full Deployment Options")
    print("=" * 50)
    print()
    print("1. Replit Deploy (Recommended - Easiest)")
    print("   - Click 'Deploy' button in Replit")
    print("   - Choose 'Autoscale Deployment'")
    print("   - Instant deployment with custom domain")
    print()
    print("2. Railway (Free tier + easy setup)")
    print("   - Great for production with custom domains")
    print("   - Automatic builds from Git")
    print()
    print("3. Render (Free tier available)")
    print("   - Good performance and reliability")
    print("   - Easy GitHub integration")
    print()
    print("4. Heroku (Classic platform)")
    print("   - Established platform with addons")
    print("   - Good documentation and community")
    print()
    print("5. Docker (Self-hosted)")
    print("   - Complete control over deployment")
    print("   - Can be deployed anywhere")

def check_files():
    """Check if all required deployment files exist"""
    required_files = [
        'main.py',
        'Procfile',
        'runtime.txt',
        'render.yaml',
        'Dockerfile',
        'pyproject.toml'
    ]
    
    print("📋 Checking deployment files...")
    all_present = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing!")
            all_present = False
    
    if all_present:
        print("\n🎉 All deployment files are ready!")
    else:
        print("\n⚠️  Some files are missing. Please ensure all files are present.")
    
    return all_present

def show_replit_instructions():
    print("\n🔧 Replit Deployment Instructions:")
    print("-" * 40)
    print("1. In your Replit project, click the 'Deploy' button (top right)")
    print("2. Select 'Autoscale Deployment'")
    print("3. Your app will be live at: https://your-repl-name.replit.app")
    print("4. Configure environment variables if needed:")
    print("   - OPENAI_API_KEY (optional, for enhanced AI features)")
    print("   - HUGGINGFACE_API_KEY (optional, for enhanced models)")

def show_railway_instructions():
    print("\n🚂 Railway Deployment Instructions:")
    print("-" * 40)
    print("1. Install Railway CLI: npm install -g @railway/cli")
    print("2. Login: railway login")
    print("3. Initialize: railway init")
    print("4. Deploy: railway up")
    print("5. Set environment variables in Railway dashboard")

def show_render_instructions():
    print("\n🎨 Render Deployment Instructions:")
    print("-" * 40)
    print("1. Push code to GitHub repository")
    print("2. Go to render.com and create new Web Service")
    print("3. Connect your GitHub repo")
    print("4. Render will auto-detect the render.yaml configuration")
    print("5. Set environment variables in Render dashboard")

def show_heroku_instructions():
    print("\n📦 Heroku Deployment Instructions:")
    print("-" * 40)
    print("1. Install Heroku CLI")
    print("2. git init (if not already done)")
    print("3. git add .")
    print("4. git commit -m 'Deploy GraviLog'")
    print("5. heroku create your-app-name")
    print("6. git push heroku main")
    print("7. Set environment variables: heroku config:set KEY=value")

def show_docker_instructions():
    print("\n🐳 Docker Deployment Instructions:")
    print("-" * 40)
    print("1. Build image: docker build -t gravilog .")
    print("2. Run locally: docker run -p 5000:5000 gravilog")
    print("3. For production:")
    print("   - Push to Docker Hub: docker push your-username/gravilog")
    print("   - Deploy to any cloud platform supporting Docker")

def main():
    print_deployment_options()
    print()
    
    if not check_files():
        print("\n❌ Cannot proceed with deployment - missing files!")
        return
    
    print("\n" + "=" * 50)
    print("Choose your deployment platform:")
    print("1. Replit (Recommended)")
    print("2. Railway")
    print("3. Render")
    print("4. Heroku")
    print("5. Docker")
    print("6. Show all instructions")
    
    try:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            show_replit_instructions()
        elif choice == "2":
            show_railway_instructions()
        elif choice == "3":
            show_render_instructions()
        elif choice == "4":
            show_heroku_instructions()
        elif choice == "5":
            show_docker_instructions()
        elif choice == "6":
            show_replit_instructions()
            show_railway_instructions()
            show_render_instructions()
            show_heroku_instructions()
            show_docker_instructions()
        else:
            print("Invalid choice. Please run the script again.")
    
    except KeyboardInterrupt:
        print("\n\nDeployment helper cancelled.")

if __name__ == "__main__":
    main()