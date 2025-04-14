"""
Database initialization script.
Run this script to create and seed the database with initial data.
"""
from utils.database import init_db, seed_database

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database tables created.")
    
    print("Seeding database with initial data...")
    seed_database()
    print("Database seeded successfully.")
    
    print("Database setup complete!")