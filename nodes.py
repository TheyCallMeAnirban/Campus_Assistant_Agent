import os
import re
from difflib import get_close_matches
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from prompts import INTENT_PROMPT, ANSWER_PROMPT
from state import CollegeState

# Load environment variables
load_dotenv()

# Instantiate Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0,
)

PROCESSED_DIR = "knowledge/processed"

# Load domain-specific dataframes once in memory at startup
college_info_df = pd.read_csv(os.path.join(PROCESSED_DIR, "college_info.csv")) if os.path.exists(os.path.join(PROCESSED_DIR, "college_info.csv")) else None
fees_df = pd.read_csv(os.path.join(PROCESSED_DIR, "fees.csv")) if os.path.exists(os.path.join(PROCESSED_DIR, "fees.csv")) else None
placements_df = pd.read_csv(os.path.join(PROCESSED_DIR, "placements.csv")) if os.path.exists(os.path.join(PROCESSED_DIR, "placements.csv")) else None
hostel_df = pd.read_csv(os.path.join(PROCESSED_DIR, "hostel.csv")) if os.path.exists(os.path.join(PROCESSED_DIR, "hostel.csv")) else None
admission_df = pd.read_csv(os.path.join(PROCESSED_DIR, "admission.csv")) if os.path.exists(os.path.join(PROCESSED_DIR, "admission.csv")) else None
exam_rules_df = pd.read_csv(os.path.join(PROCESSED_DIR, "exam_rules.csv")) if os.path.exists(os.path.join(PROCESSED_DIR, "exam_rules.csv")) else None
scholarship_df = pd.read_csv(os.path.join(PROCESSED_DIR, "scholarship.csv")) if os.path.exists(os.path.join(PROCESSED_DIR, "scholarship.csv")) else None


def find_matching_college(query: str, college_names: list) -> str:
    """Find matching college using substring matching and difflib token similarity."""
    query_clean = re.sub(r"[^\w\s]", "", query.lower())
    query_words = query_clean.split()

    # 1. Substring match
    for name in college_names:
        name_clean = re.sub(r"[^\w\s]", "", name.lower())
        if name_clean in query_clean or query_clean in name_clean:
            return name

    # 2. Fuzzy match word-by-word with difflib
    check_words = [w for w in query_words if len(w) >= 4]
    for name in college_names:
        name_words = re.sub(r"[^\w\s]", "", name.lower()).split()
        for qw in check_words:
            if get_close_matches(qw, name_words, n=1, cutoff=0.8):
                return name

    return None


def format_row(row) -> str:
    """Format a Pandas Series cleanly as key: value pairs to avoid truncation and metadata."""
    if row is None or row.empty:
        return "N/A"
    return "\n".join([f"{k}: {v}" for k, v in row.items()])


def intent_node(state: CollegeState):
    """Hybrid Intent Router: fast-path keyword checks + Gemini fallback."""
    question = state["question"].lower()

    if any(k in question for k in ["fee", "fees", "cost", "charge", "tuition", "price", "payment", "bursar"]):
        return {"intent": "fees"}
    if any(k in question for k in ["scholarship", "financial aid", "grant", "fellowship"]):
        return {"intent": "scholarship"}
    if any(k in question for k in ["exam", "exams", "midterm", "final", "test", "grading", "attendance"]):
        return {"intent": "exam"}
    if any(k in question for k in ["placement", "package", "lpa", "salary", "nirf", "rank", "rating", "located", "where", "city", "state", "type", "about", "college", "info", "admission", "admitted", "eligibility"]):
        return {"intent": "college_info"}

    # Hybrid Fallback
    response = llm.invoke(f"{INTENT_PROMPT}\n\nQuestion:\n{state['question']}")
    intent = response.content.strip().lower()
    valid_intents = ["college_info", "fees", "scholarship", "exam"]
    if intent not in valid_intents:
        intent = "college_info"
    return {"intent": intent}


