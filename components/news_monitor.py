"""
News monitor component for the pharma CI platform.
Renders the news feed with NLP-based summarization and sentiment analysis.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.news_scraper import get_news_articles
from utils.text_processing import analyze_sentiment, extract_drug_entities
from utils.visualization import create_sentiment_chart

def render_news_monitor():
    """Render the news monitoring page with NLP-enhanced features"""
    st.title("Pharma News Monitor")
    
    # Add sidebar filters
    with st.sidebar:
        st.subheader("News Filters")
        
        # Company filter
        major_pharma = ["Pfizer", "Novartis", "Roche", "Merck", "AstraZeneca", 
                        "Johnson & Johnson", "Sanofi", "GlaxoSmithKline", "Gilead", 
                        "Bristol Myers Squibb", "Amgen", "AbbVie", "Eli Lilly"]
        
        selected_companies = st.multiselect(
            "Filter by Companies:",
            options=major_pharma,
            default=[]
        )
        
        # Drug filter - would typically be populated from a database
        sample_drugs = ["Keytruda", "Humira", "Revlimid", "Eliquis", "Opdivo", 
                       "Eylea", "Rituxan", "Xarelto", "Ozempic", "Biktarvy"]
        
        selected_drugs = st.multiselect(
            "Filter by Drugs:",
            options=sample_drugs,
            default=[]
        )
        
        # Sentiment filter
        sentiments = ["positive", "neutral", "negative"]
        selected_sentiments = st.multiselect(
            "Filter by Sentiment:",
            options=sentiments,
            default=sentiments
        )
        
        # Time period filter
        time_period = st.radio(
            "Time Period:",
            ["Last 24 Hours", "Last Week", "Last Month", "All"]
        )
        
        # Refresh data option
        refresh_news = st.button("Refresh News Data")
    
    # Show loading spinner while data is being fetched
    with st.spinner("Loading news data..."):
        # Get news data
        news_data = get_news_articles(
            company_names=selected_companies if selected_companies else None,
            drug_names=selected_drugs if selected_drugs else None,
            max_results=50,
            refresh=refresh_news
        )
        
        # Filter news by sentiment if selected
        if selected_sentiments and news_data:
            news_data = [article for article in news_data if article.get('sentiment', 'neutral') in selected_sentiments]
        
        # Filter by time period if selected
        if time_period != "All" and news_data:
            current_date = datetime.now()
            
            # Convert string dates to datetime objects for comparison
            filtered_news = []
            for article in news_data:
                try:
                    # Handle various date formats
                    pub_date = article.get('published_at', '')
                    if isinstance(pub_date, str):
                        try:
                            # Try common formats
                            pub_datetime = datetime.strptime(pub_date, '%Y-%m-%d')
                        except:
                            try:
                                pub_datetime = datetime.strptime(pub_date, '%b %d, %Y')
                            except:
                                # If we can't parse the date, include it anyway
                                filtered_news.append(article)
                                continue
                    else:
                        # If it's not a string, keep the article
                        filtered_news.append(article)
                        continue
                    
                    # Apply time filter
                    if time_period == "Last 24 Hours":
                        days_diff = (current_date - pub_datetime).days
                        if days_diff <= 1:
                            filtered_news.append(article)
                    elif time_period == "Last Week":
                        days_diff = (current_date - pub_datetime).days
                        if days_diff <= 7:
                            filtered_news.append(article)
                    elif time_period == "Last Month":
                        days_diff = (current_date - pub_datetime).days
                        if days_diff <= 30:
                            filtered_news.append(article)
                except:
                    # If there's any error processing the date, include the article
                    filtered_news.append(article)
            
            news_data = filtered_news
    
    # News sentiment overview
    st.subheader("News Sentiment Overview")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Sentiment chart
        if news_data:
            sentiment_chart = create_sentiment_chart(news_data)
            st.plotly_chart(sentiment_chart, use_container_width=True, key="news_sentiment_chart")
        else:
            st.info("No news articles available to analyze.")
    
    with col2:
        # Sentiment metrics
        if news_data:
            # Calculate sentiment counts
            sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
            for article in news_data:
                sentiment = article.get('sentiment', 'neutral')
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1
            
            # Display metrics
            metric_cols = st.columns(3)
            
            with metric_cols[0]:
                positive_pct = round(sentiment_counts['positive'] / len(news_data) * 100, 1)
                st.metric("Positive", f"{positive_pct}%", f"{sentiment_counts['positive']} articles")
            
            with metric_cols[1]:
                neutral_pct = round(sentiment_counts['neutral'] / len(news_data) * 100, 1)
                st.metric("Neutral", f"{neutral_pct}%", f"{sentiment_counts['neutral']} articles")
            
            with metric_cols[2]:
                negative_pct = round(sentiment_counts['negative'] / len(news_data) * 100, 1)
                st.metric("Negative", f"{negative_pct}%", f"{sentiment_counts['negative']} articles")
            
            # Overall sentiment
            overall = "Positive" if positive_pct > (neutral_pct + negative_pct) else \
                     "Negative" if negative_pct > (neutral_pct + positive_pct) else "Neutral"
            
            st.info(f"Overall industry sentiment is **{overall}** based on {len(news_data)} recent articles.")
        else:
            st.info("No news articles available to analyze.")
    
    # News feed
    st.subheader("Pharmaceutical News Feed")
    
    if news_data:
        # Display each news article
        for i, article in enumerate(news_data):
            # Determine card border color based on sentiment
            sentiment = article.get('sentiment', 'neutral')
            sentiment_colors = {
                'positive': 'green',
                'neutral': 'blue',
                'negative': 'red'
            }
            border_color = sentiment_colors.get(sentiment, 'gray')
            
            # Create an expandable card for each article
            with st.expander(f"{article['title']}"):
                # Article metadata
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Source:** {article.get('source', 'Unknown')}")
                    st.markdown(f"**Published:** {article.get('published_at', 'Unknown date')}")
                
                with col2:
                    # Display sentiment badge
                    sentiment_badge = {
                        'positive': '🟢 Positive',
                        'neutral': '🔵 Neutral',
                        'negative': '🔴 Negative'
                    }
                    st.markdown(f"**Sentiment:** {sentiment_badge.get(sentiment, 'Unknown')}")
                
                # Article summary
                st.markdown("### Summary")
                st.markdown(article.get('summary', 'No summary available'))
                
                # Entity extraction
                if 'content' in article:
                    entities = extract_drug_entities(article['content'])
                    
                    if entities:
                        st.markdown("### Mentioned Entities")
                        
                        # Display extracted entities
                        entity_cols = st.columns(3)
                        
                        with entity_cols[0]:
                            if 'DRUG' in entities:
                                st.markdown("**Drug Names:**")
                                st.markdown("<br>".join([f"• {drug}" for drug in entities['DRUG'][:5]]), unsafe_allow_html=True)
                        
                        with entity_cols[1]:
                            if 'ORG' in entities:
                                st.markdown("**Organizations:**")
                                st.markdown("<br>".join([f"• {org}" for org in entities['ORG'][:5]]), unsafe_allow_html=True)
                        
                        with entity_cols[2]:
                            if 'PERSON' in entities:
                                st.markdown("**People:**")
                                st.markdown("<br>".join([f"• {person}" for person in entities['PERSON'][:5]]), unsafe_allow_html=True)
                
                # Link to full article
                st.markdown(f"[Read full article]({article.get('url', '#')})")
    else:
        st.info("No news articles available for the selected filters.")
    
    # Topic trends section
    if news_data:
        st.subheader("Recent Topic Trends")
        
        # Extract all entities from news
        all_entities = {}
        for article in news_data:
            if 'content' in article:
                entities = extract_drug_entities(article['content'])
                
                # Merge entities by type
                for entity_type, values in entities.items():
                    if entity_type not in all_entities:
                        all_entities[entity_type] = {}
                    
                    for value in values:
                        if value not in all_entities[entity_type]:
                            all_entities[entity_type][value] = 1
                        else:
                            all_entities[entity_type][value] += 1
        
        # Display top entities by type
        entity_types = ['DRUG', 'ORG', 'PERSON', 'GPE']  # GPE are geopolitical entities (countries, cities)
        
        topics_cols = st.columns(len([t for t in entity_types if t in all_entities]))
        
        col_idx = 0
        for entity_type in entity_types:
            if entity_type in all_entities and all_entities[entity_type]:
                with topics_cols[col_idx]:
                    # Display entity type header
                    type_labels = {
                        'DRUG': 'Top Mentioned Drugs',
                        'ORG': 'Top Organizations',
                        'PERSON': 'Top Mentioned People',
                        'GPE': 'Top Locations'
                    }
                    
                    st.markdown(f"**{type_labels.get(entity_type, entity_type)}**")
                    
                    # Sort entities by frequency
                    sorted_entities = sorted(all_entities[entity_type].items(), key=lambda x: x[1], reverse=True)
                    
                    # Display top 10 entities
                    for entity, count in sorted_entities[:10]:
                        st.markdown(f"{entity} ({count})")
                
                col_idx += 1
