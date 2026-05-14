import pandas as pd
import re

# =========================
# LOAD FILES
# =========================

aishe_df = pd.read_csv("data/raw/colleges_aishe.csv")
contacts_df = pd.read_csv("data/raw/contacts_scraped.csv")
phones_df = pd.read_csv("data/raw/phones_scraped.csv")

# =========================
# STANDARDIZE COLUMN NAMES
# =========================

aishe_df.columns = aishe_df.columns.str.lower().str.strip()
contacts_df.columns = contacts_df.columns.str.lower().str.strip()
phones_df.columns = phones_df.columns.str.lower().str.strip()

# =========================
# CLEAN TEXT FUNCTION
# =========================

def clean_text(value):

    if pd.isna(value):
        return None

    value = str(value).strip()

    value = re.sub(r"\s+", " ", value)

    return value

# =========================
# CLEAN ALL TEXT COLUMNS
# =========================

for col in aishe_df.columns:
    aishe_df[col] = aishe_df[col].apply(clean_text)

for col in contacts_df.columns:
    contacts_df[col] = contacts_df[col].apply(clean_text)

for col in phones_df.columns:
    phones_df[col] = phones_df[col].apply(clean_text)

# =========================
# STANDARDIZE COLLEGE NAMES
# =========================

aishe_df["name"] = aishe_df["name"].str.title()
contacts_df["name"] = contacts_df["name"].str.title()
phones_df["name"] = phones_df["name"].str.title()

# =========================
# CLEAN EMAILS
# =========================

def clean_email(email):

    if pd.isna(email):
        return None

    email = str(email).lower().strip()

    # Keep first email if multiple exist
    if "," in email:
        email = email.split(",")[0].strip()

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if re.match(pattern, email):
        return email

    return None

contacts_df["email"] = contacts_df["email"].apply(clean_email)

# =========================
# CLEAN PHONE NUMBERS
# =========================

def clean_phone(phone):

    if pd.isna(phone):
        return None

    phone = str(phone)

    # Keep only digits
    phone = re.sub(r"\D", "", phone)

    if len(phone) < 6:
        return None

    return phone

phones_df["phone"] = phones_df["phone"].apply(clean_phone)

# =========================
# CLEAN WEBSITES
# =========================

def clean_website(website):

    if pd.isna(website):
        return None

    website = str(website).lower().strip()

    website = website.replace("http://", "")
    website = website.replace("https://", "")
    website = website.replace("www.", "")

    return website

aishe_df["website"] = aishe_df["website"].apply(clean_website)
contacts_df["website"] = contacts_df["website"].apply(clean_website)

# =========================
# CLEAN PRINCIPAL NAMES
# =========================

def clean_principal(name):

    if pd.isna(name):
        return None

    name = str(name).strip()

    name = re.sub(r"\s+", " ", name)

    name = re.sub(r"[^a-zA-Z\s\.]", "", name)

    unwanted_words = [
        "principal",
        "professor",
        "prof",
        "dr",
        "mr",
        "mrs",
        "ms",
        "phd",
        "director",
        "dean",
        "hod"
    ]

    words = name.split()

    cleaned_words = []

    for word in words:

        word_lower = word.lower().replace(".", "")

        if word_lower not in unwanted_words:
            cleaned_words.append(word)

    name = " ".join(cleaned_words)

    if len(name.split()) > 5:
        return None

    if len(name.split()) < 2:
        return None

    return name.title()

contacts_df["principal_name"] = contacts_df["principal_name"].apply(clean_principal)

# =========================
# REMOVE DUPLICATES
# =========================

aishe_df = aishe_df.drop_duplicates()
contacts_df = contacts_df.drop_duplicates()
phones_df = phones_df.drop_duplicates()

# =========================
# REMOVE PHONE COLUMN
# FROM AISHE DATA
# =========================

if "phone" in aishe_df.columns:
    aishe_df = aishe_df.drop(columns=["phone"])

# =========================
# MERGE AISHE + CONTACTS
# =========================

merged_df = pd.merge(
    aishe_df,
    contacts_df,
    on="name",
    how="left",
    suffixes=("", "_contact")
)

# =========================
# MERGE PHONE DATA
# =========================

merged_df = pd.merge(
    merged_df,
    phones_df[["name", "phone"]],
    on="name",
    how="left"
)

# =========================
# KEEP BEST WEBSITE
# =========================

merged_df["website"] = merged_df["website"].fillna(
    merged_df["website_contact"]
)

if "website_contact" in merged_df.columns:
    merged_df = merged_df.drop(columns=["website_contact"])

# =========================
# CREATE COMPANY SIZE CATEGORY
# =========================

def get_company_size(student_count):

    if pd.isna(student_count):
        return None

    try:
        student_count = int(student_count)

        if student_count < 500:
            return "Small"

        elif student_count <= 1500:
            return "Medium"

        else:
            return "Large"

    except:
        return None

merged_df["company_size_category"] = merged_df["student_count"].apply(
    get_company_size
)

# Add a column "board"
merged_df["board"]=None

# =========================
# REMOVE FINAL DUPLICATES
# =========================

merged_df = merged_df.drop_duplicates()

# =========================
# FINAL COLUMN ORDER
# =========================

final_columns = [
    "name",
    "state",
    "district",
    "type",
    "board",
    "student_count",
    "company_size_category",
    "website",
    "principal_name",
    "email",
    "phone"
]

merged_df = merged_df[final_columns]

# =========================
# SAVE INITIAL CLEAN DATA
# =========================

merged_df.to_csv(
    "data/interim/initial_clean.csv",
    index=False
)


# =========================
# SUMMARY
# =========================

print("Initial cleaning completed successfully")
print("Total rows:", len(merged_df))
print("Saved to: data/interim/initial_clean.csv")