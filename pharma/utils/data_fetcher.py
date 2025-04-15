"""
Data fetching utilities for the PharmaIntelScan application.
Handles API calls to clinicaltrials.gov, FDA, and other data sources.
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure requests session
session = requests.Session()

def fetch_clinical_trials(company_name=None, days_back=30):
    """Fetch clinical trials data from clinicaltrials.gov"""
    try:
        base_url = "https://clinicaltrials.gov/api/query/study_fields"
        fields = [
            "NCTId", "BriefTitle", "Condition", "InterventionName",
            "SponsorName", "LeadSponsorName", "Phase", "StudyType",
            "OverallStatus", "LastUpdatePostDate", "EnrollmentCount"
        ]
        
        # Build query
        if company_name:
            query = f'"{company_name}"[Sponsor]'
        else:
            date_str = (datetime.now() - timedelta(days=days_back)).strftime("%m/%d/%Y")
            query = f'AREA[LastUpdatePostDate] RANGE[{date_str}, MAX]'
        
        params = {
            "fmt": "json",
            "max_rank": 50,
            "term": query,
            "fields": ",".join(fields)
        }
        
        response = session.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if 'StudyFieldsResponse' in data and 'StudyFields' in data['StudyFieldsResponse']:
            studies = data['StudyFieldsResponse']['StudyFields']
            return pd.DataFrame(studies)
        return pd.DataFrame()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching clinical trials data: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error fetching clinical trials: {e}")
        return pd.DataFrame()

def fetch_fda_data(days_back=30):
    """Fetch FDA drug approval data"""
    try:
        base_url = "https://api.fda.gov/drug/drugsfda.json"
        date_str = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
        
        params = {
            "limit": 50,
            "search": f"effective_time:[{date_str} TO 99991231]"
        }
        
        response = session.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if 'results' in data:
            return pd.DataFrame(data['results'])
        return pd.DataFrame()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching FDA data: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error fetching FDA data: {e}")
        return pd.DataFrame()

def get_pipeline_data():
    """Get combined pipeline data from multiple sources"""
    try:
        # Try to get data from APIs first
        clinical_trials = fetch_clinical_trials()
        fda_data = fetch_fda_data()
        
        # If both API calls fail, use database as fallback
        if clinical_trials.empty and fda_data.empty:
            logger.info("Using database as fallback for pipeline data")
            from .database import get_db
            db = next(get_db())
            pipeline_data = pd.read_sql("SELECT * FROM drugs", db.bind)
            return pipeline_data
            
        # Combine and process data from APIs
        # Add your data processing logic here
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Error getting pipeline data: {e}")
        return pd.DataFrame() 