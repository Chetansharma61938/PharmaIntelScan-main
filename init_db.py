"""
Database initialization script.
Run this script to create and seed the database with initial data.
"""
from utils.database import init_db, seed_database
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='pharma_intel'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE pharma_intel")
            print("Database created successfully.")
        else:
            print("Database already exists.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

if __name__ == "__main__":
    try:
        print("Creating database if it doesn't exist...")
        create_database()
        
        print("Initializing database...")
        init_db()
        print("Database tables created.")
        
        print("Seeding database with initial data...")
        seed_database()
        print("Database seeded successfully.")
        
        print("Database setup complete!")
    except Exception as e:
        print(f"Error during database setup: {e}")
        raise