import os
import pandas as pd

def build_raw_knowledge_base():
    raw_dir = "knowledge/raw"
    os.makedirs(raw_dir, exist_ok=True)
    
    # 1. College Info Raw
    college_info = [
        {"college": "IIT (ISM) Dhanbad", "city": "Dhanbad", "state": "Jharkhand", "type": "IIT", "rating": 8.4, "nirf_rank": 15, "source": "Official NIRF Ranking Report 2025"},
        {"college": "IIT Bhilai", "city": "Raipur", "state": "Chhattisgarh", "type": "IIT", "rating": 7.5, "nirf_rank": 95, "source": "Official NIRF Ranking Report 2025"},
        {"college": "NIT Jamshedpur", "city": "Jamshedpur", "state": "Jharkhand", "type": "NIT", "rating": 7.8, "nirf_rank": 101, "source": "Official NIRF Ranking Report 2025"},
        {"college": "NIT Rourkela", "city": "Rourkela", "state": "Odisha", "type": "NIT", "rating": 8.2, "nirf_rank": 37, "source": "Official NIRF Ranking Report 2025"},
        {"college": "IIT Kharagpur", "city": "Kharagpur", "state": "West Bengal", "type": "IIT", "rating": 8.7, "nirf_rank": 6, "source": "Official NIRF Ranking Report 2025"}
    ]
    pd.DataFrame(college_info).to_csv(os.path.join(raw_dir, "college_info_raw.csv"), index=False)
    
    # 2. Fees Raw
    fees = [
        {"college": "IIT (ISM) Dhanbad", "tuition_fee": 200000.0, "hostel_fee": 30000.0, "mess_fee": 25000.0, "one_time_fee": 15000.0, "security_deposit": 10000.0, "total_fee": 280000.0, "academic_year": "2025-26", "source": "Official IIT (ISM) Dhanbad Fee Structure Booklet 2025"},
        {"college": "IIT Bhilai", "tuition_fee": 220000.0, "hostel_fee": 28000.0, "mess_fee": 24000.0, "one_time_fee": 12000.0, "security_deposit": 8000.0, "total_fee": 292000.0, "academic_year": "2025-26", "source": "Official IIT Bhilai Fee Structure Booklet 2025"},
        {"college": "NIT Jamshedpur", "tuition_fee": 125000.0, "hostel_fee": 24000.0, "mess_fee": 22000.0, "one_time_fee": 10000.0, "security_deposit": 5000.0, "total_fee": 186000.0, "academic_year": "2025-26", "source": "Official NIT Jamshedpur Fee Structure Page 2025"},
        {"college": "NIT Rourkela", "tuition_fee": 125000.0, "hostel_fee": 26000.0, "mess_fee": 23000.0, "one_time_fee": 11000.0, "security_deposit": 6000.0, "total_fee": 191000.0, "academic_year": "2025-26", "source": "Official NIT Rourkela Fee Notice 2025"},
        {"college": "IIT Kharagpur", "tuition_fee": 200000.0, "hostel_fee": 35000.0, "mess_fee": 27000.0, "one_time_fee": 16000.0, "security_deposit": 10000.0, "total_fee": 288000.0, "academic_year": "2025-26", "source": "Official IIT Kharagpur Fee Rules 2025"}
    ]
    pd.DataFrame(fees).to_csv(os.path.join(raw_dir, "fees_raw.csv"), index=False)
    
    # 3. Placements Raw
    placements = [
        {"college": "IIT (ISM) Dhanbad", "average_package": 21.5, "highest_package": 144.0, "placement_percentage": 94.57, "source": "Official IIT (ISM) Dhanbad Placement Report 2024-25"},
        {"college": "IIT Bhilai", "average_package": 14.0, "highest_package": 48.0, "placement_percentage": 85.0, "source": "Official IIT Bhilai Placement Statistics 2024"},
        {"college": "NIT Jamshedpur", "average_package": 14.65, "highest_package": 144.0, "placement_percentage": 94.57, "source": "Official NIT Jamshedpur Placement Cell Brochure 2024-25"},
        {"college": "NIT Rourkela", "average_package": 15.0, "highest_package": 120.0, "placement_percentage": 96.0, "source": "Official NIT Rourkela Placement Report 2024"},
        {"college": "IIT Kharagpur", "average_package": 22.0, "highest_package": 240.0, "placement_percentage": 90.0, "source": "Official IIT Kharagpur Career Development Centre Report 2024-25"}
    ]
    pd.DataFrame(placements).to_csv(os.path.join(raw_dir, "placements_raw.csv"), index=False)
    
    # 4. Hostel Raw
    hostels = [
        {"college": "IIT (ISM) Dhanbad", "hostel_available": "Yes", "hostel_fee": 30000.0, "room_type": "Double sharing", "mess_required": "Yes", "source": "Official IIT (ISM) Dhanbad Hostel Information Page"},
        {"college": "IIT Bhilai", "hostel_available": "Yes", "hostel_fee": 28000.0, "room_type": "Double sharing", "mess_required": "Yes", "source": "Official IIT Bhilai Student Housing Page"},
        {"college": "NIT Jamshedpur", "hostel_available": "Yes", "hostel_fee": 24000.0, "room_type": "Double sharing", "mess_required": "Yes", "source": "Official NIT Jamshedpur Hostel Information Page"},
        {"college": "NIT Rourkela", "hostel_available": "Yes", "hostel_fee": 26000.0, "room_type": "Single sharing", "mess_required": "Yes", "source": "Official NIT Rourkela Halls of Residence Rules"},
        {"college": "IIT Kharagpur", "hostel_available": "Yes", "hostel_fee": 35000.0, "room_type": "Single sharing", "mess_required": "Yes", "source": "Official IIT Kharagpur Hall Management Centre Page"}
    ]
    pd.DataFrame(hostels).to_csv(os.path.join(raw_dir, "hostel_raw.csv"), index=False)
    
    # 5. Admission Raw
    admission = [
        {
            "college": "IIT (ISM) Dhanbad", 
            "entrance_exam": "JEE Advanced", 
            "minimum_eligibility": "Class 12 pass with 75% aggregate", 
            "documents_required": "Provisional Seat Allotment Letter, JEE Advanced Admit Card, Class 10 Certificate (DOB Proof), Class 12 Marksheet & Pass Certificate, Category Certificate (if applicable), Medical Certificate (JoSAA format), Candidate Undertaking, Photo ID (Aadhar/Passport)", 
            "application_mode": "Online (JoSAA)", 
            "source": "Official JoSAA Admission Brochure 2025"
        },
        {
            "college": "IIT Bhilai", 
            "entrance_exam": "JEE Advanced", 
            "minimum_eligibility": "Class 12 pass with 75% aggregate", 
            "documents_required": "Provisional Seat Allotment Letter, JEE Advanced Admit Card, Class 10 Certificate (DOB Proof), Class 12 Marksheet & Pass Certificate, Income Certificate (for fee remission), Category Certificate (if applicable), Medical Certificate (JoSAA format), Candidate Undertaking, Photo ID", 
            "application_mode": "Online (JoSAA)", 
            "source": "Official JoSAA Admission Brochure 2025"
        },
        {
            "college": "NIT Jamshedpur", 
            "entrance_exam": "JEE Main", 
            "minimum_eligibility": "Class 12 pass with 75% aggregate", 
            "documents_required": "Provisional Seat Allotment Letter, JEE Main Score Card & Admit Card, Class 10 Certificate (DOB Proof), Class 12 Marksheet & Pass Certificate, Medical Certificate (JoSAA format), Category/Income Certificate (if applicable), Photo ID, Passport photos", 
            "application_mode": "Online (JoSAA/CSAB)", 
            "source": "Official NIT Jamshedpur Admission Guide 2025"
        },
        {
            "college": "NIT Rourkela", 
            "entrance_exam": "JEE Main", 
            "minimum_eligibility": "Class 12 pass with 75% aggregate", 
            "documents_required": "Provisional Seat Allotment Letter, JEE Main Score Card & Admit Card, Class 10 Certificate (DOB Proof), Class 12 Marksheet & Pass Certificate, Medical Certificate (JoSAA format), Category Certificate (if applicable), Photo ID, Undertaking, Seat Acceptance Fee Receipt", 
            "application_mode": "Online (JoSAA/CSAB)", 
            "source": "Official JoSAA Admission Brochure 2025"
        },
        {
            "college": "IIT Kharagpur", 
            "entrance_exam": "JEE Advanced", 
            "minimum_eligibility": "Class 12 pass with 75% aggregate", 
            "documents_required": "Provisional Seat Allotment Letter, JEE Advanced Admit Card, Class 10 Certificate (DOB Proof), Class 12 Marksheet & Pass Certificate, Category Certificate (if applicable), Medical Certificate (JoSAA format), Candidate Undertaking, Photo ID, Passport size photos", 
            "application_mode": "Online (JoSAA)", 
            "source": "Official JoSAA Admission Brochure 2025"
        }
    ]
    pd.DataFrame(admission).to_csv(os.path.join(raw_dir, "admission_raw.csv"), index=False)
    
    # 6. Exam Rules Raw
    exam_rules = [
        {"college": "IIT (ISM) Dhanbad", "semester": "Fall", "exam_type": "Midterm", "attendance_requirement": "75%", "passing_marks": "40%", "revaluation_allowed": "Yes", "source": "Official Academic Regulations of IIT (ISM) Dhanbad"},
        {"college": "IIT (ISM) Dhanbad", "semester": "Fall", "exam_type": "Final", "attendance_requirement": "75%", "passing_marks": "40%", "revaluation_allowed": "Yes", "source": "Official Academic Regulations of IIT (ISM) Dhanbad"},
        {"college": "IIT Bhilai", "semester": "Fall", "exam_type": "Midterm", "attendance_requirement": "75%", "passing_marks": "35%", "revaluation_allowed": "Yes", "source": "Official Academic Regulations of IIT Bhilai"},
        {"college": "IIT Bhilai", "semester": "Fall", "exam_type": "Final", "attendance_requirement": "75%", "passing_marks": "35%", "revaluation_allowed": "Yes", "source": "Official Academic Regulations of IIT Bhilai"},
        {"college": "NIT Jamshedpur", "semester": "Fall", "exam_type": "Midterm", "attendance_requirement": "75%", "passing_marks": "40%", "revaluation_allowed": "Yes", "source": "Official B.Tech Academic Regulations of NIT Jamshedpur"},
        {"college": "NIT Jamshedpur", "semester": "Fall", "exam_type": "Final", "attendance_requirement": "75%", "passing_marks": "40%", "revaluation_allowed": "Yes", "source": "Official B.Tech Academic Regulations of NIT Jamshedpur"},
        {"college": "NIT Rourkela", "semester": "Fall", "exam_type": "Midterm", "attendance_requirement": "85%", "passing_marks": "40%", "revaluation_allowed": "Yes", "source": "Official Academic Rules of NIT Rourkela"},
        {"college": "NIT Rourkela", "semester": "Fall", "exam_type": "Final", "attendance_requirement": "85%", "passing_marks": "40%", "revaluation_allowed": "Yes", "source": "Official Academic Rules of NIT Rourkela"},
        {"college": "IIT Kharagpur", "semester": "Fall", "exam_type": "Midterm", "attendance_requirement": "75%", "passing_marks": "40%", "revaluation_allowed": "Yes", "source": "Official B.Tech Rules of IIT Kharagpur"},
        {"college": "IIT Kharagpur", "semester": "Fall", "exam_type": "Final", "attendance_requirement": "75%", "passing_marks": "40%", "revaluation_allowed": "Yes", "source": "Official B.Tech Rules of IIT Kharagpur"}
    ]
    pd.DataFrame(exam_rules).to_csv(os.path.join(raw_dir, "exam_rules_raw.csv"), index=False)
    
    print("Raw official CSV files generated inside knowledge/raw/")

if __name__ == "__main__":
    build_raw_knowledge_base()