def college_info_node(state: CollegeState):
    """Retrieve college, placements, hostel, or admissions stats using Python, then query Gemini."""
    query = state["question"]
    query_lower = query.lower()
    context = ""
    matched_entity = "Unknown"
    source = "Official Sources"

    if college_info_df is not None:
        college_names = college_info_df["college"].tolist()
        matched_college = find_matching_college(query, college_names)

        if matched_college:
            row_info = college_info_df[college_info_df["college"] == matched_college].iloc[0]
            
            # Fetch domain-specific rows for the matched college
            row_placement = placements_df[placements_df["college"] == matched_college].iloc[0] if placements_df is not None else None
            row_hostel = hostel_df[hostel_df["college"] == matched_college].iloc[0] if hostel_df is not None else None
            row_admission = admission_df[admission_df["college"] == matched_college].iloc[0] if admission_df is not None else None
            
            context_parts = [
                "College Details:",
                format_row(row_info),
                "\nPlacement Details:",
                format_row(row_placement),
                "\nHostel Details:",
                format_row(row_hostel),
                "\nAdmission Details:",
                format_row(row_admission)
            ]
            context = "\n".join(context_parts)
            matched_entity = matched_college
            source = row_info.get("source", "Official Institutional Data")
        else:
            # Check if state is mentioned
            states = college_info_df["state"].unique()
            matched_state = next((s for s in states if s.lower() in query_lower), None)

            if matched_state:
                subset = college_info_df[college_info_df["state"] == matched_state]
                subset = subset.sort_values(by="rating", ascending=False).head(10)
                context = f"Colleges in State '{matched_state}':\n{subset.to_string(index=False)}"
                matched_entity = matched_state
                source = "Official NIRF Ranking Report 2025"
            else:
                # Check if city is mentioned
                cities = college_info_df["city"].dropna().unique()
                matched_city = next((c for c in cities if c.lower() in query_lower), None)
                if matched_city:
                    subset = college_info_df[college_info_df["city"] == matched_city]
                    subset = subset.sort_values(by="rating", ascending=False).head(10)
                    context = f"Colleges in City '{matched_city}':\n{subset.to_string(index=False)}"
                    matched_entity = matched_city
                    source = "Official NIRF Ranking Report 2025"

    # Check if admissions score stats are requested
    if not context and scholarship_df is not None:
        numbers = [int(n) for n in re.findall(r"\d+", query_lower)]
        if numbers:
            val = numbers[0]
            if 0 < val <= 100:
                subset = scholarship_df[
                    (scholarship_df["board_percentage"] >= val - 3) &
                    (scholarship_df["board_percentage"] <= val + 3)
                ]
                for cat in ["general", "ews", "sc", "st", "obc"]:
                    if cat in query_lower:
                        subset = subset[subset["category"].str.lower() == cat]
                        break

                if not subset.empty:
                    total = len(subset)
                    admitted = len(subset[subset["admission_status"].str.lower() == "admitted"])
                    admission_rate = (admitted / total) * 100 if total > 0 else 0.0
                    context = (
                        f"Admission Statistics for board percentage {val}% (+/- 3%):\n"
                        f"- Total matching students: {total}\n"
                        f"- Admitted students: {admitted}\n"
                        f"- Admission rate: {admission_rate:.1f}%"
                    )
                    matched_entity = "Admission Statistics"
                    source = "Historical Admissions Dataset"

    if not context:
        context = "No matching college, location, or student score profiles found in the database."

    response = llm.invoke(f"{ANSWER_PROMPT}\n\nContext:\n{context}\n\nQuestion:\n{query}")
    return {"answer": response.content.strip(), "matched_entity": matched_entity, "source": source}


