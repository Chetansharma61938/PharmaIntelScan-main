"""
News scraping module for the pharma CI platform.
Fetches and processes news articles using AI or falls back to demo data.
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

# Try to import Groq, but don't fail if not available
try:
    import groq
    GROQ_AVAILABLE = True
    # Initialize Groq client without proxies
    groq_client = groq.Groq(
        api_key=os.getenv("GROQ_API_KEY"),
        http_client=None  # Let Groq handle its own HTTP client
    )
except ImportError:
    GROQ_AVAILABLE = False
    print("Groq package not available. Using demo data instead.")
except Exception as e:
    GROQ_AVAILABLE = False
    print(f"Error initializing Groq client: {e}. Using demo data instead.")

def get_demo_articles(query: str = None, max_results: int = 10) -> List[Dict]:
    """
    Generate demo news articles when API is not available.
    """
    demo_articles = [
        {
            "title": "FDA Approves Breakthrough Cancer Treatment",
            "source": "PharmaNews",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "url": "https://example.com/news/1",
            "summary": "The FDA has approved a groundbreaking new cancer treatment that shows promising results in clinical trials.",
            "sentiment": 0.8
        },
        {
            "title": "Moderna Announces Success in Phase 3 Trial",
            "source": "BioTechDaily",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "url": "https://example.com/news/2",
            "summary": "Moderna's latest vaccine candidate shows 95% efficacy in Phase 3 clinical trials.",
            "sentiment": 0.9
        },
        {
            "title": "Pfizer Expands Research into Rare Diseases",
            "source": "HealthWire",
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "url": "https://example.com/news/3",
            "summary": "Pfizer announces major investment in rare disease research program.",
            "sentiment": 0.7
        },
        {
            "title": "New Study Shows Promise for Alzheimer's Treatment",
            "source": "MedicalDaily",
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "url": "https://example.com/news/4",
            "summary": "Researchers report positive results from early trials of new Alzheimer's drug.",
            "sentiment": 0.6
        },
        {
            "title": "Johnson & Johnson Partners with Biotech Startup",
            "source": "PharmaInsider",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "url": "https://example.com/news/5",
            "summary": "Strategic partnership aims to accelerate drug development pipeline.",
            "sentiment": 0.5
        }
    ]
    
    if query:
        # Filter articles based on query
        query_terms = query.lower().split(" OR ")
        filtered_articles = [
            article for article in demo_articles
            if any(term.lower() in article["title"].lower() or term.lower() in article["summary"].lower()
                  for term in query_terms)
        ]
        return filtered_articles[:max_results] if filtered_articles else demo_articles[:max_results]
    
    return demo_articles[:max_results]

def get_news_articles(company_names: List[str] = None, drug_names: List[str] = None, max_results: int = 10) -> List[Dict]:
    """
    Fetch pharmaceutical news articles using Groq's AI API or return demo data if not available.
    
    Args:
        company_names (List[str], optional): List of company names to search for
        drug_names (List[str], optional): List of drug names to search for
        max_results (int): Maximum number of results to return
        
    Returns:
        List[Dict]: List of news articles with metadata
    """
    try:
        # Prepare search query
        search_terms = []
        if company_names:
            search_terms.extend(company_names)
        if drug_names:
            search_terms.extend(drug_names)
        
        # If no specific terms provided, use general pharma terms
        if not search_terms:
            search_terms = ["pharmaceutical industry", "drug development", "FDA approval", "clinical trials"]
        
        query = " OR ".join(search_terms)
        
        if not GROQ_AVAILABLE:
            return get_demo_articles(query, max_results)
        
        # Use Groq to get news
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "system",
                    "content": """You are a pharmaceutical industry news expert. Find and summarize recent news articles.
                    For each article provide:
                    1. Title: Clear and concise title
                    2. Source: Publication name
                    3. Date: YYYY-MM-DD format
                    4. URL: Full article URL
                    5. Summary: 2-3 sentence summary
                    6. Sentiment: Brief sentiment analysis (-1 to 1 scale)"""
                },
                {
                    "role": "user",
                    "content": f"Find {max_results} recent pharmaceutical industry news articles about: {query}. Focus on high-quality sources and important developments."
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        # Process the response
        articles = []
        content = response.choices[0].message.content
        article_blocks = content.split("\n\n")
        
        for block in article_blocks:
            if not block.strip():
                continue
            
            try:
                lines = block.split("\n")
                if len(lines) >= 6:  # Ensure we have all required fields
                    article = {
                        "title": lines[0].replace("Title: ", "").strip(),
                        "source": lines[1].replace("Source: ", "").strip(),
                        "date": lines[2].replace("Date: ", "").strip(),
                        "url": lines[3].replace("URL: ", "").strip(),
                        "summary": lines[4].replace("Summary: ", "").strip(),
                        "sentiment": float(lines[5].replace("Sentiment: ", "").strip())
                    }
                    articles.append(article)
            except Exception as e:
                print(f"Error processing article block: {e}")
                continue
        
        return articles[:max_results] if articles else get_demo_articles(query, max_results)
        
    except Exception as e:
        print(f"Error fetching news articles: {e}")
        return get_demo_articles(query, max_results)

def get_company_news(company_name: str, max_results: int = 5) -> List[Dict]:
    """
    Get news articles for a specific company.
    
    Args:
        company_name (str): Company name to search for
        max_results (int): Maximum number of articles to return
        
    Returns:
        List[Dict]: List of dictionaries containing article data
    """
    return get_news_articles(company_names=[company_name], max_results=max_results)

def analyze_news_sentiment(articles: List[Dict]) -> List[Dict]:
    """
    Analyze sentiment of news articles using Groq's API.
    """
    try:
        for article in articles:
            try:
                response = groq_client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a sentiment analysis expert. Return only a number between -1 and 1 representing the sentiment score."
                        },
                        {
                            "role": "user",
                            "content": f"Analyze the sentiment of this pharmaceutical news text and return only a number: {article['content'][:500]}"
                        }
                    ],
                    temperature=0.3,
                    max_tokens=10
                )
                
                sentiment_text = response.choices[0].message.content.strip()
                try:
                    sentiment_score = float(sentiment_text)
                    article["sentiment"] = max(min(sentiment_score, 1.0), -1.0)  # Ensure within bounds
                except:
                    article["sentiment"] = 0.0
                
                # Add a small delay to avoid rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error analyzing article sentiment: {e}")
                article["sentiment"] = 0.0
        
        return articles
        
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        # Add neutral sentiment if analysis fails
        for article in articles:
            if "sentiment" not in article:
                article["sentiment"] = 0.0
        return articles

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
