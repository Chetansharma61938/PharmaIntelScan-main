"""
Competitor pipeline component for the pharma CI platform.
Renders the pipeline tracking view with development stages visualization.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.data_aggregation import get_pipeline_data
from utils.visualization import create_company_comparison_chart

def render_competitor_pipeline():
    """Render the competitor pipeline tracking page"""
    st.title("Competitor Pipeline Tracker")
    
    # Add sidebar filters
    with st.sidebar:
        st.subheader("Pipeline Filters")
        
        # Company filter
        major_pharma = ["Pfizer", "Novartis", "Roche", "Merck", "AstraZeneca", 
                        "Johnson & Johnson", "Sanofi", "GlaxoSmithKline", "Gilead", 
                        "Bristol Myers Squibb", "Amgen", "AbbVie", "Eli Lilly"]
        
        selected_companies = st.multiselect(
            "Filter by Companies:",
            options=major_pharma,
            default=major_pharma[:3]  # Default to first 3 companies
        )
        
        # Phase filter
        phases = ['Preclinical', 'Phase 1', 'Phase 1/2', 'Phase 2', 'Phase 2/3', 'Phase 3', 'Phase 4', 'Approved']
        selected_phases = st.multiselect(
            "Filter by Phase:",
            options=phases,
            default=phases
        )
        
        # Therapeutic area filter
        areas = ['Oncology', 'Immunology', 'Neurology', 'Cardiovascular', 
                 'Infectious Disease', 'Metabolic', 'Respiratory', 'Other']
        
        selected_areas = st.multiselect(
            "Filter by Therapeutic Area:",
            options=areas,
            default=[]
        )
        
        # Refresh data option
        refresh_data = st.button("Refresh Pipeline Data")
    
    # Show loading spinner while data is being fetched
    with st.spinner("Loading pipeline data..."):
        # Get pipeline data
        pipeline_data = get_pipeline_data(
            company_names=selected_companies if selected_companies else None,
            refresh=refresh_data
        )
        
        # Clean and filter pipeline data
        if not pipeline_data.empty:
            # Add therapeutic area category
            def categorize_condition(condition):
                condition = str(condition).lower()
                keywords = {
                    'Oncology': ['cancer', 'oncology', 'tumor', 'neoplasm', 'carcinoma', 'leukemia', 'melanoma'],
                    'Neurology': ['brain', 'neural', 'alzheimer', 'parkinson', 'epilepsy', 'seizure', 'neurology'],
                    'Cardiovascular': ['heart', 'cardio', 'vascular', 'hypertension', 'stroke', 'artery'],
                    'Immunology': ['immune', 'antibody', 'rheumatoid', 'autoimmune', 'psoriasis', 'arthritis'],
                    'Infectious Disease': ['infection', 'bacterial', 'viral', 'antibacterial', 'antiviral', 'vaccine'],
                    'Metabolic': ['diabetes', 'metabolic', 'obesity', 'lipid', 'cholesterol'],
                    'Respiratory': ['respiratory', 'asthma', 'pulmonary', 'lung', 'copd', 'bronchitis'],
                }
                
                for area, terms in keywords.items():
                    if any(term in condition for term in terms):
                        return area
                return 'Other'
            
            pipeline_data['therapeutic_area'] = pipeline_data['condition'].apply(categorize_condition)
            
            # Apply filters
            if selected_phases:
                pipeline_data = pipeline_data[pipeline_data['phase'].isin(selected_phases)]
            
            if selected_areas:
                pipeline_data = pipeline_data[pipeline_data['therapeutic_area'].isin(selected_areas)]
    
    # Overview metrics
    if selected_companies:
        st.subheader(f"Pipeline Overview: {', '.join(selected_companies)}")
    else:
        st.subheader("Industry Pipeline Overview")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total drugs in pipeline
        drug_count = len(pipeline_data) if not pipeline_data.empty else 0
        st.metric("Total Pipeline Assets", drug_count)
    
    with col2:
        # Count of late-stage (Phase 3) drugs
        if not pipeline_data.empty:
            late_stage_count = len(pipeline_data[pipeline_data['phase'].isin(['Phase 3', 'Phase 2/3'])])
        else:
            late_stage_count = 0
        st.metric("Late-Stage Assets", late_stage_count)
    
    with col3:
        # Count of early-stage drugs
        if not pipeline_data.empty:
            early_stage_count = len(pipeline_data[pipeline_data['phase'].isin(['Preclinical', 'Phase 1', 'Phase 1/2'])])
        else:
            early_stage_count = 0
        st.metric("Early-Stage Assets", early_stage_count)
    
    with col4:
        # Count of approved drugs
        if not pipeline_data.empty:
            approved_count = len(pipeline_data[pipeline_data['phase'] == 'Approved'])
        else:
            approved_count = 0
        st.metric("Approved Drugs", approved_count)
    
    # Company comparison chart
    st.subheader("Pipeline Comparison")
    
    if not pipeline_data.empty and len(pipeline_data['company'].unique()) > 1:
        company_chart = create_company_comparison_chart(pipeline_data)
        st.plotly_chart(company_chart, use_container_width=True, key="pipeline_company_chart")
    else:
        st.info("Select multiple companies to view comparison chart.")
    
    # Pipeline stages visualization
    st.subheader("Development Pipeline by Stage")
    
    if not pipeline_data.empty:
        # Create pipeline stage columns
        stage_cols = st.columns(len(phases))
        
        # Display drugs by development stage
        for i, phase in enumerate(phases):
            with stage_cols[i]:
                st.markdown(f"**{phase}**")
                phase_drugs = pipeline_data[pipeline_data['phase'] == phase]
                
                if not phase_drugs.empty:
                    for _, drug in phase_drugs.iterrows():
                        # Color based on therapeutic area
                        area_colors = {
                            'Oncology': 'red',
                            'Neurology': 'blue',
                            'Cardiovascular': 'green',
                            'Immunology': 'purple',
                            'Infectious Disease': 'orange',
                            'Metabolic': 'teal',
                            'Respiratory': 'brown',
                            'Other': 'gray'
                        }
                        
                        area = drug.get('therapeutic_area', 'Other')
                        color = area_colors.get(area, 'gray')
                        
                        # Display drug card
                        # Get data source and display icon
                        source = drug.get('source', 'Unknown')
                        source_icon = {
                            'Database': '🗃️',
                            'ClinicalTrials.gov': '🔬',
                            'FDA': '✅',
                            'Unknown': '❓'
                        }.get(source, '❓')
                        
                        # Format condition text properly without arbitrary cutoff
                        condition = drug['condition']
                        if len(condition) > 60:
                            condition_display = f"{condition[:60]}..."
                        else:
                            condition_display = condition
                            
                        # Add status badge with appropriate color
                        status = drug.get('status', 'Unknown')
                        status_colors = {
                            'Marketed': '#2ecc71',  # Green
                            'Recruiting': '#3498db',  # Blue
                            'Active, not recruiting': '#f39c12',  # Orange
                            'Post-marketing surveillance': '#2ecc71',  # Green
                            'Post-approval study': '#2ecc71',  # Green
                            'Not yet recruiting': '#95a5a6',  # Gray
                            'IND-enabling studies': '#95a5a6',  # Gray
                            'Lead optimization': '#95a5a6',  # Gray
                        }
                        status_color = status_colors.get(status, '#95a5a6')  # Default gray
                        
                        st.markdown(
                            f"""
                            <div style="border-left: 4px solid {color}; border-radius: 4px; padding: 10px; margin-bottom: 12px; background-color: rgba(240,240,240,0.3);">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div><b>{drug['drug_name']}</b> {source_icon}</div>
                                    <div><span style="background-color: {status_color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7em;">{status}</span></div>
                                </div>
                                <div style="font-size: 0.9em; color: #444; margin-top: 5px;">{drug['company']}</div>
                                <div style="font-size: 0.85em; margin-top: 3px; color: #666;" title="{condition}">{condition_display}</div>
                                <div style="margin-top: 5px; font-size: 0.8em;">
                                    <a href="{drug['url']}" target="_blank" style="text-decoration: none; color: #2980b9;">Details</a> 
                                    <span style="color: #7f8c8d;">•</span> 
                                    <span style="color: #7f8c8d;">Source: {source}</span>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown("*No drugs in this phase*")
    else:
        st.info("No pipeline data available for the selected filters.")
    
    # Detailed pipeline table
    st.subheader("Detailed Pipeline Data")
    
    if not pipeline_data.empty:
        # Add some conditional formatting
        def highlight_phase(val):
            colors = {
                'Preclinical': 'background-color: #f8f9fa',
                'Phase 1': 'background-color: #e3f2fd',
                'Phase 1/2': 'background-color: #bbdefb',
                'Phase 2': 'background-color: #90caf9',
                'Phase 2/3': 'background-color: #64b5f6',
                'Phase 3': 'background-color: #42a5f5',
                'Phase 4': 'background-color: #2196f3',
                'Approved': 'background-color: #1976d2; color: white'
            }
            return colors.get(val, '')
        
        # Display sortable, filterable table
        display_cols = ['drug_name', 'company', 'phase', 'condition', 'therapeutic_area', 'status', 'last_updated', 'source']
        st.dataframe(
            pipeline_data[display_cols].style.map(
                highlight_phase, subset=['phase']
            ),
            height=400,
            use_container_width=True
        )
        
        # Add download button
        csv = pipeline_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Pipeline Data",
            csv,
            "pipeline_data.csv",
            "text/csv",
            key='download-pipeline-csv'
        )
    else:
        st.info("No pipeline data available for the selected filters.")
    
    # Recent pipeline updates
    st.subheader("Recent Pipeline Updates")
    
    if not pipeline_data.empty:
        # Sort by last updated
        recent_updates = pipeline_data.sort_values('last_updated', ascending=False).head(10)
        
        for _, update in recent_updates.iterrows():
            source = update.get('source', 'Unknown')
            source_icon = {
                'Database': '🗃️',
                'ClinicalTrials.gov': '🔬',
                'FDA': '✅',
                'Unknown': '❓'
            }.get(source, '❓')
            
            with st.expander(f"{update['drug_name']} - {update['company']} {source_icon}"):
                st.write(f"**Phase:** {update['phase']}")
                st.write(f"**Indication:** {update['condition']}")
                st.write(f"**Status:** {update['status']}")
                st.write(f"**Last Updated:** {update['last_updated']}")
                st.write(f"**Source:** {source}")
                st.write(f"[View Details]({update['url']})")
    else:
        st.info("No recent pipeline updates available.")
