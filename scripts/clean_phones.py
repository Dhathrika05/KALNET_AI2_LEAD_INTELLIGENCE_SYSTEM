import pandas as pd
import re
import os

def normalize_name(name):
    if pd.isna(name):
        return ""
    # Lowercase, remove special characters and extra spaces
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    return name

def clean_phone(phone):
    if pd.isna(phone) or phone == "":
        return None
    
    phone_str = str(phone).strip()
    
    # If it's a landline (starts with 0 and contains a hyphen)
    if phone_str.startswith('0') and '-' in phone_str:
        # Preserve proper landline formatting as requested
        return phone_str
    
    # Remove all non-numeric characters for general cleaning
    cleaned = re.sub(r'\D', '', phone_str)
    
    # Basic validation
    if len(cleaned) < 8 or len(cleaned) > 15:
        return None
    
    # Mobile number logic (usually 10 digits in India)
    # If it starts with 0 and length is 11, it might be a mobile with leading zero OR a landline
    # If it's a landline (without hyphen), we should keep the zero.
    # If it's a mobile, we might strip it.
    # But to be safe and "preserve landline formatting", we keep the zero if it's 11 digits starting with 0.
    
    # If starts with 91 and length is 12, it's likely country code + mobile
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
        
    # Remove obviously fake numbers
    if re.match(r'^0+$', cleaned) or re.match(r'^1+$', cleaned) or cleaned == '0000000020':
        return None
        
    return cleaned

def start_cleaning():
    scraped_path = r'c:\Users\poolt\Desktop\data cleaning\KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM\data\raw\phones_scraped.csv'
    leads_path = r'c:\Users\poolt\Desktop\data cleaning\KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM\data\processed\cleaned_leads.csv'
    
    print(f"Loading scraped data from {scraped_path}...")
    df_scraped = pd.read_csv(scraped_path)
    
    print(f"Loading leads data from {leads_path}...")
    df_leads = pd.read_csv(leads_path)
    
    # Clean scraped phone numbers
    print("Cleaning scraped phone numbers...")
    df_scraped['phone_cleaned'] = df_scraped['phone'].apply(clean_phone)
    
    # Normalize names for matching
    df_scraped['name_norm'] = df_scraped['name'].apply(normalize_name)
    df_leads['name_norm'] = df_leads['name'].apply(normalize_name)
    
    # Create a mapping from normalized name to cleaned phone
    phone_map = df_scraped.dropna(subset=['phone_cleaned']).set_index('name_norm')['phone_cleaned'].to_dict()
    
    print("Updating phone numbers in leads...")
    def update_phone(row):
        # If phone is already present and not empty, keep it? 
        # Or update it if it's empty.
        if pd.isna(row['phone']) or str(row['phone']).strip() == "":
            return phone_map.get(row['name_norm'], row['phone'])
        return row['phone']
    
    df_leads['phone'] = df_leads.apply(update_phone, axis=1)
    
    # Remove the helper column
    df_leads = df_leads.drop(columns=['name_norm'])
    
    # Save back to cleaned_leads.csv
    print(f"Saving updated leads to {leads_path}...")
    df_leads.to_csv(leads_path, index=False)
    print("Cleaning and update process completed successfully.")

if __name__ == "__main__":
    start_cleaning()
