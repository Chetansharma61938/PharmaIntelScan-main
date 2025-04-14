"""
KOL insights component for the pharma CI platform.
Renders information about Key Opinion Leaders in the pharmaceutical industry.
"""
import streamlit as st
import pandas as pd
from utils.pubmed import get_pubmed_data
from utils.text_processing import identify_kols
from utils.news_scraper import get_kol_mentions

def render_kol_insights():
    """Render the KOL insights page with analysis of key opinion leaders"""
    st.title("Key Opinion Leaders Insights")
    
    # Add sidebar filters
    with st.sidebar:
        st.subheader("KOL Filters")
        
        # Therapeutic area filter
        areas = ['Oncology', 'Immunology', 'Neurology', 'Cardiovascular', 
                 'Infectious Disease', 'Metabolic', 'Respiratory']
        
        selected_area = st.selectbox(
            "Therapeutic Area:",
            options=['All'] + areas,
            index=0
        )
        
        # Publication count minimum filter
        min_publications = st.slider(
            "Minimum Publications:",
            min_value=1,
            max_value=20,
            value=3
        )
        
        # Time period filter
        time_period = st.radio(
            "Time Period:",
            ["Last Year", "Last 5 Years", "All Time"]
        )
        
        # Refresh data option
        refresh_data = st.button("Refresh KOL Data")
    
    # Build search query based on filters
    search_terms = []
    
    if selected_area != 'All':
        search_terms.append(selected_area.lower())
    
    # Add time constraints based on selection
    if time_period == "Last Year":
        search_terms.append("2022[PDAT] OR 2023[PDAT]")
    elif time_period == "Last 5 Years":
        years = list(range(2018, 2024))
        year_query = " OR ".join([f"{year}[PDAT]" for year in years])
        search_terms.append(f"({year_query})")
    
    # Show loading spinner while data is being fetched
    with st.spinner("Loading KOL data..."):
        # Get publication data from PubMed
        publications = get_pubmed_data(
            drug_names=search_terms if search_terms else None,
            max_results=100,
            refresh=refresh_data
        )
        
        # Identify potential KOLs from publications
        kols = identify_kols(publications)
        
        # Filter by publication count
        kols = [kol for kol in kols if kol['publication_count'] >= min_publications]
    
    # KOL overview
    st.subheader("Top Key Opinion Leaders")
    
    if kols:
        # Create columns for top KOLs
        col1, col2 = st.columns(2)
        
        with col1:
            # Display top 5 KOLs
            for i, kol in enumerate(kols[:5]):
                with st.expander(f"{i+1}. {kol['name']} ({kol['publication_count']} publications)"):
                    st.write(f"**Journals:** {', '.join(kol['journals'][:3])}")
                    st.write(f"**Recent work:** {kol['recent_publication']}")
                    st.write(f"[View on PubMed]({kol['url']})")
        
        with col2:
            # Display next 5 KOLs
            for i, kol in enumerate(kols[5:10]):
                with st.expander(f"{i+6}. {kol['name']} ({kol['publication_count']} publications)"):
                    st.write(f"**Journals:** {', '.join(kol['journals'][:3])}")
                    st.write(f"**Recent work:** {kol['recent_publication']}")
                    st.write(f"[View on PubMed]({kol['url']})")
    else:
        st.info("No KOLs found matching the selected criteria.")
    
    # KOL network visualization (placeholder)
    st.subheader("KOL Network")
    
    # In a real application, this would be an interactive network graph
    # For MVP, we'll use a simplified representation
    if kols:
        # Create a simple visualization of KOL connections
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 5px;">
            <p style="text-align: center;">KOL Network Visualization</p>
            <p style="text-align: center; color: #777;">A full interactive network graph would be implemented here.</p>
            <p style="text-align: center; color: #777;">For the MVP, we display tabular data below.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show KOL data in a table
        kol_df = pd.DataFrame(kols)
        if not kol_df.empty:
            # Select and rename columns for display
            display_cols = ['name', 'publication_count', 'journals', 'recent_publication']
            display_names = {'name': 'KOL Name', 'publication_count': 'Publications', 
                            'journals': 'Journals', 'recent_publication': 'Recent Publication'}
            
            # Create displayable dataframe
            display_df = kol_df[display_cols].copy()
            display_df.columns = [display_names.get(col, col) for col in display_cols]
            
            # Convert journal lists to strings
            display_df['Journals'] = display_df['Journals'].apply(lambda x: ', '.join(x[:2]) + ('...' if len(x) > 2 else ''))
            
            # Display the table
            st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No KOL data available for network visualization.")
    
    # KOL mentions and sentiment analysis
    st.subheader("KOL Activity Tracker")
    
    # Allow searching for specific KOL
    kol_search = st.text_input("Search for a specific KOL:")
    
    if kol_search:
        with st.spinner(f"Searching for mentions of {kol_search}..."):
            # Get mentions of the KOL
            mentions = get_kol_mentions(kol_search)
            
            if mentions:
                st.success(f"Found {len(mentions)} mentions of {kol_search}")
                
                # Display mentions
                for mention in mentions:
                    with st.expander(f"{mention['title']} ({mention['source']})"):
                        st.write(f"**Date:** {mention.get('date', 'Unknown')}")
                        st.write(f"**Type:** {mention.get('type', 'Publication')}")
                        st.write(f"**Context:** {mention.get('context', 'No context available')}")
                        st.write(f"[View Source]({mention.get('url', '#')})")
            else:
                st.warning(f"No mentions found for {kol_search}")
    
    # KOL trends and insights
    st.subheader("KOL Publication Trends")
    
    if kols:
        # In a real application, this would show publication trends over time
        # For the MVP, we'll display a message about this feature
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 5px;">
            <p style="text-align: center;">KOL Publication Trends Analysis</p>
            <p style="text-align: center; color: #777;">This feature would show publication frequency, co-authorship patterns, and citation metrics over time.</p>
            <p style="text-align: center; color: #777;">For the MVP, we display the most active KOLs by publication count.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display most active KOLs
        if kols:
            # Sort by publication count
            top_active_kols = sorted(kols, key=lambda x: x['publication_count'], reverse=True)[:10]
            
            # Create data for horizontal bar chart
            kol_names = [kol['name'].split()[-1] for kol in top_active_kols]  # Use last name for brevity
            pub_counts = [kol['publication_count'] for kol in top_active_kols]
            
            # Create a simple horizontal bar chart using HTML
            st.markdown("<h4>Most Active KOLs by Publication Count</h4>", unsafe_allow_html=True)
            
            max_count = max(pub_counts)
            for i, (name, count) in enumerate(zip(kol_names, pub_counts)):
                # Calculate percentage width
                width_pct = int((count / max_count) * 100)
                
                # Create bar
                st.markdown(f"""
                <div style="margin-bottom: 5px;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 100px; text-align: right; padding-right: 10px;">{name}</div>
                        <div style="flex-grow: 1;">
                            <div style="background-color: #2196f3; width: {width_pct}%; height: 20px; border-radius: 2px;"></div>
                        </div>
                        <div style="width: 50px; text-align: left; padding-left: 10px;">{count}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No KOL data available for trend analysis.")
