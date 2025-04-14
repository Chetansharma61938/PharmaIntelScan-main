"""
Text processing module for NLP tasks in the pharma CI platform.
Handles entity extraction, sentiment analysis, and text summarization.
"""
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import spacy

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model for entity extraction
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If model isn't available, download it
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Note: We're using a simple extractive summarization approach
# rather than the transformers library for the MVP

def extract_entities(text, entity_types=None):
    """
    Extract named entities from text.
    
    Args:
        text (str): Text to extract entities from
        entity_types (list): Types of entities to extract (ORG, PERSON, etc.)
        
    Returns:
        dict: Dictionary of entity types and values
    """
    if not text:
        return {}
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Dictionary to store entities by type
    entities = {}
    
    # Filter by entity type if specified
    for ent in doc.ents:
        if entity_types and ent.label_ not in entity_types:
            continue
            
        if ent.label_ not in entities:
            entities[ent.label_] = []
            
        # Add entity if it's not already in the list
        if ent.text not in entities[ent.label_]:
            entities[ent.label_].append(ent.text)
    
    return entities

def extract_drug_entities(text):
    """
    Extract drug names and related entities from pharmaceutical text.
    
    Args:
        text (str): Text to extract entities from
        
    Returns:
        dict: Dictionary of pharmaceutical entities
    """
    # This is a simplified implementation that would be enhanced with
    # domain-specific NER models in a production environment
    
    # Use general NER first
    entities = extract_entities(text)
    
    # Look for specific drug-related patterns
    drug_patterns = [
        r'\b[A-Z][a-z]*mab\b',  # Monoclonal antibodies
        r'\b[A-Z][a-z]*nib\b',  # Kinase inhibitors
        r'\b[A-Z][a-z]*zumab\b',  # Humanized antibodies
        r'\b[A-Z][a-z]*tinib\b',  # Tyrosine kinase inhibitors
        r'\b[A-Z][a-z]*ciclib\b',  # CDK inhibitors
    ]
    
    drug_candidates = set()
    
    # Extract using regex patterns
    for pattern in drug_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            drug_candidates.add(match.group(0))
    
    # Add drug candidates to entities
    if drug_candidates:
        if 'DRUG' not in entities:
            entities['DRUG'] = []
        entities['DRUG'].extend(list(drug_candidates))
    
    return entities

def analyze_sentiment(text):
    """
    Analyze sentiment of text (positive, negative, neutral).
    
    Args:
        text (str): Text to analyze
        
    Returns:
        str: Sentiment classification
    """
    if not text:
        return "neutral"
    
    # Use TextBlob for sentiment analysis
    blob = TextBlob(text)
    
    # Get polarity score (-1 to 1)
    polarity = blob.sentiment.polarity
    
    # Classify sentiment
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

def summarize_text(text, max_length=150):
    """
    Generate a summary of the given text.
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum length of summary
        
    Returns:
        str: Summarized text
    """
    if not text:
        return ""
    
    # We're using extractive summarization for the MVP
    # In a production environment, we would use a more sophisticated model
    
    # Extractive summarization as a fallback
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Return the text as is if it's already short
    if len(sentences) <= 3:
        return text[:max_length] + "..." if len(text) > max_length else text
    
    # Create word frequency table
    stop_words = set(stopwords.words('english'))
    word_frequencies = {}
    
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        for word in words:
            if word not in stop_words and word.isalnum():
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
    
    # Calculate sentence scores based on word frequency
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        words = word_tokenize(sentence.lower())
        score = sum(word_frequencies.get(word, 0) for word in words if word.isalnum())
        sentence_scores[i] = score
    
    # Select top sentences
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Sort by original position
    
    # Build summary
    summary = ' '.join(sentences[i] for i, _ in top_sentences)
    
    # Truncate if needed
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    
    return summary

def identify_kols(publications):
    """
    Identify potential KOLs from a set of publications.
    
    Args:
        publications (list): List of publication dictionaries
        
    Returns:
        list: List of potential KOLs with their metrics
    """
    # Count author occurrences
    author_counts = {}
    author_publications = {}
    
    for pub in publications:
        authors = pub.get('all_authors', [])
        
        for author in authors:
            if author not in author_counts:
                author_counts[author] = 1
                author_publications[author] = [pub]
            else:
                author_counts[author] += 1
                author_publications[author].append(pub)
    
    # Create KOL list
    kols = []
    
    for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 2:  # Consider authors with at least 2 publications
            # Get journals for this author
            journals = set(pub.get('journal', 'Unknown') for pub in author_publications[author])
            
            # Get most recent publication safely
            try:
                # Filter out publications with None pub_date
                valid_pubs = [p for p in author_publications[author] if p.get('pub_date') is not None]
                
                if valid_pubs:
                    recent_pub = max(valid_pubs, key=lambda x: x.get('pub_date', ''))
                    recent_title = recent_pub.get('title', 'Unknown title')
                else:
                    recent_title = author_publications[author][0].get('title', 'Unknown title')
            except:
                recent_title = "Publication information unavailable"
            
            kol = {
                'name': author,
                'publication_count': count,
                'journals': list(journals),
                'recent_publication': recent_title,
                'url': author_publications[author][0].get('url', '')
            }
            
            kols.append(kol)
    
    return kols[:20]  # Return top 20 KOLs
