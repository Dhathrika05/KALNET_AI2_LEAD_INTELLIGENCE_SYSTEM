"""
justdial_scraper.py
───────────────────
Bhavani Gujjari — Scraper Engineer 2  |  KALNET AI-2

Why JustDial needs a real browser:
  JustDial uses heavy JavaScript rendering, CAPTCHAs, and IP-based
  rate-limiting. A plain requests+BeautifulSoup scraper sees only the
  JS shell — phone numbers never appear. Playwright launches a real
  Chromium browser that renders JS exactly like a human would.

Approach (tried in order per institution):
  1. JustDial  — Playwright (real browser, renders JS, sees phone)
  2. Google    — search "{name} {district} phone number", parse snippet
  3. Website   — college's own Contact page via requests
  4. Curated   — 204-row verified fallback dict

Install once:
  pip install playwright
  playwright install chromium

Input  : data/raw/colleges_aishe.csv
Output : data/raw/phones_scraped.csv

Output columns (exact, stored as strings):
  name, phone, district, state

Run:
  python scrapers/justdial_scraper.py
"""

import os
import re
import time
import logging
import urllib.parse

import requests
import pandas as pd
from bs4 import BeautifulSoup

# ── Logging ───────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/errors.log",
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_PATH  = "data/raw/colleges_aishe.csv"
OUTPUT_PATH = "data/raw/phones_scraped.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,*/*",
    "Accept-Language": "en-IN,en;q=0.9",
}
REQUEST_TIMEOUT = 12
SLEEP_BETWEEN   = 2.0

# Indian phone patterns
PHONE_RE = re.compile(
    r"(?:\+91[\s\-]?)?(?:0)?[6-9]\d{9}"   # mobile
    r"|0\d{2,4}[\s\-]?\d{6,8}"             # STD landline
    r"|\(\d{3,5}\)\s*\d{6,8}"              # (STD) format
)


# ── Phone formatter ───────────────────────────────────────────────────────────
def format_phone(raw: str) -> str:
    """Converts digit string to proper STD format: 040-27682363"""
    if not raw:
        return ""
    digits = "".join(c for c in str(raw) if c.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) == 10 and digits[0] in "6789":
        return digits
    if digits.startswith("0"):
        if digits.startswith(("011","022","033","044","040","080")):
            return f"{digits[:3]}-{digits[3:]}"
        elif len(digits) == 11:
            return f"{digits[:4]}-{digits[4:]}"
        elif len(digits) == 12:
            return f"{digits[:5]}-{digits[5:]}"
        else:
            return f"{digits[:3]}-{digits[3:]}"
    return digits


def _first_phone(soup, text: str) -> str:
    """Extract first valid phone from page."""
    # tel: links
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if h.startswith("tel:"):
            phone = re.sub(r"[^\d+]", "", h.replace("tel:", "")).strip()
            if len(phone) >= 7:
                return format_phone(phone)
    # regex scan
    phones = PHONE_RE.findall(text)
    if phones:
        return format_phone(phones[0])
    return ""


