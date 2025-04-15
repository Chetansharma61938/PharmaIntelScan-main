"""
FDA data collection module for the pharma CI platform.
Fetches and processes data from the FDA API.
"""
import requests
import pandas as pd
import time
import os
import hashlib
from datetime import datetime, timedelta

# Cache directory
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_cache_key(params):
    """Generate a cache key from the parameters"""
    param_str = str(sorted(params.items()))
    return hashlib.md5(param_str.encode()).hexdigest()

def get_fda_data(company_names=None, drug_names=None, max_results=50, refresh=False):
    """
    Fetch drug approval data from the FDA's openFDA API.
    
    Args:
        company_names (list): List of company names to filter by
        drug_names (list): List of drug names to filter by
        max_results (int): Maximum number of results to return
        refresh (bool): Whether to refresh the cache
        
    Returns:
        list: List of dictionaries containing FDA approval data
    """
    # Build query parameters
    params = {"limit": max_results}
    search_terms = []
    
    if company_names:
        company_terms = " OR ".join([f'openfda.manufacturer_name:"{company}"' for company in company_names])
        search_terms.append(f"({company_terms})")
    
    if drug_names:
        drug_terms = " OR ".join([f'openfda.brand_name:"{drug}" OR openfda.generic_name:"{drug}"' for drug in drug_names])
        search_terms.append(f"({drug_terms})")
    
    # If no specific filters, get recent approvals
    if not search_terms:
        # Get approvals from the last 365 days
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        search_terms.append(f"effective_time:[{one_year_ago} TO 99991231]")
    
    # Combine search terms
    if search_terms:
        params["search"] = " AND ".join(search_terms)
    
    # Generate cache key
    cache_key = generate_cache_key(params)
    cache_file = os.path.join(CACHE_DIR, f"fda_{cache_key}.json")
    
    # Check if cached data exists and is fresh (less than 12 hours old)
    if not refresh and os.path.exists(cache_file):
        file_time = os.path.getmtime(cache_file)
        if (time.time() - file_time) < 43200:  # 12 hours in seconds
            try:
                return pd.read_json(cache_file).to_dict('records')
            except:
                # If there's an error reading the cache, continue to fetch fresh data
                pass
    
    approvals = []
    
    try:
        # FDA drug approvals API endpoint
        base_url = "https://api.fda.gov/drugs/drugsfda.json"
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process results
        if 'results' in data:
            for result in data['results']:
                # Get the most recent approval
                products = result.get('products', [])
                
                for product in products:
                    # Basic information
                    drug_name = product.get('brand_name', 'Unknown')
                    
                    # Get manufacturer name
                    company = "Unknown"
                    if 'openfda' in result and 'manufacturer_name' in result['openfda']:
                        companies = result['openfda']['manufacturer_name']
                        company = companies[0] if companies else "Unknown"
                    
                    # Get approval info
                    approval_date = "Unknown"
                    indication = "Unknown"
                    
                    # Try to find the most recent approval
                    if 'submissions' in result:
                        for submission in sorted(result['submissions'], 
                                                key=lambda x: x.get('submission_status_date', ''), 
                                                reverse=True):
                            if submission.get('submission_status') == 'AP':  # AP = Approved
                                approval_date = submission.get('submission_status_date', 'Unknown')
                                
                                # Find indication (therapeutic use)
                                if 'indications_and_usage' in result.get('openfda', {}):
                                    indications = result['openfda']['indications_and_usage']
                                    indication = indications[0] if indications else "Unknown"
                                
                                break
                    
                    # Create approval entry
                    approval_entry = {
                        "drug_name": drug_name,
                        "company": company,
                        "approval_date": approval_date,
                        "indication": indication,
                        "application_number": result.get('application_number', 'Unknown'),
                        "url": f"https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo={result.get('application_number', '')}"
                    }
                    
                    approvals.append(approval_entry)
        
        # Save to cache
        pd.DataFrame(approvals).to_json(cache_file)
        
        return approvals
    
    except Exception as e:
        print(f"Error fetching FDA data: {e}")
        # If there was an error but we have cached data, use it regardless of age
        if os.path.exists(cache_file):
            try:
                return pd.read_json(cache_file).to_dict('records')
            except:
                pass
        
        return []
