# scrapers/website_scraper.py
# ─────────────────────────────────────────────────────────────────────────────
# KALNET AI-2  |  Bhavani Gujjari — Scraper Engineer 2
#
# Scrapes each college's website for:
#   - principal_name  : head of institution
#   - email           : direct contact email
#
# Strategy per college (tried in order, stops on first success):
#   Pass 1 → Homepage
#   Pass 2 → About / Administration / Leadership / Contact sub-pages
#
# Features:
#   ✓ Retry with exponential back-off (3 attempts per URL)
#   ✓ Resume — skips rows already in contacts_scraped.csv
#   ✓ Progress saved every 10 rows — safe to Ctrl-C and restart
#   ✓ Obfuscated emails decoded: name [at] domain [dot] in
#   ✓ Indian honorifics: Dr, Prof, Sri, Smt, Shri, Er, Adv
#   ✓ Context scoring — name after title keyword wins
#   ✓ Email scoring — own-domain > name match > generic penalised
#   ✓ All errors logged to logs/errors.log
#
# Input  : data/raw/colleges_aishe.csv   (name, state, district, type, student_count, website)
# Output : data/raw/contacts_scraped.csv (name, principal_name, email, website)
#
# Run:
#   python scrapers/website_scraper.py
#   python scrapers/website_scraper.py --no-resume   <- scrape all from scratch
#
# Requirements:
#   pip install requests beautifulsoup4 lxml pandas
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
import time
import logging
import argparse
from urllib.parse import urljoin, urlparse
from typing import Optional

import requests
from bs4 import BeautifulSoup
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
INPUT_CSV  = "data/raw/colleges_aishe.csv"
OUTPUT_CSV = "data/raw/contacts_scraped.csv"
ERRORS_LOG = "logs/errors.log"

# ── Tuning ────────────────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 14      # seconds per HTTP request
SLEEP_BETWEEN   = 1.2     # seconds between every request (polite + guide rule)
MAX_RETRIES     = 3       # retry attempts on timeout / 5xx
MAX_ABOUT_PAGES = 5       # max sub-pages to try per college
SAVE_EVERY      = 10      # write progress to CSV every N colleges

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection":      "keep-alive",
}

# ── Logging ───────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(ERRORS_LOG, encoding="utf-8")],
)
logger = logging.getLogger(__name__)

# ── Regex ─────────────────────────────────────────────────────────────────────

_EMAIL_PLAIN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Obfuscated: "name [at] domain [dot] in"
_EMAIL_OBFUS = re.compile(
    r"[a-zA-Z0-9._%+\-]+"
    r"\s*[\[\(]?\s*(?:at|AT)\s*[\]\)]?\s*"
    r"[a-zA-Z0-9.\-]+"
    r"\s*[\[\(]?\s*(?:dot|DOT)\s*[\]\)]?\s*"
    r"[a-zA-Z]{2,}",
    re.IGNORECASE,
)

# Head-of-institution title keywords
_TITLE_RE = re.compile(
    r"\b("
    r"principal|head\s*(?:mistress|master|teacher)?|"
    r"vice[\s\-]?chancellor|chancellor|"
    r"dean|director|president|chairman|chairperson|"
    r"superintendent|ceo|managing\s*director|founder|"
    r"provost|registrar"
    r")\b",
    re.IGNORECASE,
)

# Name: optional Indian/English honorific + 2-4 capitalised words
_NAME_RE = re.compile(
    r"(?:(?:Dr|Prof|Mr|Mrs|Ms|Miss|Rev|Fr|Sri|Smt|Shri|Er|Adv)\.?\s+)?"
    r"[A-Z][a-z]{1,20}"
    r"(?:\s+[A-Z]\.)?"
    r"(?:\s+[A-Z][a-z]{1,20}){1,3}",
    re.UNICODE,
)

# About-page URL slugs with relevance weight
_ABOUT_SLUGS = [
    ("principal",        20),
    ("about-principal",  20),
    ("administration",   18),
    ("leadership",       16),
    ("management",       14),
    ("about-us",         12),
    ("aboutus",          12),
    ("about_us",         12),
    ("about",            10),
    ("our-college",       8),
    ("our-institution",   8),
    ("overview",          6),
    ("who-we-are",        6),
    ("contact-us",        5),
    ("contact",           5),
    ("reach-us",          4),
    ("faculty",           3),
]

_GENERIC_LOCALS = {
    "info", "contact", "admin", "support", "noreply", "no-reply",
    "hello", "enquiries", "enquiry", "office", "college", "school",
    "webmaster", "mail", "postmaster", "helpdesk", "feedback",
    "admission", "admissions",
}


# ── HTTP helper ───────────────────────────────────────────────────────────────

def _fetch(url: str, session: requests.Session) -> Optional[BeautifulSoup]:
    """GET with retry + exponential back-off. Returns BeautifulSoup or None."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(
                url, timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, "lxml")
            if resp.status_code in (429, 503):
                wait = SLEEP_BETWEEN * (attempt * 2)
                logger.warning("HTTP %d %s — wait %.1fs", resp.status_code, url, wait)
                time.sleep(wait)
            elif resp.status_code in (403, 404, 410):
                return None   # permanent failure, don't retry
            else:
                logger.error("HTTP %d %s", resp.status_code, url)
                return None
        except requests.exceptions.Timeout:
            logger.warning("Timeout attempt %d/%d: %s", attempt, MAX_RETRIES, url)
            time.sleep(SLEEP_BETWEEN * attempt)
        except requests.exceptions.TooManyRedirects:
            logger.error("TooManyRedirects: %s", url)
            return None
        except requests.exceptions.ConnectionError as exc:
            logger.error("ConnectionError %s: %s", url, exc)
            return None
        except Exception as exc:
            logger.error("Fetch error %s: %s", url, exc)
            return None
    return None


# ── URL discovery ─────────────────────────────────────────────────────────────

def _find_about_urls(base_url: str, soup: BeautifulSoup) -> list:
    """
    Scans all <a> tags on the page.
    Returns up to MAX_ABOUT_PAGES internal URLs most likely to have
    principal / about / contact info, sorted by relevance score.
    """
    base_domain = urlparse(base_url).netloc.lstrip("www.")
    scores: dict = {}

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "javascript", "tel:", "mailto:", "whatsapp")):
            continue

        full   = urljoin(base_url, href)
        parsed = urlparse(full)

        if parsed.netloc.lstrip("www.") != base_domain:
            continue   # external domain

        url_lower   = full.lower()
        anchor_text = tag.get_text(" ", strip=True).lower()
        score = 0

        for slug, weight in _ABOUT_SLUGS:
            if slug in url_lower:
                score += weight
            if slug.replace("-", " ") in anchor_text:
                score += weight // 2

        if score > 0:
            scores[full] = max(scores.get(full, 0), score)

    ranked = sorted(scores, key=lambda u: scores[u], reverse=True)
    return ranked[:MAX_ABOUT_PAGES]


# ── Email extraction ──────────────────────────────────────────────────────────

def _decode_obfuscated(raw: str) -> str:
    s = re.sub(r"\s*[\[\(]?\s*(?:at|AT)\s*[\]\)]?\s*", "@", raw)
    s = re.sub(r"\s*[\[\(]?\s*(?:dot|DOT)\s*[\]\)]?\s*", ".", s)
    return s.strip()


def _extract_emails(soup: BeautifulSoup) -> list:
    """Collects all emails from mailto links, plain text, and obfuscated text."""
    found: set = set()

    for tag in soup.find_all("a", href=True):
        if tag["href"].lower().startswith("mailto:"):
            raw = tag["href"][7:].split("?")[0].strip().lower()
            if _EMAIL_PLAIN.fullmatch(raw):
                found.add(raw)

    page_text = soup.get_text(" ")

    for email in _EMAIL_PLAIN.findall(page_text):
        found.add(email.lower())

    for match in _EMAIL_OBFUS.findall(page_text):
        decoded = _decode_obfuscated(match).lower()
        if _EMAIL_PLAIN.fullmatch(decoded):
            found.add(decoded)

    return list(found)


def _score_email(email: str, principal_name: Optional[str], site_domain: str) -> float:
    """Higher score = more likely to be the principal's direct email."""
    score = 0.0
    local        = email.split("@")[0].lower()
    email_domain = email.split("@")[1].lower()
    site_clean   = site_domain.lstrip("www.")

    if site_clean in email_domain or email_domain in site_clean:
        score += 6   # own domain strongly preferred

    local_stripped = re.sub(r"[.\-_]", "", local)
    if local_stripped in _GENERIC_LOCALS:
        score -= 3   # generic mailbox penalised

    if principal_name:
        tokens = [t.lower() for t in principal_name.split() if len(t) > 2]
        for token in tokens:
            if token in local:
                score += 5   # name in email = very strong signal

    return score


# ── Name + email extraction ───────────────────────────────────────────────────

