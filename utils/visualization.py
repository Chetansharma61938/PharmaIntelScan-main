"""
Visualization module for the pharma CI platform.
Creates charts and visualizations for the dashboard.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def create_pipeline_phase_chart(pipeline_data):
    """
    Create a bar chart showing drug count by development phase.

    Args:
        pipeline_data (pd.DataFrame): DataFrame with pipeline data

    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if pipeline_data.empty:
        return go.Figure()

    # Count drugs by phase
    phase_counts = pipeline_data['phase'].value_counts().reset_index()
    phase_counts.columns = ['Phase', 'Count']

    # Define phase order
    phase_order = ['Preclinical', 'Phase 1', 'Phase 1/2', 'Phase 2', 'Phase 2/3', 'Phase 3', 'Phase 4', 'Approved']

    # Filter and order phases
    phase_counts = phase_counts[phase_counts['Phase'].isin(phase_order)]
    phase_counts['Phase'] = pd.Categorical(phase_counts['Phase'], categories=phase_order, ordered=True)
    phase_counts = phase_counts.sort_values('Phase')

    # Create the figure
    fig = px.bar(
        phase_counts, 
        x='Phase', 
        y='Count',
        color='Phase',
        title='Drug Pipeline by Phase',
        labels={'Count': 'Number of Drugs', 'Phase': 'Development Phase'},
        color_discrete_sequence=px.colors.qualitative.G10
    )

    # Update layout
    fig.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': phase_order},
        hovermode='closest',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def create_company_comparison_chart(pipeline_data, top_n=5):
    """
    Create a stacked bar chart comparing top companies' pipelines.

    Args:
        pipeline_data (pd.DataFrame): DataFrame with pipeline data
        top_n (int): Number of top companies to display

    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if pipeline_data.empty:
        return go.Figure()

    # Get top companies by drug count
    top_companies = pipeline_data['company'].value_counts().nlargest(top_n).index.tolist()

    # Filter data for top companies
    company_data = pipeline_data[pipeline_data['company'].isin(top_companies)]

    # Count drugs by company and phase
    company_phase_counts = company_data.groupby(['company', 'phase']).size().reset_index(name='count')

    # Define phase order
    phase_order = ['Preclinical', 'Phase 1', 'Phase 1/2', 'Phase 2', 'Phase 2/3', 'Phase 3', 'Phase 4', 'Approved']

    # Create figure
    fig = px.bar(
        company_phase_counts,
        x='company',
        y='count',
        color='phase',
        title=f'Pipeline Comparison - Top {top_n} Companies',
        labels={'company': 'Company', 'count': 'Number of Drugs', 'phase': 'Phase'},
        category_orders={'phase': phase_order},
        color_discrete_sequence=px.colors.qualitative.Plotly
    )

    # Update layout
    fig.update_layout(
        xaxis_title='Company',
        yaxis_title='Number of Drugs',
        legend_title='Phase',
        height=500,
        margin=dict(l=20, r=20, t=40, b=100)
    )

    # Rotate x-axis labels if needed
    fig.update_xaxes(tickangle=45)

    return fig

def create_therapeutic_area_chart(pipeline_data):
    """
    Create a pie chart showing distribution of therapeutic areas.

    Args:
        pipeline_data (pd.DataFrame): DataFrame with pipeline data

    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if pipeline_data.empty:
        return go.Figure()

    # Clean and categorize conditions
    keywords = {
        'Oncology': ['cancer', 'oncology', 'tumor', 'neoplasm', 'carcinoma', 'leukemia', 'melanoma', 'lymphoma'],
        'Neurology': ['brain', 'neural', 'alzheimer', 'parkinson', 'epilepsy', 'seizure', 'neurology', 'cognitive'],
        'Cardiovascular': ['heart', 'cardio', 'vascular', 'hypertension', 'stroke', 'artery', 'thrombosis'],
        'Immunology': ['immune', 'antibody', 'rheumatoid', 'autoimmune', 'psoriasis', 'arthritis'],
        'Infectious Disease': ['infection', 'bacterial', 'viral', 'antibacterial', 'antiviral', 'vaccine'],
        'Metabolic': ['diabetes', 'metabolic', 'obesity', 'lipid', 'cholesterol'],
        'Respiratory': ['respiratory', 'asthma', 'pulmonary', 'lung', 'copd', 'bronchitis'],
    }

    def categorize_condition(condition):
        condition = str(condition).lower()
        for category, terms in keywords.items():
            if any(term in condition for term in terms):
                return category
        return 'Other'

    # Add therapeutic area category
    pipeline_data['therapeutic_area'] = pipeline_data['condition'].apply(categorize_condition)

    # Count by therapeutic area
    area_counts = pipeline_data['therapeutic_area'].value_counts().reset_index()
    area_counts.columns = ['Therapeutic Area', 'Count']

    # Create pie chart
    fig = px.pie(
        area_counts,
        values='Count',
        names='Therapeutic Area',
        title='Distribution by Therapeutic Area',
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )

    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    # Update traces
    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig

def create_sentiment_chart(news_data):
    """
    Create a donut chart showing sentiment distribution of news.

    Args:
        news_data (list): List of news article dictionaries

    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if not news_data:
        return go.Figure()

    # Count sentiment occurrences
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}

    for article in news_data:
        sentiment = article.get('sentiment', 'neutral')
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

    # Prepare data for chart
    labels = list(sentiment_counts.keys())
    values = list(sentiment_counts.values())

    # Color mapping
    colors = {'positive': '#2ECC71', 'neutral': '#3498DB', 'negative': '#E74C3C'}

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=[colors[label] for label in labels]
    )])

    # Update layout
    fig.update_layout(
        title='News Sentiment Analysis',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig