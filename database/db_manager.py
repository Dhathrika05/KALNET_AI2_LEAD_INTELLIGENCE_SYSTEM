# Inside database/db_manager.py
from .config import Config 
import mysql.connector
from sqlalchemy import create_engine

def get_db_connection():
    """
    KALNET AI-2 Core Database Connector
    Logic: Fetches validated credentials from Config class and returns a active connection.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        if connection.is_connected():
            # This print helps you verify the connection in the main.py terminal
            print(f"KALNET AI-2: Connected to {Config.DB_NAME} successfully.")
            return connection
            
    except mysql.connector.Error as e:
        # As Lead, you need specific error reporting to debug team issues
        print(f"CRITICAL: Database connection failed. Error: {e}")
        return None
# New function for pandas
def get_engine():
    try:
        engine = create_engine(
            f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"
        )
        return engine
    except Exception as e:
        print(f"Engine creation failed: {e}")
        return None
    
    