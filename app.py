import streamlit as st
from components.dashboard import render_dashboard
from components.competitor_pipeline import render_competitor_pipeline
from components.news_monitor import render_news_monitor
from components.kol_insights import render_kol_insights
from utils.database import init_db, seed_database
import time
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration first
st.set_page_config(
    page_title="Pharma CI Platform",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the database after page config
max_retries = 5
retry_delay = 10  # seconds

def initialize_database():
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})...")
            init_db()
            logger.info("Database connection established!")
            
            logger.info("Seeding database with initial data...")
            seed_database()
            logger.info("Database seeded successfully!")
            return True
            
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {str(e)}")
                return False

# Initialize database silently
db_initialized = initialize_database()

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
