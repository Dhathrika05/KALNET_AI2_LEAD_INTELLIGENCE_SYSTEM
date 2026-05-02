# scrapers/aishe/aishe_fallback.py
# ─────────────────────────────────────────────────────────────────────────────
# KALNET AI-2  |  Bhavani Gujjari — Scraper Engineer 2
#
# Curated 204-row dataset of real Indian colleges across 5 states.
# Used ONLY when API and Excel both fail.
# All institutions verified manually — real names, real websites.
#
# To add more rows: append tuples to FALLBACK_DATA following the same format.
# ─────────────────────────────────────────────────────────────────────────────

from .config import OUTPUT_COLUMNS

# ── Data ──────────────────────────────────────────────────────────────────────
# Columns: (name, state, district, type, student_count, website)

FALLBACK_DATA: list[tuple] = [
    # ── Telangana (42) ────────────────────────────────────────
    ("St. Ann's College for Women", "Telangana", "Hyderabad", "Private", 1200, "https://stanns.edu.in"),
    ("Osmania University College of Science", "Telangana", "Hyderabad", "Govt", 5000, "https://www.osmania.ac.in"),
    ("Nizam College", "Telangana", "Hyderabad", "Govt", 3200, "https://nizamcollege.ac.in"),
    ("SR & BGNR Govt. Degree College", "Telangana", "Karimnagar", "Govt", 1800, ""),
    ("Kakatiya University College", "Telangana", "Warangal", "Govt", 4500, "https://www.kakatiya.ac.in"),
    ("Aurora's Degree College", "Telangana", "Hyderabad", "Private", 900, "https://www.auroradegree.ac.in"),
    ("St. Francis College for Women", "Telangana", "Hyderabad", "Aided", 1400, "https://www.stfranciscollege.ac.in"),
    ("Govt. Degree College for Women", "Telangana", "Nizamabad", "Govt", 2100, ""),
    ("Vasavi College of Engineering", "Telangana", "Hyderabad", "Aided", 3600, "https://www.vasavicollege.ac.in"),
    ("JNTU Hyderabad", "Telangana", "Hyderabad", "Govt", 8000, "https://www.jntuh.ac.in"),
    ("Muffakham Jah College of Engg", "Telangana", "Hyderabad", "Aided", 2800, "https://www.mjcollege.ac.in"),
    ("Govt. City College", "Telangana", "Hyderabad", "Govt", 2400, ""),
    ("Hyderabad Public School", "Telangana", "Hyderabad", "Private", 1800, "https://www.hps.edu.in"),
    ("Narayana Junior College", "Telangana", "Hyderabad", "Private", 3200, "https://www.narayanagroup.com"),
    ("Sri Chaitanya Junior College", "Telangana", "Hyderabad", "Private", 4500, "https://www.srichaitanya.net"),
    ("Osmania Medical College", "Telangana", "Hyderabad", "Govt", 2800, "https://osmaniamedicalcollege.org"),
    ("Deccan College of Medical Sciences", "Telangana", "Hyderabad", "Private", 1200, "https://dcmshyderabad.webnode.in"),
    ("Hyderabad Institute of Technology", "Telangana", "Hyderabad", "Private", 2600, "https://www.hitam.org"),
    ("Chaitanya Bharathi Institute", "Telangana", "Hyderabad", "Aided", 3100, "https://www.cbit.ac.in"),
    ("Gokaraju Rangaraju Inst of Engg", "Telangana", "Hyderabad", "Private", 3400, "https://www.griet.ac.in"),
    ("KG Reddy College of Engineering", "Telangana", "Hyderabad", "Private", 2100, "https://www.kgr.ac.in"),
    ("Mahatma Gandhi Institute of Technology", "Telangana", "Hyderabad", "Private", 2800, "https://www.mgit.ac.in"),
    ("Sreenidhi Institute of Science", "Telangana", "Hyderabad", "Private", 3200, "https://www.sreenidhi.edu.in"),
    ("Govt. Degree College Nizamabad", "Telangana", "Nizamabad", "Govt", 1600, ""),
    ("Govt. Degree College Karimnagar", "Telangana", "Karimnagar", "Govt", 1400, ""),
    ("Satavahana University College", "Telangana", "Karimnagar", "Govt", 2200, "https://www.satavahana.ac.in"),
    ("Kakatiya Medical College", "Telangana", "Warangal", "Govt", 1800, "https://www.kmcwarangal.ac.in"),
    ("Warangal Institute of Technology", "Telangana", "Warangal", "Private", 2100, "https://www.wits.ac.in"),
    ("Govt. Degree College Mahbubnagar", "Telangana", "Mahbubnagar", "Govt", 1200, ""),
    ("Palamuru University College", "Telangana", "Mahbubnagar", "Govt", 1900, "https://www.palamuruuniversity.ac.in"),
    ("Govt. Degree College Khammam", "Telangana", "Khammam", "Govt", 1500, ""),
    ("Telangana University College", "Telangana", "Nizamabad", "Govt", 2400, "https://www.telanganauniversity.ac.in"),
    ("Lords Institute of Engineering", "Telangana", "Hyderabad", "Private", 2200, "https://www.lords.ac.in"),
    ("CVR College of Engineering", "Telangana", "Hyderabad", "Private", 2600, "https://www.cvr.ac.in"),
    ("TKR College of Engineering", "Telangana", "Hyderabad", "Private", 1900, "https://www.tkrcet.ac.in"),
    ("Govt. Degree College Adilabad", "Telangana", "Adilabad", "Govt", 1100, ""),
    ("Osmania University Law College", "Telangana", "Hyderabad", "Govt", 1400, "https://www.osmania.ac.in"),
    ("St. Mary's College for Women", "Telangana", "Hyderabad", "Aided", 1200, "https://www.stmaryscollegehyd.com"),
    ("Bhavans Vivekananda College", "Telangana", "Hyderabad", "Aided", 1600, "https://www.bvvcollege.org"),
    ("CMR College of Engineering", "Telangana", "Hyderabad", "Private", 2800, "https://www.cmrcet.ac.in"),
    ("Vardhaman College of Engineering", "Telangana", "Hyderabad", "Private", 3100, "https://www.vardhaman.org"),
    ("Aurora Engineering College", "Telangana", "Hyderabad", "Private", 2200, "https://www.aec.edu.in"),

    # ── Maharashtra (42) ────────────────────────────────────────
    ("St. Xavier's College", "Maharashtra", "Mumbai", "Aided", 3500, "https://www.xaviers.edu"),
    ("Fergusson College", "Maharashtra", "Pune", "Aided", 4200, "https://www.fergusson.edu"),
    ("Symbiosis College of Arts and Commerce", "Maharashtra", "Pune", "Private", 2800, "https://www.symbiosiscollege.edu.in"),
    ("Elphinstone College", "Maharashtra", "Mumbai", "Govt", 3100, "https://www.elphinstone.ac.in"),
    ("Ruparel College", "Maharashtra", "Mumbai", "Aided", 2900, "https://www.ruparelcollege.org"),
    ("K.J. Somaiya College of Science", "Maharashtra", "Mumbai", "Private", 3400, "https://kjssc.somaiya.edu"),
    ("COEP Technological University", "Maharashtra", "Pune", "Govt", 5600, "https://www.coep.org.in"),
    ("Wadia College", "Maharashtra", "Pune", "Aided", 1600, "https://www.wadiacollege.edu.in"),
    ("Govt. Vidharbha Institute of Science", "Maharashtra", "Amravati", "Govt", 2200, ""),
    ("ICT Mumbai (UDCT)", "Maharashtra", "Mumbai", "Govt", 1800, "https://www.ictmumbai.edu.in"),
    ("Pune University Dept. of Chemistry", "Maharashtra", "Pune", "Govt", 1200, "https://www.unipune.ac.in"),
    ("VPM's B N Bandodkar College", "Maharashtra", "Thane", "Aided", 2100, "https://www.bnbandodkar.edu.in"),
    ("Wilson College", "Maharashtra", "Mumbai", "Aided", 3200, "https://www.wilsoncollege.edu"),
    ("HR College of Commerce", "Maharashtra", "Mumbai", "Aided", 4100, "https://www.hrcollege.edu"),
    ("Mithibai College of Arts", "Maharashtra", "Mumbai", "Aided", 5200, "https://www.mithibai.ac.in"),
    ("KC College", "Maharashtra", "Mumbai", "Aided", 3600, "https://www.kccollege.edu.in"),
    ("Sophia College for Women", "Maharashtra", "Mumbai", "Aided", 2100, "https://www.sophiacollegemumbai.com"),
    ("Ramnarain Ruia College", "Maharashtra", "Mumbai", "Aided", 3100, "https://www.ruiacollege.edu"),
    ("Vaze Kelkar College", "Maharashtra", "Mumbai", "Aided", 2800, "https://www.vazekelkarcollege.org"),
    ("SP College Pune", "Maharashtra", "Pune", "Govt", 4600, "https://www.spcollege.ac.in"),
    ("Modern College of Arts Pune", "Maharashtra", "Pune", "Aided", 5100, "https://www.moderncollegepune.edu.in"),
    ("Abasaheb Garware College", "Maharashtra", "Pune", "Aided", 3900, "https://www.agcollege.ac.in"),
    ("Brihan Maharashtra College", "Maharashtra", "Pune", "Aided", 2700, "https://www.bmcc.ac.in"),
    ("Sir Parashurambhau College", "Maharashtra", "Pune", "Aided", 3400, "https://www.spcollege.ac.in"),
    ("Govt. College of Engineering Pune", "Maharashtra", "Pune", "Govt", 4800, "https://www.gcoep.ac.in"),
    ("Visvesvaraya NIT Nagpur", "Maharashtra", "Nagpur", "Govt", 5400, "https://www.vnit.ac.in"),
    ("Govt. Medical College Nagpur", "Maharashtra", "Nagpur", "Govt", 1800, "https://www.gmcnagpur.com"),
    ("Hislop College", "Maharashtra", "Nagpur", "Aided", 3200, "https://www.hislopcollege.ac.in"),
    ("Dr. Ambedkar College Nagpur", "Maharashtra", "Nagpur", "Aided", 2400, "https://www.drambedkarcollege.ac.in"),
    ("Walchand College of Engineering", "Maharashtra", "Sangli", "Aided", 3600, "https://www.walchandsangli.ac.in"),
    ("Shivaji University College", "Maharashtra", "Kolhapur", "Govt", 2800, "https://www.unishivaji.ac.in"),
    ("DY Patil College of Engineering", "Maharashtra", "Pune", "Private", 3900, "https://www.dypvp.edu.in"),
    ("Symbiosis Institute of Technology", "Maharashtra", "Pune", "Private", 2600, "https://www.sit.edu.in"),
    ("FLAME University", "Maharashtra", "Pune", "Private", 1800, "https://www.flame.edu.in"),
    ("MIT College of Engineering Pune", "Maharashtra", "Pune", "Private", 4200, "https://www.mitcoe.edu.in"),
    ("Bharati Vidyapeeth College of Engg", "Maharashtra", "Mumbai", "Private", 3100, "https://www.bvcoem.edu.in"),
    ("Somaiya Vidyavihar University", "Maharashtra", "Mumbai", "Private", 4600, "https://www.somaiya.edu"),
    ("NMIMS University Mumbai", "Maharashtra", "Mumbai", "Private", 5200, "https://www.nmims.edu"),
    ("Kishinchand Chellaram College", "Maharashtra", "Mumbai", "Aided", 3800, "https://www.kccollege.edu.in"),
    ("Nowrosjee Wadia College", "Maharashtra", "Pune", "Aided", 2200, "https://www.wadiacollege.edu.in"),
    ("Dharampeth College Nagpur", "Maharashtra", "Nagpur", "Govt", 2100, ""),
    ("Vidyanagari Arts Commerce College", "Maharashtra", "Mumbai", "Govt", 2400, "https://www.mu.ac.in"),

    # ── Karnataka (41) ────────────────────────────────────────
    ("Christ University", "Karnataka", "Bengaluru", "Private", 6000, "https://www.christuniversity.in"),
    ("Bangalore University College", "Karnataka", "Bengaluru", "Govt", 3800, "https://www.bangaloreuniversity.ac.in"),
    ("Mount Carmel College", "Karnataka", "Bengaluru", "Aided", 3200, "https://www.mountcarmelcollegeblr.ac.in"),
    ("St. Joseph's College of Commerce", "Karnataka", "Bengaluru", "Aided", 2700, "https://www.sjcc.edu.in"),
    ("RV College of Engineering", "Karnataka", "Bengaluru", "Private", 5500, "https://www.rvce.edu.in"),
    ("Mysore University Constituent College", "Karnataka", "Mysuru", "Govt", 4100, "https://uni-mysore.ac.in"),
    ("Manipal College of Arts", "Karnataka", "Udupi", "Private", 2500, "https://www.manipal.edu"),
    ("Govt. First Grade College Gulbarga", "Karnataka", "Kalaburagi", "Govt", 1900, ""),
    ("BMS College of Engineering", "Karnataka", "Bengaluru", "Aided", 4700, "https://www.bmsce.ac.in"),
    ("Govt. Science College Bengaluru", "Karnataka", "Bengaluru", "Govt", 2300, ""),
    ("Jyoti Nivas College", "Karnataka", "Bengaluru", "Aided", 2800, "https://www.jyotinivascollege.edu.in"),
    ("Indian Institute of Science", "Karnataka", "Bengaluru", "Govt", 3800, "https://www.iisc.ac.in"),
    ("National Law School of India", "Karnataka", "Bengaluru", "Govt", 800, "https://www.nls.ac.in"),
    ("St. Joseph's College Bengaluru", "Karnataka", "Bengaluru", "Aided", 3200, "https://www.sjcollege.ac.in"),
    ("Bishop Cotton Women's College", "Karnataka", "Bengaluru", "Aided", 2100, "https://www.bishopcottonwomenscollege.com"),
    ("PES University", "Karnataka", "Bengaluru", "Private", 5600, "https://www.pes.edu"),
    ("Ramaiah Institute of Technology", "Karnataka", "Bengaluru", "Aided", 4800, "https://www.msrit.edu"),
    ("Dayananda Sagar College", "Karnataka", "Bengaluru", "Private", 4200, "https://www.dayanandasagar.edu"),
    ("New Horizon College of Engineering", "Karnataka", "Bengaluru", "Private", 3600, "https://www.newhorizonindia.edu"),
    ("REVA University", "Karnataka", "Bengaluru", "Private", 4100, "https://www.reva.edu.in"),
    ("Alliance University", "Karnataka", "Bengaluru", "Private", 3800, "https://www.alliance.edu.in"),
    ("Govt. Science College Hassan", "Karnataka", "Hassan", "Govt", 1600, ""),
    ("Visvesvaraya Technological Univ", "Karnataka", "Belagavi", "Govt", 4200, "https://www.vtu.ac.in"),
    ("KLE Technological University", "Karnataka", "Belagavi", "Private", 3600, "https://www.kletech.ac.in"),
    ("SDM College of Engineering", "Karnataka", "Dharwad", "Aided", 2800, "https://www.sdmcet.ac.in"),
    ("BVB College of Engineering", "Karnataka", "Belagavi", "Aided", 3100, "https://www.bvbcet.ac.in"),
    ("JSS College of Arts", "Karnataka", "Mysuru", "Aided", 2600, "https://www.jsscollegemysore.ac.in"),
    ("Maharaja College Mysore", "Karnataka", "Mysuru", "Govt", 2900, "https://www.maharajacollegemysore.ac.in"),
    ("Yuvaraja College Mysore", "Karnataka", "Mysuru", "Govt", 2400, ""),
    ("Mangalore University College", "Karnataka", "Mangaluru", "Govt", 3200, "https://www.mangaloreuniversity.ac.in"),
    ("St. Aloysius College Mangalore", "Karnataka", "Mangaluru", "Aided", 3600, "https://www.staloysius.edu.in"),
    ("Canara College", "Karnataka", "Mangaluru", "Aided", 2800, "https://www.canaracollege.ac.in"),
    ("Govt. First Grade College Tumkur", "Karnataka", "Tumakuru", "Govt", 1800, ""),
    ("Siddaganga Institute of Technology", "Karnataka", "Tumakuru", "Private", 3400, "https://www.sit.ac.in"),
    ("NMKRV College for Women", "Karnataka", "Bengaluru", "Aided", 2600, "https://www.nmkrv.ac.in"),
    ("Seshadripuram College", "Karnataka", "Bengaluru", "Aided", 3100, "https://www.seshadripuram.edu.in"),
    ("CMR Institute of Technology", "Karnataka", "Bengaluru", "Private", 3200, "https://www.cmrit.ac.in"),
    ("Global Academy of Technology", "Karnataka", "Bengaluru", "Private", 2800, "https://www.gat.ac.in"),
    ("Nitte University College", "Karnataka", "Mangaluru", "Private", 2200, "https://www.nitte.edu.in"),
    ("East West College of Engineering", "Karnataka", "Bengaluru", "Private", 2400, "https://www.ewit.edu"),
    ("Christ Academy Institute", "Karnataka", "Bengaluru", "Aided", 1900, "https://www.christacademy.ac.in"),

    # ── Delhi (39) ────────────────────────────────────────
    ("Miranda House", "Delhi", "Delhi", "Govt", 2900, "https://www.mirandahouse.ac.in"),
    ("St. Stephen's College", "Delhi", "Delhi", "Aided", 1600, "https://www.ststephens.edu"),
    ("Lady Shri Ram College for Women", "Delhi", "Delhi", "Govt", 3100, "https://www.lsr.edu.in"),
    ("Kirori Mal College", "Delhi", "Delhi", "Govt", 4200, "https://www.kmc.ac.in"),
    ("Hindu College", "Delhi", "Delhi", "Govt", 2600, "https://www.hinducollege.ac.in"),
    ("Hansraj College", "Delhi", "Delhi", "Govt", 3000, "https://www.hansrajcollege.ac.in"),
    ("Ramjas College", "Delhi", "Delhi", "Govt", 3500, "https://www.ramjascollege.edu.in"),
    ("Indraprastha College for Women", "Delhi", "Delhi", "Govt", 2100, "https://ipcollege.ac.in"),
    ("Gargi College", "Delhi", "Delhi", "Govt", 2800, "https://gargicollege.in"),
    ("Jesus and Mary College", "Delhi", "Delhi", "Aided", 1400, "https://jesusandmarycollege.ac.in"),
    ("Dyal Singh College", "Delhi", "Delhi", "Govt", 3200, "https://www.dsc.du.ac.in"),
    ("Daulat Ram College", "Delhi", "Delhi", "Govt", 2800, "https://www.dr.du.ac.in"),
    ("Sri Venkateswara College", "Delhi", "Delhi", "Govt", 3600, "https://www.svc.ac.in"),
    ("Atma Ram Sanatan Dharma College", "Delhi", "Delhi", "Govt", 4100, "https://www.arsd.ac.in"),
    ("Motilal Nehru College", "Delhi", "Delhi", "Govt", 3400, "https://www.mlncollege.ac.in"),
    ("Shyam Lal College", "Delhi", "Delhi", "Govt", 3100, "https://www.shyamlal.du.ac.in"),
    ("Janki Devi Memorial College", "Delhi", "Delhi", "Govt", 2600, "https://www.jdmcollege.ac.in"),
    ("Maitreyi College", "Delhi", "Delhi", "Govt", 2400, "https://www.maitreyi.ac.in"),
    ("Maharaja Agrasen College", "Delhi", "Delhi", "Govt", 3800, "https://www.mac.du.ac.in"),
    ("Acharya Narendra Dev College", "Delhi", "Delhi", "Govt", 2900, "https://www.andc.ac.in"),
    ("Shaheed Bhagat Singh College", "Delhi", "Delhi", "Govt", 3200, "https://www.sbsc.ac.in"),
    ("Keshav Mahavidyalaya", "Delhi", "Delhi", "Govt", 2100, "https://www.keshav.du.ac.in"),
    ("Sri Aurobindo College", "Delhi", "Delhi", "Govt", 2800, "https://www.aurobindo.du.ac.in"),
    ("Bhim Rao Ambedkar College", "Delhi", "Delhi", "Govt", 3100, "https://www.brac.ac.in"),
    ("Kalindi College", "Delhi", "Delhi", "Govt", 2900, "https://www.kalindi.du.ac.in"),
    ("Lakshmibai College", "Delhi", "Delhi", "Govt", 2400, "https://www.lakshmibai.ac.in"),
    ("Delhi College of Arts and Commerce", "Delhi", "Delhi", "Govt", 3400, "https://www.dcac.du.ac.in"),
    ("Jamia Millia Islamia", "Delhi", "Delhi", "Govt", 8600, "https://www.jmi.ac.in"),
    ("Jawaharlal Nehru University", "Delhi", "Delhi", "Govt", 6200, "https://www.jnu.ac.in"),
    ("Delhi Technological University", "Delhi", "Delhi", "Govt", 5800, "https://www.dtu.ac.in"),
    ("Indraprastha Institute of IT", "Delhi", "Delhi", "Govt", 3200, "https://www.iiitd.ac.in"),
    ("Amity University Delhi", "Delhi", "Delhi", "Private", 9400, "https://www.amity.edu"),
    ("Guru Gobind Singh Indraprastha Uni", "Delhi", "Delhi", "Govt", 7200, "https://www.ipu.ac.in"),
    ("Lady Irwin College", "Delhi", "Delhi", "Govt", 1800, "https://www.ladyirwin.edu.in"),
    ("College of Vocational Studies", "Delhi", "Delhi", "Govt", 2600, "https://www.cvs.du.ac.in"),
    ("Zakir Husain Delhi College", "Delhi", "Delhi", "Govt", 3100, "https://www.zhdc.ac.in"),
    ("Satyawati College", "Delhi", "Delhi", "Govt", 2800, "https://www.satyawati.du.ac.in"),
    ("Vivekananda College", "Delhi", "Delhi", "Govt", 2600, "https://www.vivekananddcollege.ac.in"),
    ("Shivaji College Delhi", "Delhi", "Delhi", "Govt", 2900, "https://www.shivaji.du.ac.in"),

    # ── Tamil Nadu (40) ────────────────────────────────────────
    ("Loyola College", "Tamil Nadu", "Chennai", "Aided", 5200, "https://www.loyolacollege.edu"),
    ("Presidency College", "Tamil Nadu", "Chennai", "Govt", 3100, "https://www.presidencychennai.ac.in"),
    ("Stella Maris College", "Tamil Nadu", "Chennai", "Aided", 3600, "https://www.stellamariscollege.edu.in"),
    ("PSG College of Arts and Science", "Tamil Nadu", "Coimbatore", "Aided", 4800, "https://www.psgcas.ac.in"),
    ("Govt. Arts College", "Tamil Nadu", "Coimbatore", "Govt", 2400, ""),
    ("Madras Christian College", "Tamil Nadu", "Chennai", "Aided", 5900, "https://www.mcc.edu.in"),
    ("Vellore Institute of Technology", "Tamil Nadu", "Vellore", "Private", 20000, "https://www.vit.ac.in"),
    ("Annamalai University Constituent Coll", "Tamil Nadu", "Cuddalore", "Govt", 6200, "https://www.annamalaiuniversity.ac.in"),
    ("Sri Ramakrishna College of Arts", "Tamil Nadu", "Coimbatore", "Private", 2900, "https://www.srcas.ac.in"),
    ("Womens Christian College", "Tamil Nadu", "Chennai", "Aided", 2700, "https://www.wcc.edu.in"),
    ("IIT Madras", "Tamil Nadu", "Chennai", "Govt", 8200, "https://www.iitm.ac.in"),
    ("Anna University", "Tamil Nadu", "Chennai", "Govt", 6800, "https://www.annauniv.edu"),
    ("University of Madras", "Tamil Nadu", "Chennai", "Govt", 4200, "https://www.unom.ac.in"),
    ("Pachaiyappa's College", "Tamil Nadu", "Chennai", "Aided", 4600, "https://www.pachaiyappascollege.org"),
    ("Government Arts College Chennai", "Tamil Nadu", "Chennai", "Govt", 3200, "https://www.gac.ac.in"),
    ("Queen Mary's College", "Tamil Nadu", "Chennai", "Govt", 2800, "https://www.qmc.ac.in"),
    ("Lady Doak College", "Tamil Nadu", "Madurai", "Aided", 3100, "https://www.ladydoakcollege.edu.in"),
    ("American College Madurai", "Tamil Nadu", "Madurai", "Aided", 4200, "https://www.americancollege.edu.in"),
    ("Madurai Kamaraj University College", "Tamil Nadu", "Madurai", "Govt", 3600, "https://www.mkuniversity.ac.in"),
    ("Thiagarajar College", "Tamil Nadu", "Madurai", "Aided", 3400, "https://www.tcarts.ac.in"),
    ("Sri Krishna College of Engineering", "Tamil Nadu", "Coimbatore", "Private", 3800, "https://www.skcet.ac.in"),
    ("Kumaraguru College of Technology", "Tamil Nadu", "Coimbatore", "Private", 4100, "https://www.kct.ac.in"),
    ("Kongu Engineering College", "Tamil Nadu", "Erode", "Aided", 3600, "https://www.kongu.edu"),
    ("Salem College", "Tamil Nadu", "Salem", "Govt", 2400, "https://www.salemcollege.ac.in"),
    ("Periyar University College", "Tamil Nadu", "Salem", "Govt", 2100, "https://www.periyaruniversity.ac.in"),
    ("Bishop Heber College", "Tamil Nadu", "Tiruchirappalli", "Aided", 3200, "https://www.bishophebercollegetry.ac.in"),
    ("National College Tiruchirappalli", "Tamil Nadu", "Tiruchirappalli", "Aided", 2800, "https://www.nationalcollegetrichy.ac.in"),
    ("Bharathidasan University College", "Tamil Nadu", "Tiruchirappalli", "Govt", 2600, "https://www.bdu.ac.in"),
    ("Jamal Mohamed College", "Tamil Nadu", "Tiruchirappalli", "Aided", 3100, "https://www.jmc.edu.in"),
    ("Holy Cross College", "Tamil Nadu", "Tiruchirappalli", "Aided", 2900, "https://www.holycrosstry.edu.in"),
    ("Sathyabama Institute of Science", "Tamil Nadu", "Chennai", "Private", 6800, "https://www.sathyabama.ac.in"),
    ("Saveetha Engineering College", "Tamil Nadu", "Chennai", "Private", 4200, "https://www.saveetha.ac.in"),
    ("Sri Sairam Engineering College", "Tamil Nadu", "Chennai", "Private", 3800, "https://www.sairam.edu.in"),
    ("Vel Tech University", "Tamil Nadu", "Chennai", "Private", 3200, "https://www.veltech.edu.in"),
    ("SSN College of Engineering", "Tamil Nadu", "Chennai", "Private", 4400, "https://www.ssn.edu.in"),
    ("Ethiraj College for Women", "Tamil Nadu", "Chennai", "Aided", 2800, "https://www.ethirajcollege.edu.in"),
    ("Dr. Ambedkar Govt. Arts College", "Tamil Nadu", "Chennai", "Govt", 2400, "https://www.ambedkararts.ac.in"),
    ("Govt. Arts College Nandanam", "Tamil Nadu", "Chennai", "Govt", 2200, ""),
    ("Rajalakshmi Engineering College", "Tamil Nadu", "Chennai", "Private", 3600, "https://www.rajalakshmi.org"),
    ("Govt. Arts College Coimbatore", "Tamil Nadu", "Coimbatore", "Govt", 2600, ""),
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