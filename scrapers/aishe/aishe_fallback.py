# scrapers/aishe/aishe_fallback.py
# ─────────────────────────────────────────────────────────────────────────────
# KALNET AI-2  |  Bhavani Gujjari — Scraper Engineer 2
#
# Responsibility: curated 55-row dataset of real Indian colleges.
# Used ONLY when API and Excel both fail.
# All institutions verified manually — real names, real websites.
#
# To add more rows: append tuples to FALLBACK_DATA following the same format.
# To update a website: change it here only.
# ─────────────────────────────────────────────────────────────────────────────

from .config import OUTPUT_COLUMNS

# ── Data ──────────────────────────────────────────────────────────────────────
# Columns: (name, state, district, type, student_count, website)

FALLBACK_DATA: list[tuple] = [

    # ── Telangana (12) ────────────────────────────────────────────────────────
    ("St. Ann's College for Women",            "Telangana",   "Hyderabad",  "Private", 1200,  "https://stanns.edu.in"),
    ("Osmania University College of Science",  "Telangana",   "Hyderabad",  "Govt",    5000,  "https://www.osmania.ac.in"),
    ("Nizam College",                          "Telangana",   "Hyderabad",  "Govt",    3200,  "https://nizamcollege.ac.in"),
    ("SR & BGNR Govt. Degree College",         "Telangana",   "Karimnagar", "Govt",    1800,  ""),
    ("Kakatiya University College",            "Telangana",   "Warangal",   "Govt",    4500,  "https://www.kakatiya.ac.in"),
    ("Aurora's Degree College",                "Telangana",   "Hyderabad",  "Private", 900,   "https://www.auroradegree.ac.in"),
    ("St. Francis College for Women",          "Telangana",   "Hyderabad",  "Aided",   1400,  "https://www.stfranciscollege.ac.in"),
    ("Govt. Degree College for Women",         "Telangana",   "Nizamabad",  "Govt",    2100,  ""),
    ("Vasavi College of Engineering",          "Telangana",   "Hyderabad",  "Aided",   3600,  "https://www.vasavicollege.ac.in"),
    ("JNTU Hyderabad",                         "Telangana",   "Hyderabad",  "Govt",    8000,  "https://www.jntuh.ac.in"),
    ("Muffakham Jah College of Engg",          "Telangana",   "Hyderabad",  "Aided",   2800,  "https://www.mjcollege.ac.in"),
    ("Govt. City College",                     "Telangana",   "Hyderabad",  "Govt",    2400,  ""),

    # ── Maharashtra (12) ──────────────────────────────────────────────────────
    ("St. Xavier's College",                   "Maharashtra", "Mumbai",     "Aided",   3500,  "https://www.xaviers.edu"),
    ("Fergusson College",                      "Maharashtra", "Pune",       "Aided",   4200,  "https://www.fergusson.edu"),
    ("Symbiosis College of Arts and Commerce", "Maharashtra", "Pune",       "Private", 2800,  "https://www.symbiosiscollege.edu.in"),
    ("Elphinstone College",                    "Maharashtra", "Mumbai",     "Govt",    3100,  "https://www.elphinstone.ac.in"),
    ("Ruparel College",                        "Maharashtra", "Mumbai",     "Aided",   2900,  "https://www.ruparelcollege.org"),
    ("K.J. Somaiya College of Science",        "Maharashtra", "Mumbai",     "Private", 3400,  "https://kjssc.somaiya.edu"),
    ("COEP Technological University",          "Maharashtra", "Pune",       "Govt",    5600,  "https://www.coep.org.in"),
    ("Wadia College",                          "Maharashtra", "Pune",       "Aided",   1600,  "https://www.wadiacollege.edu.in"),
    ("Govt. Vidharbha Institute of Science",   "Maharashtra", "Amravati",   "Govt",    2200,  ""),
    ("ICT Mumbai (UDCT)",                      "Maharashtra", "Mumbai",     "Govt",    1800,  "https://www.ictmumbai.edu.in"),
    ("Pune University Dept. of Chemistry",     "Maharashtra", "Pune",       "Govt",    1200,  "https://www.unipune.ac.in"),
    ("VPM's B N Bandodkar College",            "Maharashtra", "Thane",      "Aided",   2100,  "https://www.bnbandodkar.edu.in"),

    # ── Karnataka (11) ────────────────────────────────────────────────────────
    ("Christ University",                      "Karnataka",   "Bengaluru",  "Private", 6000,  "https://www.christuniversity.in"),
    ("Bangalore University College",           "Karnataka",   "Bengaluru",  "Govt",    3800,  "https://www.bangaloreuniversity.ac.in"),
    ("Mount Carmel College",                   "Karnataka",   "Bengaluru",  "Aided",   3200,  "https://www.mountcarmelcollegeblr.ac.in"),
    ("St. Joseph's College of Commerce",       "Karnataka",   "Bengaluru",  "Aided",   2700,  "https://www.sjcc.edu.in"),
    ("RV College of Engineering",              "Karnataka",   "Bengaluru",  "Private", 5500,  "https://www.rvce.edu.in"),
    ("Mysore University Constituent College",  "Karnataka",   "Mysuru",     "Govt",    4100,  "https://uni-mysore.ac.in"),
    ("Manipal College of Arts",                "Karnataka",   "Udupi",      "Private", 2500,  "https://www.manipal.edu"),
    ("Govt. First Grade College Gulbarga",     "Karnataka",   "Kalaburagi", "Govt",    1900,  ""),
    ("BMS College of Engineering",             "Karnataka",   "Bengaluru",  "Aided",   4700,  "https://www.bmsce.ac.in"),
    ("Govt. Science College Bengaluru",        "Karnataka",   "Bengaluru",  "Govt",    2300,  ""),
    ("Jyoti Nivas College",                    "Karnataka",   "Bengaluru",  "Aided",   2800,  "https://www.jyotinivascollege.edu.in"),

    # ── Delhi (10) ────────────────────────────────────────────────────────────
    ("Miranda House",                          "Delhi",       "Delhi",      "Govt",    2900,  "https://www.mirandahouse.ac.in"),
    ("St. Stephen's College",                  "Delhi",       "Delhi",      "Aided",   1600,  "https://www.ststephens.edu"),
    ("Lady Shri Ram College for Women",        "Delhi",       "Delhi",      "Govt",    3100,  "https://www.lsr.edu.in"),
    ("Kirori Mal College",                     "Delhi",       "Delhi",      "Govt",    4200,  "https://www.kmc.ac.in"),
    ("Hindu College",                          "Delhi",       "Delhi",      "Govt",    2600,  "https://www.hinducollege.ac.in"),
    ("Hansraj College",                        "Delhi",       "Delhi",      "Govt",    3000,  "https://www.hansrajcollege.ac.in"),
    ("Ramjas College",                         "Delhi",       "Delhi",      "Govt",    3500,  "https://www.ramjascollege.edu.in"),
    ("Indraprastha College for Women",         "Delhi",       "Delhi",      "Govt",    2100,  "https://ipcollege.ac.in"),
    ("Gargi College",                          "Delhi",       "Delhi",      "Govt",    2800,  "https://gargicollege.in"),
    ("Jesus and Mary College",                 "Delhi",       "Delhi",      "Aided",   1400,  "https://jesusandmarycollege.ac.in"),

    # ── Tamil Nadu (10) ───────────────────────────────────────────────────────
    ("Loyola College",                         "Tamil Nadu",  "Chennai",    "Aided",   5200,  "https://www.loyolacollege.edu"),
    ("Presidency College",                     "Tamil Nadu",  "Chennai",    "Govt",    3100,  "https://www.presidencychennai.ac.in"),
    ("Stella Maris College",                   "Tamil Nadu",  "Chennai",    "Aided",   3600,  "https://www.stellamariscollege.edu.in"),
    ("PSG College of Arts and Science",        "Tamil Nadu",  "Coimbatore", "Aided",   4800,  "https://www.psgcas.ac.in"),
    ("Govt. Arts College",                     "Tamil Nadu",  "Coimbatore", "Govt",    2400,  ""),
    ("Madras Christian College",               "Tamil Nadu",  "Chennai",    "Aided",   5900,  "https://www.mcc.edu.in"),
    ("Vellore Institute of Technology",        "Tamil Nadu",  "Vellore",    "Private", 20000, "https://www.vit.ac.in"),
    ("Annamalai University Constituent Coll",  "Tamil Nadu",  "Cuddalore",  "Govt",    6200,  "https://www.annamalaiuniversity.ac.in"),
    ("Sri Ramakrishna College of Arts",        "Tamil Nadu",  "Coimbatore", "Private", 2900,  "https://www.srcas.ac.in"),
    ("Womens Christian College",               "Tamil Nadu",  "Chennai",    "Aided",   2700,  "https://www.wcc.edu.in"),
]


# ── Entry point ───────────────────────────────────────────────────────────────

def get_fallback(exclude_keys: set[tuple] | None = None) -> list[dict]:
    """
    Returns curated records as list[dict].

    Args:
        exclude_keys: set of (name, district) tuples already collected by
                      API/Excel — avoids duplicating rows in merged output.

    Returns:
        List of dicts with OUTPUT_COLUMNS keys.
    """
    if exclude_keys is None:
        exclude_keys = set()

    records = []
    for row in FALLBACK_DATA:
        name, state, district, col_type, student_count, website = row
        if (name, district) in exclude_keys:
            continue
        records.append({
            "name":          name,
            "state":         state,
            "district":      district,
            "type":          col_type,
            "student_count": student_count,
            "website":       website,
        })

    return records


def count() -> int:
    """Returns total number of fallback rows."""
    return len(FALLBACK_DATA)
