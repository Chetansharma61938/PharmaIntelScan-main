"""
Visualization module for the pharma CI platform.
Creates charts and visualizations for the dashboard.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def create_pipeline_phase_chart(pipeline_data):
    """Create a bar chart showing the distribution of drugs by phase"""
    try:
        # Define expected phases
        expected_phases = ['Preclinical', 'Phase 1', 'Phase 2', 'Phase 3', 'Approved']
        
        # Initialize phase counts with zeros
        phase_counts = {phase: 0 for phase in expected_phases}
        
        # Handle empty or invalid data
        if pipeline_data is None or not isinstance(pipeline_data, pd.DataFrame) or pipeline_data.empty:
            print("Creating empty chart due to invalid data")
            return create_empty_chart(expected_phases)
        
        # Ensure phase column exists
        if 'phase' not in pipeline_data.columns:
            print("No phase column found")
            return create_empty_chart(expected_phases)
        
        # Count phases manually, excluding placeholder rows
        for _, row in pipeline_data.iterrows():
            phase = row['phase']
            if phase in phase_counts and not row['name'].startswith('placeholder_'):
                phase_counts[phase] += 1
        
        # Create the bar chart using the counts dictionary
        fig = px.bar(
            x=list(phase_counts.keys()),
            y=list(phase_counts.values()),
            title='Pipeline by Phase',
            labels={'x': 'Phase', 'y': 'Number of Drugs'}
        )
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            xaxis_title='Phase',
            yaxis_title='Number of Drugs',
            plot_bgcolor='white'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating phase chart: {str(e)}")
        return create_empty_chart(expected_phases)

def create_empty_chart(phases):
    """Helper function to create an empty chart"""
    return px.bar(
        x=phases,
        y=[0] * len(phases),
        title='Pipeline by Phase',
        labels={'x': 'Phase', 'y': 'Number of Drugs'}
    )

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

def create_recent_activity_timeline(pipeline_data, news_data, max_items=10):
    """
    Create a combined timeline of recent pipeline and news activity with enhanced UI.

    Args:
        pipeline_data (pd.DataFrame): DataFrame with pipeline data
        news_data (list): List of news article dictionaries
        max_items (int): Maximum number of items to display

    Returns:
        plotly.graph_objects.Figure: Plotly figure object with improved styling
    """
    from datetime import datetime

    # Create a combined list of events
    events = []
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Add pipeline events
    if not pipeline_data.empty:
        try:
            # Get the most recent updates
            recent_pipeline = pipeline_data.head(max_items)

            for _, row in recent_pipeline.iterrows():
                # Handle any date format issues
                date_str = current_date  # Use current date as default
                try:
                    if isinstance(row['last_updated'], str):
                        date_str = row['last_updated']
                    elif hasattr(row['last_updated'], 'strftime'):
                        date_str = row['last_updated'].strftime('%Y-%m-%d')
                except:
                    pass  # Keep default date

                events.append({
                    'date': date_str,
                    'title': f"{row['drug_name']} - {row['phase']}",
                    'description': f"{row['company']}: {row['condition']}",
                    'type': 'pipeline'
                })
        except Exception as e:
            print(f"Error processing pipeline data for timeline: {e}")

    # Add news events
    if news_data:
        try:
            for article in news_data[:max_items]:
                # Handle any date format issues
                date_str = current_date  # Use current date as default
                try:
                    pub_date = article.get('published_at', '')
                    if isinstance(pub_date, str):
                        date_str = pub_date
                    elif hasattr(pub_date, 'strftime'):
                        date_str = pub_date.strftime('%Y-%m-%d')
                except:
                    pass  # Keep default date

                events.append({
                    'date': date_str,
                    'title': article.get('title', 'News Update'),
                    'description': article.get('source', ''),
                    'type': 'news'
                })
        except Exception as e:
            print(f"Error processing news data for timeline: {e}")

    # If we have no events, add a placeholder to avoid empty chart
    if not events:
        events.append({
            'date': current_date,
            'title': 'No recent activity',
            'description': 'Check back later for updates',
            'type': 'news'
        })

    # Sort by date and take most recent - with error handling
    try:
        events = sorted(events, key=lambda x: x['date'], reverse=True)[:max_items]
    except Exception as e:
        print(f"Error sorting timeline events: {e}")
        # Just take the first max_items without sorting
        events = events[:max_items]

    # Create the figure with improved styling
    fig = go.Figure()

    # Create custom timeline layout with enhanced visuals
    for i, event in enumerate(events):
        # Add vertical line for timeline
        if i > 0:
            fig.add_shape(
                type="line",
                x0=0, x1=0,
                y0=i-1, y1=i,
                line=dict(color="#d1d8e0", width=4),
            )

        # Add event marker with improved visibility
        marker_color = '#4b7bec' if event['type'] == 'news' else '#fc5c65'
        fig.add_trace(go.Scatter(
            x=[0],
            y=[i],
            mode='markers',
            marker=dict(
                size=16,
                color=marker_color,
                symbol='circle',
                line=dict(color='white', width=2),
                opacity=1
            ),
            showlegend=False,
            hoverinfo='text',
            hovertext=f"{event['date']}: {event['title']}"
        ))

        # Add date with improved spacing
        fig.add_trace(go.Scatter(
            x=[-0.2],
            y=[i],
            mode='text',
            text=[f"<b>{event['date']}</b>"],
            textposition='middle right',
            textfont=dict(size=12, color='#2d3436', family='Arial'),
            showlegend=False
        ))

        # Add event details with clearer hierarchy
        fig.add_trace(go.Scatter(
            x=[0.2],
            y=[i],
            mode='text',
            text=[f"<b style='font-size:13px'>{event['title']}</b><br><span style='color:#636e72;font-size:12px'>{event['description']}</span>"],
            textposition='middle left',
            textfont=dict(size=12, family='Arial'),
            showlegend=False
        ))

    # Update layout with improved spacing and dimensions
    fig.update_layout(
        title=dict(
            text='Recent Activity Timeline',
            font=dict(size=20, family='Arial', color='#2d3436'),
            x=0.02,
            y=0.98
        ),
        height=400,  # Fixed height to enable scrolling
        margin=dict(l=120, r=120, t=40, b=20),
        xaxis=dict(visible=False, range=[-0.5, 1.5], fixedrange=True),
        yaxis=dict(
            visible=False, 
            range=[-0.5, len(events) - 0.5],
            scaleanchor="x",
            scaleratio=1,
            fixedrange=True
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Arial'
        ),
        hovermode='closest',
        # Enable zooming
        dragmode='zoom',
        # Configure modebar
        modebar=dict(
            bgcolor='rgba(255, 255, 255, 0.7)',
            color='#333',
            activecolor='#000',
            orientation='v'
        )
    )

    return fig