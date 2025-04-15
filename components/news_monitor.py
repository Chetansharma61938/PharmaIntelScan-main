"""
News monitor component for the pharma CI platform.
Renders the news feed with NLP-based summarization and sentiment analysis.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.news_scraper import get_news_articles, analyze_news_sentiment
from utils.nlp import extract_drug_entities
import plotly.express as px

def render_news_monitor():
    st.title("Pharma News Monitor")
    
    # Sidebar filters
    with st.sidebar:
        st.header("News Filters")
        
        # Company filter with default selections
        company_filter = st.multiselect(
            "Filter by Companies:",
            ["Pfizer", "Moderna", "Johnson & Johnson", "Novartis", "Roche", "AstraZeneca", "Merck", "GSK", "Sanofi", "Gilead"],
            default=["Pfizer", "Moderna"]
        )
        
        # Drug filter with common drugs
        drug_filter = st.multiselect(
            "Filter by Drugs:",
            ["COVID-19 Vaccine", "Keytruda", "Humira", "Revlimid", "Eliquis", "Opdivo", "Ozempic", "Wegovy", "Tecfidera", "Imbruvica"]
        )
        
        # Time range filter
        date_range = st.radio(
            "Time Range",
            ["Last 24 Hours", "Last Week", "Last Month", "All Time"],
            index=1  # Default to Last Week
        )
        
        # Number of results
        max_results = st.slider("Maximum Results", min_value=5, max_value=30, value=10)
        
        # Search button
        search_clicked = st.button("Search News", type="primary")
    
    # Main content area
    if search_clicked:
        with st.spinner("Fetching and analyzing news articles..."):
            # Calculate date range
            end_date = datetime.now()
            if date_range == "Last 24 Hours":
                start_date = end_date - timedelta(days=1)
            elif date_range == "Last Week":
                start_date = end_date - timedelta(weeks=1)
            elif date_range == "Last Month":
                start_date = end_date - timedelta(days=30)
            else:  # All Time
                start_date = None
            
            # Get news articles
            news_data = get_news_articles(
                company_names=company_filter if company_filter else None,
                drug_names=drug_filter if drug_filter else None,
                max_results=max_results
            )
            
            if news_data:
                # Filter by date if needed
                if start_date:
                    news_data = [
                        article for article in news_data
                        if datetime.strptime(article['date'], '%Y-%m-%d') >= start_date
                    ]
                
                # Analyze sentiment
                try:
                    news_data = analyze_news_sentiment(news_data)
                except Exception as e:
                    st.warning(f"Could not analyze sentiment: {str(e)}")
                    for article in news_data:
                        article['sentiment'] = 0  # Neutral sentiment as fallback
                
                # Convert to DataFrame
                df = pd.DataFrame(news_data)
                
                # Create tabs for different views
                news_tab, trends_tab = st.tabs(["📰 News Feed", "📊 Trends & Analysis"])
                
                with news_tab:
                    # Sentiment Overview
                    st.subheader("Sentiment Overview")
                    col1, col2, col3 = st.columns(3)
                    
                    positive_count = len([a for a in news_data if a['sentiment'] > 0.2])
                    neutral_count = len([a for a in news_data if -0.2 <= a['sentiment'] <= 0.2])
                    negative_count = len([a for a in news_data if a['sentiment'] < -0.2])
                    total = len(news_data)
                    
                    if total > 0:
                        col1.metric("Positive", f"{(positive_count/total)*100:.0f}%")
                        col2.metric("Neutral", f"{(neutral_count/total)*100:.0f}%")
                        col3.metric("Negative", f"{(negative_count/total)*100:.0f}%")
                    
                    # News Articles
                    st.subheader("Latest News")
                    for idx, article in enumerate(news_data):
                        with st.expander(
                            f"📰 {article['title']} - {article['source']} ({article['date']})",
                            expanded=(idx == 0)  # Expand first article by default
                        ):
                            # Article metadata
                            st.markdown(f"**Source:** {article['source']}")
                            st.markdown(f"**Published:** {article['date']}")
                            
                            # Sentiment indicator
                            sentiment = article['sentiment']
                            sentiment_color = (
                                "🟢" if sentiment > 0.2 else
                                "🔴" if sentiment < -0.2 else
                                "⚪"
                            )
                            st.markdown(f"**Sentiment:** {sentiment_color} ({sentiment:.2f})")
                            
                            # Article content
                            st.markdown("---")
                            if 'summary' in article:
                                st.markdown(f"**Summary:**\n{article['summary']}")
                            st.markdown(f"[Read full article]({article['url']})")
                
                with trends_tab:
                    # Sentiment Distribution
                    st.subheader("Sentiment Distribution")
                    fig = px.histogram(
                        df,
                        x="sentiment",
                        nbins=20,
                        title="Distribution of News Sentiment",
                        labels={"sentiment": "Sentiment Score", "count": "Number of Articles"},
                        color_discrete_sequence=['#3366cc']
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Topic Analysis
                    st.subheader("Topic Analysis")
                    
                    try:
                        # Extract entities from both title and content
                        all_entities = {
                            'DRUG': set(),
                            'ORG': set(),
                            'PERSON': set(),
                            'GPE': set()
                        }
                        
                        for article in news_data:
                            # Extract from title
                            title_entities = extract_drug_entities(article['title'])
                            for entity_type, values in title_entities.items():
                                all_entities[entity_type].update(values)
                            
                            # Extract from content if available
                            if 'content' in article:
                                content_entities = extract_drug_entities(article['content'])
                                for entity_type, values in content_entities.items():
                                    all_entities[entity_type].update(values)
                        
                        # Convert sets to frequency dictionaries
                        entity_frequencies = {
                            entity_type: {entity: sum(1 for article in news_data 
                                                    if entity.lower() in article['title'].lower() 
                                                    or entity.lower() in article.get('content', '').lower())
                                        for entity in entities}
                            for entity_type, entities in all_entities.items()
                        }
                        
                        # Display entities if found
                        if any(frequencies for frequencies in entity_frequencies.values()):
                            entity_types = ['DRUG', 'ORG', 'PERSON', 'GPE']
                            available_types = [t for t in entity_types if entity_frequencies[t]]
                            
                            if available_types:
                                cols = st.columns(len(available_types))
                                
                                for idx, entity_type in enumerate(available_types):
                                    with cols[idx]:
                                        type_labels = {
                                            'DRUG': '💊 Top Drugs',
                                            'ORG': '🏢 Top Organizations',
                                            'PERSON': '👤 Top People',
                                            'GPE': '🌍 Top Locations'
                                        }
                                        
                                        st.markdown(f"**{type_labels.get(entity_type, entity_type)}**")
                                        
                                        # Sort and display top entities
                                        sorted_entities = sorted(
                                            entity_frequencies[entity_type].items(),
                                            key=lambda x: x[1],
                                            reverse=True
                                        )
                                        
                                        for entity, count in sorted_entities[:10]:
                                            if count > 0:  # Only show entities that actually appear
                                                st.markdown(f"{entity.title()} ({count})")
                            else:
                                st.info("No significant topics found in the current articles.")
                    except Exception as e:
                        st.warning(f"Could not perform topic analysis: {str(e)}")
                        
            else:
                st.warning("No news articles found matching your criteria. Try adjusting your filters.")
    else:
        # Initial state
        st.info("👈 Use the filters on the left and click 'Search News' to view pharmaceutical industry news.")
