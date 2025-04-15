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
    Get pipeline data for specified companies.
    
    Args:
        company_names (list): List of company names to filter by
        refresh (bool): Whether to force refresh cached data
        
    Returns:
        pd.DataFrame: DataFrame containing pipeline data
    """
    try:
        # Get data from all sources
        all_data = aggregate_data(company_names=company_names, refresh=refresh)
        
        # Process and combine the data
        pipeline_data = []
        
        # Process clinical trials data
        clinical_trials = all_data.get("clinical_trials", [])
        for trial in clinical_trials:
            if not trial:
                continue
                
            pipeline_entry = {
                "drug_name": trial.get("intervention", "Unknown"),
                "company": trial.get("sponsor", "Unknown"),
                "phase": trial.get("phase", "Unknown"),
                "condition": trial.get("condition", "Unknown"),
                "status": trial.get("status", "Unknown"),
                "last_updated": trial.get("last_updated", "Unknown"),
                "url": trial.get("url", ""),
                "source": "ClinicalTrials.gov"
            }
            pipeline_data.append(pipeline_entry)
        
        # Process FDA approval data
        for approval in all_data.get("fda", []):
            if not approval:
                continue
                
            pipeline_entry = {
                "drug_name": approval.get("drug_name", "Unknown"),
                "company": approval.get("company", "Unknown"),
                "phase": "Approved",  # FDA data is for approved drugs
                "condition": approval.get("indication", "Unknown"),
                "status": "Approved",
                "last_updated": approval.get("approval_date", "Unknown"),
                "url": approval.get("url", ""),
                "source": "FDA"
            }
            pipeline_data.append(pipeline_entry)
        
        # If no data from external APIs, use database as fallback
        if not pipeline_data:
            print("Using database as fallback for pipeline data")
            try:
                db = get_db()
                query = db.query(Drug).join(Company)
                
                if company_names:
                    query = query.filter(Company.name.in_(company_names))
                    
                drug_records = query.all()
                
                for drug in drug_records:
                    pipeline_entry = {
                        "drug_name": drug.name,
                        "company": drug.company.name,
                        "phase": drug.phase,
                        "condition": drug.condition,
                        "status": drug.status,
                        "last_updated": drug.last_updated.strftime('%Y-%m-%d') if drug.last_updated else "Unknown",
                        "url": drug.url or "#",
                        "source": "Database",
                        "therapeutic_area": drug.therapeutic_area
                    }
                    pipeline_data.append(pipeline_entry)
            except Exception as e:
                print(f"Error getting pipeline data from database: {e}")
            finally:
                if 'db' in locals():
                    db.close()
        
        # Convert to DataFrame (create empty one if no data)
        pipeline_df = pd.DataFrame(pipeline_data) if pipeline_data else pd.DataFrame(columns=[
            'drug_name', 'company', 'phase', 'condition', 'status', 
            'last_updated', 'url', 'source', 'therapeutic_area'
        ])
        
        # Clean up and standardize phases and add missing therapeutic areas
        if not pipeline_df.empty:
            # Add therapeutic area if missing
            if 'therapeutic_area' not in pipeline_df.columns:
                pipeline_df['therapeutic_area'] = 'Other'
            
            # Fill NaN values
            pipeline_df = pipeline_df.fillna({
                'therapeutic_area': 'Other',
                'phase': 'Unknown',
                'condition': 'Unknown',
                'status': 'Unknown',
                'last_updated': 'Unknown',
                'url': '#'
            })
            
            # Map phase text to standardized values
            phase_map = {
                "Preclinical": "Preclinical",
                "Phase 1": "Phase 1",
                "Phase 2": "Phase 2", 
                "Phase 3": "Phase 3",
                "Phase 4": "Phase 4",
                "Phase 1/Phase 2": "Phase 1/2",
                "Phase 2/Phase 3": "Phase 2/3",
                "Phase 1/2": "Phase 1/2",
                "Phase 2/3": "Phase 2/3",
                "Early Phase 1": "Phase 1",
                "N/A": "Preclinical",
                "Unknown": "Unknown",
                "Approved": "Approved"
            }
            
            # Apply phase mapping with default to "Unknown"
            pipeline_df['phase'] = pipeline_df['phase'].apply(
                lambda x: phase_map.get(str(x).strip(), "Unknown")
            )
        
        return pipeline_df
    
    except Exception as e:
        print(f"Error in get_pipeline_data: {e}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            'drug_name', 'company', 'phase', 'condition', 'status', 
            'last_updated', 'url', 'source', 'therapeutic_area'
        ])
