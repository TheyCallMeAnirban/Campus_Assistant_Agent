"""
Synthetic Benchmark Corpus Generator (Jharkhand Only)
=====================================================
Generates a deterministic, statistically plausible synthetic benchmark corpus
of engineering colleges in Jharkhand for demonstration and evaluation
of retrieval-augmented conversational AI systems.

All institution names are based on real/authentic or realistic Jharkhand institutions.
No real fees, placements, or rankings are associated with any real institution.

Usage:
    python knowledge/generate_dataset.py
"""

import os
import json
import random
import csv
import hashlib
from datetime import date
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

SEED = 42
OUTPUT_DIR = Path("knowledge")
CORPUS_DIR = OUTPUT_DIR / "corpus"
RULES_PATH = OUTPUT_DIR / "generation_rules.json"

DEPARTMENTS = [
    "Computer Science & Engineering",
    "Electronics & Communication Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Information Technology",
    "Biotechnology",
    "Metallurgical & Materials Engineering",
    "Mining Engineering",
    "Production & Industrial Engineering",
    "Instrumentation Engineering",
    "Environmental Engineering",
    "Architecture",
    "Applied Mathematics & Computing",
]

BRANCH_ABBR = {
    "Computer Science & Engineering": "CSE",
    "Electronics & Communication Engineering": "ECE",
    "Electrical Engineering": "EE",
    "Mechanical Engineering": "ME",
    "Civil Engineering": "CE",
    "Chemical Engineering": "CHE",
    "Information Technology": "IT",
    "Biotechnology": "BT",
    "Metallurgical & Materials Engineering": "MME",
    "Mining Engineering": "MIN",
    "Production & Industrial Engineering": "PIE",
    "Instrumentation Engineering": "IE",
    "Environmental Engineering": "ENV",
    "Architecture": "ARCH",
    "Applied Mathematics & Computing": "AMC",
}

RECRUITERS_POOL = {
    "iit_tier": [
        "Google", "Microsoft", "Amazon", "Goldman Sachs", "TATA Steel", "SAIL", "Adani Power", "Coal India",
        "Uber", "Flipkart", "Texas Instruments", "Qualcomm", "Intel",
        "Apple", "Meta", "Oracle", "Adobe", "DE Shaw", "Schlumberger",
    ],
    "nit_tier": [
        "TATA Steel", "SAIL", "HINDALCO", "L&T", "TCS", "Infosys", "Wipro", "HCL", "Cognizant",
        "Samsung", "Bosch", "Tata Motors", "Mahindra", "Amazon", "Deloitte", "Accenture",
    ],
    "iiit_tier": [
        "TCS", "Infosys", "Wipro", "Cognizant", "Mindtree", "Tech Mahindra",
        "Amazon", "Byju's", "Razorpay", "Swiggy", "Jio", "EPAM",
    ],
    "government": [
        "SAIL Bokaro", "TATA Steel", "BCCL Dhanbad", "CCL Ranchi", "HEC Ranchi", "NTPC Patratu",
        "TCS", "Infosys", "Wipro", "L&T", "JSW Steel", "Usha Martin",
    ],
    "state_university": [
        "TCS", "Infosys", "Wipro", "Cognizant", "SAIL", "TATA Motors", "Vedanta", "JSPL",
    ],
    "private": [
        "TCS", "Infosys", "Cognizant", "Capgemini", "Accenture", "Wipro", "Tech Mahindra", "Genpact",
    ],
}

SCHOLARSHIP_TYPES = [
    "E-Kalyan Jharkhand Post-Matric Scholarship",
    "Mukhyamantri Medha Chatravriti Yojana",
    "Jharkhand Government EWS Scheme",
    "Birsa Munda Merit Scholarship",
    "Jharkhand State Sports Promotion Board Scholarship",
    "Jharkhand Minority Scholarship Scheme",
    "Merit-cum-Means Scholarship (Jharkhand State)",
    "Post-Matric Scholarship for SC/ST/OBC Students (e-Kalyan)",
]

# ── Generator ────────────────────────────────────────────────────────────────

