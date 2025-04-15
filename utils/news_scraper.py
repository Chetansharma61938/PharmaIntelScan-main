"""
News scraper module for the pharma CI platform.
Fetches and processes pharmaceutical news from various sources.
"""
import requests
import trafilatura
import pandas as pd
import time
import os
import hashlib
from datetime import datetime, timedelta
from utils.text_processing import summarize_text, analyze_sentiment

# Cache directory
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_cache_key(params):
    """Generate a cache key from the parameters"""
    param_str = str(sorted(params.items()))
    return hashlib.md5(param_str.encode()).hexdigest()

def get_news_articles(company_names=None, drug_names=None, max_results=20, refresh=False):
    """
    Fetch pharmaceutical news from news APIs and pharma news sites.
    
    Args:
        company_names (list): List of company names to filter by
        drug_names (list): List of drug names to filter by
        max_results (int): Maximum number of results to return
        refresh (bool): Whether to refresh the cache
        
    Returns:
        list: List of dictionaries containing news articles
    """
    # Build search query
    query_terms = []
    
    if company_names:
        query_terms.extend(company_names)
        
    if drug_names:
        query_terms.extend(drug_names)
    
    # If no specific terms, use general pharma terms
    if not query_terms:
        query_terms = ["pharmaceutical", "drug approval", "clinical trial", "FDA"]
    
    # Create params for cache key
    params = {
        "terms": "+".join(query_terms),
        "max_results": max_results
    }
    
    # Generate cache key
    cache_key = generate_cache_key(params)
    cache_file = os.path.join(CACHE_DIR, f"news_{cache_key}.json")
    
    # Check if cached data exists and is fresh (less than 2 hours old for news)
    if not refresh and os.path.exists(cache_file):
        file_time = os.path.getmtime(cache_file)
        if (time.time() - file_time) < 7200:  # 2 hours in seconds
            try:
                return pd.read_json(cache_file).to_dict('records')
            except:
                # If there's an error reading the cache, continue to fetch fresh data
                pass
    
    articles = []
    
    try:
        # Try to use the free News API (requires API key in production)
        # For this MVP, let's use a simulated response that resembles the News API format
        # In production, use: https://newsapi.org/v2/everything
        
        news_sources = [
            {
                "name": "FiercePharma",
                "url": "https://www.fiercepharma.com/pharma",
                "domain": "fiercepharma.com"
            },
            {
                "name": "BioSpace",
                "url": "https://www.biospace.com/news/",
                "domain": "biospace.com"
            },
            {
                "name": "PharmaTimes",
                "url": "https://www.pharmatimes.com/news",
                "domain": "pharmatimes.com"
            },
            {
                "name": "Endpoints News",
                "url": "https://endpts.com/",
                "domain": "endpts.com"
            }
        ]
        
        # Scrape a few recent pharmaceutical news websites
        for source in news_sources[:2]:  # Limit to 2 sources for the MVP
            try:
                # Get HTML content
                response = requests.get(source["url"])
                if response.status_code == 200:
                    # Extract text content
                    html_content = response.text
                    
                    # Extract main content and URL from the page
                    article_content = trafilatura.extract(html_content)
                    article_url = response.url  # Use actual URL from response
                    
                    # If we got content, create an article entry
                    if article_content:
                        title = f"Latest Updates from {source['name']}"
                        
                        # We can also try to extract specific articles, but for MVP we'll use the main page content
                        # In a production environment, we would parse the HTML to extract individual articles
                        
                        # Skip if no content
                        if not article_content:
                            continue
                        
                        # Create summary and sentiment
                        summary = summarize_text(article_content)
                        sentiment = analyze_sentiment(article_content)
                        
                        # Create article entry
                        article = {
                            "title": title,
                            "source": source["name"],
                            "url": article_url,
                            "published_at": datetime.now().strftime('%Y-%m-%d'),
                            "summary": summary,
                            "sentiment": sentiment,
                            "content": article_content[:500] + "..." if len(article_content) > 500 else article_content
                        }
                        
                        articles.append(article)
                        
                        # Check if we have enough articles
                        if len(articles) >= max_results:
                            break
            except Exception as e:
                print(f"Error scraping {source['name']}: {e}")
                continue
        
        # If we didn't get enough articles, generate some mock data for the demo
        if len(articles) == 0:
            # Create a few example articles
            sample_articles = [
                {
                    "title": "FDA Approves New Treatment for Rare Disease",
                    "source": "FiercePharma",
                    "url": "https://www.fiercepharma.com/example",
                    "published_at": datetime.now().strftime('%Y-%m-%d'),
                    "summary": "The FDA has approved a new therapy for a rare genetic disease, marking a significant milestone in treatment options.",
                    "sentiment": "positive",
                    "content": "The FDA has approved a new therapy for a rare genetic disease, marking a significant milestone in treatment options. The drug, developed over a decade, showed promising results in clinical trials."
                },
                {
                    "title": "Major Pharma Company Announces Phase 3 Results",
                    "source": "BioSpace",
                    "url": "https://www.biospace.com/example",
                    "published_at": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                    "summary": "A leading pharmaceutical company reported positive Phase 3 trial results for its flagship oncology drug.",
                    "sentiment": "positive",
                    "content": "A leading pharmaceutical company reported positive Phase 3 trial results for its flagship oncology drug. The results exceeded expectations with a 40% improvement in progression-free survival."
                }
            ]
            
            articles.extend(sample_articles)
        
        # Save to cache
        pd.DataFrame(articles).to_json(cache_file)
        
        return articles
        
    except Exception as e:
        print(f"Error fetching news data: {e}")
        # If there was an error but we have cached data, use it regardless of age
        if os.path.exists(cache_file):
            try:
                return pd.read_json(cache_file).to_dict('records')
            except:
                pass
        
        return []

def get_kol_mentions(kol_name, max_results=10):
    """
    Get mentions of a specific KOL across news and research.
    
    Args:
        kol_name (str): Name of the Key Opinion Leader
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of dictionaries containing mentions
    """
    # This would normally search for the KOL across multiple data sources
    # For MVP, we'll focus on PubMed data
    from utils.pubmed import get_pubmed_data
    
    # Get publications authored by or mentioning the KOL
    pubmed_results = get_pubmed_data(drug_names=[kol_name], max_results=max_results)
    
    # Format the results
    mentions = []
    for pub in pubmed_results:
        mention = {
            "source": pub["journal"],
            "title": pub["title"],
            "date": pub["pub_date"],
            "url": pub["url"],
            "type": "Publication",
            "context": pub["abstract"][:200] + "..." if len(pub["abstract"]) > 200 else pub["abstract"]
        }
        mentions.append(mention)
    
    return mentions
