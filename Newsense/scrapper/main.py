# enhanced_news_scraper.py
import requests
import feedparser
from bs4 import BeautifulSoup
import datetime
import logging
import json
import os
from newspaper import Article, Config
import csv
from urllib.parse import urlparse
from pathlib import Path
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class EnhancedNewsScraper:
    def __init__(self, output_dir="scraped_news"):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("scraper.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("EnhancedNewsScraper")
        
        # Download NLTK data for categorization (if not already downloaded)
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        # News sources configuration with default categories
        self.sources = [
            {"name": "BBC", "url": "https://www.bbc.com/news", "type": "web", "default_category": "general"},
            {"name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss", "type": "rss", "default_category": "general"},
            {"name": "Reuters", "url": "https://www.reuters.com/", "type": "web", "default_category": "general"},
            {"name": "NYTimes", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "type": "rss", "default_category": "world"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "type": "rss", "default_category": "technology"},
            {"name": "ESPN", "url": "https://www.espn.com/espn/rss/news", "type": "rss", "default_category": "sports"},
            {"name": "BBC Technology", "url": "http://feeds.bbci.co.uk/news/technology/rss.xml", "type": "rss", "default_category": "technology"},
            {"name": "BBC Business", "url": "http://feeds.bbci.co.uk/news/business/rss.xml", "type": "rss", "default_category": "business"},
            {"name": "BBC Health", "url": "http://feeds.bbci.co.uk/news/health/rss.xml", "type": "rss", "default_category": "health"},
            {"name": "BBC Science", "url": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "type": "rss", "default_category": "science"},
            {"name": "BBC Entertainment", "url": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "type": "rss", "default_category": "entertainment"},
        ]
        
        # Define main categories
        self.categories = [
            "politics", "business", "technology", "entertainment", 
            "sports", "science", "health", "world", "general"
        ]
        
        # Keywords associated with each category for classification
        self.category_keywords = {
            "politics": ["government", "election", "president", "democracy", "vote", "parliament", "minister", "policy", "political", "campaign", "senator", "congress"],
            "business": ["economy", "market", "stock", "trade", "company", "industry", "corporate", "finance", "investor", "economic", "startup", "ceo", "profit", "revenue"],
            "technology": ["tech", "software", "computer", "digital", "internet", "app", "cyber", "innovation", "ai", "artificial intelligence", "robot", "smartphone", "gadget"],
            "entertainment": ["movie", "film", "actor", "celebrity", "music", "star", "hollywood", "tv", "television", "show", "concert", "award", "artist", "drama"],
            "sports": ["game", "player", "team", "championship", "tournament", "match", "athlete", "coach", "league", "soccer", "football", "basketball", "baseball", "tennis"],
            "science": ["research", "study", "scientist", "discovery", "space", "physics", "chemistry", "biology", "experiment", "nasa", "planet", "climate", "environment"],
            "health": ["medical", "disease", "doctor", "patient", "hospital", "treatment", "drug", "healthcare", "cancer", "covid", "virus", "vaccine", "medicine", "wellness"],
            "world": ["international", "global", "foreign", "country", "nation", "diplomatic", "treaty", "war", "peace", "border", "immigration", "refugee", "united nations"],
        }
        
        # Create newspaper config with browser user-agent
        self.newspaper_config = Config()
        self.newspaper_config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.newspaper_config.request_timeout = 10
        self.newspaper_config.fetch_images = True  # Enable image fetching
        
        # Create output directory if it doesn't exist
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create a CSV file to store article metadata
        self.csv_path = os.path.join(self.output_dir, "articles_index.csv")
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'title', 'source', 'url', 'published_date', 
                                 'scraped_date', 'categories', 'has_image', 'filename'])
    
    def scrape_all_sources(self):
        """Scrape news from all configured sources"""
        self.logger.info("Starting scraping process for all sources")
        
        articles_count = 0
        for source in self.sources:
            try:
                self.logger.info(f"Scraping {source['name']} from {source['url']}")
                
                if source["type"] == "rss":
                    articles = self.scrape_rss(source["name"], source["url"], source.get("default_category", "general"))
                elif source["type"] == "web":
                    articles = self.scrape_website(source["name"], source["url"], source.get("default_category", "general"))
                else:
                    self.logger.warning(f"Unknown source type: {source['type']} for {source['name']}")
                    continue
                
                # Save articles
                for article in articles:
                    self.save_article(article)
                
                articles_count += len(articles)
                self.logger.info(f"Successfully scraped {len(articles)} articles from {source['name']}")
                
            except Exception as e:
                self.logger.error(f"Error scraping {source['name']}: {str(e)}")
        
        self.logger.info(f"Completed scraping. Total articles: {articles_count}")
        return articles_count
    
    def determine_categories(self, title, content, default_category):
        """Determine article categories based on content analysis"""
        # Start with default category
        categories = [default_category]
        
        # Combine title and content for analysis, convert to lowercase
        text = (title + " " + content).lower()
        
        # Tokenize and remove stopwords
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word.isalpha() and word not in stop_words]
        
        # Count category keyword occurrences
        category_scores = {category: 0 for category in self.categories}
        
        # Skip the default category that was already added
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                count = sum(1 for word in filtered_text if keyword == word)
                # Also check for multi-word keywords
                count += text.count(keyword)
                category_scores[category] += count
        
        # Normalize by the number of keywords in each category
        for category in category_scores:
            if category in self.category_keywords:
                num_keywords = len(self.category_keywords[category])
                if num_keywords > 0:
                    category_scores[category] /= num_keywords
        
        # Add categories that score above threshold (excluding default category)
        threshold = 0.5
        for category, score in category_scores.items():
            if score > threshold and category != default_category:
                categories.append(category)
        
        return list(set(categories))  # Remove duplicates
    
    def scrape_rss(self, source_name, rss_url, default_category):
        """Scrape articles from RSS feed"""
        articles = []
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:10]:  # Limit to 10 articles per source
            try:
                # Check if we have URL
                if not hasattr(entry, 'link'):
                    continue
                    
                # Extract article content using newspaper3k
                article = Article(entry.link, config=self.newspaper_config)
                article.download()
                article.parse()
                article.nlp()  # Run NLP to extract keywords and summary
                
                # Parse published date
                if hasattr(entry, "published_parsed"):
                    published_date = datetime.datetime(*entry.published_parsed[:6])
                elif article.publish_date:
                    published_date = article.publish_date
                else:
                    published_date = datetime.datetime.now()
                
                # Get the top image if available
                image_url = ""
                if article.top_image:
                    image_url = article.top_image
                elif hasattr(entry, 'media_content') and entry.media_content:
                    for media in entry.media_content:
                        if 'url' in media:
                            image_url = media['url']
                            break
                
                # Determine categories
                categories = self.determine_categories(article.title, article.text, default_category)
                
                # Create article object
                article_data = {
                    "title": entry.title,
                    "content": article.text,
                    "url": entry.link,
                    "source": source_name,
                    "published_date": published_date.isoformat(),
                    "scraped_date": datetime.datetime.now().isoformat(),
                    "html": article.html,
                    "authors": article.authors,
                    "keywords": article.keywords,
                    "summary": article.summary,
                    "categories": categories,
                    "image_url": image_url,
                }
                
                articles.append(article_data)
                self.logger.info(f"Scraped RSS article: {entry.title} (Categories: {', '.join(categories)})")
                
            except Exception as e:
                self.logger.error(f"Error processing RSS article {entry.link if hasattr(entry, 'link') else 'unknown'}: {str(e)}")
                
        return articles
    
    def scrape_website(self, source_name, website_url, default_category):
        """Scrape articles from a website"""
        articles = []
        
        try:
            # Use a realistic user agent to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(website_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract domain for relative URL handling
            parsed_url = urlparse(website_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Find article links - this pattern needs to be customized for each site
            article_links = set()
            
            # Look for common article link patterns
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Skip navigation, social, and other non-article links
                if any(skip in href for skip in ['javascript:', 'mailto:', '#', 'twitter.com', 'facebook.com']):
                    continue
                    
                # Look for links that might be articles based on URL structure
                if any(pattern in href for pattern in ['/news/', '/article/', '/story/', '/2023/', '/2024/', '/content/']):
                    # Handle relative URLs
                    if href.startswith('/'):
                        full_url = base_url + href
                    elif not href.startswith(('http://', 'https://')):
                        full_url = base_url + '/' + href
                    else:
                        full_url = href
                    
                    # Only add URLs from the same domain
                    if urlparse(full_url).netloc == parsed_url.netloc:
                        article_links.add(full_url)
            
            # Limit the number of articles to process
            article_links = list(article_links)[:10]  # Process max 10 articles per source
            
            # Process each article link
            for url in article_links:
                try:
                    article = Article(url, config=self.newspaper_config)
                    article.download()
                    article.parse()
                    article.nlp()  # Run NLP to extract keywords and summary
                    
                    # Skip articles with minimal content
                    if len(article.text) < 500:
                        continue
                    
                    # Get published date or use current time
                    published_date = article.publish_date if article.publish_date else datetime.datetime.now()
                    
                    # Determine categories
                    categories = self.determine_categories(article.title, article.text, default_category)
                    
                    article_data = {
                        "title": article.title,
                        "content": article.text,
                        "url": url,
                        "source": source_name,
                        "published_date": published_date.isoformat(),
                        "scraped_date": datetime.datetime.now().isoformat(),
                        "html": article.html,
                        "authors": article.authors,
                        "keywords": article.keywords,
                        "summary": article.summary,
                        "categories": categories,
                        "image_url": article.top_image,
                    }
                    
                    articles.append(article_data)
                    self.logger.info(f"Scraped web article: {article.title} (Categories: {', '.join(categories)})")
                    
                except Exception as e:
                    self.logger.error(f"Error processing web article {url}: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Error scraping website {website_url}: {str(e)}")
            
        return articles
    
    def save_article(self, article):
        """Save article to disk and update the index"""
        try:
            # Create a unique ID for the article based on URL
            import hashlib
            article_id = hashlib.md5(article["url"].encode()).hexdigest()
            
            # Create a filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{article_id}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save the full article data as JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article, f, ensure_ascii=False, indent=4)
            
            # Update the CSV index
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    article_id,
                    article["title"],
                    article["source"],
                    article["url"],
                    article["published_date"],
                    article["scraped_date"],
                    ",".join(article["categories"]),
                    "yes" if article.get("image_url") else "no",
                    filename
                ])
                
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving article {article['url']}: {str(e)}")
            return None

    def get_recent_articles(self, limit=20, category=None):
        """Get the most recently scraped articles with optional category filter"""
        articles = []
        
        try:
            if os.path.exists(self.csv_path):
                with open(self.csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    # Sort by scraped_date (newest first)
                    rows.sort(key=lambda x: x.get('scraped_date', ''), reverse=True)
                    
                    # Filter by category if specified
                    if category:
                        rows = [row for row in rows if category in row.get('categories', '').split(',')]
                    
                    # Get the most recent articles
                    recent_rows = rows[:limit]
                    
                    for row in recent_rows:
                        try:
                            # Load the full article data
                            filepath = os.path.join(self.output_dir, row['filename'])
                            if os.path.exists(filepath):
                                with open(filepath, 'r', encoding='utf-8') as af:
                                    article = json.load(af)
                                    articles.append(article)
                        except Exception as e:
                            self.logger.error(f"Error loading article {row['filename']}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error getting recent articles: {str(e)}")
            
        return articles
    
    def get_articles_by_category(self, category, limit=20):
        """Get articles filtered by category"""
        return self.get_recent_articles(limit=limit, category=category)
    
    def get_available_categories(self):
        """Get list of all categories found in articles"""
        categories = set()
        
        try:
            if os.path.exists(self.csv_path):
                with open(self.csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        for cat in row.get('categories', '').split(','):
                            if cat:
                                categories.add(cat)
        except Exception as e:
            self.logger.error(f"Error getting categories: {str(e)}")
            
        return sorted(list(categories))

# Example usage
if __name__ == "__main__":
    scraper = EnhancedNewsScraper(output_dir="scraped_news")
    num_articles = scraper.scrape_all_sources()
    print(f"Scraped {num_articles} articles")
    
    # Get all available categories
    categories = scraper.get_available_categories()
    print(f"Available categories: {', '.join(categories)}")
    
    # Get recent articles
    recent = scraper.get_recent_articles(5)
    for article in recent:
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Categories: {', '.join(article['categories'])}")
        print(f"Image URL: {article.get('image_url', 'None')}")
        print(f"URL: {article['url']}")
        print(f"Date: {article['published_date']}")
        print("-" * 50)