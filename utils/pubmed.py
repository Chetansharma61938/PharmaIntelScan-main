"""
PubMed data collection module for the pharma CI platform.
Fetches and processes data from PubMed using BioPython.
"""
import os
import time
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from Bio import Entrez
from urllib.error import HTTPError

# Cache directory
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Set your email for Entrez
Entrez.email = "user@example.com"  # should be a real email in production

def generate_cache_key(params):
    """Generate a cache key from the parameters"""
    param_str = str(sorted(params.items()))
    return hashlib.md5(param_str.encode()).hexdigest()

def get_pubmed_data(company_names=None, drug_names=None, max_results=50, refresh=False):
    """
    Fetch publication data from PubMed using Entrez.
    
    Args:
        company_names (list): List of company names to filter by
        drug_names (list): List of drug names to filter by
        max_results (int): Maximum number of results to return
        refresh (bool): Whether to refresh the cache
        
    Returns:
        list: List of dictionaries containing publication data
    """
    # Build search query
    query_parts = []
    
    if company_names:
        company_query = " OR ".join([f'"{company}"[Affiliation]' for company in company_names])
        query_parts.append(f"({company_query})")
    
    if drug_names:
        drug_query = " OR ".join([f'"{drug}"[Title/Abstract]' for drug in drug_names])
        query_parts.append(f"({drug_query})")
    
    # Focus on recent pharma industry publications if no specific filters
    if not query_parts:
        # Publications in the last 30 days related to pharmaceuticals
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y/%m/%d')
        query_parts.append(f"(pharmaceutical[Title/Abstract] OR drug[Title/Abstract] OR therapy[Title/Abstract])")
        query_parts.append(f'("{thirty_days_ago}"[Date - Publication] : "3000"[Date - Publication])')
    
    # Add pharma/drug filter if company names were provided but no drug names
    if company_names and not drug_names:
        query_parts.append("(pharmaceutical[Title/Abstract] OR drug[Title/Abstract] OR medicine[Title/Abstract] OR therapy[Title/Abstract])")
    
    # Combine all parts with AND
    query = " AND ".join(query_parts)
    
    # Parameters for cache
    params = {
        "term": query,
        "max_results": max_results
    }
    
    # Generate cache key
    cache_key = generate_cache_key(params)
    cache_file = os.path.join(CACHE_DIR, f"pubmed_{cache_key}.json")
    
    # Check if cached data exists and is fresh (less than 12 hours old)
    if not refresh and os.path.exists(cache_file):
        file_time = os.path.getmtime(cache_file)
        if (time.time() - file_time) < 43200:  # 12 hours in seconds
            try:
                return pd.read_json(cache_file).to_dict('records')
            except:
                # If there's an error reading the cache, continue to fetch fresh data
                pass
    
    publications = []
    
    try:
        # Search PubMed
        search_handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        search_results = Entrez.read(search_handle)
        search_handle.close()
        
        id_list = search_results.get("IdList", [])
        
        if id_list:
            # Fetch details for found IDs
            fetch_handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
            articles = Entrez.read(fetch_handle)['PubmedArticle']
            fetch_handle.close()
            
            # Process each article
            for article in articles:
                # Extract article metadata
                article_data = article['MedlineCitation']
                article_id = article_data['PMID']
                
                # Get basic article info
                article_info = article_data['Article']
                title = article_info.get('ArticleTitle', 'No title available')
                
                # Get authors
                author_list = []
                if 'AuthorList' in article_info:
                    for author in article_info['AuthorList']:
                        if 'LastName' in author and 'ForeName' in author:
                            author_list.append(f"{author['LastName']} {author['ForeName']}")
                        elif 'LastName' in author:
                            author_list.append(author['LastName'])
                        elif 'CollectiveName' in author:
                            author_list.append(author['CollectiveName'])
                
                # Get journal info
                journal = article_info.get('Journal', {})
                journal_title = journal.get('Title', 'Unknown Journal')
                
                # Get publication date
                pub_date = None
                if 'PubDate' in journal.get('JournalIssue', {}).get('PubDate', {}):
                    date_parts = journal['JournalIssue']['PubDate']
                    if 'Year' in date_parts:
                        pub_date = date_parts.get('Year', '')
                        if 'Month' in date_parts:
                            pub_date = f"{date_parts.get('Month', '')} {pub_date}"
                            if 'Day' in date_parts:
                                pub_date = f"{date_parts.get('Day', '')} {pub_date}"
                
                # Get abstract
                abstract = "No abstract available"
                if 'Abstract' in article_info and 'AbstractText' in article_info['Abstract']:
                    abstract_parts = article_info['Abstract']['AbstractText']
                    if isinstance(abstract_parts, list):
                        abstract = " ".join([str(part) for part in abstract_parts])
                    else:
                        abstract = str(abstract_parts)
                
                # Create publication entry
                pub_entry = {
                    "pmid": str(article_id),
                    "title": title,
                    "authors": ", ".join(author_list[:3]) + ("..." if len(author_list) > 3 else ""),
                    "all_authors": author_list,
                    "journal": journal_title,
                    "pub_date": pub_date,
                    "abstract": abstract,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/"
                }
                
                publications.append(pub_entry)
        
        # Save to cache
        pd.DataFrame(publications).to_json(cache_file)
        
        return publications
    
    except HTTPError as e:
        print(f"HTTP Error with PubMed API: {e}")
    except Exception as e:
        print(f"Error fetching PubMed data: {e}")
    
    # If there was an error but we have cached data, use it regardless of age
    if os.path.exists(cache_file):
        try:
            return pd.read_json(cache_file).to_dict('records')
        except:
            pass
    
    return []