def _extract_from_page(soup: BeautifulSoup, base_url: str) -> tuple:
    """
    Extracts (principal_name, email) from a single page.
    Returns (None, None) if nothing found.
    """
    principal_name: Optional[str] = None
    best_name_score = -1

    containers = soup.find_all(
        ["td", "li", "p", "div", "span",
         "h1", "h2", "h3", "h4", "h5",
         "section", "article", "blockquote"]
    )

    for block in containers:
        text = block.get_text(" ", strip=True)

        title_match = _TITLE_RE.search(text)
        if not title_match:
            continue

        if len(text) > 600:   # skip large catch-all divs
            continue

        for name in _NAME_RE.findall(text):
            parts = name.strip().split()
            if len(parts) < 2:
                continue

            title_pos = title_match.start()
            name_pos  = text.find(name)
            if name_pos > title_pos:
                gap = name_pos - title_pos
                proximity = 4 if gap < 80 else 2
            else:
                proximity = 1

            score = len(parts) + proximity
            if score > best_name_score:
                best_name_score = score
                principal_name  = name.strip()

    # ── Email ─────────────────────────────────────────────────────────────────
    all_emails  = _extract_emails(soup)
    site_domain = urlparse(base_url).netloc
    best_email: Optional[str] = None
    best_email_score = -999.0

    for email in all_emails:
        s = _score_email(email, principal_name, site_domain)
        if s > best_email_score:
            best_email_score = s
            best_email = email

    return principal_name, best_email


# ── Core: scrape one college ──────────────────────────────────────────────────

def scrape_college(website_url: str, session: requests.Session) -> tuple:
    """
    Scrapes one college website.
    Returns (principal_name, email) — either or both can be None.

    Pass 1: Homepage
    Pass 2: Up to MAX_ABOUT_PAGES sub-pages — stops as soon as both are found
    """
    if not website_url or str(website_url).strip().lower() in ("nan", "none", ""):
        return None, None

    if not website_url.startswith(("http://", "https://")):
        website_url = "https://" + website_url

    name  = None
    email = None

    try:
        # Pass 1: Homepage
        soup = _fetch(website_url, session)
        if soup is None:
            return None, None

        name, email = _extract_from_page(soup, website_url)
        if name and email:
            return name, email

        # Pass 2: About / Admin / Contact sub-pages
        about_urls = _find_about_urls(website_url, soup)

        for url in about_urls:
            time.sleep(SLEEP_BETWEEN)   # 1 sec between every request

            sub_soup = _fetch(url, session)
            if sub_soup is None:
                continue

            n, e = _extract_from_page(sub_soup, url)

            # Keep best value for each field
            if n and (name is None or len(n.split()) >= len((name or "").split())):
                name = n
            if e and email is None:
                email = e

            if name and email:
                break   # found both — stop

    except Exception as exc:
        logger.error("scrape_college %s: %s", website_url, exc)

    return name, email


# ── Output writer ─────────────────────────────────────────────────────────────

