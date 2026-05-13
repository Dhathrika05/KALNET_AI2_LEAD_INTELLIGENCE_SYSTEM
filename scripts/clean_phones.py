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
    phones_path = r'c:\Users\poolt\Desktop\data cleaning\KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM\data\raw\phones_scraped.csv'
    contacts_path = r'c:\Users\poolt\Desktop\data cleaning\KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM\data\raw\contacts_scraped.csv'
    leads_path = r'c:\Users\poolt\Desktop\data cleaning\KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM\data\processed\cleaned_leads.csv'
    
    print(f"Loading raw data...")
    df_phones = pd.read_csv(phones_path)
    df_contacts = pd.read_csv(contacts_path)
    df_leads = pd.read_csv(leads_path)
    
    # Clean phone numbers from phones_scraped
    print("Cleaning phone numbers...")
    df_phones['phone_cleaned'] = df_phones['phone'].apply(clean_phone)
    
    # Normalize names for matching across all files
    df_phones['name_norm'] = df_phones['name'].apply(normalize_name)
    df_contacts['name_norm'] = df_contacts['name'].apply(normalize_name)
    df_leads['name_norm'] = df_leads['name'].apply(normalize_name)
    
    # Create mappings
    phone_map = df_phones.dropna(subset=['phone_cleaned']).set_index('name_norm')['phone_cleaned'].to_dict()
    email_map = df_contacts.dropna(subset=['email']).set_index('name_norm')['email'].to_dict()
    principal_map = df_contacts.dropna(subset=['principal_name']).set_index('name_norm')['principal_name'].to_dict()
    website_map = df_contacts.dropna(subset=['website']).set_index('name_norm')['website'].to_dict()
    
    print("Updating leads data with information from raw files...")
    
    def enrich_row(row):
        # Update phone if empty
        if pd.isna(row['phone']) or str(row['phone']).strip() == "":
            row['phone'] = phone_map.get(row['name_norm'], row['phone'])
            
        # Update email if empty
        if pd.isna(row['email']) or str(row['email']).strip() == "":
            row['email'] = email_map.get(row['name_norm'], row['email'])
            
        # Update principal_name if empty
        if pd.isna(row['principal_name']) or str(row['principal_name']).strip() == "":
            row['principal_name'] = principal_map.get(row['name_norm'], row['principal_name'])
            
        # Update website if empty
        if pd.isna(row['website']) or str(row['website']).strip() == "":
            row['website'] = website_map.get(row['name_norm'], row['website'])
            
        return row
    
    df_leads = df_leads.apply(enrich_row, axis=1)
    
    # Remove helper column
    df_leads = df_leads.drop(columns=['name_norm'])
    
    # Save back to cleaned_leads.csv
    print(f"Saving enriched leads to {leads_path}...")
    df_leads.to_csv(leads_path, index=False)
    print("Enrichment process completed successfully.")

if __name__ == "__main__":
    start_cleaning()
