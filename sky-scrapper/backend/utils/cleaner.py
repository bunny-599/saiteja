import re
import html
from difflib import SequenceMatcher
from bs4 import BeautifulSoup

try:
    from langdetect import detect
except ImportError:
    # Fallback if langdetect is not present
    def detect(text):
        return "en"

def strip_html(text: str) -> str:
    """Strips HTML tags and decodes HTML entities."""
    if not text:
        return ""
    # Strip HTML using BeautifulSoup
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text(separator=" ")
    # Replace multiple spaces with a single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return html.unescape(cleaned).strip()

def is_similar(s1: str, s2: str, threshold: float = 0.8) -> bool:
    """Check if two strings are fuzzy duplicates."""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio() > threshold

def deduplicate_sentences(text: str) -> str:
    """Splits text into sentences and removes duplicate/highly similar ones."""
    if not text:
        return ""
    # Split text into sentences using simple regex
    sentences = re.split(r'(?<=[.!?])\s+', text)
    unique_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Check similarity with existing unique sentences
        is_dup = False
        for unique in unique_sentences:
            if len(sentence) > 10 and len(unique) > 10:
                if is_similar(sentence, unique):
                    is_dup = True
                    break
        
        if not is_dup:
            unique_sentences.append(sentence)
            
    return " ".join(unique_sentences)

def clean_review(review_text: str, max_chars: int = 300) -> str:
    """Clean, dedup, and truncate review text."""
    cleaned = strip_html(review_text)
    cleaned = deduplicate_sentences(cleaned)
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars].strip() + "..."
    return cleaned

def is_english(text: str) -> bool:
    """Check if the text is English. Gracefully handles errors."""
    if not text or len(text.strip()) < 5:
        # Too short, assume true to not drop it
        return True
    try:
        lang = detect(text)
        return lang == "en"
    except Exception:
        # Fallback to True if langdetect fails
        return True

def clean_text_for_ai(text: str) -> str:
    """Main cleaner for scraping text to feed into AI."""
    cleaned = strip_html(text)
    cleaned = deduplicate_sentences(cleaned)
    # Filter non-English sentences if possible or keep if it is fine
    # For large blobs, we can check overall if it is English
    if not is_english(cleaned):
        return ""
    return cleaned
