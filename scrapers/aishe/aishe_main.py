# scrapers/aishe/aishe_main.py
# ─────────────────────────────────────────────────────────────────────────────
# KALNET AI-2  |  Bhavani Gujjari — Scraper Engineer 2
#
# Responsibility: orchestrate the 3 approaches, deduplicate, write CSV.
# This file has NO scraping logic — it only imports and calls the other modules.
#
# Run:
#     python -m scrapers.aishe.aishe_main
#   or from project root:
#     python scrapers/aishe/aishe_main.py
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys
import logging
import time
from datetime import datetime

import pandas as pd

# ── Path fix when running directly (not as a package) ─────────────────────────
if __name__ == "__main__":
    # Add project root to sys.path so relative imports work
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scrapers.aishe.config import (
    OUTPUT_PATH, LOG_PATH, ERROR_LOG,
    WEEK1_TARGET, OUTPUT_COLUMNS,
)
from scrapers.aishe.aishe_api      import fetch_all_states
from scrapers.aishe.aishe_excel    import fetch_from_excel
from scrapers.aishe.aishe_fallback import get_fallback, count as fallback_count


# ── Logging setup ─────────────────────────────────────────────────────────────

def _setup_logging():
    os.makedirs("logs", exist_ok=True)
    fmt = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

    # Root logger — writes everything to file
    logging.basicConfig(
        filename=ERROR_LOG,
        level=logging.ERROR,
        format=fmt,
    )
    # Module-level logger — also prints INFO to console
    log = logging.getLogger("aishe_main")
    log.setLevel(logging.INFO)
    ch  = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(fmt))
    log.addHandler(ch)
    return log


# ── Deduplication ─────────────────────────────────────────────────────────────

def deduplicate(records: list[dict]) -> list[dict]:
    """
    Removes duplicate colleges by (name, state, district).
    Keeps the first occurrence — API records are preferred since
    aishe_main merges in order: API → Excel → fallback.
    """
    seen  = set()
    clean = []
    for r in records:
        key = (r["name"].lower(), r["state"].lower(), r["district"].lower())
        if key not in seen:
            seen.add(key)
            clean.append(r)
    return clean


# ── Chunked CSV write ─────────────────────────────────────────────────────────

def write_csv(records: list[dict], output_path: str):
    """
    Writes records to CSV in chunks.
    Safe for 500–5000+ rows without memory spikes.
    Overwrites any existing file cleanly.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    CHUNK = 100
    first = True

    for i in range(0, len(records), CHUNK):
        chunk = records[i: i + CHUNK]
        df    = pd.DataFrame(chunk)[OUTPUT_COLUMNS]
        df["website"] = df["website"].fillna("")

        df.to_csv(
            output_path,
            index=False,
            mode="w" if first else "a",
            header=first,
            encoding="utf-8",
        )
        first = False

    print(f"\n  ✓ Written {len(records)} rows in chunks → {output_path}")


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(df: pd.DataFrame, source: str, elapsed: float):
    w = 55
    print("\n" + "=" * w)
    print(f"  AISHE Scraper  |  KALNET AI-2")
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * w)
    print(f"  Source       : {source}")
    print(f"  Total rows   : {len(df)}")
    print(f"  Has website  : {(df['website'] != '').sum()} / {len(df)}")
    print(f"  Time taken   : {elapsed:.1f}s")
    print(f"\n  State breakdown:")
    for state, n in df["state"].value_counts().items():
        print(f"    {state:<20} {n}")
    print(f"\n  Type breakdown:")
    for t, n in df["type"].value_counts().items():
        print(f"    {t:<12} {n}")
    goal = "✓ PASS" if len(df) >= WEEK1_TARGET else "✗ FAIL"
    print(f"\n  Week-1 goal (≥{WEEK1_TARGET}): {goal}")
    print("=" * w)


# ── Main ──────────────────────────────────────────────────────────────────────

def run(output_path: str = OUTPUT_PATH):
    log   = _setup_logging()
    start = time.time()

    print("=" * 55)
    print("  AISHE College Scraper  |  KALNET AI-2")
    print("=" * 55)

    all_records, source = [], "unknown"

    # ── Approach 1: API ───────────────────────────────────────────────────────
    print("\n[1/3] AISHE HE Directory API...")
    api_records = fetch_all_states()
    log.info(f"API returned {len(api_records)} records")

    if len(api_records) >= WEEK1_TARGET:
        all_records = api_records
        source      = "AISHE HE Directory API"
        print(f"\n  ✓ API gave {len(api_records)} rows — done.")
    else:
        print(f"\n  API: {len(api_records)} rows — trying Excel...")

        # ── Approach 2: Excel ─────────────────────────────────────────────────
        print("\n[2/3] AISHE Annual Excel download...")
        excel_records = fetch_from_excel()
        log.info(f"Excel returned {len(excel_records)} records")

        if len(excel_records) >= WEEK1_TARGET:
            # Merge with any API records (API has priority)
            existing  = {(r["name"], r["district"]) for r in api_records}
            new_excel = [r for r in excel_records
                         if (r["name"], r["district"]) not in existing]
            all_records = api_records + new_excel
            source      = "AISHE Excel"
            print(f"\n  ✓ Excel gave {len(all_records)} rows — done.")
        else:
            print(f"\n  Excel: {len(excel_records)} rows — using fallback...")

            # ── Approach 3: Fallback ──────────────────────────────────────────
            print(f"\n[3/3] Curated fallback ({fallback_count()} rows)...")
            existing = {(r["name"], r["district"])
                        for r in api_records + excel_records}
            fallback = get_fallback(exclude_keys=existing)
            all_records = api_records + excel_records + fallback
            source      = "curated fallback (API+Excel unavailable)"
            log.warning(f"Using fallback: {len(fallback)} rows added")
            print(f"  ✓ Fallback added {len(fallback)} rows.")

    # ── Deduplicate ───────────────────────────────────────────────────────────
    before       = len(all_records)
    all_records  = deduplicate(all_records)
    removed      = before - len(all_records)
    if removed:
        print(f"\n  Deduplication: removed {removed} duplicates "
              f"({before} → {len(all_records)})")

    # ── Write ─────────────────────────────────────────────────────────────────
    write_csv(all_records, output_path)

    # ── Summary ───────────────────────────────────────────────────────────────
    df = pd.read_csv(output_path)
    print_summary(df, source, elapsed=time.time() - start)
    log.info(f"Saved {len(df)} rows to {output_path}  |  source={source}")


if __name__ == "__main__":
    run()
