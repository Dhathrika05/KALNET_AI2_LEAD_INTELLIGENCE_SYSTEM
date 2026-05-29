# KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM

## Overview

KALNET AI-2 Lead Intelligence System is a college lead intelligence platform designed to collect, clean, score, and serve  institutional data for search and prioritization.

The system processes college data, stores it in PostgreSQL, exposes APIs using FastAPI, and provides a dashboard to search and explore college data from the database.

## Features

-   College data collection and scraping
-   Data cleaning and preprocessing
-   Rule-based ICP scoring
-   PostgreSQL database integration
-   FastAPI backend APIs
-   Swagger UI API documentation
-   Streamlit dashboard for searching college data
-   Deployment support through Render

## Tech Stack

-   Python
-   PostgreSQL
-   SQLAlchemy
-   FastAPI
-   Streamlit
-   Pandas
-   Swagger UI
-   Render

## System Workflow

``` text
Scraping → Cleaning → ICP Scoring → Database → API → Dashboard
```

## Project Structure

``` text
KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM/
│── api/
│   ├── main.py
│
│── clean_sscoring/
│   └── icp_scorer.py
│
│── Dashboard/
│   └── app.py
│
│── data/
│   ├── raw/
│   │   ├── colleges_aishe.csv
│   │   ├── contacts_scraped.csv
│   │   └── phones_scraped.csv
│   │
│   ├── interim/
│   │   └── initial_clean.csv
│   │
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
```

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

Based on the total score, institutions are categorized into ICP tiers.

## API

### Endpoint

``` text
/leads
```

### Swagger Documentation

After running FastAPI:

``` text
/docs
```

Swagger UI can be used to test APIs and view request/response formats.

## Dashboard

The dashboard is used to search and explore college data stored in
PostgreSQL.

It supports: - searching institutional records - filtering available
lead data - viewing ICP scoring information

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
streamlit run Dashboard/app.py
```

## Deployment

The project is deployed using Render.

## Future Improvements

-   Advanced filtering and analytics
-   Better lead prioritization
-   Improved contact extraction
-   ML-based scoring enhancements (future scope)

## Status

Current system includes: - Data cleaning - ICP scoring - Database
integration - API integration - Dashboard functionality - Deployment
readiness
