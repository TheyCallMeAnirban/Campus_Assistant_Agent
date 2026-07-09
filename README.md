# Campus Assistant Agent

A conversational AI assistant for Indian higher education, built with **LangGraph**, **Google Gemini**, and **React**. Ask natural-language questions about colleges, fees, scholarships, and exam policies — and get grounded, source-cited answers.

---

## Architecture

```
User Question
      │
      ▼
┌─────────────┐
│ Intent Node │  ← Hybrid: keyword fast-path + Gemini fallback
└──────┬──────┘
       │ intent
       ▼
┌──────────────────────────────────────────────┐
│              LangGraph Router                │
└──┬──────────┬──────────┬──────────┬──────────┘
   ▼          ▼          ▼          ▼
College     Exam       Fees    Scholarship
 Info       Node       Node       Node
   │          │          │          │
   └──────────┴──────────┴──────────┘
                    │
                    ▼
           Structured Response
        { intent, matched_entity,
            source, answer }
```

Each specialized node:
1. Looks up relevant structured data from domain-specific CSVs (no cross-domain mega-joins)
2. Formats it as plain context
3. Sends it to Gemini with a strict "answer only from context" system prompt

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM | Google Gemini 2.5 Flash Lite (via `langchain-google-genai`) |
| API Server | FastAPI + Uvicorn |
| Frontend | React (Vite) |
| Data | Pandas — domain-specific CSV files |

---

## Project Structure

```
College Project/
├── app.py                  # FastAPI server — single /chat endpoint
├── graph.py                # LangGraph workflow: nodes + conditional routing
├── nodes.py                # All 5 node implementations (intent + 4 specialized)
├── prompts.py              # System prompts for intent classification and answering
├── state.py                # CollegeState TypedDict
├── requirements.txt
│
├── knowledge/
│   ├── build_knowledge_base.py   # Downloads, parses, cleans, and validates data
│   ├── preprocess.py             # Generates domain-specific processed CSVs
│   ├── College_Admission.csv     # Raw admissions dataset (~1.8 MB)
│   ├── india_colleges.csv        # College directory
│   ├── india_cities.csv
│   ├── exam_rules.csv
│   └── processed/
│       ├── college_info.csv      # College metadata (NIRF rank, rating, location, type)
│       ├── fees.csv              # Tuition, hostel, mess, and one-time fees
│       ├── placements.csv        # Placement stats (avg/max package, placement rate)
│       ├── hostel.csv            # Hostel availability and charges
│       ├── admission.csv         # Admission requirements and documents
│       ├── exam_rules.csv        # Midterm/final exam policies
│       └── scholarship.csv       # Historical scholarship eligibility records
│
└── frontend/
    ├── index.html
    └── src/
        ├── App.jsx               # Main UI — chat interface with frosted-glass panels
        └── App.css               # Design system: glassmorphism, Inter font, dark palette
```

---

## Supported Intents

| Intent | Example Question |
|---|---|
| `college_info` | "What is the NIRF rank of IIT ISM Dhanbad?" |
| `fees` | "What are the fees at NIT Jamshedpur?" |
| `scholarship` | "What is the scholarship eligibility rate for SC students with 85%?" |
| `exam` | "What is the attendance policy for midterm exams?" |

The intent node uses a **keyword fast-path** (no LLM call for obvious queries) and falls back to Gemini only when keywords are ambiguous.

---

## Covered Colleges

| College | Location |
|---|---|
| IIT (ISM) Dhanbad | Jharkhand |
| NIT Jamshedpur | Jharkhand |
| BIT Mesra | Jharkhand |
| NIT Rourkela | Odisha |
| IIT Kharagpur | West Bengal |

---

## Quickstart

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Google Gemini API key ([get one free](https://aistudio.google.com/app/apikey))

### 1. Clone

```bash
git clone https://github.com/TheyCallMeAnirban/Campus_Assistant_Agent.git
cd Campus_Assistant_Agent
```

### 2. Backend

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo GOOGLE_API_KEY=your_key_here > .env

# Start the API server
uvicorn app:app --reload
```

Server will be live at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI will be live at `http://localhost:5173`.

---

## API Reference

### `POST /chat`

```json
// Request
{ "question": "What are the fees at NIT Jamshedpur?" }

// Response
{
  "intent": "fees",
  "matched_entity": "NIT Jamshedpur",
  "source": "Official Fee Structure 2025-26",
  "answer": "The tuition fee at NIT Jamshedpur is ₹X per semester..."
}
```

---

## Data Pipeline

```
build_knowledge_base.py   →   raw/             (official sources)
preprocess.py             →   knowledge/processed/   (domain CSVs)
```

Run these only if you want to refresh the knowledge base:

```bash
cd knowledge
python build_knowledge_base.py
python preprocess.py
```

The processed CSVs are committed to the repository so you don't need to run this for normal usage.

---

## Design Decisions

**Why domain-specific CSVs instead of one merged file?**  
Each node loads only the data it needs. If placement figures are updated, you regenerate `placements.csv` — not a monolithic joined table. This keeps preprocessing simple, debugging straightforward, and data freshness isolated.

**Why a keyword fast-path before the LLM?**  
Most real queries contain an obvious keyword (`fee`, `scholarship`, `exam`). Invoking Gemini for intent classification on every request adds ~1 second of latency and burns quota. The fast-path makes those the zero-cost path; Gemini handles only genuinely ambiguous queries.

**Why "answer only from context" in the system prompt?**  
Without grounding, LLMs hallucinate fees, ranks, and scholarship percentages. The strict prompt forces the model to cite or refuse, making the answers auditable.

---

## License

MIT
