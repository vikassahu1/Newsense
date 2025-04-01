from scrapper.main import EnhancedNewsScraper
import logging

def main():
    # Initialize the scraper
    scraper = EnhancedNewsScraper(output_dir="scrapper/scraped_news")
    
    # Start scraping
    try:
        articles_count = scraper.scrape_all_sources()
        print(f"Successfully scraped {articles_count} articles!")
    except Exception as e:
        print(f"An error occurred while scraping: {str(e)}")

if __name__ == "__main__":
    main() 