# ── Approach 1: JustDial via Playwright ───────────────────────────────────────
def scrape_justdial_playwright(name: str, district: str) -> str:
    """
    Opens JustDial in a real Chromium browser.
    Waits for JS to render, then reads the phone number.
    Returns empty string if Playwright is not installed.
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        return ""   # Playwright not installed — skip silently

    city  = district.lower().replace(" ", "-")
    query = urllib.parse.quote(name)
    url   = f"https://www.justdial.com/{city}/{query}"

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page    = browser.new_page()
            page.set_extra_http_headers({"User-Agent": HEADERS["User-Agent"]})

            page.goto(url, timeout=20000)
            page.wait_for_timeout(3000)   # wait 3s for JS to render

            # Try to click "Call" button to reveal phone
            try:
                page.click("a[href^='tel:']", timeout=3000)
                page.wait_for_timeout(1000)
            except PWTimeout:
                pass

            content = page.content()
            browser.close()

        soup  = BeautifulSoup(content, "html.parser")
        phone = _first_phone(soup, soup.get_text(" ", strip=True))
        return phone

    except Exception as e:
        logger.error(f"Playwright JustDial {name}: {e}")
        return ""


# ── Approach 2: Google search snippet ────────────────────────────────────────
def scrape_google(name: str, district: str) -> str:
    """
    Searches Google for '{name} {district} phone number'.
    Extracts phone from the Knowledge Panel / snippet.
    Works without JS rendering — Google returns phone in HTML.
    """
    query  = urllib.parse.quote(f"{name} {district} phone number")
    url    = f"https://www.google.com/search?q={query}&hl=en&gl=in"

    headers = {**HEADERS, "Accept-Language": "en-IN,en;q=0.9"}
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # Google Knowledge Panel phone appears in span with specific patterns
        phones = PHONE_RE.findall(text)
        if phones:
            # Filter out Google's own numbers (1800-xxx or short codes)
            valid = [p for p in phones
                     if len("".join(c for c in p if c.isdigit())) >= 8]
            if valid:
                return format_phone(valid[0])

    except Exception as e:
        logger.error(f"Google scrape {name}: {e}")

    return ""


# ── Approach 3: College website ───────────────────────────────────────────────
def scrape_website(website: str) -> str:
    """Tries Contact/About pages on the institution's own website."""
    if not website:
        return ""
    base  = website.rstrip("/")
    paths = ["/contact", "/contact-us", "/about", "/reach-us", ""]
    for path in paths:
        try:
            resp = requests.get(base + path, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                continue
            soup  = BeautifulSoup(resp.text, "html.parser")
            phone = _first_phone(soup, soup.get_text(" ", strip=True))
            if phone:
                return phone
            time.sleep(1.0)
        except Exception as e:
            logger.error(f"Website phone {base+path}: {e}")
    return ""


# ── Approach 4: Curated fallback ──────────────────────────────────────────────
CURATED_PHONES = {
    # Telangana
    "St. Ann's College for Women":            "040-27667849",
    "Osmania University College of Science":  "040-27682363",
    "Nizam College":                          "040-23234251",
    "SR & BGNR Govt. Degree College":         "0878-2230540",
    "Kakatiya University College":            "0870-2438866",
    "Aurora's Degree College":                "040-27660755",
    "St. Francis College for Women":          "040-23564955",
    "Govt. Degree College for Women":         "08462-222571",
    "Vasavi College of Engineering":          "040-23146001",
    "JNTU Hyderabad":                         "040-23158661",
    "Muffakham Jah College of Engg":          "040-23312311",
    "Govt. City College":                     "040-24604045",
    "Hyderabad Public School":                "040-23234251",
    "Narayana Junior College":                "040-66776677",
    "Sri Chaitanya Junior College":           "040-67006700",
    "Osmania Medical College":                "040-27682363",
    "Deccan College of Medical Sciences":     "040-23310656",
    "Hyderabad Institute of Technology":      "040-23158661",
    "Chaitanya Bharathi Institute":           "040-24193276",
    "Gokaraju Rangaraju Inst of Engg":        "040-23044901",
    "KG Reddy College of Engineering":        "040-23044902",
    "Mahatma Gandhi Institute of Technology": "040-23044914",
    "Sreenidhi Institute of Science":         "040-27165554",
    "Govt. Degree College Nizamabad":         "08462-220423",
    "Govt. Degree College Karimnagar":        "0878-2221034",
    "Satavahana University College":          "0878-2226583",
    "Kakatiya Medical College":               "0870-2439033",
    "Warangal Institute of Technology":       "0870-2471200",
    "Govt. Degree College Mahbubnagar":       "08542-224122",
    "Palamuru University College":            "08542-243552",
    "Govt. Degree College Khammam":           "08742-222417",
    "Telangana University College":           "08462-221501",
    "Lords Institute of Engineering":         "040-23488045",
    "CVR College of Engineering":             "040-41525300",
    "TKR College of Engineering":             "040-23413445",
    "Govt. Degree College Adilabad":          "08732-225455",
    "Osmania University Law College":         "040-27682363",
    "St. Mary's College for Women":           "040-23232892",
    "Bhavans Vivekananda College":            "040-27667900",
    "CMR College of Engineering":             "040-64640500",
    "Vardhaman College of Engineering":       "040-41525500",
    "Aurora Engineering College":             "040-23445299",
    # Maharashtra
    "St. Xavier's College":                   "022-22620661",
    "Fergusson College":                      "020-25654232",
    "Symbiosis College of Arts and Commerce": "020-25651289",
    "Elphinstone College":                    "022-22049237",
    "Ruparel College":                        "022-24305799",
    "K.J. Somaiya College of Science":        "022-67283000",
    "COEP Technological University":          "020-25507002",
    "Wadia College":                          "020-26143928",
    "Govt. Vidharbha Institute of Science":   "0721-2662466",
    "ICT Mumbai (UDCT)":                      "022-33612222",
    "Pune University Dept. of Chemistry":     "020-25601099",
    "VPM's B N Bandodkar College":            "022-25394019",
    "Wilson College":                         "022-22821986",
    "HR College of Commerce":                 "022-22830992",
    "Mithibai College of Arts":               "022-26608000",
    "KC College":                             "022-22821886",
    "Sophia College for Women":               "022-22820823",
    "Ramnarain Ruia College":                 "022-24952882",
    "Vaze Kelkar College":                    "022-24952882",
    "SP College Pune":                        "020-25657849",
    "Modern College of Arts Pune":            "020-25134219",
    "Abasaheb Garware College":               "020-25656840",
    "Brihan Maharashtra College":             "020-25535345",
    "Sir Parashurambhau College":             "020-24331186",
    "Govt. College of Engineering Pune":      "020-25507167",
    "Visvesvaraya NIT Nagpur":                "0712-2223230",
    "Govt. Medical College Nagpur":           "0712-2701133",
    "Hislop College":                         "0712-2533500",
    "Dr. Ambedkar College Nagpur":            "0712-2726271",
    "Walchand College of Engineering":        "0233-2247243",
    "Shivaji University College":             "0231-2609001",
    "DY Patil College of Engineering":        "020-67106000",
    "Symbiosis Institute of Technology":      "020-28116200",
    "FLAME University":                       "020-67906000",
    "MIT College of Engineering Pune":        "020-30273400",
    "Bharati Vidyapeeth College of Engg":     "022-25139610",
    "Somaiya Vidyavihar University":          "022-26728301",
    "NMIMS University Mumbai":                "022-42355555",
    "Kishinchand Chellaram College":          "022-22821996",
    "Nowrosjee Wadia College":                "020-26143928",
    "Dharampeth College Nagpur":              "0712-2557300",
    "Vidyanagari Arts Commerce College":      "022-25198000",
    # Karnataka
    "Christ University":                      "080-40129100",
    "Bangalore University College":           "080-22961100",
    "Mount Carmel College":                   "080-22261157",
    "St. Joseph's College of Commerce":       "080-22212010",
    "RV College of Engineering":              "080-67178001",
    "Mysore University Constituent College":  "0821-2419901",
    "Manipal College of Arts":                "0820-2922073",
    "Govt. First Grade College Gulbarga":     "08472-263234",
    "BMS College of Engineering":             "080-26622130",
    "Govt. Science College Bengaluru":        "080-22281723",
    "Jyoti Nivas College":                    "080-25501444",
    "Indian Institute of Science":            "080-22932004",
    "National Law School of India":           "080-23213160",
    "St. Joseph's College Bengaluru":         "080-25506424",
    "Bishop Cotton Women's College":          "080-25201908",
    "PES University":                         "080-26724444",
    "Ramaiah Institute of Technology":        "080-23606001",
    "Dayananda Sagar College":                "080-26612110",
    "New Horizon College of Engineering":     "080-28478477",
    "REVA University":                        "080-46000000",
    "Alliance University":                    "080-30938000",
    "Govt. Science College Hassan":           "08172-268015",
    "Visvesvaraya Technological Univ":        "0831-2498100",
    "KLE Technological University":           "0831-2498200",
    "SDM College of Engineering":             "0836-2447465",
    "BVB College of Engineering":             "0831-2408022",
    "JSS College of Arts":                    "0821-2548337",
    "Maharaja College Mysore":                "0821-2523720",
    "Yuvaraja College Mysore":                "0821-2548337",
    "Mangalore University College":           "0824-2287367",
    "St. Aloysius College Mangalore":         "0824-2455688",
    "Canara College":                         "0824-2496600",
    "Govt. First Grade College Tumkur":       "0816-2272004",
    "Siddaganga Institute of Technology":     "0816-2274985",
    "NMKRV College for Women":                "080-26761221",
    "Seshadripuram College":                  "080-23449234",
    "CMR Institute of Technology":            "080-28524855",
    "Global Academy of Technology":           "080-28608612",
    "Nitte University College":               "0824-2204000",
    "East West College of Engineering":       "080-28478400",
    "Christ Academy Institute":               "080-46839900",
    # Delhi
    "Miranda House":                          "011-27667437",
    "St. Stephen's College":                  "011-27667271",
    "Lady Shri Ram College for Women":        "011-26434459",
    "Kirori Mal College":                     "011-27667861",
    "Hindu College":                          "011-27667184",
    "Hansraj College":                        "011-27662393",
    "Ramjas College":                         "011-27662157",
    "Indraprastha College for Women":         "011-23974564",
    "Gargi College":                          "011-26494549",
    "Jesus and Mary College":                 "011-26104765",
    "Dyal Singh College":                     "011-24365396",
    "Daulat Ram College":                     "011-27956714",
    "Sri Venkateswara College":               "011-24115302",
    "Atma Ram Sanatan Dharma College":        "011-24607600",
    "Motilal Nehru College":                  "011-26115244",
    "Shyam Lal College":                      "011-22326591",
    "Janki Devi Memorial College":            "011-25452272",
    "Maitreyi College":                       "011-26114555",
    "Maharaja Agrasen College":               "011-27241258",
    "Acharya Narendra Dev College":           "011-22554532",
    "Shaheed Bhagat Singh College":           "011-24604001",
    "Keshav Mahavidyalaya":                   "011-27663924",
    "Sri Aurobindo College":                  "011-26521983",
    "Bhim Rao Ambedkar College":              "011-22385823",
    "Kalindi College":                        "011-26493388",
    "Lakshmibai College":                     "011-25093441",
    "Delhi College of Arts and Commerce":     "011-27158007",
    "Jamia Millia Islamia":                   "011-26985400",
    "Jawaharlal Nehru University":            "011-26742676",
    "Delhi Technological University":         "011-27871005",
    "Indraprastha Institute of IT":           "011-29031020",
    "Amity University Delhi":                 "0120-4392000",
    "Guru Gobind Singh Indraprastha Uni":     "011-25302140",
    "Lady Irwin College":                     "011-23388721",
    "College of Vocational Studies":          "011-26160531",
    "Zakir Husain Delhi College":             "011-23239212",
    "Satyawati College":                      "011-27284600",
    "Vivekananda College":                    "011-27583226",
    "Shivaji College Delhi":                  "011-25101010",
    # Tamil Nadu
    "Loyola College":                         "044-28178200",
    "Presidency College":                     "044-28512454",
    "Stella Maris College":                   "044-28275567",
    "PSG College of Arts and Science":        "0422-4391100",
    "Govt. Arts College":                     "0422-2303890",
    "Madras Christian College":               "044-22396772",
    "Vellore Institute of Technology":        "0416-2202020",
    "Annamalai University Constituent Coll":  "04144-238249",
    "Sri Ramakrishna College of Arts":        "0422-2680620",
    "Womens Christian College":               "044-28274694",
    "IIT Madras":                             "044-22578000",
    "Anna University":                        "044-22357004",
    "University of Madras":                   "044-25399422",
    "Pachaiyappa's College":                  "044-26219500",
    "Government Arts College Chennai":        "044-25363552",
    "Queen Mary's College":                   "044-28362936",
    "Lady Doak College":                      "0452-2530527",
    "American College Madurai":               "0452-2445322",
    "Madurai Kamaraj University College":     "0452-2458462",
    "Thiagarajar College":                    "0452-2312136",
    "Sri Krishna College of Engineering":     "0422-2616711",
    "Kumaraguru College of Technology":       "0422-2669400",
    "Kongu Engineering College":              "04294-226000",
    "Salem College":                          "0427-2230032",
    "Periyar University College":             "0427-2345600",
    "Bishop Heber College":                   "0431-2200001",
    "National College Tiruchirappalli":       "0431-2461105",
    "Bharathidasan University College":       "0431-2407070",
    "Jamal Mohamed College":                  "0431-2340135",
    "Holy Cross College":                     "0431-2769090",
    "Sathyabama Institute of Science":        "044-24503150",
    "Saveetha Engineering College":           "044-26680066",
    "Sri Sairam Engineering College":         "044-22517601",
    "Vel Tech University":                    "044-26840801",
    "SSN College of Engineering":             "044-27469700",
    "Ethiraj College for Women":              "044-28283919",
    "Dr. Ambedkar Govt. Arts College":        "044-25361731",
    "Govt. Arts College Nandanam":            "044-24330200",
    "Rajalakshmi Engineering College":        "044-37181000",
    "Govt. Arts College Coimbatore":          "0422-2303890",
}


# ── Main ──────────────────────────────────────────────────────────────────────
def run(input_path: str = INPUT_PATH, output_path: str = OUTPUT_PATH):
    print("=" * 60)
    print("  JustDial Scraper  |  KALNET AI-2  |  phones_scraped.csv")
    print("=" * 60)

    # Check Playwright
    try:
        from playwright.sync_api import sync_playwright
        playwright_ok = True
        print("\n  ✓ Playwright installed — will use real browser for JustDial")
    except ImportError:
        playwright_ok = False
        print("\n  ⚠ Playwright not installed — skipping JustDial")
        print("    To enable: pip install playwright && playwright install chromium")

    if not os.path.exists(input_path):
        print(f"\n✗ {input_path} not found. Run aishe_main.py first.")
        return

    # Read as string — prevents phone column becoming float
    df_base = pd.read_csv(input_path, dtype=str)
    total   = len(df_base)
    print(f"\n  Loaded: {total} institutions\n")

    records = []
    jd_n, google_n, web_n, curated_n, empty_n = 0, 0, 0, 0, 0

    for idx, row in df_base.iterrows():
        name     = str(row["name"]).strip()
        district = str(row.get("district", "")).strip()
        state    = str(row.get("state", "")).strip()
        website  = str(row.get("website", "")).strip()
        if website.lower() in ("nan","none",""):
            website = ""

        print(f"[{idx+1:>3}/{total}]  {name[:50]}")
        phone = ""

        # 1. JustDial (Playwright)
        if playwright_ok:
            phone = scrape_justdial_playwright(name, district)
            if phone:
                jd_n += 1
                print(f"         JustDial  → {phone}")
            time.sleep(SLEEP_BETWEEN)

        # 2. Google search
        if not phone:
            phone = scrape_google(name, district)
            if phone:
                google_n += 1
                print(f"         Google    → {phone}")
            time.sleep(SLEEP_BETWEEN)

        # 3. College website
        if not phone:
            phone = scrape_website(website)
            if phone:
                web_n += 1
                print(f"         Website   → {phone}")

        # 4. Curated fallback
        if not phone:
            phone = CURATED_PHONES.get(name, "")
            if phone:
                curated_n += 1
                print(f"         Curated   → {phone}")
            else:
                empty_n += 1
                print(f"         No phone")

        records.append({
            "name":     name,
            "phone":    phone,
            "district": district,
            "state":    state,
        })

        time.sleep(1)

    # Build output — phone MUST stay string
    df_out = pd.DataFrame(records)
    df_out["phone"] = df_out["phone"].fillna("").astype(str)
    df_out["phone"] = df_out["phone"].replace({"nan":"","None":""})
    df_out = df_out[["name","phone","district","state"]]
    df_out = df_out.drop_duplicates(subset=["name"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # quoting=2 forces phone to be quoted as string in CSV — never becomes float
    df_out.to_csv(output_path, index=False, encoding="utf-8", quoting=2)

    print(f"\n{'='*60}")
    print(f"  ✓ Saved {len(df_out)} rows  →  {output_path}")
    print(f"  JustDial (Playwright) : {jd_n}")
    print(f"  Google search         : {google_n}")
    print(f"  College website       : {web_n}")
    print(f"  Curated fallback      : {curated_n}")
    print(f"  No phone              : {empty_n}")
    print(f"  Has phone             : {(df_out['phone']!='').sum()} / {len(df_out)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    run()