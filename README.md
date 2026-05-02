# KALNET AI-2 — Lead Intelligence System

**System 4 · AI/ML Track · April 2026**
Intern cohort project — KALNET, Hyderabad

---

## What this system builds

A searchable database of 500+ Indian schools and colleges with ICP (Ideal Customer Profile) scores, accessible via a Streamlit dashboard and FastAPI. AI-1 agents query this database to generate personalised outreach emails.

---

## Team

| Name | Role | Files owned |
|---|---|---|
| Vangala Dhathrika | Pod Lead + DB Architect | `database/`, `load_data.py`, `Dashboard/app.py` |
| Ushasree Nirumalla | Scraper Engineer 1 | `Scrapers/udise_scraper.py` |
| **Bhavani Gujjari** | **Scraper Engineer 2** | **`Scrapers/aishe/`, `Scrapers/website_scraper.py`, `Scrapers/justdial_scraper.py`** |
| Chintala Trisha | ICP Scorer | `Cleaning_Scoring/icp_scorer.py` |
| M. Goutham Reddy | API + Dashboard | `main1.py`, `Dashboard/app.py` |
| Sangani Guna Sahithi | Data Cleaning + ML | `Cleaning_Scoring/clean_leads.py` |

---

## Project structure

```
KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM/
│
├── Scrapers/
│   ├── __init__.py
│   ├── aishe/                          ← Bhavani: AISHE college scraper (modular)
│   │   ├── __init__.py                 ← package entry point
│   │   ├── config.py                   ← ALL constants — change URLs/columns here only
│   │   ├── aishe_api.py                ← Approach 1: AISHE HE Directory API
│   │   ├── aishe_excel.py              ← Approach 2: AISHE Annual Excel download
│   │   ├── aishe_fallback.py           ← Approach 3: curated 55-row safety dataset
│   │   └── aishe_main.py               ← orchestrator — run this file
│   ├── website_scraper.py              ← Bhavani: principal name + email
│   ├── justdial_scraper.py             ← Bhavani: phone numbers
│   ├── udise_scraper.py                ← Ushasree: school records from UDISE+
│   └── errors.log                      ← auto-generated: all scraping failures
│
├── data/
│   ├── raw/                            ← all scraped CSVs saved here
│   │   ├── colleges_aishe.csv          ← Bhavani output (Week 1)
│   │   ├── contacts_scraped.csv        ← Bhavani output (Week 2)
│   │   ├── phones_scraped.csv          ← Bhavani output (Week 2)
│   │   └── schools_udise.csv           ← Ushasree output
│   └── processed/
│       └── leads_scored.csv            ← Trisha output (Tier 1 / 2 / 3)
│
├── Cleaning_Scoring/
│   ├── clean_leads.py                  ← Guna Sahithi
│   └── icp_scorer.py                   ← Trisha
│
├── database/
│   ├── __init__.py
│   ├── config.py                       ← DB connection settings
│   └── db_manager.py                   ← Dhathrika: MySQL connection + load
│
├── Dashboard/
│   └── app.py                          ← Dhathrika + Goutham (Streamlit)
│
├── logs/                               ← auto-generated: scraper logs
├── main1.py                            ← Goutham: FastAPI entry point
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/Dhathrika05/KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM.git
cd KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Create required local folders (gitignored — not in the repo)
mkdir data\raw
mkdir data\processed
mkdir logs
```

---

## Data flow

```
AISHE HE Directory  ──►  Scrapers/aishe/aishe_main.py  ──►  data/raw/colleges_aishe.csv   ──┐
UDISE+ Portal       ──►  Scrapers/udise_scraper.py     ──►  data/raw/schools_udise.csv    ──┤
Institution websites ──► Scrapers/website_scraper.py   ──►  data/raw/contacts_scraped.csv ──┤
JustDial listings   ──►  Scrapers/justdial_scraper.py  ──►  data/raw/phones_scraped.csv   ──┤
                                                                                             ▼
                                                                                  database/db_manager.py
                                                                                          │
                                                                                          ▼
                                                                                    MySQL Database
                                                                                 (institutions +
                                                                                  contacts tables)
                                                                                          │
                                                              ┌───────────────────────────┤
                                                              ▼                           ▼
                                                   Cleaning_Scoring/              main1.py (FastAPI)
                                                   clean_leads.py                         │
                                                          │                               ▼
                                                          ▼                       Dashboard/app.py
                                                   icp_scorer.py                   (Streamlit)
                                                          │
                                                          ▼
                                              data/processed/leads_scored.csv
                                                    (Tier 1 / 2 / 3)
```

---

## Running Bhavani's scrapers

Always run in this order — each file depends on the previous output.

```bash
# Week 1 — Run first
# Produces: data/raw/colleges_aishe.csv
python -m Scrapers.aishe.aishe_main

# Week 2 — Run after aishe_main
# Produces: data/raw/contacts_scraped.csv  (principal name + email)
python Scrapers/website_scraper.py

# Week 2 — Run after website_scraper
# Produces: data/raw/phones_scraped.csv  (phone numbers)
python Scrapers/justdial_scraper.py
```

> **Important:** `aishe_main.py` must be run with `python -m` because it uses relative imports inside the `Scrapers/aishe/` package. The other scrapers run directly with `python`.

