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
    
    # Add custom CSS for overall layout and components
    st.markdown("""
        <style>
        /* Main layout */
        .main {
            padding: 1rem;
        }
        
        /* Card styling */
        .metric-card {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #f0f2f5;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            color: #111827;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        /* Pipeline card styling */
        .pipeline-card {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #f0f2f5;
            transition: all 0.2s ease;
        }
        
        .pipeline-card:hover {
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transform: translateY(-2px);
        }
        
        /* Phase header styling */
        .phase-header {
            background-color: #f8fafc;
            border-radius: 6px;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            font-weight: 600;
            color: #334155;
            border: 1px solid #e2e8f0;
        }
        
        /* Timeline styling */
        .timeline-container {
            padding: 1rem;
            background-color: white;
            border-radius: 8px;
            border: 1px solid #f0f2f5;
        }
        
        .timeline-card {
            border-left: 3px solid #3498db;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            position: relative;
            background-color: #f8fafc;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .timeline-card::before {
            content: '';
            width: 12px;
            height: 12px;
            background: #3498db;
            position: absolute;
            left: -7px;
            top: 1.5rem;
            border-radius: 50%;
            border: 2px solid white;
        }
        
        /* Tag styling */
        .status-tag {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-right: 0.5rem;
        }
        
        /* Table styling */
        .styled-table {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Button styling */
        .download-button {
            background-color: #3498db;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .download-button:hover {
            background-color: #2980b9;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Overview metrics with improved styling
    if selected_companies:
        st.markdown(f"<h2 style='color: #1e293b; margin-bottom: 1.5rem;'>Pipeline Overview: {', '.join(selected_companies)}</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color: #1e293b; margin-bottom: 1.5rem;'>Industry Pipeline Overview</h2>", unsafe_allow_html=True)
    
    # Create metrics columns with improved styling
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_data = [
        {"label": "Total Pipeline Assets", "value": len(pipeline_data) if not pipeline_data.empty else 0},
        {"label": "Late-Stage Assets", "value": len(pipeline_data[pipeline_data['phase'].isin(['Phase 3', 'Phase 2/3'])]) if not pipeline_data.empty else 0},
        {"label": "Early-Stage Assets", "value": len(pipeline_data[pipeline_data['phase'].isin(['Preclinical', 'Phase 1', 'Phase 1/2'])]) if not pipeline_data.empty else 0},
        {"label": "Approved Drugs", "value": len(pipeline_data[pipeline_data['phase'] == 'Approved']) if not pipeline_data.empty else 0}
    ]
    
    for col, metric in zip([col1, col2, col3, col4], metrics_data):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{metric['label']}</div>
                    <div class="metric-value">{metric['value']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Company comparison chart
    st.subheader("Pipeline Comparison")
    
    if not pipeline_data.empty and len(pipeline_data['company'].unique()) > 1:
        company_chart = create_company_comparison_chart(pipeline_data)
        st.plotly_chart(company_chart, use_container_width=True, key="pipeline_company_chart")
    else:
        st.info("Select multiple companies to view comparison chart.")
    
    # Update the pipeline stages visualization
    st.markdown("<h2 style='color: #1e293b; margin: 2rem 0 1rem;'>Development Pipeline by Stage</h2>", unsafe_allow_html=True)
    
    if not pipeline_data.empty:
        for phase in phases:
            st.markdown(f"""
                <div class="phase-header">
                    {phase}
                </div>
            """, unsafe_allow_html=True)
            
            phase_drugs = pipeline_data[pipeline_data['phase'] == phase].drop_duplicates(subset=['drug_name', 'company'])
            
            if not phase_drugs.empty:
                for _, drug in phase_drugs.iterrows():
                    area = drug.get('therapeutic_area', 'Other')
                    area_colors = {
                        'Oncology': '#ef4444',
                        'Neurology': '#3b82f6',
                        'Cardiovascular': '#22c55e',
                        'Immunology': '#a855f7',
                        'Infectious Disease': '#f97316',
                        'Metabolic': '#14b8a6',
                        'Respiratory': '#92400e',
                        'Other': '#64748b'
                    }
                    color = area_colors.get(area, '#64748b')
                    
                    source = drug.get('source', 'Unknown')
                    source_icon = {
                        'Database': '🗃️',
                        'ClinicalTrials.gov': '🔬',
                        'FDA': '✅',
                        'Unknown': '❓'
                    }.get(source, '❓')
                    
                    status = drug.get('status', 'Unknown')
                    status_colors = {
                        'Marketed': '#22c55e',
                        'Recruiting': '#3b82f6',
                        'Active, not recruiting': '#f97316',
                        'Post-marketing surveillance': '#22c55e',
                        'Post-approval study': '#22c55e',
                        'Not yet recruiting': '#64748b',
                        'IND-enabling studies': '#64748b',
                        'Lead optimization': '#64748b',
                    }
                    status_color = status_colors.get(status, '#64748b')
                    
                    st.markdown(f"""
                        <div class="pipeline-card" style="border-left: 4px solid {color}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">
                                    {drug['drug_name']} {source_icon}
                                </div>
                                <div class="status-tag" style="background-color: {status_color}; color: white;">
                                    {status}
                                </div>
                            </div>
                            <div style="color: #475569; margin-top: 0.5rem;">
                                {drug['company']}
                            </div>
                            <div style="color: #64748b; margin-top: 0.5rem; font-size: 0.875rem;">
                                {drug['condition']}
                            </div>
                            <div style="margin-top: 0.75rem; display: flex; align-items: center; gap: 1rem;">
                                <a href="{drug['url']}" target="_blank" style="color: #3b82f6; text-decoration: none; font-size: 0.875rem; font-weight: 500;">
                                    View Details →
                                </a>
                                <span style="color: #94a3b8; font-size: 0.875rem;">
                                    Source: {source}
                                </span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: #64748b; font-style: italic; padding: 1rem;">No drugs in this phase</div>', unsafe_allow_html=True)
    else:
        st.info("No pipeline data available for the selected filters.")
    
    # Update the detailed pipeline table styling
    st.markdown("<h2 style='color: #1e293b; margin: 2rem 0 1rem;'>Detailed Pipeline Data</h2>", unsafe_allow_html=True)
    
    if not pipeline_data.empty:
        # Add download button with improved styling
        csv = pipeline_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "↓ Download Pipeline Data",
            csv,
            "pipeline_data.csv",
            "text/csv",
            key='download-pipeline-csv',
            help="Download the complete pipeline data as CSV",
            use_container_width=False
        )
        
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        
        # Add some conditional formatting
        def highlight_phase(val):
            colors = {
                'Preclinical': '#f8f9fa',
                'Phase 1': '#e3f2fd',
                'Phase 1/2': '#bbdefb',
                'Phase 2': '#90caf9',
                'Phase 2/3': '#64b5f6',
                'Phase 3': '#42a5f5',
                'Phase 4': '#2196f3',
                'Approved': '#1976d2'
            }
            return f"background-color: {colors.get(val, '#ffffff')}"
        
        # Remove duplicates based on drug_name and company
        unique_pipeline_data = pipeline_data.drop_duplicates(subset=['drug_name', 'company'])
        
        # Display sortable, filterable table without serial numbers
        display_cols = ['drug_name', 'company', 'phase', 'condition', 'therapeutic_area', 'status', 'last_updated', 'source']
        display_df = unique_pipeline_data[display_cols].copy()
        
        try:
            styled_df = display_df.style.applymap(highlight_phase, subset=['phase'])
            st.markdown('<div class="styled-table">', unsafe_allow_html=True)
            st.dataframe(
                styled_df,
                height=400,
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning("Could not apply styling to the table. Displaying without styling.")
            st.dataframe(
                display_df,
                height=400,
                use_container_width=True
            )
    else:
        st.info("No pipeline data available for the selected filters.")
    
    # Recent pipeline updates
    st.subheader("Recent Pipeline Updates")
    
    if not pipeline_data.empty:
        # Sort by last updated
        recent_updates = pipeline_data.sort_values('last_updated', ascending=False).head(10)
        
        # Custom CSS for timeline
        st.markdown("""
            <style>
            .timeline-card {
                border-left: 2px solid #3498db;
                padding: 10px 20px;
                margin: 20px 0;
                position: relative;
                background-color: #f8f9fa;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .timeline-card::before {
                content: '';
                width: 12px;
                height: 12px;
                background: #3498db;
                position: absolute;
                left: -7px;
                top: 20px;
                border-radius: 50%;
            }
            .update-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            .update-title {
                font-size: 1.1em;
                font-weight: bold;
                color: #2c3e50;
            }
            .update-date {
                font-size: 0.9em;
                color: #7f8c8d;
            }
            .update-details {
                margin-top: 10px;
                font-size: 0.95em;
            }
            .update-tag {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.85em;
                margin-right: 8px;
                margin-bottom: 4px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        for _, update in recent_updates.iterrows():
            source = update.get('source', 'Unknown')
            source_icon = {
                'Database': '🗃️',
                'ClinicalTrials.gov': '🔬',
                'FDA': '✅',
                'Unknown': '❓'
            }.get(source, '❓')
            
            # Define status color
            status_colors = {
                'Marketed': '#2ecc71',
                'Recruiting': '#3498db',
                'Active, not recruiting': '#f39c12',
                'Post-marketing surveillance': '#2ecc71',
                'Post-approval study': '#2ecc71',
                'Not yet recruiting': '#95a5a6',
                'IND-enabling studies': '#95a5a6',
                'Lead optimization': '#95a5a6',
            }
            status_color = status_colors.get(update['status'], '#95a5a6')
            
            # Define phase color
            phase_colors = {
                'Preclinical': '#f8f9fa',
                'Phase 1': '#e3f2fd',
                'Phase 1/2': '#bbdefb',
                'Phase 2': '#90caf9',
                'Phase 2/3': '#64b5f6',
                'Phase 3': '#42a5f5',
                'Phase 4': '#2196f3',
                'Approved': '#1976d2'
            }
            phase_color = phase_colors.get(update['phase'], '#ffffff')
            
            st.markdown(f"""
                <div class="timeline-card">
                    <div class="update-header">
                        <span class="update-title">{update['drug_name']} {source_icon}</span>
                        <span class="update-date">{update['last_updated']}</span>
                    </div>
                    <div style="color: #34495e; font-weight: 500;">{update['company']}</div>
                    <div class="update-details">
                        <span class="update-tag" style="background-color: {phase_color}; color: #000000;">{update['phase']}</span>
                        <span class="update-tag" style="background-color: {status_color}; color: white;">{update['status']}</span>
                        <div style="margin-top: 8px;">
                            <strong>Indication:</strong> {update['condition']}
                        </div>
                        <div style="margin-top: 4px;">
                            <strong>Source:</strong> {source}
                            <a href="{update['url']}" target="_blank" style="margin-left: 10px; color: #3498db; text-decoration: none;">View Details →</a>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent pipeline updates available.")
