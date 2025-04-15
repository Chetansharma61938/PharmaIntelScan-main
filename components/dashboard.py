"""
Dashboard component for the pharma CI platform.
Renders the main dashboard view with multiple visualizations.
"""
import streamlit as st
import pandas as pd
from utils.data_aggregation import aggregate_data, get_pipeline_data
from utils.news_scraper import get_news_articles
from utils.visualization import (
    create_pipeline_phase_chart,
    create_company_comparison_chart,
    create_therapeutic_area_chart,
    create_sentiment_chart
)

def render_dashboard():
    """Render the main dashboard with overview panels and visualizations"""
    st.title("Pharmaceutical CI Dashboard")
    
    # Add sidebar filters
    with st.sidebar:
        st.subheader("Dashboard Filters")
        
        # Company filter
        major_pharma = ["Pfizer", "Novartis", "Roche", "Merck", "AstraZeneca", 
                        "Johnson & Johnson", "Sanofi", "GlaxoSmithKline", "Gilead", 
                        "Bristol Myers Squibb", "Amgen", "AbbVie", "Eli Lilly"]
        
        selected_companies = st.multiselect(
            "Filter by Companies:",
            options=major_pharma,
            default=[]
        )
        
        # Refresh data option
        refresh_data = st.button("Refresh Data")
    
    # Show loading spinner while data is being fetched
    with st.spinner("Loading dashboard data..."):
        # Get pipeline data
        pipeline_data = get_pipeline_data(
            company_names=selected_companies if selected_companies else None,
            refresh=refresh_data
        )
        
        # Get news data
        news_data = get_news_articles(
            company_names=selected_companies if selected_companies else None,
            max_results=10,
            refresh=refresh_data
        )
    
    # Overview metrics
    st.subheader("Industry Overview")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total drugs in pipeline
        drug_count = len(pipeline_data) if not pipeline_data.empty else 0
        st.metric("Drugs in Pipeline", drug_count)
    
    with col2:
        # Count of late-stage (Phase 3) drugs
        if not pipeline_data.empty:
            late_stage_count = len(pipeline_data[pipeline_data['phase'].isin(['Phase 3', 'Phase 2/3'])])
        else:
            late_stage_count = 0
        st.metric("Late-Stage Candidates", late_stage_count)
    
    with col3:
        # Count of approved drugs
        if not pipeline_data.empty:
            approved_count = len(pipeline_data[pipeline_data['phase'] == 'Approved'])
        else:
            approved_count = 0
        st.metric("Recent Approvals", approved_count)
    
    with col4:
        # News sentiment overview
        if news_data:
            positive_count = sum(1 for article in news_data if article.get('sentiment') == 'positive')
            sentiment_ratio = f"{positive_count}/{len(news_data)}"
            st.metric("Positive News Ratio", sentiment_ratio)
        else:
            st.metric("Positive News Ratio", "0/0")
    
    # Pipeline charts
    st.subheader("Pipeline Analysis")
    
    # Create chart columns
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Phase distribution chart
        phase_chart = create_pipeline_phase_chart(pipeline_data)
        st.plotly_chart(phase_chart, use_container_width=True, key="dashboard_phase_chart")
    
    with chart_col2:
        # Therapeutic area chart
        area_chart = create_therapeutic_area_chart(pipeline_data)
        st.plotly_chart(area_chart, use_container_width=True, key="dashboard_area_chart")
    
    # Company comparison
    st.subheader("Company Comparison")
    company_chart = create_company_comparison_chart(pipeline_data)
    st.plotly_chart(company_chart, use_container_width=True, key="dashboard_company_chart")
    
    # News and activity section
    st.subheader("Recent News & Activity")
    
    # News sentiment chart
    sentiment_chart = create_sentiment_chart(news_data)
    st.plotly_chart(sentiment_chart, use_container_width=True, key="dashboard_sentiment_chart")
    
    # Latest industry news
    st.subheader("Latest Industry News")
    
    if news_data:
        for article in news_data[:5]:
            with st.expander(f"{article['title']} ({article['source']})"):
                st.write(f"**Published:** {article.get('published_at', 'Unknown date')}")
                st.write(f"**Sentiment:** {article.get('sentiment', 'neutral').capitalize()}")
                st.write(f"**Summary:** {article.get('summary', 'No summary available')}")
                st.write(f"[Read full article]({article.get('url', '#')})")
    else:
        st.write("No news articles available at this time.")
