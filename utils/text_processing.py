"""
Text processing utilities for the pharma CI platform.
Includes functions for identifying Key Opinion Leaders (KOLs) and processing text data.
"""
from collections import defaultdict
from typing import List, Dict, Any
import re

def identify_kols(publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify Key Opinion Leaders from publication data.
    
    Args:
        publications (List[Dict]): List of publication dictionaries from PubMed
        
    Returns:
        List[Dict]: List of identified KOLs with their metrics
    """
    # Initialize dictionary to track author metrics
    author_metrics = defaultdict(lambda: {
        'publication_count': 0,
        'journals': set(),
        'recent_publication': None,
        'url': None
    })
    
    # Process each publication
    for pub in publications:
        # Extract authors from the publication
        authors = pub.get('authors', [])
        if not authors:
            continue
            
        # Update metrics for each author
        for author in authors:
            # Clean author name
            author_name = clean_author_name(author)
            
            # Update metrics
            metrics = author_metrics[author_name]
            metrics['publication_count'] += 1
            metrics['journals'].add(pub.get('journal', ''))
            
            # Keep track of most recent publication
            if not metrics['recent_publication'] or pub.get('date', '') > metrics['recent_publication']:
                metrics['recent_publication'] = pub.get('title', '')
                metrics['url'] = pub.get('url', '')
    
    # Convert to list of KOL dictionaries
    kols = []
    for name, metrics in author_metrics.items():
        kols.append({
            'name': name,
            'publication_count': metrics['publication_count'],
            'journals': sorted(list(metrics['journals'])),
            'recent_publication': metrics['recent_publication'],
            'url': metrics['url']
        })
    
    # Sort KOLs by publication count
    kols.sort(key=lambda x: x['publication_count'], reverse=True)
    
    return kols

def clean_author_name(name: str) -> str:
    """
    Clean and standardize author names.
    
    Args:
        name (str): Raw author name
        
    Returns:
        str: Cleaned author name
    """
    # Remove common suffixes
    suffixes = ['Jr.', 'Sr.', 'II', 'III', 'IV', 'PhD', 'MD', 'Dr.', 'Prof.']
    for suffix in suffixes:
        name = name.replace(suffix, '').strip()
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Standardize capitalization
    name = name.title()
    
    return name

def extract_drug_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract drug-related entities from text.
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        Dict[str, List[str]]: Dictionary of entity types and their values
    """
    # Initialize result dictionary
    entities = {
        'DRUG': set(),
        'ORG': set(),
        'PERSON': set(),
        'GPE': set()  # Geo-Political Entity
    }
    
    # Basic drug name patterns
    drug_patterns = [
        r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)*\b',  # Standard drug names
        r'\b[A-Z]{2,}\d+\b',  # Drug codes
        r'\b[A-Z][a-z]+(?:-[A-Z][a-z]+)*\s*(?:\([A-Za-z0-9]+\))?\b'  # Drug names with codes
    ]
    
    # Extract drug names
    for pattern in drug_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            entities['DRUG'].add(match.group())
    
    return {k: list(v) for k, v in entities.items()} 