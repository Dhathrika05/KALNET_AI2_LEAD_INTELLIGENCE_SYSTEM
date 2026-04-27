import pandas as pd

# -------------------------------
# Step 1: Load data (first 50 rows)
# -------------------------------
try:
    df = pd.read_csv("data/raw/colleges_aishe.csv").head(50)
except FileNotFoundError:
    print("Error: CSV file not found. Check path.")
    exit()

print("Original shape:", df.shape)

# -------------------------------
# Step 2: Standardize column names (lowercase, remove spaces)
# -------------------------------
df.columns = df.columns.str.strip().str.lower()

# -------------------------------
# Step 3: Check required columns
# -------------------------------
required_cols = ["name", "state", "district"]

missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print(f"Missing required columns: {missing_cols}")
    exit()

# -------------------------------
# Step 4: Remove missing values
# -------------------------------
df = df.dropna(subset=required_cols)

# -------------------------------
# Step 5: Remove duplicates
# -------------------------------
df = df.drop_duplicates(subset=["name", "district"])

# -------------------------------
# Step 6: Standardize text fields
# -------------------------------
df["name"] = df["name"].str.strip().str.title()
df["state"] = df["state"].str.strip().str.title()
df["district"] = df["district"].str.strip().str.title()

if "type" in df.columns:
    df["type"] = df["type"].astype(str).str.strip().str.title()

# -------------------------------
# Step 7: Create full_name column
# -------------------------------
df["full_name"] = df["name"]

# -------------------------------
# Step 8: Create company_size_category safely
# -------------------------------
def categorize_size(count):
    try:
        count = float(count)
    except:
        return "Unknown"

    if count < 1000:
        return "Small"
    elif count < 5000:
        return "Medium"
    else:
        return "Large"

if "student_count" in df.columns:
    df["company_size_category"] = df["student_count"].apply(categorize_size)
else:
    df["company_size_category"] = "Unknown"

# -------------------------------
# Step 9: Create processed folder if not exists
# -------------------------------
import os
os.makedirs("data/processed", exist_ok=True)

# -------------------------------
# Step 10: Save cleaned data
# -------------------------------
output_path = "data/processed/leads_cleaned.csv"
df.to_csv(output_path, index=False)

print("Cleaned shape:", df.shape)
print(f"File saved successfully at: {output_path}")