def fees_node(state: CollegeState):
    """Retrieve college fees, then formulate response using Gemini."""
    query = state["question"]
    context = ""
    matched_entity = "Unknown"
    source = "Official Sources"

    if fees_df is not None:
        college_names = fees_df["college"].tolist()
        matched_college = find_matching_college(query, college_names)

        if matched_college:
            row = fees_df[fees_df["college"] == matched_college].iloc[0]
            context = f"Tuition & Hostel Fees:\n{format_row(row)}"
            matched_entity = matched_college
            source = row.get("source", "Official Fee Structure 2025-26")
        else:
            context = "College fee information could not be found for the specified college."

    response = llm.invoke(f"{ANSWER_PROMPT}\n\nContext:\n{context}\n\nQuestion:\n{query}")
    return {"answer": response.content.strip(), "matched_entity": matched_entity, "source": source}


def scholarship_node(state: CollegeState):
    """Calculate scholarship rates, then explain them using Gemini."""
    query = state["question"]
    query_lower = query.lower()
    context = ""
    matched_entity = "Scholarship Statistics"
    source = "Historical Admissions Dataset"

    if scholarship_df is not None:
        numbers = [int(n) for n in re.findall(r"\d+", query_lower)]
        board_score = next((n for n in numbers if 40 <= n <= 100), None)

        subset = scholarship_df
        category_matched = None
        for cat in ["general", "ews", "sc", "st", "obc"]:
            if cat in query_lower:
                subset = subset[subset["category"].str.lower() == cat]
                category_matched = cat
                break

        if board_score is not None:
            subset = subset[
                (subset["board_percentage"] >= board_score - 3) &
                (subset["board_percentage"] <= board_score + 3)
            ]

        if not subset.empty:
            total = len(subset)
            eligible = len(subset[subset["scholarship_eligibility"].str.lower() == "yes"])
            rate = (eligible / total) * 100 if total > 0 else 0.0

            filter_description = []
            if category_matched:
                filter_description.append(f"Category: {category_matched.upper()}")
            if board_score:
                filter_description.append(f"Board Percentage: {board_score}% (+/- 3%)")
            filter_str = ", ".join(filter_description) if filter_description else "All students"

            context = (
                f"Scholarship Statistics for historical records matching '{filter_str}':\n"
                f"- Total matching student records: {total}\n"
                f"- Number of students eligible for scholarship: {eligible}\n"
                f"- Scholarship eligibility rate: {rate:.1f}%"
            )
        else:
            context = "No historical student records match the provided score/category profile."

    response = llm.invoke(f"{ANSWER_PROMPT}\n\nContext:\n{context}\n\nQuestion:\n{query}")
    return {"answer": response.content.strip(), "matched_entity": matched_entity, "source": source}


def exam_node(state: CollegeState):
    """Retrieve exam rules or policies, then formulate response using Gemini."""
    query = state["question"]
    query_lower = query.lower()
    context = ""
    matched_entity = "All Colleges"
    source = "Official Academic Regulations"

    if exam_rules_df is not None:
        college_names = exam_rules_df["college"].tolist()
        matched_college = find_matching_college(query, college_names)
        
        subset = exam_rules_df
        if matched_college:
            subset = subset[subset["college"] == matched_college]
            matched_entity = matched_college

        exam_type = None
        if "midterm" in query_lower or "mid semester" in query_lower:
            exam_type = "Midterm"
        elif "final" in query_lower or "end semester" in query_lower:
            exam_type = "Final"

        if exam_type:
            subset = subset[subset["exam_type"] == exam_type]

        if not subset.empty:
            context = f"Exam rules and schedules found:\n{subset.to_string(index=False)}"
            row = subset.iloc[0]
            source = row.get("source", "Official Academic Regulations")
        else:
            context = f"All general exam rules and schedules:\n{exam_rules_df.to_string(index=False)}"

    response = llm.invoke(f"{ANSWER_PROMPT}\n\nContext:\n{context}\n\nQuestion:\n{query}")
    return {"answer": response.content.strip(), "matched_entity": matched_entity, "source": source}
