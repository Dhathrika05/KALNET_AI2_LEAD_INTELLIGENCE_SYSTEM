import pandas as pd
import os

print("🚀 ICP Scorer started")

# -----------------------------
# Get project root directory
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------
# File paths
# -----------------------------
CLEAN_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_leads.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "leads_scored.csv")

# -----------------------------
# Ensure cleaned file exists
# -----------------------------
if not os.path.exists(CLEAN_PATH):
    print("❌ cleaned_leads.csv not found. Run clean_leads.py first.")
    exit()

# -----------------------------
# Create processed folder
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Load cleaned data
# -----------------------------
df = pd.read_csv(CLEAN_PATH)

print(f"✅ Using CLEANED data: {len(df)} rows")
print("Columns:", df.columns.tolist())

# -----------------------------
# Target states
# -----------------------------
target_states = [
    "Maharashtra",
    "Telangana",
    "Delhi",
    "Karnataka",
    "Tamil Nadu"
]

# -----------------------------
# ICP Scoring Function
# -----------------------------
def score_lead(row):

    score = 0

    # Private institution
    if "private" in str(row.get("type", "")).lower():
        score += 25

    # Target state
    if row.get("state") in target_states:
        score += 20

    # Medium / Large institution
    if str(row.get("company_size_category", "")).lower() in ["medium", "large"]:
        score += 20

    # Website available
    if pd.notna(row.get("website")) and str(row.get("website")).strip() != "":
        score += 10

    # Email available
    if pd.notna(row.get("email")) and str(row.get("email")).strip() != "":
        score += 15

    # Principal name available
    if pd.notna(row.get("principal_name")) and str(row.get("principal_name")).strip() != "":
        score += 10

    return score

# -----------------------------
# Apply scoring
# -----------------------------
df["icp_score"] = df.apply(score_lead, axis=1)

# -----------------------------
# Tier Assignment
# -----------------------------
def assign_tier(score):

    if score >= 70:
        return "Tier1"

    elif score >= 40:
        return "Tier2"

    else:
        return "Tier3"

df["icp_tier"] = df["icp_score"].apply(assign_tier)

# -----------------------------
# Save output
# -----------------------------
try:
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n💾 File saved at:")
    print(OUTPUT_FILE)

except Exception as e:
    print("❌ Error saving file:", e)

# -----------------------------
# Print distribution
# -----------------------------
print("\n📊 Tier Distribution:\n")
print(df["icp_tier"].value_counts())

print("\n📈 Score Summary:\n")
print(df["icp_score"].describe())

print("\n🔥 ICP Scoring completed successfully!")