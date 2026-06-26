# KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM

## Overview

KALNET AI-2 Lead Intelligence System is a college lead intelligence platform designed to collect, clean, score, and serve institutional data for search and prioritization.

The system processes college data, stores it in PostgreSQL, exposes APIs using FastAPI, and provides a React-based dashboard to search, filter, and explore college data from the database.

## Features

-   College data collection and scraping
-   Data cleaning and preprocessing
-   Rule-based ICP scoring
-   PostgreSQL database integration
-   FastAPI backend APIs
-   Swagger UI API documentation
-   React dashboard for searching college data with CSV upload option
-   Deployment support through Vercel

## Tech Stack

-   Python
-   PostgreSQL
-   SQLAlchemy
-   FastAPI
-   React
-   Pandas
-   Swagger UI
-   Render

## System Workflow

Scraping → Cleaning → ICP Scoring → Database → API → Dashboard

## Project Structure

KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM/
│── api/
│   └── main.py
│
│── clean_scoring/
│   └── icp_scorer.py
│
│── dashboard/
│   └── frontend/   # React app folder
│       ├── src/
│       └── public/
│
│── data/
│   ├── raw/
│   │   ├── colleges_aishe.csv
│   │   ├── contacts_scraped.csv
│   │   └── phones_scraped.csv
│
│   ├── interim/
│   │   └── initial_clean.csv
│
│   └── processed/
│       ├── cleaned_leads.csv
│       └── leads_scored.csv
│
│── database/
│   ├── config.py
│   ├── db_manager.py
│   └── .env
│
│── scrapers/
│   ├── aishe/
│   ├── justdial_scraper.py
│   └── website_scraper.py
│
│── scripts/
│   ├── clean_leads.py
│   └── load_data.py
│
├── requirements.txt
└── README.md
## Scarper

### Overview

The Scraper Module is responsible for collecting and enriching institutional lead data from multiple sources. It forms the first stage of the KALNET AI-2 Lead Intelligence pipeline.

### AISHE Scraper

The AISHE (All India Survey on Higher Education) scraper collects core institutional information.

#### Extracted Fields

* name
* state
* district
* type
* student_count
* website

#### Output

`data/raw/colleges_aishe.csv`

The AISHE scraper acts as the master dataset for all subsequent enrichment processes.

---

### Website Scraper

The Website Scraper enriches institutional records by extracting contact information from official institution websites.

#### Extracted Fields

* principal_name
* email
* website

#### Output

`data/raw/contacts_scraped.csv`

#### Features

* Searches official institution websites
* Extracts official email addresses
* Attempts principal name identification
* Filters invalid or non-official emails
* Supports continuous CSV saving for fault tolerance

---

### JustDial Scraper

The JustDial Scraper enriches institutional records with phone numbers.

#### Extraction Strategy

The scraper follows a multi-stage fallback approach:

1. JustDial using Playwright (real browser rendering)
2. Google Search snippets
3. Institution website contact pages
4. Curated verified fallback database

#### Output

`data/raw/phones_scraped.csv`

#### Extracted Fields

* name
* phone
* district
* state

#### Features

* JavaScript-rendered page support using Playwright
* Multiple fallback mechanisms
* Phone number normalization and formatting
* Error logging and retry handling
* Duplicate prevention

---

### Design Principle

Raw institutional data and enriched contact data are stored separately to maintain data quality and ensure easier validation, updating, and downstream processing.
         
         **JustDial Scraper (scrapers/justdial_scraper.py)** – Extracts phone numbers of institutions.
         **Website Scraper (scrapers/website_scraper.py)** – Extracts email addresses from institution websites.

Raw scraped files are stored in:
             data/raw
**Data Processing**
         - Raw datasets are merged and cleaned.
         - Cleaned data is saved as:
                          data/interim/initial_clean.csv
After manual verification, the final dataset is saved as:
                          data/processed/cleaned_leads.csv
## Database Schema

**Table:** `institutions`

Columns: - name 
         - state 
         - district 
         - type 
         - board 
         - student_count 
         - company_size_category 
         - website 
         - principal_name 
         - email 
         - phone 
         - icp_score 
         - icp_tier

## ICP Scoring Logic

The project uses rule-based ICP scoring to prioritize institutions.

  Condition                      Score
  ---------------------------- -------
  Private institution              +25
  Target state                     +20
  Medium / Large institution       +20
  Website available                +10
  Email available                  +15
  Principal name available         +10

ICP Tier:

         ≥70 → Tier 1
         ≥40 → Tier 2
         Else → Tier 3

Based on the total score, institutions are categorized into ICP tiers.

## API

### Endpoint

/leads


### Swagger Documentation

After running FastAPI:

/docs


Swagger UI can be used to test APIs and view request/response formats.

## Dashboard

The React-based dashboard allows:

         - Searching and filtering institutional records
         - Viewing ICP scoring information
         - Uploading CSVs for bulk lead import

## Setup Instructions

### 1. Clone Repository

``` bash
git clone <repo-url>
cd KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM
```

### 2. Install Dependencies

``` bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Update `.env` with PostgreSQL credentials.

Example:

``` env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kalnet_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### 4. Run FastAPI

``` bash
uvicorn api.main:app --reload
```

### 5. Open Swagger UI

``` text
http://127.0.0.1:8000/docs
```

### 6. Run Dashboard

``` bash
cd dashboard/frontend
npm install
npm run dev
```

## Deployment

The project is deployed using vercel.

## Future Improvements

-   Advanced filtering and analytics
-   Better lead prioritization
-   Improved contact extraction
-   ML-based scoring enhancements (future scope)

## Status

Current system includes:   - Data cleaning 
                           - ICP scoring 
                           - Database integration 
                           - API integration 
                           - Dashboard functionality 
                           - Deployment readiness
