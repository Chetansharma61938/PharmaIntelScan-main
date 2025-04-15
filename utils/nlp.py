"""
Natural Language Processing module for the pharma CI platform.
Provides entity extraction capabilities.
"""
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from typing import Dict, Set

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')
try:
    nltk.data.find('maxent_ne_chunker')
except LookupError:
    nltk.download('maxent_ne_chunker')
try:
    nltk.data.find('words')
except LookupError:
    nltk.download('words')

# Common pharmaceutical companies
PHARMA_COMPANIES = {
    'pfizer', 'moderna', 'johnson & johnson', 'novartis', 'roche', 'merck',
    'astrazeneca', 'gsk', 'glaxosmithkline', 'sanofi', 'gilead', 'bayer',
    'abbvie', 'amgen', 'biogen', 'bristol myers squibb', 'eli lilly',
    'regeneron', 'vertex', 'alexion', 'bms', 'j&j'
}

# Common drug names and medical terms
DRUG_TERMS = {
    'vaccine', 'antibody', 'treatment', 'therapy', 'drug', 'medicine',
    'therapeutic', 'dose', 'trial', 'study', 'clinical', 'phase',
    'keytruda', 'humira', 'revlimid', 'eliquis', 'opdivo', 'ozempic',
    'wegovy', 'tecfidera', 'imbruvica', 'eylea', 'skyrizi', 'dupixent',
    'covid-19 vaccine', 'mrna vaccine'
}

def extract_drug_entities(text: str) -> Dict[str, Set[str]]:
    """
    Extract pharmaceutical entities from text using NLTK and pattern matching.
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        Dict[str, Set[str]]: Dictionary of entity types and their values
    """
    try:
        entities = {
            'DRUG': set(),
            'ORG': set(),
            'PERSON': set(),
            'GPE': set()
        }
        
        # Clean and prepare text
        sentences = sent_tokenize(text)
        
        # Process each sentence
        for sentence in sentences:
            # Tokenize and tag parts of speech
            tokens = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(tokens)
            
            # Extract named entities
            chunks = nltk.ne_chunk(tagged)
            
            # Process named entity chunks
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    entity_type = chunk.label()
                    
                    if entity_type in entities:
                        entities[entity_type].add(entity_text.lower())
            
            # Additional pattern matching for drugs and companies
            text_lower = sentence.lower()
            
            # Find drug mentions
            for drug in DRUG_TERMS:
                if drug in text_lower:
                    entities['DRUG'].add(drug)
            
            # Find company mentions
            for company in PHARMA_COMPANIES:
                if company in text_lower:
                    entities['ORG'].add(company)
            
            # Find drug names using patterns
            drug_patterns = [
                r'\b[A-Z][a-z]+(?:mab|nib|zib|mib|lin|nat|nex|cel|zol|mar|mus)\b',  # Common drug suffix patterns
                r'\b[A-Z][a-z]+(?:io|ra|la|na|ri|pi|xi|vi|bi|li|mi|di|ci|ti)\b',    # Additional patterns
                r'\b[A-Z][a-z]+(?:-[0-9]+|/[0-9]+)\b'                               # Drugs with numbers
            ]
            
            for pattern in drug_patterns:
                matches = re.finditer(pattern, sentence)
                for match in matches:
                    drug_name = match.group()
                    if len(drug_name) > 3:  # Avoid short matches
                        entities['DRUG'].add(drug_name.lower())
        
        return entities
        
    except Exception as e:
        print(f"Error in extract_drug_entities: {e}")
        return {'DRUG': set(), 'ORG': set(), 'PERSON': set(), 'GPE': set()} 