# Newsense - AI News Summarizer

An AI-powered news aggregation and summarization web application that fetches, summarizes, and displays news articles from various sources.

## Features

- **Two-section Layout**: 
  - Left sidebar (30%) for filtering options
  - Right main section (70%) for news feed

- **Filtering Options**:
  - Select news channel (BBC, CNN, The Hindu, etc.)
  - Apply button to fetch articles

- **News Fetching & Processing**:
  - Fetches the top 20 articles from selected channel
  - AI-powered summarization of news content
  - Sequential loading of articles for a smoother experience

- **News Feed Display**:
  - Card-based article display
  - Clickable titles linking to original articles
  - Thumbnail images with lazy loading
  - Author information and published dates
  - Categories displayed on each card
  - "Read More" button

- **Enhanced User Experience**:
  - Loading indicators while fetching news
  - Success/error alerts for clear feedback
  - Lazy loading for better performance
  - Smooth transitions and animations

## Tech Stack

- **Backend**: FastAPI
- **Templating**: Jinja2
- **Frontend**: HTML, Tailwind CSS
- **Interactions**: JavaScript
- **AI Summarization**: Transformer-based models

## Setup & Installation

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd Newsense
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Download NLTK data** (required for summarization):
   ```
   python download_nltk_data.py
   ```

4. **Run the scraper** to fetch news articles:
   ```
   python run_scraper.py
   ```

5. **Start the FastAPI server**:
   ```
   python -m app.main
   ```

6. **Access the application**:
   Open your browser and navigate to `http://localhost:8000`

## Project Structure

- `app/` - FastAPI web application
  - `main.py` - FastAPI application and routes
  - `templates/` - Jinja2 HTML templates
  - `static/` - CSS, JS and image files
- `scrapper/` - News scraping functionality
  - `main.py` - Enhanced news scraper implementation
- `summarizer.py` - AI-powered news summarization
- `run_scraper.py` - Script to run the news scraper

## License

MIT 