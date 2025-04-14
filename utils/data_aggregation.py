"""
Data aggregation module for the pharma CI platform.
Coordinates data collection from various sources.
"""
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from utils.clinical_trials import get_clinical_trials_data
from utils.pubmed import get_pubmed_data
from utils.fda import get_fda_data
from utils.database import get_db, Company, Drug, Publication, NewsArticle

def aggregate_data(company_names=None, drug_names=None, max_results=50, refresh=False):
    """
    Aggregate data from all sources.
    
    Args:
        company_names (list): List of company names to filter by
        drug_names (list): List of drug names to filter by
        max_results (int): Maximum number of results to return per source
        refresh (bool): Whether to force refresh cached data
        
    Returns:
        dict: Dictionary containing aggregated data from all sources
    """
    # Using ThreadPoolExecutor to fetch data from multiple sources concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Start fetching data from all sources
        clinical_trials_future = executor.submit(
            get_clinical_trials_data, 
            company_names=company_names, 
            drug_names=drug_names, 
            max_results=max_results,
            refresh=refresh
        )
        
        pubmed_future = executor.submit(
            get_pubmed_data, 
            company_names=company_names, 
            drug_names=drug_names, 
            max_results=max_results,
            refresh=refresh
        )
        
        fda_future = executor.submit(
            get_fda_data, 
            company_names=company_names, 
            drug_names=drug_names, 
            max_results=max_results,
            refresh=refresh
        )
        
        # Collect results as they complete
        clinical_trials_data = clinical_trials_future.result()
        pubmed_data = pubmed_future.result()
        fda_data = fda_future.result()
    
    # Combine the data into a single structure
    aggregated_data = {
        "clinical_trials": clinical_trials_data,
        "pubmed": pubmed_data,
        "fda": fda_data,
    }
    
    return aggregated_data

def get_pipeline_data(company_names=None, refresh=False):
    """
    Get pipeline data from database and external sources.
    
    Args:
        company_names (list): List of company names to filter by
        refresh (bool): Whether to force refresh cached data
        
    Returns:
        pd.DataFrame: DataFrame containing pipeline data
    """
    try:
        # Get data from database
        db = next(get_db())
        
        # Base query
        query = db.query(Drug)
        
        # Apply company filter if provided
        if company_names:
            query = query.join(Company).filter(Company.name.in_(company_names))
        
        # Execute query and convert to DataFrame
        drugs = query.all()
        pipeline_data = pd.DataFrame([{
            'name': drug.name,
            'company': drug.company.name if drug.company else None,
            'phase': drug.phase,
            'condition': drug.condition,
            'therapeutic_area': drug.therapeutic_area,
            'status': drug.status,
            'last_updated': drug.last_updated
        } for drug in drugs])
        
        # Standardize phase values
        if not pipeline_data.empty and 'phase' in pipeline_data.columns:
            phase_mapping = {
                'preclinical': 'Preclinical',
                'phase 1': 'Phase 1',
                'phase 2': 'Phase 2',
                'phase 3': 'Phase 3',
                'approved': 'Approved',
                'phase 2/3': 'Phase 2/3',
                'phase 1/2': 'Phase 1/2'
            }
            
            # Convert to lowercase and map phases
            pipeline_data['phase'] = pipeline_data['phase'].astype(str).str.lower().str.strip()
            pipeline_data['phase'] = pipeline_data['phase'].map(phase_mapping).fillna('Other')
            
            # Ensure all expected phases are present
            expected_phases = ['Preclinical', 'Phase 1', 'Phase 2', 'Phase 3', 'Approved']
            for phase in expected_phases:
                if phase not in pipeline_data['phase'].unique():
                    # Add a row with zero count for missing phases
                    pipeline_data = pd.concat([
                        pipeline_data,
                        pd.DataFrame([{
                            'name': f'placeholder_{phase}',
                            'company': 'System',
                            'phase': phase,
                            'condition': 'N/A',
                            'therapeutic_area': 'N/A',
                            'status': 'N/A',
                            'last_updated': pd.Timestamp.now()
                        }])
                    ])
        
        return pipeline_data
        
    except Exception as e:
        print(f"Error getting pipeline data: {e}")
        return pd.DataFrame()
