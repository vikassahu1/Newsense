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
import subprocess
import time

# Add the parent directory to sys.path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from summarizer import summarize_news, NewsSummarizer

# Initialize FastAPI app
app = FastAPI(title="Newsense - AI News Summarizer")

# Define model holder for startup initialization
summarizer_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize the summarization model at app startup"""
    global summarizer_model
    
    # Preload the summarizer model to avoid repeated loading
    print("Preloading summarization model (this may take a minute)...")
    try:
        # Create a simplified summarizer for faster processing
        # This skips the heavy transformer model and uses a simple extractive approach
        class SimplifiedSummarizer:
            def __init__(self):
                print("Initializing simplified summarizer for faster processing")
                # Import nltk here to avoid global import
                import nltk
                # Ensure necessary NLTK data is downloaded
                try:
                    nltk.data.find('tokenizers/punkt')
                except LookupError:
                    nltk.download('punkt', quiet=True)
            
            def summarize(self, content, max_length=100):
                """Simple extractive summarization by taking first few sentences"""
                import nltk
                sentences = nltk.sent_tokenize(content)
                # Take first 3-5 sentences as summary
                summary_sentences = sentences[:min(5, len(sentences))]
                summary = " ".join(summary_sentences)
                
                # Truncate if necessary
                words = nltk.word_tokenize(summary)
                if len(words) > max_length:
                    summary = " ".join(words[:max_length]) + "..."
                    
                return summary
        
        # Use the simplified summarizer instead of the heavy transformer model
        summarizer_model = SimplifiedSummarizer()
        print("Using simplified summarizer for faster processing")
        
    except Exception as e:
        print(f"Error initializing summarizer: {str(e)}")
        # Create a very basic summarizer as fallback
        class BasicSummarizer:
            def summarize(self, content, max_length=100):
                # Just return the first portion of the text
                return content[:300] + "..." if len(content) > 300 else content
        
        summarizer_model = BasicSummarizer()
        print("Using basic summarizer due to initialization error")

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
        print(f"Fetching articles from source: {source}")
        
        # Handle the case where TheHindu and The Hindu are treated as the same source
        articles = []
        if source == "The Hindu" or source == "TheHindu":
            # Try to load from both directory names to handle different scraping formats
            try:
                articles.extend(load_articles_from_source("The Hindu", limit))
            except Exception as e:
                print(f"Error loading from 'The Hindu': {str(e)}")
            
            try:
                articles.extend(load_articles_from_source("TheHindu", limit))
            except Exception as e:
                print(f"Error loading from 'TheHindu': {str(e)}")
            
            # Remove duplicates by titles
            seen_titles = set()
            unique_articles = []
            for article in articles:
                if article.get('title') not in seen_titles:
                    seen_titles.add(article.get('title'))
                    unique_articles.append(article)
            
            articles = unique_articles[:limit]  # Limit the total number
        else:
            # For other sources, load normally
            articles = load_articles_from_source(source, limit)
            
        print(f"Successfully fetched {len(articles)} articles from {source}")
        return {"status": "success", "articles": articles, "count": len(articles)}
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error fetching articles from {source}: {error_msg}")
        print(traceback.format_exc())
        return {"status": "error", "message": error_msg}

@app.get("/api/refresh-news")
async def refresh_news():
    """Run the news scraper to fetch fresh articles"""
    try:
        print("Starting news refresh process...")
        start_time = time.time()
        
        # Execute the run_scraper.py script
        result = subprocess.run(
            ["python", "run_scraper.py"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check the result
        if result.returncode == 0:
            # Success
            end_time = time.time()
            duration = end_time - start_time
            message = f"News refresh completed successfully in {duration:.1f} seconds"
            print(message)
            return {"status": "success", "message": message}
        else:
            # Error
            error_message = f"Error running scraper: {result.stderr}"
            print(error_message)
            return {"status": "error", "message": error_message}
    
    except Exception as e:
        error_message = f"Failed to refresh news: {str(e)}"
        print(error_message)
        return {"status": "error", "message": error_message}

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
    
    if not json_files:
        print(f"No JSON files found in {source_dir}")
        return []
    
    # Debug: Print all file names
    print(f"Found {len(json_files)} files in {source_dir}:")
    for file in json_files[:5]:  # Show only first 5 to avoid too much output
        print(f"  - {os.path.basename(file)}")
    if len(json_files) > 5:
        print(f"  - ... and {len(json_files) - 5} more files")
    
    # Sort files by modification time (newest first) and limit
    json_files = sorted(json_files, key=os.path.getmtime, reverse=True)[:limit]
    
    # Tracking seen titles within this source only
    seen_titles = set()
    
    articles = []
    for file_path in json_files:
        try:
            print(f"Processing file: {os.path.basename(file_path)}")
            with open(file_path, 'r', encoding='utf-8') as f:
                article = json.load(f)
                
                # Skip articles with duplicate titles within this source
                if article.get('title') in seen_titles:
                    print(f"    Skipping duplicate article: {article.get('title')}")
                    continue
                
                # Add to seen titles
                seen_titles.add(article.get('title'))
                
                # Normalize date field - some sources use "date" instead of "published_date"
                if not article.get('published_date') and article.get('date'):
                    article['published_date'] = article['date']
                
                # Normalize category field - some sources use "category" (string) instead of "categories" (array)
                if not article.get('categories') and article.get('category'):
                    if isinstance(article['category'], str):
                        article['categories'] = [article['category']]
                    elif isinstance(article['category'], list):
                        article['categories'] = article['category']
                
                # Add summary if not already present
                if 'content' in article and not article.get('summary'):
                    try:
                        # Summarize the content (max 100 words) with timeout protection
                        content = article['content']
                        if len(content) > 50000:  # If content is extremely large, truncate it
                            content = content[:50000] + "..."
                        
                        # Use the preloaded model for summarization
                        article['summary'] = summarizer_model.summarize(content, max_length=100)
                    except Exception as e:
                        print(f"Error summarizing article {file_path}: {str(e)}")
                        article['summary'] = article.get('description', 'Summary not available')
                
                # Ensure we have a placeholder for missing data
                if not article.get('author'):
                    article['author'] = "Unknown Author"
                    
                if not article.get('image_url'):
                    article['image_url'] = "/static/images/placeholder.jpg"
                
                # Validate image URLs
                if article.get('image_url'):
                    # Check if the URL starts with https:// or http://
                    if not (article['image_url'].startswith('http://') or article['image_url'].startswith('https://')):
                        article['image_url'] = "/static/images/placeholder.jpg"
                
                # Add file path for reference and make it part of a unique ID to distinguish articles with same title
                article['file_path'] = os.path.basename(file_path)
                article['id'] = os.path.basename(file_path).split('.')[0]
                
                articles.append(article)
                print(f"    Article added successfully")
                
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in file {file_path}: {str(e)}")
            continue
        except Exception as e:
            print(f"Error loading article {file_path}: {str(e)}")
            continue
    
    print(f"Loaded {len(articles)} unique articles from {source}")
    return articles

# Run the FastAPI app with uvicorn if this file is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 