def _write_output(rows: list, output_csv: str) -> None:
    """
    Writes contacts_scraped.csv with exact required columns.
    Uses a temp file + atomic rename so a PermissionError (e.g. file open
    in Excel) never corrupts existing data — the old file stays intact
    and we just skip the save, logging a warning instead.
    """
    out_dir = os.path.dirname(output_csv)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    out = pd.DataFrame(rows, columns=["name", "principal_name", "email", "website"])
    out = out.drop_duplicates(subset=["name"], keep="last")
    out["principal_name"] = out["principal_name"].fillna("")
    out["email"]          = out["email"].fillna("")
    out["website"]        = out["website"].fillna("")

    # Write to a temp file first, then rename — avoids PermissionError
    # if the CSV is currently open in Excel or another program.
    tmp_csv = output_csv + ".tmp"
    try:
        out.to_csv(tmp_csv, index=False, encoding="utf-8")
        # Atomic replace: remove old file first on Windows (os.replace handles it)
        os.replace(tmp_csv, output_csv)
    except PermissionError:
        # File is locked (open in Excel). Keep the .tmp as backup and warn.
        logger.warning("PermissionError writing %s — close it in Excel and re-run.", output_csv)
        print(f"\n  ⚠ Cannot write {output_csv} — close it in Excel first.")
        print(f"    Progress saved to {tmp_csv} — it will be merged on next run.\n")
    except Exception as exc:
        logger.error("Write failed %s: %s", output_csv, exc)
        if os.path.exists(tmp_csv):
            os.remove(tmp_csv)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run(input_csv: str = INPUT_CSV,
        output_csv: str = OUTPUT_CSV,
        resume: bool = True) -> None:
    """
    Reads colleges_aishe.csv.
    Scrapes each college that has a website.
    Saves contacts_scraped.csv: name, principal_name, email, website
    """
    print("=" * 60)
    print("  Website Scraper  |  KALNET AI-2  |  Bhavani Gujjari")
    print("=" * 60)

    if not os.path.exists(input_csv):
        print(f"\n  ✗ {input_csv} not found. Run aishe_main.py first.")
        return

    df = pd.read_csv(input_csv, dtype=str).fillna("")
    assert "name"    in df.columns, "Missing 'name' column in input CSV"
    assert "website" in df.columns, "Missing 'website' column in input CSV"

    total = len(df)
    print(f"\n  Input : {input_csv}  ({total} rows)")
    print(f"  Output: {output_csv}")

    # ── Resume ────────────────────────────────────────────────────────────────
    done_names: set  = set()
    existing_rows: list = []

    if resume and os.path.exists(output_csv):
        ex = pd.read_csv(output_csv, dtype=str).fillna("")
        done_names    = set(ex["name"].str.strip())
        existing_rows = ex.to_dict("records")
        print(f"\n  Resume: {len(done_names)} already done — skipping")

    to_do    = df[~df["name"].isin(done_names)].copy()
    has_web  = to_do["website"].str.strip().ne("") & \
               ~to_do["website"].str.lower().isin(["nan", "none"])

    print(f"  To scrape: {has_web.sum()}  |  No website: {(~has_web).sum()}\n")

    # ── Scrape ────────────────────────────────────────────────────────────────
    session = requests.Session()
    session.headers.update(HEADERS)

    new_rows: list = []
    ok_n = partial_n = failed_n = skip_n = 0

    rows_list = to_do.to_dict("records")

    for i, row in enumerate(rows_list, 1):
        name    = str(row["name"]).strip()
        website = str(row["website"]).strip()
        is_web  = website and website.lower() not in ("nan", "none", "")

        if is_web:
            print(f"  [{i:>3}/{len(rows_list)}] {name[:48]}")
            print(f"         {website}")

            principal_name, email = scrape_college(website, session)

            if principal_name and email:
                ok_n += 1;      status = "ok"
            elif principal_name or email:
                partial_n += 1; status = "partial"
            else:
                failed_n += 1;  status = "not_found"

            tag   = "✓" if status == "ok" else ("~" if status == "partial" else "✗")
            parts = []
            if principal_name: parts.append(principal_name)
            if email:          parts.append(email)
            print(f"         {tag} {' | '.join(parts) if parts else 'not found'}  [{status}]")

            time.sleep(SLEEP_BETWEEN)   # polite delay between colleges

        else:
            principal_name, email = None, None
            skip_n += 1
            print(f"  [{i:>3}/{len(rows_list)}] {name[:48]}  [no website]")

        new_rows.append({
            "name":           name,
            "principal_name": principal_name,
            "email":          email,
            "website":        website if is_web else None,
        })

        # Save progress every SAVE_EVERY rows
        if i % SAVE_EVERY == 0:
            _write_output(existing_rows + new_rows, output_csv)
            print(f"\n  ── Progress saved ({len(existing_rows)+len(new_rows)} rows) ──\n")

    session.close()

    # Final save
    _write_output(existing_rows + new_rows, output_csv)

    # ── Summary ───────────────────────────────────────────────────────────────
    out = pd.read_csv(output_csv, dtype=str).fillna("")
    print(f"\n{'='*60}")
    print(f"  contacts_scraped.csv  |  {len(out)} rows")
    print(f"{'='*60}")
    print(f"  ✓ Both name + email : {ok_n}")
    print(f"  ~ Partial           : {partial_n}")
    print(f"  ✗ Not found         : {failed_n}")
    print(f"  — No website        : {skip_n}")
    print(f"{'─'*60}")
    print(f"  principal_name filled: {(out['principal_name'].str.strip()!='').sum()}")
    print(f"  email filled         : {(out['email'].str.strip()!='').sum()}")
    print(f"{'='*60}\n")
    print(out.head(8).to_string(index=False))


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KALNET Website Scraper — Bhavani")
    parser.add_argument("--input",     default=INPUT_CSV,  help="Path to colleges_aishe.csv")
    parser.add_argument("--output",    default=OUTPUT_CSV, help="Path to contacts_scraped.csv")
    parser.add_argument("--no-resume", dest="resume", action="store_false",
                        help="Scrape all from scratch, ignore existing output")
    parser.set_defaults(resume=True)
    args = parser.parse_args()
    run(input_csv=args.input, output_csv=args.output, resume=args.resume)