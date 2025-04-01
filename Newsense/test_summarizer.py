import os
import json
import sys
from summarizer import summarize_news
from pathlib import Path

def main():
    # Check if summarizer module is installed
    try:
        from transformers import pipeline
    except ImportError:
        print("Error: transformers package not installed.")
        print("Please install required packages with: pip install transformers torch nltk")
        return 1
        
    # Defining source directory where scraped news is stored
    scraped_dir = "scrapper/scraped_news"
    
    if not os.path.exists(scraped_dir):
        print(f"Error: Scraped news directory '{scraped_dir}' not found.")
        print("Please run the scraper first using: python run_scraper.py")
        return 1
    
    # Find all source directories
    source_dirs = [d for d in os.listdir(scraped_dir) 
                  if os.path.isdir(os.path.join(scraped_dir, d))]
    
    if not source_dirs:
        print("No news sources found. Please run the scraper first.")
        return 1
    
    print(f"Found {len(source_dirs)} news sources.")
    
    # Choose a random source for testing
    import random
    random_source = random.choice(source_dirs)
    source_path = os.path.join(scraped_dir, random_source)
    
    # Get all JSON files in the source directory
    json_files = [f for f in os.listdir(source_path) if f.endswith('.json')]
    
    if not json_files:
        print(f"No news articles found in {random_source}.")
        return 1
    
    # Choose a random article for summarization
    random_article_file = random.choice(json_files)
    article_path = os.path.join(source_path, random_article_file)
    
    print(f"\nReading article from {random_source}...")
    
    # Load the article
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            article = json.load(f)
    except Exception as e:
        print(f"Error reading article: {str(e)}")
        return 1
    
    # Display article info
    print(f"\nArticle Title: {article['title']}")
    print(f"Source: {article['source']}")
    print(f"Categories: {', '.join(article['categories'])}")
    print(f"URL: {article['url']}")
    
    # Display article content summary
    content = article['content']
    content_preview = content[:300] + "..." if len(content) > 300 else content
    print(f"\nOriginal Content (preview): \n{content_preview}")
    print(f"\nOriginal Length: {len(content.split())} words")
    
    # Set max length for summary
    max_length = 100
    
    print(f"\nGenerating summary (max {max_length} words)...")
    
    # Generate summary
    try:
        summary = summarize_news(content, max_length)
        print(f"\nSummary ({len(summary.split())} words):")
        print(f"{summary}")
        
        # Create a directory for summarized content
        summary_dir = Path("summarized_news")
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the summary
        summary_path = os.path.join(summary_dir, f"summary_{os.path.basename(article_path)}")
        with open(summary_path, 'w', encoding='utf-8') as f:
            # Create a new JSON with the original article plus summary
            article_with_summary = article.copy()
            article_with_summary['summary'] = summary
            json.dump(article_with_summary, f, ensure_ascii=False, indent=4)
            
        print(f"\nSummary saved to: {summary_path}")
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 