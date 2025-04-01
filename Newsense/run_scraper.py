from scrapper.main import EnhancedNewsScraper
import logging
import sys
import time
import os
from pathlib import Path

def main():
    # Set the news freshness threshold (in days)
    days_threshold = 2
    
    print(f"Starting news scraper - fetching articles from the last {days_threshold} days")
    print("News will be organized in separate folders by source")
    
    # Create output directory
    output_dir = "scrapper/scraped_news"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize the scraper
    scraper = EnhancedNewsScraper(output_dir=output_dir, days_threshold=days_threshold)
    
    # Start scraping
    try:
        start_time = time.time()
        print("Scraping in progress...")
        
        articles_count = scraper.scrape_all_sources()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nScraping completed!")
        print(f"Successfully scraped {articles_count} articles in {duration:.1f} seconds")
        print(f"Articles stored in: {os.path.abspath(output_dir)}")
        
        # List source directories
        source_dirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
        print("\nArticles organized by source:")
        for source in source_dirs:
            source_path = os.path.join(output_dir, source)
            articles = [f for f in os.listdir(source_path) if f.endswith('.json')]
            print(f"  - {source}: {len(articles)} articles")
            
    except Exception as e:
        print(f"An error occurred while scraping: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 