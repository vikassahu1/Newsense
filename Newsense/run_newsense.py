#!/usr/bin/env python
"""
Run script for Newsense AI News Summarizer

This script provides a convenient way to start the FastAPI web application.
It also provides options to:
1. Download NLTK data
2. Run the news scraper
3. Start the web server
"""

import os
import sys
import argparse
import importlib.util
from pathlib import Path

def check_requirements():
    """Check if all required dependencies are installed"""
    required_packages = [
        "fastapi", "uvicorn", "jinja2", "aiofiles",
        "nltk", "transformers", "torch", "newspaper3k"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("Downloading NLTK data...")
    try:
        from download_nltk_data import download_nltk_data
        download_nltk_data()
        print("NLTK data download completed.")
    except Exception as e:
        print(f"Error downloading NLTK data: {str(e)}")
        return False
    
    return True

def run_scraper():
    """Run the news scraper to fetch articles"""
    print("Running news scraper...")
    try:
        from run_scraper import main
        exit_code = main()
        if exit_code != 0:
            print("Scraper completed with errors.")
            return False
        print("Scraper completed successfully.")
    except Exception as e:
        print(f"Error running scraper: {str(e)}")
        return False
    
    return True

def run_web_server():
    """Start the FastAPI web server"""
    print("Starting web server...")
    try:
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"Error starting web server: {str(e)}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Newsense AI News Summarizer")
    parser.add_argument("--download-nltk", action="store_true", help="Download NLTK data")
    parser.add_argument("--run-scraper", action="store_true", help="Run the news scraper")
    parser.add_argument("--no-web", action="store_true", help="Don't start the web server")
    
    args = parser.parse_args()
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Download NLTK data if requested
    if args.download_nltk:
        if not download_nltk_data():
            return 1
    
    # Run scraper if requested
    if args.run_scraper:
        if not run_scraper():
            return 1
    
    # Start web server unless --no-web is specified
    if not args.no_web:
        return 0 if run_web_server() else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 