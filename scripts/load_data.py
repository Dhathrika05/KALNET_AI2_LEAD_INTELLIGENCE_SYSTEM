import pandas as pd
import sys
import os

# Adjusting path to import database modules from the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import get_engine

def update_institutions_table():
    """
    Reads the scored leads and updates the 'institutions' database table.
    """
    # Path to the file identified in the data/processed directory
    file_path = os.path.join('data', 'processed', 'leads_scored.csv')
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    try:
        # Loading CSV data which includes institutional fields
        df = pd.read_csv(file_path)
        
        # Initializing the SQLAlchemy engine
        engine = get_engine()
        
        if engine:
            # Updating the 'institutions' table. 
            # Use if_exists='replace' since you deleted the old table and want to recreate it.
            df.to_sql('institutions', con=engine, if_exists='replace', index=False)
            print(f"Successfully updated {len(df)} records to the 'institutions' table.")
        else:
            print("Database connection failed.")

    except Exception as e:
        # Error reporting as suggested in project requirements
        print(f"CRITICAL: Update failed. Error: {e}")

if __name__ == "__main__":
    update_institutions_table()