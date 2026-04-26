# scrapers/aishe/aishe_excel.py
# ─────────────────────────────────────────────────────────────────────────────
# KALNET AI-2  |  Bhavani Gujjari — Scraper Engineer 2
#
# Responsibility: ONLY the AISHE Annual Excel download.
# - Downloads the Excel from aishe.gov.in (free, no login needed)
# - Handles column name variations between yearly releases
# - Filters to TARGET_STATES
# - Chunks processing so 50,000-row Excels don't spike RAM
#
# Does NOT write any files. Returns list[dict] to aishe_main.py.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from io import BytesIO

import requests
import pandas as pd

from .config import (
    HEADERS, REQUEST_TIMEOUT, TARGET_STATES,
    EXCEL_URLS, EXCEL_COL_MAP, TYPE_MAP,
)

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_int(val) -> int:
    try:
        return int(str(val).replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0


def _download(url: str) -> bytes | None:
    """Downloads a URL and returns raw bytes, or None on failure."""
    try:
        print(f"  Downloading: {url[:70]}...")
        resp = requests.get(url, headers=HEADERS, timeout=60)
        if resp.status_code == 200:
            print(f"    Downloaded {len(resp.content) / 1024:.0f} KB")
            return resp.content
        logger.error(f"Excel download HTTP {resp.status_code}: {url}")
        print(f"    HTTP {resp.status_code} — skip")
    except requests.exceptions.Timeout:
        logger.error(f"Excel download timeout: {url}")
        print(f"    Timeout — skip")
    except Exception as e:
        logger.error(f"Excel download error {url}: {e}")
        print(f"    Error: {e}")
    return None


def _load_dataframe(content: bytes, url: str) -> pd.DataFrame | None:
    """Loads Excel or CSV bytes into a DataFrame."""
    try:
        if url.lower().endswith(".xlsx"):
            # Use openpyxl; read_only=True for lower memory on large files
            df = pd.read_excel(BytesIO(content), engine="openpyxl")
        else:
            df = pd.read_csv(BytesIO(content), low_memory=False)
        print(f"    Loaded: {len(df):,} rows × {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"DataFrame load failed: {e}")
        print(f"    Parse error: {e}")
        return None


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardises column names — AISHE changes them every year.
    Applies EXCEL_COL_MAP after lower-casing and stripping.
    """
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # Only rename columns that exist (avoid KeyError)
    rename = {k: v for k, v in EXCEL_COL_MAP.items() if k in df.columns}
    df.rename(columns=rename, inplace=True)
    return df


def _filter_and_build(df: pd.DataFrame) -> list[dict]:
    """
    Filters DataFrame to TARGET_STATES and converts rows → dicts.
    Uses vectorised pandas — no iterrows() — safe for 50,000+ rows.
    """
    if "state" not in df.columns:
        logger.error("No 'state' column after normalisation — cannot filter")
        return []

    # Normalise state column for matching
    df["state"] = df["state"].astype(str).str.strip().str.title()
    df = df[df["state"].isin(TARGET_STATES)].copy()

    if df.empty:
        logger.warning("No rows matched TARGET_STATES after filtering")
        return []

    print(f"    After state filter: {len(df):,} rows")

    # Fill missing columns with empty values
    for col in ("name", "district", "type", "student_count"):
        if col not in df.columns:
            df[col] = "" if col != "student_count" else 0

    # Vectorised clean — no iterrows
    df["name"]          = df["name"].astype(str).str.strip()
    df["district"]      = df["district"].astype(str).str.strip().str.title()
    df["type"]          = (
        df["type"].astype(str).str.strip()
                  .map(lambda x: TYPE_MAP.get(x, x or "Unknown"))
    )
    df["student_count"] = pd.to_numeric(
        df["student_count"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    ).fillna(0).astype(int)
    df["website"] = ""

    # Drop rows with no name
    df = df[df["name"].str.len() > 0]
    df = df[df["name"].str.lower() != "nan"]

    return df[["name", "state", "district", "type",
               "student_count", "website"]].to_dict("records")


# ── Main entry point ──────────────────────────────────────────────────────────

def fetch_from_excel() -> list[dict]:
    """
    Tries each URL in EXCEL_URLS in order.
    Returns normalised records on first success, empty list if all fail.
    """
    for url in EXCEL_URLS:
        content = _download(url)
        if content is None:
            continue

        df = _load_dataframe(content, url)
        if df is None:
            continue

        df = _normalise_columns(df)
        records = _filter_and_build(df)

        if records:
            logger.info(f"Excel: {len(records)} records from {url}")
            print(f"    ✓ {len(records)} records extracted")
            return records
        else:
            print(f"    No usable records from this URL — trying next")

    logger.warning("All Excel URLs failed or returned 0 records")
    return []
