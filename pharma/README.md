
# Pharma CI Platform

A comprehensive platform for pharmaceutical competitive intelligence monitoring, built with Streamlit and PostgreSQL.

## Features

- Dashboard with key industry metrics
- Competitor Pipeline tracking
- News Monitoring system
- KOL (Key Opinion Leader) Insights
- Real-time data visualization

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Required Python packages (installed automatically via pyproject.toml)

## Setup Instructions

1. Fork this project in Replit

2. Initialize the database:
```bash
python init_db.py
```

3. Run the application:
- Click the "Run" button in Replit
- The application will start on port 5000

## Project Structure

```
├── components/          # UI components
├── models/             # Database models
├── utils/              # Utility functions
├── app.py             # Main application
├── init_db.py         # Database initialization
└── README.md          # Documentation
```

## Data Sources

- ClinicalTrials.gov
- PubMed
- FDA Database
- PostgreSQL Database (local)

## Environment Variables

Set up the following environment variables in Replit Secrets:
- `DATABASE_URL`: PostgreSQL connection string
- `API_KEY`: API key for external services

## License

© 2023-2025 Pharma CI Platform
