"""
Clinical trials data collection module for the pharma CI platform.
Fetches and processes data from ClinicalTrials.gov.
"""
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import time
from datetime import datetime, timedelta
import os
import hashlib

# Cache directory
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_cache_key(params):
    """Generate a cache key from the parameters"""
    param_str = str(sorted(params.items()))
    return hashlib.md5(param_str.encode()).hexdigest()

def get_clinical_trials_data(company_names=None, drug_names=None, max_results=50, refresh=False):
    """
    Fetch clinical trial data from ClinicalTrials.gov API.
    
    Args:
        company_names (list): List of company names to filter by
        drug_names (list): List of drug names to filter by
        max_results (int): Maximum number of results to return
        refresh (bool): Whether to refresh the cache
        
    Returns:
        list: List of dictionaries containing clinical trial data
    """
    # Build query parameters
    params = {"fmt": "json", "max_rank": max_results}
    
    query_parts = []
    if company_names:
        company_query = " OR ".join([f'"{company}"[Sponsor]' for company in company_names])
        query_parts.append(f"({company_query})")
    
    if drug_names:
        drug_query = " OR ".join([f'"{drug}"[Intervention]' for drug in drug_names])
        query_parts.append(f"({drug_query})")
    
    # If no specific filters, get recent studies
    if not query_parts:
        # Get studies updated in the last 90 days
        ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%m/%d/%Y')
        query_parts.append(f"AREA[LastUpdatePostDate] RANGE[{ninety_days_ago}, MAX]")
    
    # Combine query parts with AND
    if query_parts:
        params["term"] = " AND ".join(query_parts)
    
    # Generate cache key from params
    cache_key = generate_cache_key(params)
    cache_file = os.path.join(CACHE_DIR, f"ct_{cache_key}.json")
    
    # Check if cached data exists and is fresh (less than 12 hours old)
    if not refresh and os.path.exists(cache_file):
        file_time = os.path.getmtime(cache_file)
        if (time.time() - file_time) < 43200:  # 12 hours in seconds
            try:
                return pd.read_json(cache_file).to_dict('records')
            except:
                # If there's an error reading the cache, continue to fetch fresh data
                pass
    
    # Fetch data from ClinicalTrials.gov API
    base_url = "https://classic.clinicaltrials.gov/api/query/study_fields"
    
    # Specify fields to retrieve
    fields = [
        "NCTId", "BriefTitle", "Condition", "InterventionName", 
        "SponsorName", "LeadSponsorName", "Phase", "StudyType",
        "OverallStatus", "LastUpdatePostDate", "EnrollmentCount"
    ]
    
    params["fields"] = ",".join(fields)
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process the response
        studies = []
        if "StudyFieldsResponse" in data and "StudyFields" in data["StudyFieldsResponse"]:
            for study in data["StudyFieldsResponse"]["StudyFields"]:
                # Extract relevant fields from the study
                study_data = {
                    "nct_id": study.get("NCTId", [""])[0],
                    "title": study.get("BriefTitle", [""])[0],
                    "condition": ", ".join(study.get("Condition", [])),
                    "intervention": ", ".join(study.get("InterventionName", [])),
                    "sponsor": study.get("LeadSponsorName", [""])[0],
                    "phase": ", ".join(study.get("Phase", [])),
                    "status": study.get("OverallStatus", [""])[0],
                    "last_updated": study.get("LastUpdatePostDate", [""])[0],
                    "enrollment": study.get("EnrollmentCount", [""])[0],
                    "url": f"https://clinicaltrials.gov/study/{study.get('NCTId', [''])[0]}"
                }
                studies.append(study_data)
        
        # Save to cache
        pd.DataFrame(studies).to_json(cache_file)
        
        return studies
    
    except Exception as e:
        print(f"Error fetching clinical trials data: {e}")
        # If there was an error but we have cached data, use it regardless of age
        if os.path.exists(cache_file):
            try:
                return pd.read_json(cache_file).to_dict('records')
            except:
                pass
        
        return []
