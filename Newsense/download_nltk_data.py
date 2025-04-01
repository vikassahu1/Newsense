import nltk

def download_nltk_data():
    print("Downloading required NLTK data...")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')
    print("NLTK data download complete!")

if __name__ == "__main__":
    download_nltk_data() 