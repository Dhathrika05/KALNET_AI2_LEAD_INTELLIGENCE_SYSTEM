# scrapers/aishe/aishe_api.py
# ─────────────────────────────────────────────────────────────────────────────
# KALNET AI-2  |  Bhavani Gujjari — Scraper Engineer 2
#
# Responsibility: ONLY the AISHE HE Directory API calls.
# - Fetches college records per state via two endpoint patterns
# - Normalises raw API dicts into the output schema
# - Retries on timeout / 5xx errors
# - Logs failures to logs/errors.log
#
# Does NOT write any files. Returns a list[dict] to aishe_main.py.
# ─────────────────────────────────────────────────────────────────────────────

import time
import logging

import requests

from .config import (
    HEADERS, REQUEST_TIMEOUT, SLEEP_BETWEEN, MAX_RETRIES,
    PAGE_SIZE, API_STATE_URL, API_PAGINATED,
    STATE_CODES, STATE_IDS, TARGET_STATES,
    TYPE_MAP, OUTPUT_COLUMNS,
)

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_int(val) -> int:
    try:
        return int(str(val).replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0


def _get_with_retry(url: str, params: dict | None = None) -> requests.Response | None:
    """
    GET request with up to MAX_RETRIES attempts.
    Returns Response on success, None on all failures.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 503):
                # Rate-limited or server overloaded — wait longer
                wait = SLEEP_BETWEEN * (attempt * 3)
                logger.warning(f"HTTP {resp.status_code} on {url} — waiting {wait}s")
                time.sleep(wait)
            else:
                logger.error(f"HTTP {resp.status_code} on {url}")
                return None
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout attempt {attempt}/{MAX_RETRIES}: {url}")
            time.sleep(SLEEP_BETWEEN * attempt)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"ConnectionError: {url} — {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {url} — {e}")
            return None
    return None


def normalise_record(raw: dict, state_name: str) -> dict | None:
    """
    Maps a raw API dict → clean output schema dict.
    Returns None if the record has no usable name.
    """
    # Try every key name the API might use for college name
    name = (
        raw.get("collegeName") or raw.get("college_name") or
        raw.get("name")        or raw.get("institutionName") or
        raw.get("heiName")     or raw.get("university_name") or ""
    ).strip()

    if not name:
        return None

    district = (
        raw.get("districtName") or raw.get("district_name") or
        raw.get("district") or ""
    ).strip().title()

    mgmt_raw = (
        raw.get("managementType") or raw.get("management_type") or
        raw.get("management")     or raw.get("type") or ""
    ).strip()

    enrol = _safe_int(
        raw.get("totalEnrolment") or raw.get("total_enrolment") or
        raw.get("enrolment")      or raw.get("totalStudents") or 0
    )

    return {
        "name":          name,
        "state":         state_name.strip().title(),
        "district":      district,
        "type":          TYPE_MAP.get(mgmt_raw, mgmt_raw or "Unknown"),
        "student_count": enrol,
        "website":       "",       # filled by website_scraper later
    }


# ── Endpoint A: state-level list ──────────────────────────────────────────────

def fetch_state_list(state_name: str, state_code: str) -> list[dict]:
    """
    Endpoint A — returns all colleges for a state in one response.
    Fast but may not be paginated.
    """
    url  = API_STATE_URL.format(state_code=state_code)
    resp = _get_with_retry(url)
    if resp is None:
        return []

    try:
        data     = resp.json()
        colleges = data if isinstance(data, list) else data.get("data", [])
        if colleges:
            logger.info(f"API-A: {len(colleges)} rows for {state_name}")
            print(f"    API-A: {len(colleges)} rows for {state_name}")
        return colleges or []
    except Exception as e:
        logger.error(f"API-A JSON parse {state_name}: {e}")
        return []


# ── Endpoint B: paginated ─────────────────────────────────────────────────────

def fetch_paginated(state_name: str, state_code: str) -> list[dict]:
    """
    Endpoint B — paginated API.
    Fetches page by page until no more results.
    Designed to handle thousands of records without memory issues:
    yields one page at a time (generator) so caller can stream to disk.
    """
    records = []

    for page in range(1, 9999):   # effectively unlimited pages
        url  = API_PAGINATED.format(
            state_code=state_code, page=page, page_size=PAGE_SIZE
        )
        resp = _get_with_retry(url)
        if resp is None:
            logger.warning(f"API-B: no response on page {page} for {state_name}")
            break

        try:
            data = resp.json()
        except Exception as e:
            logger.error(f"API-B JSON parse {state_name} p{page}: {e}")
            break

        batch = (
            data.get("data") or data.get("result") or
            data.get("colleges") or
            (data if isinstance(data, list) else [])
        )

        if not batch:
            break   # no more pages

        records.extend(batch)
        logger.info(f"API-B {state_name} p{page}: {len(batch)} rows")
        print(f"    API-B page {page}: {len(batch)} rows  ({len(records)} total)")

        if len(batch) < PAGE_SIZE:
            break   # last page

        time.sleep(SLEEP_BETWEEN)

    return records


# ── Main entry point ──────────────────────────────────────────────────────────

def fetch_all_states() -> list[dict]:
    """
    Fetches colleges for all TARGET_STATES.
    Tries Endpoint A first; falls back to Endpoint B per state.
    Returns normalised records ready for DataFrame.
    """
    all_records = []

    for state_name in TARGET_STATES:
        state_code = STATE_CODES[state_name]
        print(f"\n  [{state_name}]")

        # Try A first (faster, single call)
        raw = fetch_state_list(state_name, state_code)

        # If A gives nothing, try B (paginated)
        if not raw:
            print(f"    API-A empty — trying API-B (paginated)...")
            raw = fetch_paginated(state_name, state_code)

        # Normalise
        cleaned = [r for r in (normalise_record(x, state_name) for x in raw) if r]
        print(f"  ✓ {state_name}: {len(cleaned)} clean records")
        all_records.extend(cleaned)

        time.sleep(SLEEP_BETWEEN)

    return all_records
