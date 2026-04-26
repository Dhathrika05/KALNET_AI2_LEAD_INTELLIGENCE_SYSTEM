import pandas as pd
from database.db_manager import get_engine
# Load AISHE data
df = pd.read_csv("data/raw/colleges_aishe.csv")
# Add missing columns 
df["board"] = ""
df["email"] = ""
df["phone"] = ""
df["principal_name"] = ""
df["icp_score"] = 0
df["icp_tier"] = ""
# Clean data
df.drop_duplicates(subset=["name", "district"], inplace=True)
df.fillna("", inplace=True)
# Insert into DB
engine = get_engine()

df.to_sql(
    "institutions",
    engine,
    if_exists="append",
    index=False
)

print("AISHE data loaded successfully!")