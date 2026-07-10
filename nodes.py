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

DATA_DIR = "knowledge"

# Load domain-specific dataframes once in memory at startup
college_info_df = pd.read_csv(os.path.join(DATA_DIR, "college_info.csv")) if os.path.exists(os.path.join(DATA_DIR, "college_info.csv")) else None
fees_df = pd.read_csv(os.path.join(DATA_DIR, "fees.csv")) if os.path.exists(os.path.join(DATA_DIR, "fees.csv")) else None
placements_df = pd.read_csv(os.path.join(DATA_DIR, "placements.csv")) if os.path.exists(os.path.join(DATA_DIR, "placements.csv")) else None
hostel_df = pd.read_csv(os.path.join(DATA_DIR, "hostel.csv")) if os.path.exists(os.path.join(DATA_DIR, "hostel.csv")) else None
admission_df = pd.read_csv(os.path.join(DATA_DIR, "admission.csv")) if os.path.exists(os.path.join(DATA_DIR, "admission.csv")) else None
exam_rules_df = pd.read_csv(os.path.join(DATA_DIR, "exam_rules.csv")) if os.path.exists(os.path.join(DATA_DIR, "exam_rules.csv")) else None
scholarship_df = pd.read_csv(os.path.join(DATA_DIR, "scholarship.csv")) if os.path.exists(os.path.join(DATA_DIR, "scholarship.csv")) else None



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


def _format_colleges_list(subset: pd.DataFrame) -> str:
    """Format a filtered college DataFrame compactly for Gemini context."""
    lines = []
    for i, (_, row) in enumerate(subset.iterrows(), 1):
        parts = [f"{i}. {row['college']}"]
        city = row.get("city")
        if city and pd.notna(city) and str(city).strip():
            parts.append(str(city))
        parts.append(str(row["state"]))
        parts.append(str(row["type"]))
        nirf = row.get("nirf_rank")
        if pd.notna(nirf):
            parts.append(f"NIRF #{int(nirf)}")
        parts.append(f"Rating {row['rating']}")
        fees = row.get("fees_ug_inr")
        if pd.notna(fees):
            parts.append(f"Fees \u20b9{int(fees):,}")
        pkg = row.get("placement_avg_lpa")
        if pd.notna(pkg):
            parts.append(f"Avg Pkg {pkg} LPA")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def intent_node(state: CollegeState):
    """Hybrid Intent Router: fast-path keyword checks + Gemini fallback."""
    question = state["question"].lower()

    # ── Discovery / comparison queries take priority over domain intents ──
    if any(k in question for k in ["compare", " vs "]):
        return {"intent": "college_info"}
    if re.search(r"\btop\s+\d+\b", question):
        return {"intent": "college_info"}
    # Numeric constraint queries (e.g. "colleges under 2 lakh", "above 15 lpa")
    if re.search(r"(under|below|above|over)\s*[\u20b9\d]", question) and \
       any(k in question for k in ["lakh", "lpa", "rupee", "college", "inr"]):
        return {"intent": "college_info"}

    # ── Domain-specific intents ───────────────────────────────────────────
    if any(k in question for k in ["fee", "fees", "cost", "charge", "tuition", "price", "payment", "bursar"]):
        return {"intent": "fees"}
    if any(k in question for k in ["scholarship", "financial aid", "grant", "fellowship"]):
        return {"intent": "scholarship"}
    if any(k in question for k in ["exam", "exams", "midterm", "final", "test", "grading", "attendance"]):
        return {"intent": "exam"}
    if any(k in question for k in ["placement", "package", "lpa", "salary", "nirf", "rank", "rating",
                                    "located", "where", "city", "state", "hostel", "campus",
                                    "iit", "nit", "iiit", "iim", "show", "list"]):
        return {"intent": "college_info"}

    # ── LLM fallback ──────────────────────────────────────────────────────
    response = llm.invoke(f"{INTENT_PROMPT}\n\nQuestion:\n{state['question']}")
    intent = response.content.strip().lower()
    valid_intents = ["college_info", "fees", "scholarship", "exam"]
    if intent not in valid_intents:
        intent = "college_info"
    return {"intent": intent}


