import os
import json
import sys
import argparse
from tqdm import tqdm
from pathlib import Path
from summarizer import summarize_news

def summarize_article(article_path, max_length=100, output_dir="summarized_news"):
    """Summarize a single article and save the result"""
    try:
        # Load the article
        with open(article_path, 'r', encoding='utf-8') as f:
            article = json.load(f)
            
        # Get content
        content = article.get('content', '')
        if not content:
            return False, "Article has no content"
            
        # Generate summary
        summary = summarize_news(content, max_length)
        
        # Create the output file path
        source_name = article.get('source', 'unknown')
        source_dir = os.path.join(output_dir, source_name)
        Path(source_dir).mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        filename = f"summary_{os.path.basename(article_path)}"
        output_path = os.path.join(source_dir, filename)
        
        # Save the summary
        article_with_summary = article.copy()
        article_with_summary['summary'] = summary
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(article_with_summary, f, ensure_ascii=False, indent=4)
            
        return True, summary
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='Summarize news articles')
    parser.add_argument('--input', '-i', default='scrapper/scraped_news', 
                        help='Directory containing scraped news articles')
    parser.add_argument('--output', '-o', default='summarized_news', 
                        help='Directory to save summarized articles')
    parser.add_argument('--max-length', '-m', type=int, default=100, 
                        help='Maximum length of summaries in words')
    parser.add_argument('--source', '-s', 
                        help='Process only a specific source')
    parser.add_argument('--limit', '-l', type=int, 
                        help='Limit number of articles to process per source')
    
    args = parser.parse_args()
    
    # Check if the input directory exists
    if not os.path.exists(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return 1
        
    # Create the output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find source directories
    if args.source:
        source_dirs = [args.source] if os.path.isdir(os.path.join(args.input, args.source)) else []
        if not source_dirs:
            print(f"Error: Source '{args.source}' not found")
            return 1
    else:
        source_dirs = [d for d in os.listdir(args.input) 
                      if os.path.isdir(os.path.join(args.input, d))]
                      
    if not source_dirs:
        print("No news sources found")
        return 1
        
    print(f"Found {len(source_dirs)} news sources")
    
    # Process each source
    total_articles = 0
    successful_summaries = 0
    
    for source in source_dirs:
        source_path = os.path.join(args.input, source)
        
        # Get all JSON files in the source directory
        json_files = [f for f in os.listdir(source_path) if f.endswith('.json')]
        
        if args.limit and len(json_files) > args.limit:
            json_files = json_files[:args.limit]
            
        if not json_files:
            print(f"No news articles found in {source}")
            continue
            
        print(f"\nProcessing {len(json_files)} articles from {source}...")
        
        # Process each article
        for article_file in tqdm(json_files):
            article_path = os.path.join(source_path, article_file)
            total_articles += 1
            
            success, message = summarize_article(
                article_path, 
                max_length=args.max_length,
                output_dir=args.output
            )
            
            if success:
                successful_summaries += 1
    
    # Print summary
    print(f"\nSummarization complete!")
    print(f"Total articles processed: {total_articles}")
    print(f"Successful summaries: {successful_summaries}")
    print(f"Failed summaries: {total_articles - successful_summaries}")
    print(f"Summary success rate: {successful_summaries / total_articles * 100:.1f}%")
    print(f"Summaries saved to: {os.path.abspath(args.output)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 