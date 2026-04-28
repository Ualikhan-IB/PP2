# connect.py
import psycopg2
from config import DB_CONFIG

def get_connection():
    """Create and return a connection to the PostgreSQL database."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connection successful.")
    except psycopg2.OperationalError as e:
        print(f"❌ Unable to connect to the database: {e}")
    return conn