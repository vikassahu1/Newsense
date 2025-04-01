from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import json
import glob
from typing import List, Dict, Any, Optional
import sys

# Add the parent directory to sys.path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from summarizer import summarize_news

# Initialize FastAPI app
app = FastAPI(title="Newsense - AI News Summarizer")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Define base directory for scraped news
SCRAPED_NEWS_DIR = "scrapper/scraped_news"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main page with news feed and filters"""
    # Get available news sources (folders in the scraped_news directory)
    news_sources = get_news_sources()
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "news_sources": news_sources}
    )

@app.get("/api/sources")
async def get_sources():
    """Get all available news sources"""
    return {"sources": get_news_sources()}

@app.get("/api/articles/{source}")
async def get_articles_by_source(source: str, limit: int = 20):
    """Get articles from a specific source with summaries"""
    try:
        articles = load_articles_from_source(source, limit)
        return {"status": "success", "articles": articles, "count": len(articles)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_news_sources() -> List[str]:
    """Get list of available news sources from the directory structure"""
    if not os.path.exists(SCRAPED_NEWS_DIR):
        return []
    
    # Get directory names as source names
    sources = [
        os.path.basename(path) 
        for path in glob.glob(os.path.join(SCRAPED_NEWS_DIR, "*"))
        if os.path.isdir(path)
    ]
    
    return sorted(sources)

def load_articles_from_source(source: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Load articles from a specific source directory, with summaries"""
    source_dir = os.path.join(SCRAPED_NEWS_DIR, source)
    
    if not os.path.exists(source_dir):
        raise HTTPException(status_code=404, detail=f"Source '{source}' not found")
    
    # Get all JSON files in the source directory
    json_files = glob.glob(os.path.join(source_dir, "*.json"))
    
    # Sort files by modification time (newest first) and limit
    json_files = sorted(json_files, key=os.path.getmtime, reverse=True)[:limit]
    
    articles = []
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                article = json.load(f)
                
                # Add summary if not already present
                if 'content' in article and not article.get('summary'):
                    # Summarize the content (max 100 words)
                    article['summary'] = summarize_news(article['content'], max_length=100)
                
                # Ensure we have a placeholder for missing data
                if not article.get('author'):
                    article['author'] = "Unknown Author"
                    
                if not article.get('image_url'):
                    article['image_url'] = "/static/images/placeholder.jpg"
                
                # Add file path for reference
                article['file_path'] = os.path.basename(file_path)
                
                articles.append(article)
                
        except Exception as e:
            print(f"Error loading article {file_path}: {str(e)}")
            continue
    
    return articles

# Run the FastAPI app with uvicorn if this file is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 