import pandas as pd

# Read first 50 rows
df = pd.read_csv("data/raw/colleges_aishe.csv").head(50)

print("Original shape:", df.shape)

# Remove missing values
df = df.dropna(subset=["name", "state", "district"])

# Remove duplicates
df = df.drop_duplicates(subset=["name", "district"])

# Standardize text
df["state"] = df["state"].str.title()
df["type"] = df["type"].str.title()

# Create new columns
df["full_name"] = df["name"]

def categorize_size(count):
    if count < 1000:
        return "Small"
    elif count < 5000:
        return "Medium"
    else:
        return "Large"

df["company_size_category"] = df["student_count"].apply(categorize_size)

# Save output
df.to_csv("data/processed/leads_cleaned.csv", index=False)

print("Cleaned shape:", df.shape)
print("Saved successfully")