All output CSV files are saved to `data\raw\`. The folder is created automatically if it does not exist.

---

## How Bhavani's scrapers work

### `Scrapers/aishe/` — AISHE college scraper (modular package)

Split into 5 files so each part can be changed independently without touching the rest:

| File | What it does |
|---|---|
| `config.py` | All constants — target states, API URLs, column name mappings, output path. Only file you need to edit if AISHE changes their structure. |
| `aishe_api.py` | Calls AISHE HE Directory API for each of 5 target states. Has `_get_with_retry()` that retries 3× on timeout with increasing wait times. |
| `aishe_excel.py` | Downloads free AISHE annual Excel from `aishe.gov.in`, filters to target states using vectorised pandas — no `iterrows()`. |
| `aishe_fallback.py` | 204 hardcoded real institutions used only when both API and Excel are unavailable. |
| `aishe_main.py` | Orchestrator — tries API → Excel → fallback. Writes CSV in chunks of 100 rows to avoid memory spikes at 500+ rows. |

Output columns: `name, state, district, type, student_count, website`

### `Scrapers/website_scraper.py`

Reads `colleges_aishe.csv`, visits each institution's About/Contact page, extracts principal name and email using 3 strategies: heading/paragraph keyword search, `mailto:` links, and table row label-value pairs. Expected success rate **60–70%**. All failures logged to `Scrapers/errors.log` — not crashes.

Output columns: `name, principal_name, email, website`

### `Scrapers/justdial_scraper.py`

Searches JustDial for each institution by name and city, extracts phone numbers using 4 strategies (span class, `tel:` links, `data-*` attributes, regex). Saves a checkpoint every 25 rows so a crash never loses all progress.

Output columns: `name, phone, district, state`

---

## Known issues — fix before Week 2

| # | Issue | File | Fix |
|---|---|---|---|
| 1 | `except:` bare except swallows errors silently | `config.py` → `_safe_int()` | Change to `except (ValueError, AttributeError):` |
| 2 | `board` column missing from output | `aishe_main.py` | Add `"board": "University"` to each record |
| 3 | `source` column missing from output | all aishe files | Add `"source": "aishe_api"` / `"aishe_excel"` / `"aishe_fallback"` |

These columns are required by `database/db_manager.py` to load data into MySQL correctly.

---

## Week-by-week milestones

| Week | Bhavani's deliverable | Team milestone |
|---|---|---|
| 1 | `colleges_aishe.csv` — 50+ clean rows, push PR | DB schema live, team unblocked |
| 2 | `contacts_scraped.csv` + `phones_scraped.csv` | 200+ institutions in MySQL |
| 3 | Fix data issues flagged by Sahithi / Trisha | Dashboard live with search |
| 4 | Support integration, demo prep | ICP scoring on all 500 records |

---

## Daily standup (9:30 AM WhatsApp to Dhathrika)

```
Done:    [what you completed yesterday]
Doing:   [what you are working on today]
Blocked: [anything stopping you — write NONE if nothing]
```

Dhathrika sends the compiled summary to Rishav by 10:00 AM.

---

## Git workflow

```bash
# Never push directly to main

# Step 1 — always pull latest before starting
git checkout main
git pull origin main

# Step 2 — create your feature branch
git checkout -b bhavani/aishe-scraper-week1

# Step 3 — stage your files
git add Scrapers/aishe/
git add Scrapers/website_scraper.py
git add Scrapers/justdial_scraper.py
git add data/raw/colleges_aishe.csv
git add requirements.txt
git add README.md

# Step 4 — commit
git commit -m "feat(scraper): add AISHE modular package + website + justdial scrapers"

# Step 5 — push and raise PR
git push origin bhavani/aishe-scraper-week1
# → GitHub → Compare & pull request → assign Dhathrika as reviewer
```

### Commit message format

```
feat(scraper): add AISHE modular package with API + Excel + fallback
fix(scraper): replace bare except with specific exception types
feat(scraper): add website_scraper.py with 3 extraction strategies
feat(scraper): add justdial_scraper.py with checkpoint save every 25 rows
data: add colleges_aishe.csv 55 rows Week 1
docs: update README to reflect new modular Scrapers/aishe/ structure
```

---

## Environment variables (`.env`)

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=kalnet_leads
```

Never commit `.env` to Git — it is already in `.gitignore`.

---

## Requirements

```
requests==2.31.0
beautifulsoup4==4.12.3
lxml==5.1.0
pandas==2.2.1
openpyxl==3.1.2
sqlalchemy==2.0.28
pymysql==1.1.0
fastapi==0.110.0
uvicorn==0.27.1
streamlit==1.32.2
scikit-learn==1.4.1
python-dotenv==1.0.1
```

---

## References

| Source | URL | Used by |
|---|---|---|
| AISHE HE Directory | dashboard.aishe.gov.in/hedirectory | `Scrapers/aishe/aishe_api.py` |
| AISHE Annual Report | aishe.gov.in/aishe-final-report | `Scrapers/aishe/aishe_excel.py` |
| UDISE+ Portal | udiseplus.gov.in | `Scrapers/udise_scraper.py` |
| BeautifulSoup docs | beautiful-soup-4.readthedocs.io | `website_scraper.py`, `justdial_scraper.py` |
| Streamlit docs | docs.streamlit.io | `Dashboard/app.py` |

---

*KALNET · AI-2 Lead Intelligence System · April 2026 · Confidential*