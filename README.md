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
| Vangala Dhathrika | Pod Lead + DB Architect | `schema.sql`, `load_data.py`, `dashboard/app.py` |
| Ushasree Nirumalla | Scraper Engineer 1 | `scrapers/udise_scraper.py` |
| **Bhavani Gujjari** | **Scraper Engineer 2** | **`scrapers/aishe_scraper.py`, `scrapers/website_scraper.py`, `scrapers/justdial_scraper.py`** |
| Chintala Trisha | ICP Scorer | `pipeline/icp_scorer.py` |
| M. Goutham Reddy | API + Dashboard | `api/main.py`, `dashboard/app.py` |
| Sangani Guna Sahithi | Data Cleaning + ML | `pipeline/clean_leads.py` |

---

## Project structure

```
KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM/
│
├── scrapers/
│   ├── aishe_scraper.py        ← Bhavani: college records from AISHE
│   ├── website_scraper.py      ← Bhavani: principal name + email
│   ├── justdial_scraper.py     ← Bhavani: phone numbers
│   ├── udise_scraper.py        ← Ushasree: school records from UDISE+
│   └── errors.log              ← auto-generated: all scraping failures
│
├── data/
│   ├── raw/
│   │   ├── colleges_aishe.csv      ← Bhavani output (Week 1)
│   │   ├── contacts_scraped.csv    ← Bhavani output (Week 2)
│   │   ├── phones_scraped.csv      ← Bhavani output (Week 2)
│   │   └── schools_udise.csv       ← Ushasree output
│   └── processed/
│       └── leads_scored.csv        ← Trisha output
│
├── pipeline/
│   ├── clean_leads.py          ← Guna Sahithi
│   └── icp_scorer.py           ← Trisha
│
├── api/
│   └── main.py                 ← Goutham Reddy (FastAPI)
│
├── dashboard/
│   └── app.py                  ← Dhathrika + Goutham (Streamlit)
│
├── schema.sql                  ← Dhathrika: MySQL table definitions
├── load_data.py                ← Dhathrika: CSV → MySQL loader
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

```bash
# 1. Clone
git clone https://github.com/Dhathrika05/KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM.git
cd KALNET_AI2_LEAD_INTELLIGENCE_SYSTEM

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env
# Edit .env — fill in your MySQL host, user, password, database name
```

---

## Data flow

```
AISHE HE Directory  ──►  aishe_scraper.py  ──►  data/raw/colleges_aishe.csv  ──┐
UDISE+ Portal       ──►  udise_scraper.py  ──►  data/raw/schools_udise.csv   ──┤
Institution websites ──► website_scraper.py ──► data/raw/contacts_scraped.csv ─┤
JustDial listings   ──►  justdial_scraper.py ─► data/raw/phones_scraped.csv  ──┤
                                                                                ▼
                                                                       load_data.py
                                                                            │
                                                                            ▼
                                                                      MySQL Database
                                                                    (institutions +
                                                                      contacts tables)
                                                                            │
                                                    ┌───────────────────────┤
                                                    ▼                       ▼
                                            clean_leads.py          FastAPI (main.py)
                                                    │                       │
                                                    ▼                       ▼
                                             icp_scorer.py        Streamlit dashboard
                                                    │                  (app.py)
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
python scrapers/aishe_scraper.py

# Week 2 — Run after aishe_scraper.py
# Produces: data/raw/contacts_scraped.csv  (principal name + email)
python scrapers/website_scraper.py

# Week 2 — Run after website_scraper.py
# Produces: data/raw/phones_scraped.csv  (phone numbers)
python scrapers/justdial_scraper.py
```

All output CSV files are saved to `data\raw\` in the project folder. The folder is created automatically if it does not exist.

### How `aishe_scraper.py` works

Tries 3 approaches in order until one succeeds:

1. **AISHE HE Directory API** — calls `dashboard.aishe.gov.in` API endpoints for each of the 5 target states (MH, TS, DL, KA, TN). Returns college records with name, district, type, enrolment.
2. **AISHE Annual Excel** — downloads the free annual Excel report from `aishe.gov.in`, filters to target states, extracts matching columns.
3. **Curated 55-row fallback** — hardcoded real institutions used only when both live sources (API and Excel) are unavailable. Ensures the pipeline still runs and produces `data/raw/colleges_aishe.csv` even if the AISHE site is down.

Output columns: `name, state, district, type, student_count, website`

### How `website_scraper.py` works

Reads `colleges_aishe.csv`, visits each institution's website About/Contact page, and extracts principal name and email using 3 strategies:

- Strategy 1: Search heading/paragraph tags for keywords like "principal", "director"
- Strategy 2: Find `mailto:` links for email addresses
- Strategy 3: Scan table rows for label-value pairs

Expected success rate: **60–70%**. Failures are logged to `scrapers/errors.log` — not crashes. Falls back to known contacts for well-known institutions.

Output columns: `name, principal_name, email, website`

### How `justdial_scraper.py` works

Searches JustDial for each institution by name and city, extracts phone numbers using 4 strategies (class-based, `tel:` links, `data-*` attributes, regex). Saves a checkpoint every 25 rows so crashes don't lose progress.

Output columns: `name, phone, district, state`

---

## Known issues in current `aishe_scraper.py` — fix before Week 2

| # | Issue | Location | Fix |
|---|---|---|---|
| 1 | `except:` bare except swallows all errors silently | `_safe_int()` and `_normalise_api()` | Change to `except (ValueError, AttributeError):` |
| 2 | `board` column not produced | Output DataFrame | Add `"board": "University"` to each record |
| 3 | `source` column missing | Output DataFrame | Add `"source": "aishe_api"` or `"aishe_fallback"` |

These are needed for Dhathrika's `load_data.py` to work correctly with `schema.sql`.

---

## Week-by-week milestones

| Week | Bhavani's deliverable | Team milestone |
|---|---|---|
| 1 | `colleges_aishe.csv` — 50+ clean rows, push PR | DB schema live, team unblocked |
| 2 | `contacts_scraped.csv` + `phones_scraped.csv` | 200+ institutions in MySQL |
| 3 | Fix data issues flagged by Sahithi/Trisha | Dashboard live with search |
| 4 | Support integration, demo prep | ICP scoring on all 500 records |

---



---

## Git workflow

```bash
# Never push directly to main
# Create your branch
git checkout -b bhavani/aishe-scraper-week1

# Stage and commit
git add scrapers/aishe_scraper.py
git commit -m "feat(scraper): add aishe_scraper.py with 3-approach fallback"

# Push and raise PR
git push origin bhavani/aishe-scraper-week1
# → Open PR on GitHub → request review from Dhathrika
```

### Commit message format

```
feat(scraper): add aishe_scraper.py with API + Excel + fallback
fix(scraper): handle bare except in _safe_int
feat(scraper): add website_scraper.py with 3 extraction strategies
feat(scraper): add justdial_scraper.py with checkpoint save
data: add colleges_aishe.csv 55 rows Week 1
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

Never commit `.env` to Git. It is in `.gitignore`.

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
| AISHE HE Directory | dashboard.aishe.gov.in/hedirectory | `aishe_scraper.py` |
| AISHE Annual Report | aishe.gov.in/aishe-final-report | `aishe_scraper.py` |
| UDISE+ Portal | udiseplus.gov.in | `udise_scraper.py` |
| BeautifulSoup docs | beautiful-soup-4.readthedocs.io | `website_scraper.py`, `justdial_scraper.py` |
| Streamlit docs | docs.streamlit.io | `dashboard/app.py` |

---

*KALNET · AI-2 Lead Intelligence System · April 2026 · Confidential*