# Inside database/db_manager.py
from .config import Config 
import mysql.connector

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