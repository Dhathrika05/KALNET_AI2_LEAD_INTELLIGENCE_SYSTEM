# /scrapers/website_scraper.py

import os
import time
import pandas as pd
import re
from tavily import TavilyClient
from pathlib import Path
from dotenv import load_dotenv

# ============================================
# TAVILY API SETUP
# ============================================

# Load the variables from .env
load_dotenv()

# Get the key from the environment
api_key = os.getenv("TAVILY_API_KEY")

# Initialize the client using the variable
client = TavilyClient(api_key=api_key)


# ============================================
# PATHS
# ============================================

INPUT_FILE = "data/raw/colleges_aishe.csv"
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "contacts_scraped.csv"

# Create directory if needed
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# FILTER WORDS (REMOVE JUNK NAMES)
# ============================================

invalid_words = [
    "college", "campus", "university", "government",
    "department", "faculty", "school", "committee",
    "coordinator", "allumni", "superintendent",
    "office", "contact", "private", "born",
    "welcome", "details", "message", "home",
    "registrar", "dean", "principal office",
    "admission", "director", "chairman",
    "principal email", "our principal", "acting principal"
]


# ============================================
# VALID EMAIL DOMAINS (more official‑flavored scoring)
# ============================================

OFFICIAL_DOMAINS = {
    "edu.in", "ac.in", "org.in", "ac.uk", "edu", "ac.uk",
    "gov.in", "nic.in", "org", "com"  # keep com only if needed
}


def is_likely_official_email(email: str) -> bool:
    if not email:
        return False
    domain = email.split("@")[-1].lower()
    if not domain:
        return False
    if domain.endswith(".png") or domain.endswith(".jpg") or domain.endswith(".jpeg"):
        return False
    if any(domain.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"]):
        return False
    # Prefer .edu.in / .ac.in but don't reject .com outright
    if domain.endswith(".edu.in") or domain.endswith(".ac.in") or domain.endswith(".gov.in"):
        return True
    if domain in OFFICIAL_DOMAINS:
        return True
    return False


# ============================================
# LOAD INPUT CSV
# ============================================

try:
    data = pd.read_csv(INPUT_FILE)
except FileNotFoundError as e:
    print(f"Input file not found: {INPUT_FILE}")
    print("Create this file or adjust path.")
    exit(1)


# ============================================
# OUTPUT STORAGE
# ============================================

results_list = []


# ============================================
# START SCRAPING
# ============================================

for i, row in data.iterrows():
    college_name = str(row.get("name", "")).strip()
    website = str(row.get("website", "")).strip()

    print("\n" + "=" * 40)
    print(f"[{i+1}/{len(data)}] College: {college_name}")

    if not college_name or not website:
        print("Skip: empty name or website.")
        results_list.append({
            "name": college_name,
            "principal_name": None,
            "email": None,
            "website": website,
        })
        continue

    # ============================================
    # BETTER SEARCH QUERY
    # ============================================

    query = (
        f"{college_name} official principal email "
        f"contact about {college_name} site:.edu.in OR site:.ac.in"
    )

    principal_names = set()
    emails = set()

    try:
        # ============================================
        # SEARCH USING TAVILY
        # ============================================

        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=6,
        )

        results = response.get("results", [])

        # ============================================
        # PROCESS SEARCH RESULTS
        # ============================================

        for result in results:
            text = result.get("content", "")
            if not text:
                continue

            # Clean text
            text = re.sub(r"\s+", " ", text)

            # ============================================
            # EXTRACT EMAILS
            # ============================================

            found_emails = re.findall(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                text
            )

            for email in found_emails:
                clean_email = email.strip().lower()

                # Skip obvious image/file emails
                if any(clean_email.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]):
                    continue

                # If it looks like an official email, keep it
                if is_likely_official_email(clean_email):
                    emails.add(clean_email)

            # ============================================
            # EXTRACT PRINCIPAL NAMES
            # ============================================

            # Pattern: "Principal: Dr. Ramesh", "Dr. Ramesh (Principal)", etc.
            principal_patterns = re.findall(
                r"(?:Principal|Dr\.?|Prof\.?|Principal of|Head of|Director)\s*[:,;]?\s*"
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
                text,
                re.IGNORECASE
            )

            for name in principal_patterns:
                clean_name = re.sub(r"\s+", " ", name.strip())

                # Skip short names
                if len(clean_name.split()) < 2:
                    continue

                # Skip numbers, junk, or invalid words
                if re.search(r"\d", clean_name):
                    continue
                if any(
                    word.lower() in clean_name.lower()
                    for word in invalid_words
                ):
                    continue

                principal_names.add(clean_name)

        # ============================================
        # LOG FOUND INFO
        # ============================================

        if principal_names:
            print("\nPrincipal Names:")
            for name in sorted(principal_names):
                print("-", name)
        else:
            print("\nNo principal name found")

        if emails:
            print("\nOfficial Emails:")
            for email in sorted(emails):
                print("-", email)
        else:
            print("\nNo email found")

        # ============================================
        # SAVE RESULT ROW
        # ============================================

        results_list.append({
            "name": college_name,
            "principal_name": (
                ", ".join(sorted(principal_names))
                if principal_names else None
            ),
            "email": (
                ", ".join(sorted(emails))
                if emails else None
            ),
            "website": website,
        })

        # ============================================
        # SAVE CSV CONTINUOUSLY (robust way)
        # ============================================

        # Use a temp file first
        temp_df = pd.DataFrame(results_list)
        temp_path = OUTPUT_FILE.with_suffix(".tmp.csv")

        try:
            temp_df.to_csv(
                temp_path,
                index=False,
                encoding="utf-8",
                errors="replace",  # in case of encoding issue
            )

            # If temp save succeeds, rename over main file
            if temp_path.exists():
                if OUTPUT_FILE.exists():
                    os.remove(OUTPUT_FILE)
                os.replace(temp_path, OUTPUT_FILE)

            print("\n✓ Saved row to contacts_scraped.csv")
        except (PermissionError, OSError) as e:
            print(f"\n⚠️ Could not save to CSV: {e}")
            print("Hint: close Excel / LibreOffice / any app using contacts_scraped.csv")
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

        # ============================================
        # PREVENT API RATE LIMIT
        # ============================================

        time.sleep(2.5)

    except Exception as e:
        print(f"\n❌ Error for {college_name} (website scraper)")
        print(e)

        # Save failed row also
        results_list.append({
            "name": college_name,
            "principal_name": None,
            "email": None,
            "website": website,
        })

        # Try to save even after error
        try:
            temp_df = pd.DataFrame(results_list)
            temp_df.to_csv(
                OUTPUT_FILE,
                index=False,
                encoding="utf-8",
                mode="w",  # overwrite if needed
            )
        except (PermissionError, OSError) as pe:
            print(f"  Also could not save on error: {pe}")

        time.sleep(3)
        continue


# ============================================
# FINAL SAVE (idempotent)
# ============================================

if results_list:
    final_df = pd.DataFrame(results_list)
    final_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
        mode="w",
    )
    print("\n" + "=" * 40)
    print("SCRAPING COMPLETED")
    print(f"✓ Total rows saved: {len(final_df)}")
    print("✓ File saved at:")
    print(OUTPUT_FILE)
    print("=" * 40)
else:
    print("\nNo results were collected.")