def college_info_node(state: CollegeState):
    """Retrieve college data via Python filtering/sorting, then explain with Gemini."""
    query = state["question"]
    query_lower = query.lower()
    context = ""
    matched_entity = "Unknown"
    source = "NIRF / Official College Data 2025"

    if college_info_df is None:
        context = "College database not available."
    else:
        college_names = college_info_df["college"].tolist()

        # ── 1. Comparison: "compare A and B" / "A vs B" ──────────────────
        if "compare" in query_lower or " vs " in query_lower:
            c1, c2 = None, None
            for sep in [" and ", " vs ", " versus "]:
                idx = query_lower.find(sep)
                if idx != -1:
                    # Strip all leading comparison keywords (handles "compare between X and Y")
                    left = query_lower[:idx].strip()
                    for kw in ["compare between", "compare", "between"]:
                        if left.startswith(kw):
                            left = left[len(kw):].strip()
                            break
                    right = query_lower[idx + len(sep):].strip()
                    c1 = find_matching_college(left, college_names)
                    c2 = find_matching_college(right, college_names)
                    if c1 and c2:
                        break

            # If one college wasn't found, say so — don't silently fall through
            if (c1 or c2) and not (c1 and c2):
                missing  = right if not c2 else left
                found    = c1 or c2
                context       = f"Only '{found}' was found in the database. '{missing}' is not available in the current dataset."
                matched_entity = found
            if c1 and c2:
                r1 = college_info_df[college_info_df["college"] == c1].iloc[0]
                r2 = college_info_df[college_info_df["college"] == c2].iloc[0]

                def _v(row, col, fmt=None):
                    v = row.get(col)
                    if not pd.notna(v):
                        return "N/A"
                    try:
                        return fmt(v) if fmt else str(v)
                    except Exception:
                        return str(v)

                rows = [
                    ("State",            _v(r1, "state"),              _v(r2, "state")),
                    ("City",             _v(r1, "city"),               _v(r2, "city")),
                    ("Type",             _v(r1, "type"),               _v(r2, "type")),
                    ("NIRF Rank",        _v(r1, "nirf_rank", lambda v: f"#{int(v)}"),
                                         _v(r2, "nirf_rank", lambda v: f"#{int(v)}")),
                    ("Rating",           _v(r1, "rating"),             _v(r2, "rating")),
                    ("Avg Fee (\u20b9)",  _v(r1, "fees_ug_inr",      lambda v: f"{int(v):,}"),
                                         _v(r2, "fees_ug_inr",      lambda v: f"{int(v):,}")),
                    ("Avg Placement",    _v(r1, "placement_avg_lpa", lambda v: f"{v} LPA"),
                                         _v(r2, "placement_avg_lpa", lambda v: f"{v} LPA")),
                ]
                # Enrich with detailed fee data where available
                for cn, df_ in [(c1, fees_df), (c2, fees_df)]:
                    pass  # detailed breakdown available via fees_node if needed

                header    = f"{'Metric':<22} | {c1:<32} | {c2:<32}"
                separator = "-" * len(header)
                table     = "\n".join(f"{r[0]:<22} | {r[1]:<32} | {r[2]:<32}" for r in rows)
                context       = f"Comparison: {c1} vs {c2}\n\n{header}\n{separator}\n{table}"
                matched_entity = f"{c1} vs {c2}"

        # ── 2. Single college lookup ──────────────────────────────────────
        # Guard: skip fuzzy matching when the query is clearly a discovery/filter
        # request. The fuzzy matcher scores "colleges" ≈ "College" at ~0.93,
        # so any query containing the word "colleges" would match the first
        # college in the 1203-row list and produce a false positive.
        _known_states = {s.lower() for s in college_info_df["state"].unique()}
        _is_discovery = (
            bool(re.search(r"\btop\s+\d+\b", query_lower)) or
            any(k in query_lower for k in [
                "colleges in", "colleges of", "colleges with",
                "colleges under", "colleges above", "colleges below",
                "show colleges", "list colleges", "find me", "which colleges",
            ]) or
            any(state in query_lower for state in _known_states)
        )

        if not context and not _is_discovery:
            matched_college = find_matching_college(query, college_names)
            if matched_college:
                row_info = college_info_df[college_info_df["college"] == matched_college].iloc[0]
                context_parts  = ["College Details:", format_row(row_info)]
                matched_entity = matched_college
                source         = row_info.get("source", "NIRF / Official College Data 2025")

                # Enrich with domain-specific detail (only 5 colleges have this)
                for df_, label in [
                    (fees_df,      "Detailed Fee Breakdown"),
                    (placements_df,"Placement Details"),
                    (hostel_df,    "Hostel Details"),
                    (admission_df, "Admission Details"),
                ]:
                    if df_ is not None:
                        sub = df_[df_["college"] == matched_college]
                        if not sub.empty:
                            context_parts += [f"\n{label}:", format_row(sub.iloc[0])]

                context = "\n".join(context_parts)

        # ── 3. Filter / discover path ─────────────────────────────────────
        if not context:
            subset = college_info_df.copy()

            # Hostel-specific query — use hostel_df directly
            if "hostel" in query_lower and hostel_df is not None:
                sub = hostel_df[hostel_df["hostel_available"].str.strip().str.lower() == "yes"]
                context        = f"Colleges with hostel facilities (detailed data available):\n{sub.to_string(index=False)}"
                matched_entity = "Colleges with Hostel"
                source         = "Official Hostel Information"

            if not context:
                # Institute type filter
                type_map = {
                    "iiit": "IIIT", "iit": "IIT", "nit": "NIT",
                    "iim": "IIM",   "aiims": "AIIMS", "bits": "BITS", "nlu": "NLU",
                    "central university": "Central University",
                }
                matched_type = None
                for kw, val in type_map.items():
                    if kw in query_lower:
                        subset       = subset[subset["type"] == val]
                        matched_type = val
                        break
                if not matched_type and "engineering" in query_lower:
                    subset       = subset[subset["type"].isin(["Engineering", "IIT", "NIT", "IIIT"])]
                    matched_type = "Engineering"

                # State filter
                matched_state = next(
                    (s for s in college_info_df["state"].unique() if s.lower() in query_lower), None
                )
                if matched_state:
                    subset         = subset[subset["state"] == matched_state]
                    matched_entity = matched_state

                # City filter (only if no state matched)
                if not matched_state:
                    cities = college_info_df["city"].dropna().unique()
                    matched_city = next((c for c in cities if c and c.lower() in query_lower), None)
                    if matched_city:
                        subset         = subset[subset["city"] == matched_city]
                        matched_entity = matched_city

                # Fee constraint: "under / below X lakh"
                fee_match = re.search(
                    r"(?:under|below|less\s+than|within)\s*[\u20b9rs.\s]*([\d,.]+)\s*(lakh|lac|l\b|crore|cr)?",
                    query_lower,
                )
                sort_col    = "rating"
                sort_asc    = False
                fee_cap     = None   # track for context label
                pkg_floor   = None   # track for context label
                if fee_match:
                    raw  = fee_match.group(1).replace(",", "")
                    fee_cap = float(raw)
                    unit = (fee_match.group(2) or "").strip()
                    if "crore" in unit or unit == "cr":
                        fee_cap *= 10_000_000
                    elif "lakh" in unit or "lac" in unit or (unit == "l") or fee_cap < 500:
                        fee_cap *= 100_000
                    subset   = subset[subset["fees_ug_inr"] <= fee_cap]
                    sort_col = "rating"

                # Placement constraint: "above / over X lpa"
                pkg_match = re.search(
                    r"(?:above|over|more\s+than|at\s*least|minimum)\s*([\d.]+)\s*lpa",
                    query_lower,
                )
                if pkg_match:
                    pkg_floor = float(pkg_match.group(1))
                    subset    = subset[subset["placement_avg_lpa"] >= pkg_floor]
                    sort_col  = "placement_avg_lpa"

                # Top N detection — Python sorts, Gemini never ranks
                top_n_match = re.search(r"\btop\s+(\d+)\b", query_lower)
                if top_n_match:
                    n              = min(int(top_n_match.group(1)), 30)
                    subset         = subset.sort_values(sort_col, ascending=sort_asc).head(n)
                    matched_entity = matched_entity if matched_entity != "Unknown" else f"Top {n}"
                else:
                    subset = subset.sort_values(sort_col, ascending=sort_asc).head(20)

                if matched_type and matched_entity == "Unknown":
                    matched_entity = matched_type

                if not subset.empty:
                    # Build explicit criteria header so Gemini knows the filter applied
                    criteria = []
                    if matched_type:  criteria.append(f"Type: {matched_type}")
                    if matched_state: criteria.append(f"State: {matched_state}")
                    if fee_cap is not None:
                        criteria.append(f"Fees ≤ ₹{int(fee_cap):,}")
                    if pkg_floor is not None:
                        criteria.append(f"Avg placement package ≥ {pkg_floor} LPA")
                    criteria_str = " | ".join(criteria) if criteria else "all colleges"
                    sort_label = "average placement package" if sort_col == "placement_avg_lpa" else "rating"

                    context = (
                        f"Filter applied: {criteria_str}\n"
                        f"Showing top {len(subset)} results (sorted by {sort_label}, highest first):\n\n"
                        + _format_colleges_list(subset)
                    )
                else:
                    context = "No colleges match the specified criteria in the database."

        # ── 4. Scholarship / admission stats fallback ─────────────────────
        if not context and scholarship_df is not None:
            numbers = [int(n) for n in re.findall(r"\d+", query_lower)]
            if numbers:
                val = numbers[0]
                if 0 < val <= 100:
                    sub = scholarship_df[
                        (scholarship_df["board_percentage"] >= val - 3) &
                        (scholarship_df["board_percentage"] <= val + 3)
                    ]
                    for cat in ["general", "ews", "sc", "st", "obc"]:
                        if cat in query_lower:
                            sub = sub[sub["category"].str.lower() == cat]
                            break
                    if not sub.empty:
                        total    = len(sub)
                        admitted = len(sub[sub["admission_status"].str.lower() == "admitted"])
                        rate     = (admitted / total) * 100 if total > 0 else 0.0
                        context  = (
                            f"Admission Statistics for board percentage {val}% (+/- 3%):\n"
                            f"- Total matching students: {total}\n"
                            f"- Admitted students: {admitted}\n"
                            f"- Admission rate: {rate:.1f}%"
                        )
                        matched_entity = "Admission Statistics"
                        source         = "Historical Admissions Dataset"

        if not context:
            context = "No matching college, location, or data found in the database."

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
