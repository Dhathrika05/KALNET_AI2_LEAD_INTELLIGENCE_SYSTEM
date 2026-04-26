# scrapers/aishe/config.py
# ─────────────────────────────────────────────────────────────────────────────
# KALNET AI-2  |  Bhavani Gujjari — Scraper Engineer 2
# Single source of truth for all scraper constants.
# Change values HERE only — never hardcode in other files.
# ─────────────────────────────────────────────────────────────────────────────

# ── Output ────────────────────────────────────────────────────────────────────
OUTPUT_PATH  = "data/raw/colleges_aishe.csv"
LOG_PATH     = "logs/aishe_scraper.log"
ERROR_LOG    = "logs/errors.log"

# ── Scale targets ─────────────────────────────────────────────────────────────
WEEK1_TARGET = 50        # minimum rows for Week-1 standup
WEEK3_TARGET = 500       # final target across full project

# ── States & codes ────────────────────────────────────────────────────────────
TARGET_STATES = [
    "Maharashtra",
    "Telangana",
    "Delhi",
    "Karnataka",
    "Tamil Nadu",
]

STATE_CODES = {
    "Maharashtra": "MH",
    "Telangana":   "TS",
    "Delhi":       "DL",
    "Karnataka":   "KA",
    "Tamil Nadu":  "TN",
}

# Numeric state IDs used by some AISHE endpoints
STATE_IDS = {
    "Maharashtra": 27,
    "Telangana":   36,
    "Delhi":       7,
    "Karnataka":   29,
    "Tamil Nadu":  33,
}

# ── Type normalisation ────────────────────────────────────────────────────────
TYPE_MAP = {
    "Government":           "Govt",
    "Government Aided":     "Aided",
    "Private Unaided":      "Private",
    "Private (Un-Aided)":   "Private",
    "Private (Aided)":      "Aided",
    "Private":              "Private",
    "Central Government":   "Govt",
    "State Government":     "Govt",
    "Aided":                "Aided",
    "Govt":                 "Govt",
    "University":           "Govt",
}

# ── HTTP headers ──────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/html, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer":         "https://dashboard.aishe.gov.in/",
}

# ── Request tuning ────────────────────────────────────────────────────────────
REQUEST_TIMEOUT  = 15    # seconds per HTTP request
SLEEP_BETWEEN    = 1.2   # seconds between requests (be polite)
MAX_RETRIES      = 3     # retry count on timeout/5xx
PAGE_SIZE        = 100   # records per API page

# ── API endpoints ─────────────────────────────────────────────────────────────
API_BASE         = "https://dashboard.aishe.gov.in"
API_STATE_URL    = API_BASE + "/api/v1/college/state/{state_code}"
API_PAGINATED    = (
    API_BASE
    + "/hedirectory/api/v1/getColleges"
    "?stateCode={state_code}&pageNo={page}&pageSize={page_size}"
)

# ── Excel download URLs (try in order) ────────────────────────────────────────
EXCEL_URLS = [
    "https://aishe.gov.in/aishe/aishePublicReports/aisheAllHEIReport_21_22.xlsx",
    "https://aishe.gov.in/aishe/aishePublicReports/aisheAllHEIReport_20_21.xlsx",
    (
        "https://data.gov.in/backend/dms/v1/ogdp/resource/download/"
        "d7c97a54dfe44eaf87d37dd4e86c5d06/csv/data.csv"
    ),
]

# Column rename map for Excel files (AISHE changes names every year)
EXCEL_COL_MAP = {
    "hei_name":             "name",
    "institution_name":     "name",
    "name_of_institution":  "name",
    "college_name":         "name",
    "university_name":      "name",
    "state_name":           "state",
    "district_name":        "district",
    "management_type":      "type",
    "management":           "type",
    "type_of_institution":  "type",
    "total_enrolment":      "student_count",
    "total_enrollment":     "student_count",
    "enrolment":            "student_count",
    "enrollment":           "student_count",
}

# ── Output columns — EXACT, in order ─────────────────────────────────────────
OUTPUT_COLUMNS = ["name", "state", "district", "type", "student_count", "website"]

# ── Chunk size for writing large CSVs ────────────────────────────────────────
WRITE_CHUNK_SIZE = 100   # write to CSV every N records (avoids memory spikes)
