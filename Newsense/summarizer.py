import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
from nltk.tokenize import word_tokenize
import logging

class NewsSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        """
        Initialize the news summarizer with a pretrained model.
        
        Args:
            model_name (str): Name of the pretrained model to use
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("NewsSummarizer")
        
        try:
            self.logger.info(f"Loading model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            # Create a summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model=self.model,
                tokenizer=self.tokenizer,
                framework="pt"  # PyTorch
            )
            self.logger.info("Model loaded successfully")
            
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
                
        except Exception as e:
            self.logger.error(f"Error initializing summarizer: {str(e)}")
            raise
    
    def count_words(self, text):
        """Count the number of words in a text"""
        return len(word_tokenize(text))
    
    def summarize(self, content, max_length=200):
        """
        Summarize the given content, limiting to max_length words.
        
        Args:
            content (str): The text content to summarize
            max_length (int): Maximum number of words for the summary
            
        Returns:
            str: A summarized version of the content
        """
        if not content or len(content) < 100:
            return content  # Return original if content is too short
        
        try:
            # Calculate the appropriate max_tokens for the model
            # Rule of thumb: tokens are roughly 3/4 of words, so we multiply max_length by 4/3
            max_tokens = int(max_length * 4 / 3)
            
            # Set minimum length to about 1/3 of max_tokens to avoid too short summaries
            min_tokens = max(30, int(max_tokens / 3))
            
            # Chunk the text if it's too long for the model
            if len(content) > 1024 * 5:  # If content is very long
                chunks = self._chunk_text(content)
                summaries = []
                
                for chunk in chunks:
                    if len(chunk.strip()) < 100:  # Skip very short chunks
                        continue
                    
                    chunk_summary = self.summarizer(
                        chunk,
                        max_length=max_tokens,
                        min_length=min_tokens,
                        do_sample=False
                    )[0]['summary_text']
                    
                    summaries.append(chunk_summary)
                
                # Combine chunk summaries and re-summarize if needed
                combined_summary = " ".join(summaries)
                
                # If combined summary is too long, summarize it again
                if self.count_words(combined_summary) > max_length:
                    final_summary = self.summarizer(
                        combined_summary,
                        max_length=max_tokens,
                        min_length=min_tokens,
                        do_sample=False
                    )[0]['summary_text']
                    return final_summary
                
                return combined_summary
            else:
                # Process shorter text in a single pass
                summary = self.summarizer(
                    content,
                    max_length=max_tokens,
                    min_length=min_tokens,
                    do_sample=False
                )[0]['summary_text']
                
                return summary
                
        except Exception as e:
            self.logger.error(f"Error summarizing content: {str(e)}")
            # Fall back to a simple extraction approach if the model fails
            return self._fallback_summarize(content, max_length)
    
    def _chunk_text(self, text, chunk_size=1000):
        """Split text into chunks of approximately chunk_size words"""
        words = word_tokenize(text)
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            
        return chunks
    
    def _fallback_summarize(self, content, max_length):
        """Simple extractive summarization as a fallback method"""
        sentences = nltk.sent_tokenize(content)
        
        # For very short texts, return as is
        if len(sentences) <= 3:
            return content
        # Otherwise, take the first few sentences as a simple summary
        summary_sentences = sentences[:min(5, len(sentences))]
        summary = " ".join(summary_sentences)
        words = word_tokenize(summary)
        if len(words) > max_length:
            summary = " ".join(words[:max_length])
            
        return summary


def summarize_news(content, max_length=200):
    """
    Convenient function to summarize news content.
    
    Args:
        content (str): The text content to summarize
        max_length (int): Maximum length of summary in words
        
    Returns:
        str: Summarized content
    """
    # Lazy-load the summarizer when needed
    if not hasattr(summarize_news, "summarizer"):
        summarize_news.summarizer = NewsSummarizer()
        
    return summarize_news.summarizer.summarize(content, max_length)


# Example usage
if __name__ == "__main__":
    sample_article = """
    The European Union has agreed to impose new sanctions on Russia over its invasion of Ukraine. 
    The sanctions target Russia's financial sector, technology imports, and individuals linked to the Kremlin.
    The measures include freezing assets and travel bans for oligarchs and officials close to President Vladimir Putin.
    European Commission President Ursula von der Leyen said the sanctions would increase pressure on the Russian economy.
    "These sanctions will further isolate Russia and drain the resources it uses to finance this war," she said.
    The EU also plans to reduce its dependence on Russian energy imports by diversifying suppliers and investing in renewable energy.
    Russia has condemned the sanctions and threatened to respond with its own measures against European interests.
    The conflict in Ukraine has continued to escalate, with Russian forces intensifying attacks on major cities.
    Humanitarian organizations report growing civilian casualties and a worsening refugee crisis.
    The United Nations estimates that millions of Ukrainians have been displaced since the conflict began.
    Peace negotiations have stalled as both sides remain far apart on key issues.
    """

    summary = summarize_news(sample_article, 50)
    print(f"Original length: {len(word_tokenize(sample_article))} words")
    print(f"Summary length: {len(word_tokenize(summary))} words")
    print(f"\nSummary:\n{summary}") 