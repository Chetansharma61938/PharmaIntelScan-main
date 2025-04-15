
import streamlit as st
from components.dashboard import render_dashboard
from components.competitor_pipeline import render_competitor_pipeline
from components.news_monitor import render_news_monitor
from components.kol_insights import render_kol_insights
from utils.database import init_db, seed_database

# Set page configuration first
st.set_page_config(
    page_title="Pharma CI Platform",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the database after page config
try:
    init_db()
    seed_database()
except Exception as e:
    st.error(f"Error initializing database: {e}")
    print(f"Error initializing database: {e}")

# Add sidebar for navigation
st.sidebar.title("Pharma CI Platform")
st.sidebar.markdown("---")

# Navigation options
page = st.sidebar.radio(
    "Navigate to:",
    ["Dashboard", "Competitor Pipeline", "News Monitor", "KOL Insights"]
)

# Display the appropriate page based on selection
if page == "Dashboard":
    render_dashboard()
elif page == "Competitor Pipeline":
    render_competitor_pipeline()
elif page == "News Monitor":
    render_news_monitor()
elif page == "KOL Insights":
    render_kol_insights()

# Footer with attribution
st.sidebar.markdown("---")
st.sidebar.markdown("""
<small>Data sources: PostgreSQL Database, ClinicalTrials.gov, PubMed, FDA<br>
© 2023-2025 Pharma CI Platform</small>
""", unsafe_allow_html=True)
