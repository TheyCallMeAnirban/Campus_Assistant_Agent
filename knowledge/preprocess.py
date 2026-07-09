import os
import pandas as pd

SUPPORTED_COLLEGES = [
    "IIT (ISM) Dhanbad",
    "IIT Bhilai",
    "NIT Jamshedpur",
    "NIT Rourkela",
    "IIT Kharagpur"
]

def preprocess():
    raw_dir = "knowledge/raw"
    processed_dir = "knowledge/processed"
    os.makedirs(processed_dir, exist_ok=True)
    
    # 1. Load raw files
    df_college_info = pd.read_csv(os.path.join(raw_dir, "college_info_raw.csv"))
    df_fees = pd.read_csv(os.path.join(raw_dir, "fees_raw.csv"))
    df_placements = pd.read_csv(os.path.join(raw_dir, "placements_raw.csv"))
    df_hostel = pd.read_csv(os.path.join(raw_dir, "hostel_raw.csv"))
    df_admission = pd.read_csv(os.path.join(raw_dir, "admission_raw.csv"))
    df_exam_rules = pd.read_csv(os.path.join(raw_dir, "exam_rules_raw.csv"))
    
    # Process Scholarship (from root database)
    admissions_root_path = "knowledge/College_Admission.csv"
    if os.path.exists(admissions_root_path):
        df_sch_raw = pd.read_csv(admissions_root_path)
        scholarship_cols = [
            "gender", "category", "preferred_stream", "entrance_exam", 
            "entrance_score", "board_percentage", "scholarship_eligibility", "admission_status"
        ]
        df_scholarship = df_sch_raw[scholarship_cols].drop_duplicates()
        df_scholarship.to_csv(os.path.join(processed_dir, "scholarship.csv"), index=False)
        print("Processed scholarship.csv created.")
    else:
        print("College_Admission.csv not found at root!")

    # 2. Write processed tables
    df_college_info.drop_duplicates().to_csv(os.path.join(processed_dir, "college_info.csv"), index=False)
    df_fees.drop_duplicates().to_csv(os.path.join(processed_dir, "fees.csv"), index=False)
    df_placements.drop_duplicates().to_csv(os.path.join(processed_dir, "placements.csv"), index=False)
    df_hostel.drop_duplicates().to_csv(os.path.join(processed_dir, "hostel.csv"), index=False)
    df_admission.drop_duplicates().to_csv(os.path.join(processed_dir, "admission.csv"), index=False)
    df_exam_rules.drop_duplicates().to_csv(os.path.join(processed_dir, "exam_rules.csv"), index=False)
    
    print("All processed domain-specific CSVs written to knowledge/processed/.")

    # 3. Perform Validation and compile validation_report.csv
    report_rows = []
    
    # Check fields across files
    checks = [
        ("college_info", df_college_info, "college"),
        ("fees", df_fees, "college"),
        ("placements", df_placements, "college"),
        ("hostel", df_hostel, "college"),
        ("admission", df_admission, "college"),
        ("exam_rules", df_exam_rules, "college")
    ]
    
    for college in SUPPORTED_COLLEGES:
        for domain, df, col_name in checks:
            matching_rows = df[df[col_name].str.lower() == college.lower()]
            if matching_rows.empty:
                report_rows.append({"college": college, "field": domain, "status": "MISSING"})
            else:
                # Check for null values in critical fields
                row = matching_rows.iloc[0]
                has_null = row.isnull().any()
                status = "MISSING_FIELDS" if has_null else "OK"
                report_rows.append({"college": college, "field": domain, "status": status})
                
    report_df = pd.DataFrame(report_rows)
    report_df.to_csv("knowledge/validation_report.csv", index=False)
    print("knowledge/validation_report.csv report generated successfully.")

if __name__ == "__main__":
    preprocess()
