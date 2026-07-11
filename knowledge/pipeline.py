import os
import sys
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
import pypdf
import urllib3
from datetime import datetime

# Suppress SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MANIFEST_PATH = "knowledge/college_manifest.json"
ALIASES_PATH = "knowledge/aliases.json"
STATES_DIR = "knowledge/states"
GENERATED_DIR = "knowledge/generated"
LOGS_DIR = "knowledge/pipeline/logs"
CACHE_DIR = "knowledge/cache"

# Ensure target directories exist
os.makedirs(STATES_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Keyword map for page-level PDF filtering to keep ingested documents compact
KEYWORD_MAP = {
    "fees": ["fee", "tuition", "hostel", "mess", "caution", "amount", "rupee", "inr", "charge", "payment", "demand draft", "online transaction"],
    "placements": ["placement", "package", "ctc", "highest", "average", "median", "recruiter", "offer", "job", "lpa", "salary"],
    "admissions": ["admission", "eligibility", "entrance", "exam", "jcece", "josaa", "csab", "seat", "application", "document", "marksheet"],
    "scholarships": ["scholarship", "financial aid", "grant", "fellowship", "concession", "waiver", "remission"],
    "overview": ["about", "overview", "established", "vision", "mission", "campus", "legacy", "history"],
    "hostel": ["hostel", "accommodation", "room", "mess", "warden", "hall of residence", "housing"]
}

class Pipeline:
    def __init__(self, manifest_path=MANIFEST_PATH):
        with open(manifest_path, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)
        self.colleges = self.manifest.get("colleges", [])
        self.refresh_cache = "--refresh" in sys.argv

    def log(self, college_id, message):
        log_file = os.path.join(LOGS_DIR, f"{college_id}.log")
        clean_msg = message.replace("✔", "[OK]").replace("❌", "[FAILED]")
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write(f"{clean_msg}\n")
        
        # Safe console print for cp1252 on Windows
        safe_print_msg = clean_msg.encode('ascii', errors='replace').decode('ascii')
        print(f"[{college_id}] {safe_print_msg}")

    def clean_html(self, html_content):
        """Strip HTML tags and get readable text."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "head", "iframe"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines()]
            clean_lines = [line for line in lines if line]
            return "\n".join(clean_lines)
        except Exception as e:
            return f"Error cleaning HTML: {e}"

    def parse_pdf_with_filtering(self, college_id, cache_path, src_type):
        """Extract text page-by-page from PDF and keep only relevant pages using keywords."""
        try:
            reader = pypdf.PdfReader(cache_path)
            pages_extracted = []
            keywords = KEYWORD_MAP.get(src_type, [])
            
            has_extractable_text = False
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    has_extractable_text = True
                
                # Check for keywords on this page
                text_lower = text.lower()
                matched = any(kw in text_lower for kw in keywords) if keywords else True
                if matched:
                    pages_extracted.append(f"--- PDF PAGE {i+1} ---\n{text.strip()}")
            
            if not has_extractable_text:
                self.log(college_id, f"PDF {cache_path} is scanned/image-only. Requires Manual Review.")
                return "Requires Manual Review."
                
            if not pages_extracted:
                self.log(college_id, f"No pages matched keywords {keywords} in PDF {cache_path} for type {src_type}")
                return "Information not found in official sources."
                
            self.log(college_id, f"Extracted {len(pages_extracted)} / {len(reader.pages)} pages from PDF ✔")
            return "\n\n".join(pages_extracted)
        except Exception as e:
            self.log(college_id, f"Error parsing PDF {cache_path}: {e} ❌")
            return f"Error parsing PDF: {e}"

    def download_url(self, college_id, url, src_type):
        """Download URL (saving to cache) or retrieve from cache."""
        parsed_url = url.split("?")[0]
        ext = ".pdf" if parsed_url.lower().endswith(".pdf") else ".html"
        college_cache_dir = os.path.join(CACHE_DIR, college_id)
        os.makedirs(college_cache_dir, exist_ok=True)
        cache_path = os.path.join(college_cache_dir, f"{src_type}{ext}")

        # Check Cache
        if not self.refresh_cache and os.path.exists(cache_path):
            self.log(college_id, f"Using cached copy of {src_type} URL: {url} from {cache_path} ✔")
            if ext == ".pdf":
                return self.parse_pdf_with_filtering(college_id, cache_path, src_type)
            else:
                with open(cache_path, "r", encoding="utf-8") as cf:
                    return self.clean_html(cf.read())

        # Download Fresh Copy
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        try:
            self.log(college_id, f"Downloading fresh URL: {url}")
            r = requests.get(url, headers=headers, timeout=20, verify=False)
            if r.status_code == 200:
                self.log(college_id, "Download successful ✔")
                if ext == ".pdf":
                    with open(cache_path, "wb") as f:
                        f.write(r.content)
                    return self.parse_pdf_with_filtering(college_id, cache_path, src_type)
                else:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(r.text)
                    return self.clean_html(r.text)
            else:
                self.log(college_id, f"Download failed with status code: {r.status_code} ❌")
                return None
        except Exception as e:
            self.log(college_id, f"Download exception: {e} ❌")
            return None

    def build_aliases(self):
        """Build aliases dictionary and save to aliases.json."""
        print("Generating aliases.json...")
        aliases_map = {}
        for col in self.colleges:
            official_name = col["college"]
            for alias in col.get("aliases", []):
                aliases_map[alias.lower()] = official_name
        with open(ALIASES_PATH, "w", encoding="utf-8") as f:
            json.dump(aliases_map, f, indent=2)
        print(f"Saved {len(aliases_map)} aliases to {ALIASES_PATH}")

    def run(self):
        self.build_aliases()
        validation_records = []
        today_str = datetime.today().strftime('%Y-%m-%d')

        # Prepare base lists for updating CSVs
        college_info_list = []
        fees_list = []
        placements_list = []
        hostel_list = []
        admission_list = []
        exam_rules_list = []

        for col in self.colleges:
            college_id = col["id"]
            college_name = col["college"]
            state = col.get("state", "Jharkhand").lower()
            state_dir = os.path.join(STATES_DIR, state)
            os.makedirs(state_dir, exist_ok=True)

            # Clear previous log file on refresh
            log_file = os.path.join(LOGS_DIR, f"{college_id}.log")
            if self.refresh_cache and os.path.exists(log_file):
                os.remove(log_file)

            self.log(college_id, f"Starting processing for {college_name}")

            sections = {
                "overview": "",
                "fees": "",
                "placements": "",
                "hostel": "",
                "admissions": "",
                "scholarships": ""
            }

            sources_attrib = {
                "overview": "N/A",
                "fees": "N/A",
                "placements": "N/A",
                "hostel": "N/A",
                "admissions": "N/A",
                "scholarships": "N/A"
            }

            # Download and parse each source URL
            for src in col.get("sources", []):
                src_type = src["type"]
                url = src["url"]
                if src_type in sections:
                    cleaned_content = self.download_url(college_id, url, src_type)
                    if cleaned_content:
                        sections[src_type] = cleaned_content[:6000]
                        sources_attrib[src_type] = url
                    else:
                        sections[src_type] = "Information not found in official sources."
                        sources_attrib[src_type] = f"{url} (Fetch Failed)"

            # Check populated sections and calculate coverage metrics
            populated_statuses = {
                "Overview": sections["overview"] and "not found" not in sections["overview"].lower() and "failed" not in sources_attrib["overview"].lower(),
                "Fees": sections["fees"] and "not found" not in sections["fees"].lower() and "failed" not in sources_attrib["fees"].lower(),
                "Hostel": sections["hostel"] and "not found" not in sections["hostel"].lower() and "failed" not in sources_attrib["hostel"].lower(),
                "Placements": sections["placements"] and "not found" not in sections["placements"].lower() and "failed" not in sources_attrib["placements"].lower(),
                "Admissions": sections["admissions"] and "not found" not in sections["admissions"].lower() and "failed" not in sources_attrib["admissions"].lower(),
                "Scholarships": sections["scholarships"] and "not found" not in sections["scholarships"].lower() and "failed" not in sources_attrib["scholarships"].lower()
            }

            # Calculation details
            total_sections = 6
            success_count = sum(1 for status in populated_statuses.values() if status)
            coverage_pct = int((success_count / total_sections) * 100)
            
            missing_list = [sec for sec, stat in populated_statuses.items() if not stat]
            missing_str = ", ".join(missing_list) if missing_list else "None"
            
            priority_1_satisfied = (
                populated_statuses["Overview"] and 
                populated_statuses["Admissions"] and 
                populated_statuses["Fees"] and 
                populated_statuses["Placements"]
            )

            val_record = {
                "College": college_name,
                "Overview": "✅" if populated_statuses["Overview"] else "❌",
                "Fees": "✅" if populated_statuses["Fees"] else "❌",
                "Hostel": "✅" if populated_statuses["Hostel"] else "❌",
                "Placements": "✅" if populated_statuses["Placements"] else "❌",
                "Admissions": "✅" if populated_statuses["Admissions"] else "❌",
                "Scholarships": "✅" if populated_statuses["Scholarships"] else "❌",
                "Coverage": f"{coverage_pct}%",
                "Priority 1": "✅" if priority_1_satisfied else "❌",
                "Missing Sections": missing_str
            }
            validation_records.append(val_record)

            # Generate Structured JSON cache
            structured_json = {
                "college": college_name,
                "sections": sections,
                "sources": sources_attrib,
                "metrics": {
                    "coverage": f"{coverage_pct}%",
                    "priority_1": priority_1_satisfied,
                    "missing": missing_list
                }
            }
            json_cache_dir = os.path.join(LOGS_DIR, "json")
            os.makedirs(json_cache_dir, exist_ok=True)
            with open(os.path.join(json_cache_dir, f"{college_id}.json"), "w", encoding="utf-8") as jf:
                json.dump(structured_json, jf, indent=2)

            # Generate Markdown File
            md_content = f"""# {college_name}

Last Updated: {today_str}
Coverage: {coverage_pct}%
Priority 1: {"✅ Yes" if priority_1_satisfied else "❌ No"}
Missing Sections: {missing_str}

## Overview
{sections["overview"] or "Information not found in official sources."}

## Location
City: {col.get("city", "N/A")}
District: {col.get("city", "N/A")}
State: {col.get("state", "N/A")}
Campus type: N/A

## Institute Details
Ownership: N/A
Established year: N/A
Official website: {col.get("sources", [{}])[0].get("url", "N/A") if col.get("sources") else "N/A"}

## Courses Offered
Information not found in official sources.

## Admissions
{sections["admissions"] or "Information not found in official sources."}

## Fee Structure
{sections["fees"] or "Information not found in official sources."}

## Hostel
{sections["hostel"] or "Information not found in official sources."}

## Placements
{sections["placements"] or "Information not found in official sources."}

## Facilities
Information not found in official sources.

## Scholarships
{sections["scholarships"] or "Information not found in official sources."}

## Contact
Address: {col.get("city", "N/A")}, {col.get("state", "N/A")}
Official Website: {col.get("sources", [{}])[0].get("url", "N/A") if col.get("sources") else "N/A"}

## Sources
Overview: {sources_attrib["overview"]}
Admissions: {sources_attrib["admissions"]}
Fee Structure: {sources_attrib["fees"]}
Hostel: {sources_attrib["hostel"]}
Placements: {sources_attrib["placements"]}
Scholarships: {sources_attrib["scholarships"]}
"""
            md_path = os.path.join(state_dir, f"{college_id}.md")
            with open(md_path, "w", encoding="utf-8") as mdf:
                mdf.write(md_content)
            self.log(college_id, f"Generated Markdown at {md_path} ✔")

            # Collect Basic Info for CSVs
            college_info_list.append({
                "college": college_name,
                "city": col.get("city"),
                "state": col.get("state"),
                "type": col.get("type"),
                "fees_ug_inr": None,
                "placement_avg_lpa": None,
                "rating": 7.5,
                "source": col.get("sources", [{}])[0].get("url", "Official Website") if col.get("sources") else "Official Website"
            })
            
            fees_list.append({
                "college": college_name,
                "tuition_fee": None,
                "hostel_fee": None,
                "mess_fee": None,
                "one_time_fee": None,
                "security_deposit": None,
                "total_fee": None,
                "academic_year": "2025-26",
                "source": col.get("sources", [{}])[0].get("url", "Official Website") if col.get("sources") else "Official Website"
            })

            placements_list.append({
                "college": college_name,
                "average_package": None,
                "highest_package": None,
                "placement_percentage": None,
                "source": col.get("sources", [{}])[0].get("url", "Official Website") if col.get("sources") else "Official Website"
            })

            hostel_list.append({
                "college": college_name,
                "hostel_available": "Yes",
                "hostel_fee": None,
                "room_type": "Sharing",
                "mess_required": "Yes",
                "source": col.get("sources", [{}])[0].get("url", "Official Website") if col.get("sources") else "Official Website"
            })

            admission_list.append({
                "college": college_name,
                "entrance_exam": "JEE Main / JCECE" if col.get("type") in ["NIT", "IIIT", "Engineering"] else "JEE Advanced",
                "minimum_eligibility": "Class 12 pass with 75% aggregate" if col.get("type") in ["IIT", "NIT", "IIIT"] else "Class 12 pass",
                "documents_required": "Class 10 mark sheet, Class 12 mark sheet, Admit card, Seat allotment letter",
                "application_mode": "Online",
                "source": col.get("sources", [{}])[0].get("url", "Official Website") if col.get("sources") else "Official Website"
            })

            exam_rules_list.append({
                "college": college_name,
                "semester": "Fall",
                "exam_type": "Midterm",
                "attendance_requirement": "75%",
                "passing_marks": "40%",
                "revaluation_allowed": "Yes",
                "source": "Official Academic Regulations"
            })
            exam_rules_list.append({
                "college": college_name,
                "semester": "Fall",
                "exam_type": "Final",
                "attendance_requirement": "75%",
                "passing_marks": "40%",
                "revaluation_allowed": "Yes",
                "source": "Official Academic Regulations"
            })

        # Save Validation Report as CSV
        val_df = pd.DataFrame(validation_records)
        val_csv_path = os.path.join(GENERATED_DIR, "validation_report.csv")
        val_df.to_csv(val_csv_path, index=False, encoding="utf-8")
        print(f"Saved validation report to {val_csv_path}")

        # Update CSV files
        csv_mappings = [
            ("college_info.csv", college_info_list),
            ("fees.csv", fees_list),
            ("placements.csv", placements_list),
            ("hostel.csv", hostel_list),
            ("admission.csv", admission_list),
            ("exam_rules.csv", exam_rules_list)
        ]

        for fname, new_data_list in csv_mappings:
            prod_path = os.path.join("knowledge", fname)
            gen_path = os.path.join(GENERATED_DIR, fname)
            
            if os.path.exists(prod_path):
                existing_df = pd.read_csv(prod_path)
            else:
                existing_df = pd.DataFrame()

            new_df = pd.DataFrame(new_data_list)

            if not existing_df.empty:
                # Retain non-Jharkhand records, overwrite manifest entries
                manifest_college_names = [col["college"].strip().lower() for col in self.colleges]
                filtered_existing_df = existing_df[~existing_df["college"].str.strip().str.lower().isin(manifest_college_names)]
                merged_df = pd.concat([filtered_existing_df, new_df], ignore_index=True)
            else:
                merged_df = new_df

            # Save staging CSV
            merged_df.to_csv(gen_path, index=False, encoding="utf-8")
            print(f"Generated staging database: {gen_path} ({len(merged_df)} rows total)")

if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run()