class CorpusGenerator:
    def __init__(self):
        with open(RULES_PATH, "r") as f:
            self.rules = json.load(f)
        self.used_names = set()
        self.colleges = []

    def college_id(self, name):
        """Generate a filesystem-safe college ID."""
        return name.lower().replace(" ", "_").replace(",", "").replace("–", "").replace("-", "_").replace("(", "").replace(")", "").replace("&", "and")[:60]

    def generate_profile_jh(self, name, college_type, city, state="Jharkhand"):
        rule = self.rules[college_type]

        # Use deterministic hash seed for each college to keep random outputs reproducible
        seed_hash = int(hashlib.md5(f"{name}_{SEED}".encode('utf-8')).hexdigest(), 16) % (2**32)
        random.seed(seed_hash)

        # 1. Tier score drives everything
        tier_lo, tier_hi = rule["tier_range"]
        tier = random.uniform(tier_lo, tier_hi)

        # 2. Scores derived from tier
        a_lo, a_hi = rule["academic_score_base"]
        c_lo, c_hi = rule["campus_score_base"]
        i_lo, i_hi = rule["industry_score_base"]
        academic_score = round(a_lo + (a_hi - a_lo) * tier + random.uniform(-0.3, 0.3), 1)
        campus_score = round(c_lo + (c_hi - c_lo) * tier + random.uniform(-0.3, 0.3), 1)
        industry_score = round(i_lo + (i_hi - i_lo) * tier + random.uniform(-0.3, 0.3), 1)
        
        # Clamp scores
        academic_score = round(max(1.0, min(10.0, academic_score)), 1)
        campus_score = round(max(1.0, min(10.0, campus_score)), 1)
        industry_score = round(max(1.0, min(10.0, industry_score)), 1)
        overall_score = round((academic_score + campus_score + industry_score) / 3, 1)

        # 3. Fee derived from tier
        f_lo, f_hi = rule["fee"]
        fee = int(f_lo + (f_hi - f_lo) * tier)
        fee = round(fee / 1000) * 1000

        h_lo, h_hi = rule["hostel_fee"]
        hostel_fee = int(h_lo + (h_hi - h_lo) * tier)
        hostel_fee = round(hostel_fee / 1000) * 1000

        m_lo, m_hi = rule["mess_fee"]
        mess_fee = int(m_lo + (m_hi - m_lo) * tier)
        mess_fee = round(mess_fee / 1000) * 1000

        # 4. Placements derived from industry_score
        p_lo, p_hi = rule["placement_avg"]
        avg_package = round(p_lo + (p_hi - p_lo) * (industry_score / 10), 1)

        mul_lo, mul_hi = rule["placement_highest_multiplier"]
        multiplier = mul_lo + (mul_hi - mul_lo) * tier
        highest_package = round(avg_package * multiplier, 1)
        highest_package = max(highest_package, avg_package + 1.0)

        r_lo, r_hi = rule["placement_rate"]
        placement_rate = round(r_lo + (r_hi - r_lo) * tier, 1)
        placement_rate = min(100.0, placement_rate)

        # 5. Student strength and hostel capacity
        e_lo, e_hi = rule["established_year"]
        est_year = random.randint(e_lo, e_hi)

        s_lo, s_hi = rule["student_strength"]
        student_strength = int(s_lo + (s_hi - s_lo) * tier)
        student_strength = round(student_strength / 100) * 100

        hr_lo, hr_hi = rule["hostel_capacity_ratio"]
        hostel_ratio = random.uniform(hr_lo, hr_hi)
        hostel_capacity = int(student_strength * hostel_ratio)
        hostel_capacity = min(hostel_capacity, student_strength)

        ca_lo, ca_hi = rule["campus_area_acres"]
        age_factor = (2025 - est_year) / max(1, 2025 - e_lo)
        campus_area = int(ca_lo + (ca_hi - ca_lo) * age_factor + random.uniform(-10, 10))

        # 6. Departments
        d_lo, d_hi = rule["departments"]
        dept_count = random.randint(d_lo, d_hi)
        depts = random.sample(DEPARTMENTS, min(dept_count, len(DEPARTMENTS)))

        # 7. Recruiters
        recruiters = random.sample(RECRUITERS_POOL[college_type], min(8, len(RECRUITERS_POOL[college_type])))

        # 8. Scholarships
        scholarships = random.sample(SCHOLARSHIP_TYPES, random.randint(3, 6))

        # 9. Library books and labs
        library_books = int(10000 + 70000 * tier + random.randint(-5000, 5000))
        library_books = round(library_books / 1000) * 1000
        lab_count = random.randint(dept_count, dept_count * 2 + 4)

        col_id = self.college_id(name)

        return {
            "id": col_id,
            "college": name,
            "city": city,
            "state": state,
            "type": college_type,
            "established": est_year,
            "tier": round(tier, 3),
            "academic_score": academic_score,
            "campus_score": campus_score,
            "industry_score": industry_score,
            "overall_score": overall_score,
            "fees_ug_inr": fee,
            "hostel_fee": hostel_fee,
            "mess_fee": mess_fee,
            "placement_avg_lpa": avg_package,
            "placement_highest_lpa": highest_package,
            "placement_rate_pct": placement_rate,
            "student_strength": student_strength,
            "hostel_capacity": hostel_capacity,
            "campus_area_acres": campus_area,
            "departments": depts,
            "dept_count": len(depts),
            "recruiters": recruiters,
            "scholarships": scholarships,
            "library_books": library_books,
            "lab_count": lab_count,
            "source": "Synthetic Benchmark Corpus v1.0 (generated)",
        }

    def generate_all(self):
        """Generate the full college distribution for Jharkhand."""
        jharkhand_colleges = [
            # Real/grounded colleges from manifest
            ("IIT (ISM) Dhanbad", "Dhanbad", "iit_tier"),
            ("NIT Jamshedpur", "Jamshedpur", "nit_tier"),
            ("IIIT Ranchi", "Ranchi", "iiit_tier"),
            ("Birsa Institute of Technology", "Sindri", "government"),
            ("Dumka Engineering College", "Dumka", "government"),
            ("Government Engineering College Palamu", "Palamu", "government"),
            ("Ramgarh Engineering College", "Ramgarh", "government"),
            ("Chaibasa Engineering College", "Chaibasa", "government"),
            ("Government Engineering College Godda", "Godda", "government"),
            ("Cambridge Institute of Technology", "Ranchi", "private"),
            ("RTC Institute of Technology", "Ranchi", "private"),
            ("RVS College of Engineering and Technology", "Jamshedpur", "private"),
            
            # Enriched/synthetic Jharkhand colleges
            ("Jharkhand University of Technology", "Ranchi", "state_university"),
            ("Birla Institute of Technology Mesra", "Ranchi", "private"),
            ("Birsa Munda Institute of Technology", "Ranchi", "government"),
            ("Bokaro Institute of Technology", "Bokaro", "private"),
            ("Hazaribagh College of Engineering", "Hazaribagh", "private"),
            ("Deoghar Institute of Technology", "Deoghar", "private"),
            ("Giridih Engineering College", "Giridih", "private"),
            ("Koderma Institute of Science & Technology", "Koderma", "private"),
            ("Koyla Anchaldhan College of Engineering", "Dhanbad", "private"),
            ("Chhotanagpur Technical University", "Hazaribagh", "state_university"),
            ("Santhal Pargana Engineering College", "Dumka", "private"),
            ("Steel City Technical Campus", "Bokaro", "private"),
            ("Subarnarekha Institute of Technology", "Jamshedpur", "private"),
            ("Jamshedpur Technical Institute", "Jamshedpur", "private"),
            ("Ranchi College of Engineering & Technology", "Ranchi", "private"),
            ("Netaji Subhas University Department of Engineering", "Jamshedpur", "private"),
            ("Radha Govind University College of Engineering", "Ramgarh", "private"),
            ("Usha Martin University Faculty of Engineering", "Ranchi", "private"),
        ]

        for name, city, college_type in jharkhand_colleges:
            profile = self.generate_profile_jh(name, college_type, city, "Jharkhand")
            self.colleges.append(profile)

        print(f"Generated {len(self.colleges)} college profiles for Jharkhand.")

    def write_csvs(self):
        """Write all CSV datasets."""
        # college_info.csv
        with open(OUTPUT_DIR / "college_info.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "college", "city", "state", "type", "fees_ug_inr",
                "placement_avg_lpa", "overall_score",
                "academic_score", "campus_score", "industry_score", "source"
            ])
            w.writeheader()
            for c in self.colleges:
                w.writerow({
                    "college": c["college"], "city": c["city"], "state": c["state"],
                    "type": c["type"], "fees_ug_inr": c["fees_ug_inr"],
                    "placement_avg_lpa": c["placement_avg_lpa"],
                    "overall_score": c["overall_score"],
                    "academic_score": c["academic_score"],
                    "campus_score": c["campus_score"],
                    "industry_score": c["industry_score"],
                    "source": c["source"],
                })

        # fees.csv
        with open(OUTPUT_DIR / "fees.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "college", "tuition_fee", "hostel_fee", "mess_fee",
                "one_time_fee", "security_deposit", "total_fee", "academic_year", "source"
            ])
            w.writeheader()
            for c in self.colleges:
                one_time = round(c["fees_ug_inr"] * 0.05 / 1000) * 1000
                security = round(c["fees_ug_inr"] * 0.03 / 1000) * 1000
                total = c["fees_ug_inr"] + c["hostel_fee"] + c["mess_fee"] + one_time + security
                w.writerow({
                    "college": c["college"], "tuition_fee": c["fees_ug_inr"],
                    "hostel_fee": c["hostel_fee"], "mess_fee": c["mess_fee"],
                    "one_time_fee": one_time, "security_deposit": security,
                    "total_fee": total, "academic_year": "2025-26", "source": c["source"],
                })

        # placements.csv
        with open(OUTPUT_DIR / "placements.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "college", "average_package", "highest_package",
                "placement_percentage", "top_recruiters", "source"
            ])
            w.writeheader()
            for c in self.colleges:
                w.writerow({
                    "college": c["college"],
                    "average_package": c["placement_avg_lpa"],
                    "highest_package": c["placement_highest_lpa"],
                    "placement_percentage": c["placement_rate_pct"],
                    "top_recruiters": "; ".join(c["recruiters"][:5]),
                    "source": c["source"],
                })

        # hostel.csv
        with open(OUTPUT_DIR / "hostel.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "college", "hostel_available", "hostel_fee", "mess_fee",
                "hostel_capacity", "room_type", "source"
            ])
            w.writeheader()
            for c in self.colleges:
                w.writerow({
                    "college": c["college"], "hostel_available": "Yes",
                    "hostel_fee": c["hostel_fee"], "mess_fee": c["mess_fee"],
                    "hostel_capacity": c["hostel_capacity"],
                    "room_type": random.choice(["Shared (2-seater)", "Shared (3-seater)", "Single"]),
                    "source": c["source"],
                })

        # admission.csv
        with open(OUTPUT_DIR / "admission.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "college", "entrance_exam", "minimum_eligibility",
                "documents_required", "application_mode", "source"
            ])
            exam_map = {
                "iit_tier": "JEE Advanced",
                "nit_tier": "JEE Main",
                "iiit_tier": "JEE Main / JCECE",
                "government": "Jharkhand Combined Entrance Competitive Examination (JCECE)",
                "state_university": "Jharkhand Combined Entrance Competitive Examination (JCECE)",
                "private": "JEE Main / JCECE / Management Quota",
            }
            w.writeheader()
            for c in self.colleges:
                w.writerow({
                    "college": c["college"],
                    "entrance_exam": exam_map[c["type"]],
                    "minimum_eligibility": "Class 12 with PCM, minimum 75% (65% for SC/ST)",
                    "documents_required": "Class 10 & 12 marksheets, Admit card, Seat allotment letter, Category certificate (if applicable), Passport photo",
                    "application_mode": "Online",
                    "source": c["source"],
                })

        # exam_rules.csv
        with open(OUTPUT_DIR / "exam_rules.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "college", "semester", "exam_type", "attendance_requirement",
                "passing_marks", "revaluation_allowed", "source"
            ])
            w.writeheader()
            for c in self.colleges:
                for exam_type in ["Midterm", "Final"]:
                    w.writerow({
                        "college": c["college"], "semester": "Both",
                        "exam_type": exam_type, "attendance_requirement": "75%",
                        "passing_marks": "40%", "revaluation_allowed": "Yes",
                        "source": c["source"],
                    })

        print("Written: college_info.csv, fees.csv, placements.csv, hostel.csv, admission.csv, exam_rules.csv")

    def write_aliases(self):
        """Write aliases.json for fuzzy college matching."""
        aliases = {}
        for c in self.colleges:
            name = c["college"]
            aliases[name.lower()] = name
            # Add city-based shorthand
            city_alias = f"{c['city'].lower()} engineering college"
            if city_alias not in aliases:
                aliases[city_alias] = name
                
            # Add specific shortcuts for key Jharkhand institutions
            if "ism" in name.lower() or "dhanbad" in name.lower():
                aliases["iit ism"] = name
                aliases["ism dhanbad"] = name
                aliases["iit dhanbad"] = name
            elif "nit jamshedpur" in name.lower() or "jsr" in name.lower():
                aliases["nit jsr"] = name
                aliases["nit jamshedpur"] = name
            elif "iiit ranchi" in name.lower():
                aliases["iiit ranchi"] = name
            elif "birsa institute" in name.lower():
                aliases["bit sindri"] = name
                aliases["birsa institute of technology sindri"] = name
            elif "mesra" in name.lower():
                aliases["bit mesra"] = name
                aliases["birla institute of technology mesra ranchi"] = name
            elif "cambridge" in name.lower():
                aliases["cit ranchi"] = name
            elif "rtc" in name.lower():
                aliases["rtc ranchi"] = name
            elif "rvs" in name.lower():
                aliases["rvs jamshedpur"] = name
            elif "dumka" in name.lower():
                aliases["dumka engineering college"] = name
            elif "palamu" in name.lower():
                aliases["palamu engineering college"] = name
            elif "ramgarh" in name.lower():
                aliases["ramgarh engineering college"] = name
            elif "chaibasa" in name.lower():
                aliases["chaibasa engineering college"] = name
            elif "godda" in name.lower():
                aliases["godda engineering college"] = name
                
        with open(OUTPUT_DIR / "aliases.json", "w", encoding="utf-8") as f:
            json.dump(aliases, f, indent=2)
        print(f"Written: aliases.json ({len(aliases)} aliases)")

    def write_markdown(self):
        """Write per-college, per-section markdown files to corpus/."""
        today = date.today().isoformat()
        written = 0

        for c in self.colleges:
            state_slug = c["state"].lower().replace(" ", "_")
            col_dir = CORPUS_DIR / state_slug / c["id"]
            col_dir.mkdir(parents=True, exist_ok=True)

            depts_str = ", ".join(c["departments"])
            recruiters_str = ", ".join(c["recruiters"])
            scholarships_str = "\n".join(f"- {s}" for s in c["scholarships"])
            type_label = {
                "iit_tier": "an IIT-tier autonomous institute",
                "nit_tier": "a National Institute of Technology (NIT)",
                "iiit_tier": "an Institute of Information Technology",
                "government": "a government engineering college",
                "state_university": "a state technical university",
                "private": "a private engineering institute",
            }[c["type"]]

            # ── overview.md ──────────────────────────────────────────────
            (col_dir / "overview.md").write_text(f"""# {c['college']}

> **Source:** Synthetic Benchmark Corpus v1.0 | **Confidence:** Generated | **Date:** {today}

## Overview
{c['college']} is {type_label} established in {c['established']}, located in {c['city']}, {c['state']}. \
The institute offers undergraduate and postgraduate engineering programmes across {c['dept_count']} departments \
and has a student strength of approximately {c['student_strength']:,} students.

The institute is committed to academic excellence and industry engagement, maintaining an overall benchmark \
score of {c['overall_score']}/10 (Academic: {c['academic_score']}, Campus: {c['campus_score']}, Industry: {c['industry_score']}).

## Departments
{depts_str}

## Programmes Offered
- B.Tech (4-year undergraduate programme)
- M.Tech (2-year postgraduate programme, select departments)
- Ph.D. (Doctoral research programme, select departments)

## Location
- **City:** {c['city']}
- **State:** {c['state']}
- **Campus Area:** Approximately {c['campus_area_acres']} acres

## Approvals & Affiliations
- Approved by All India Council for Technical Education (AICTE)
- Affiliated to the Jharkhand University of Technology (JUT) or respective university
- Accreditation status: NBA-accredited programmes (select branches)
""", encoding="utf-8")

            # ── fees.md ──────────────────────────────────────────────────
            one_time = round(c["fees_ug_inr"] * 0.05 / 1000) * 1000
            security = round(c["fees_ug_inr"] * 0.03 / 1000) * 1000
            (col_dir / "fees.md").write_text(f"""# Fee Structure — {c['college']}

> **Source:** Synthetic Benchmark Corpus v1.0 | **Confidence:** Generated | **Date:** {today}

## Annual Fee Structure (B.Tech, 2025–26)

| Component | Amount (₹) |
|---|---|
| Tuition Fee | ₹{c['fees_ug_inr']:,} |
| One-Time Admission Fee | ₹{one_time:,} |
| Security Deposit (refundable) | ₹{security:,} |

## Hostel & Mess Fees (per semester)

| Component | Amount (₹) |
|---|---|
| Hostel Rent | ₹{c['hostel_fee']:,} |
| Mess / Food Charges | ₹{c['mess_fee']:,} |

## Payment
All fees are payable online through the institute's student portal. \
A late payment penalty of ₹500/week applies beyond the due date.

## Fee Waivers
SC/ST students are eligible for a full tuition fee waiver subject to Jharkhand state government norms. \
EWS students may apply for fee concession through the National Scholarship Portal or Jharkhand e-Kalyan portal.
""", encoding="utf-8")

            # ── hostel.md ────────────────────────────────────────────────
            (col_dir / "hostel.md").write_text(f"""# Hostel & Accommodation — {c['college']}

> **Source:** Synthetic Benchmark Corpus v1.0 | **Confidence:** Generated | **Date:** {today}

## Hostel Availability
Hostel accommodation is available on campus for both boys and girls.

| Detail | Information |
|---|---|
| Total Hostel Capacity | {c['hostel_capacity']:,} seats |
| Annual Hostel Rent | ₹{c['hostel_fee']:,} |
| Annual Mess Charges | ₹{c['mess_fee']:,} |
| Room Type | Shared (2–3 occupants) |

## Facilities
- 24-hour security and CCTV surveillance
- High-speed Wi-Fi in all hostel blocks
- Indoor common room with television and recreational facilities
- Laundry and ironing room
- Medical room with first-aid provisions
- Generator backup for uninterrupted power

## Mess
The institute runs a centrally managed mess serving breakfast, lunch, snacks, and dinner. \
Special dietary menus are available on request.

## Admission to Hostel
Hostel allocation is managed by the Dean of Student Welfare on a first-come, first-served basis \
with priority given to students from outside {c['city']}.
""", encoding="utf-8")

            # ── admissions.md ────────────────────────────────────────────
            exam_map = {
                "iit_tier": "JEE Advanced",
                "nit_tier": "JEE Main",
                "iiit_tier": "JEE Main / JCECE",
                "government": "Jharkhand Combined Entrance Competitive Examination (JCECE)",
                "state_university": "Jharkhand Combined Entrance Competitive Examination (JCECE)",
                "private": "JEE Main / JCECE / Management Quota",
            }
            (col_dir / "admissions.md").write_text(f"""# Admissions — {c['college']}

> **Source:** Synthetic Benchmark Corpus v1.0 | **Confidence:** Generated | **Date:** {today}

## Entrance Examination
Admission to the B.Tech programme is based on performance in **{exam_map[c['type']]}**.

## Eligibility Criteria
- Passed Class 12 (or equivalent) with Physics, Chemistry, and Mathematics
- Minimum aggregate: **75%** (65% for SC/ST/PwD candidates)
- Age: Not more than 25 years at the time of admission (30 for SC/ST/PwD)

## Application Process
1. Register on the official Jharkhand JCECEB or national JOSAA portal
2. Fill in the online application form and upload documents
3. Pay the application fee online
4. Attend counselling as per schedule

## Documents Required
- Class 10 mark sheet and certificate
- Class 12 mark sheet and certificate
- Entrance exam scorecard / rank card
- Seat allotment letter
- Category certificate (SC/ST/OBC/EWS, if applicable, issued by Jharkhand authority)
- Passport-size photographs (6 copies)
- Medical fitness certificate
- Character certificate from the last institution attended

## Important Dates (Indicative)
- Application window: April – June
- Counselling rounds: June – July
- Classes commence: August
""", encoding="utf-8")

            # ── placements.md ────────────────────────────────────────────
            (col_dir / "placements.md").write_text(f"""# Placements — {c['college']}

> **Source:** Synthetic Benchmark Corpus v1.0 | **Confidence:** Generated | **Date:** {today}

## Placement Statistics (2024–25)

| Metric | Value |
|---|---|
| Average Package | ₹{c['placement_avg_lpa']} LPA |
| Highest Package | ₹{c['placement_highest_lpa']} LPA |
| Placement Rate | {c['placement_rate_pct']}% |

## Top Recruiters
{recruiters_str}

## Internships
The institute's Training & Placement Cell facilitates pre-final year internships with leading \
companies. Students are encouraged to apply through the institute portal as well as directly \
on company career pages.

## Training & Placement Cell
The cell organises mock interviews, resume workshops, aptitude training, and group discussion \
sessions throughout the academic year to prepare students for campus recruitment drives.
""", encoding="utf-8")

            # ── scholarships.md ──────────────────────────────────────────
            (col_dir / "scholarships.md").write_text(f"""# Scholarships — {c['college']}

> **Source:** Synthetic Benchmark Corpus v1.0 | **Confidence:** Generated | **Date:** {today}

## Available Scholarships

{scholarships_str}

## Application
Most scholarships are applied for through the **e-Kalyan Portal (ekalyan.cgg.gov.in)** for Jharkhand \
state schemes, or through the National Scholarship Portal. Students should apply within 30 days of the \
commencement of the first semester.

## Additional Support
The institute has a Student Welfare Fund to provide emergency financial assistance to students \
in genuine need. Applications can be made to the Dean of Student Welfare at any time.
""", encoding="utf-8")

            # ── campus.md ────────────────────────────────────────────────
            (col_dir / "campus.md").write_text(f"""# Campus Facilities — {c['college']}

> **Source:** Synthetic Benchmark Corpus v1.0 | **Confidence:** Generated | **Date:** {today}

## Academic Infrastructure
- **Laboratories:** {c['lab_count']} well-equipped labs across all departments
- **Central Library:** {c['library_books']:,} books, journals, and digital resources
- **Classrooms:** Fully furnished with projectors and smart-board technology
- **Seminar Halls:** Available for guest lectures, workshops, and conferences

## Campus
- **Area:** {c['campus_area_acres']} acres of landscaped campus
- **Established:** {c['established']}
- **Student Strength:** Approximately {c['student_strength']:,}

## Sports & Recreation
- Open playgrounds for cricket, football, and athletics
- Indoor sports complex: badminton, table tennis, chess, carrom
- Annual sports meet and inter-college tournaments

## Student Clubs & Activities
- Technical clubs (Coding, Robotics, Electronics)
- Cultural clubs (Music, Drama, Fine Arts)
- Entrepreneurship and Innovation Cell
- NSS (National Service Scheme) chapter
- Literary and Debate Society

## Medical & Wellness
- On-campus medical centre with qualified doctors
- Ambulance facility for emergencies
- Counselling and mental health support services

## Transportation
- Institute bus service connecting key city points
- Parking facilities for two-wheelers and four-wheelers
""", encoding="utf-8")

            # ── faq.md ───────────────────────────────────────────────────
            (col_dir / "faq.md").write_text(f"""# Frequently Asked Questions — {c['college']}

> **Source:** Synthetic Benchmark Corpus v1.0 | **Confidence:** Generated | **Date:** {today}

**Q: What is the annual tuition fee?**
A: The annual tuition fee for B.Tech is ₹{c['fees_ug_inr']:,}.

**Q: Is hostel accommodation available?**
A: Yes. The institute provides hostel accommodation for up to {c['hostel_capacity']:,} students. \
Hostel rent is ₹{c['hostel_fee']:,} per year.

**Q: What is the average placement package?**
A: The average package for the 2024–25 batch was ₹{c['placement_avg_lpa']} LPA, \
with the highest package at ₹{c['placement_highest_lpa']} LPA.

**Q: Which entrance exam is accepted for admission?**
A: {exam_map[c['type']]}.

**Q: Are scholarships available?**
A: Yes. The institute offers {len(c['scholarships'])} scholarship schemes including merit-based \
and category-based financial aid. See the Scholarships section for details.

**Q: How many departments does the institute have?**
A: The institute has {c['dept_count']} departments: {depts_str}.
""", encoding="utf-8")

            written += 1

        print(f"Written: {written} college markdown packages to corpus/")

    def write_dataset_info(self):
        """Write the self-describing dataset manifest."""
        states = list(set(c["state"] for c in self.colleges))
        info = {
            "dataset_type": "synthetic",
            "version": "1.0",
            "generator_seed": SEED,
            "generated_on": date.today().isoformat(),
            "college_count": len(self.colleges),
            "type_distribution": {
                "iit_tier": sum(1 for c in self.colleges if c["type"] == "iit_tier"),
                "nit_tier": sum(1 for c in self.colleges if c["type"] == "nit_tier"),
                "iiit_tier": sum(1 for c in self.colleges if c["type"] == "iiit_tier"),
                "government": sum(1 for c in self.colleges if c["type"] == "government"),
                "state_university": sum(1 for c in self.colleges if c["type"] == "state_university"),
                "private": sum(1 for c in self.colleges if c["type"] == "private"),
            },
            "states_covered": len(states),
            "disclaimer": (
                "This dataset contains entirely fictional or semi-fictionalized institution names and synthetic statistics. "
                "It is intended solely for demonstration, benchmarking, and evaluation of "
                "retrieval-augmented conversational AI systems. It does not represent any real "
                "institution, its fees, placements, or rankings."
            ),
        }
        with open(OUTPUT_DIR / "dataset_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
        print(f"Written: dataset_info.json ({len(self.colleges)} colleges, {len(states)} states)")

    def print_summary(self):
        """Print a distribution summary table."""
        from collections import Counter
        counts = Counter(c["type"] for c in self.colleges)
        print("\n=== Corpus Summary ===")
        for t, n in counts.items():
            print(f"  {t:<20} {n:>4} colleges")
        fees = [c["fees_ug_inr"] for c in self.colleges]
        pkgs = [c["placement_avg_lpa"] for c in self.colleges]
        print(f"\n  Fee range:       Rs. {min(fees):,} - Rs. {max(fees):,}")
        print(f"  Avg package:     {min(pkgs):.1f} - {max(pkgs):.1f} LPA")
        print(f"  Total colleges:  {len(self.colleges)}")
        print("======================\n")

    def run(self):
        self.generate_all()
        self.write_csvs()
        self.write_aliases()
        self.write_markdown()
        self.write_dataset_info()
        self.print_summary()


if __name__ == "__main__":
    CorpusGenerator().run()
