# Jharkhand Campus Assistant — Enterprise College Discovery Agent

Jharkhand Campus Assistant is an enterprise-grade, high-performance college analytics and discovery assistant. Specifically built and optimized for the state of **Jharkhand, India**, the agent assists prospective students, parent organizations, and academic counselors in navigating the engineering college landscape of the region.

The system is powered by a hybrid orchestration pipeline using **FastAPI**, **LangGraph**, **Groq (Llama-3.3-70b-versatile)**, and **React + Vite**. It implements a strict deterministic data-grounding layer to completely eliminate LLM hallucinations by serving source-cited answers directly from curated state-wide directories.

---

## 🏛️ System Architecture

The assistant employs a single-pass Directed Acyclic Graph (DAG) query routing system. Obvious search parameters (e.g. fees, scholarships) bypass LLM inference entirely (executing in **<2ms**), while complex natural language queries fall back to a semantic router.

```
                    [ User Query ]
                           │
                           ▼
             +───────────────────────────+
             |        Intent Node        |
             |  (Keyword Fast-Path +     |
             |    Groq Semantic Router)  |
             +─────────────┬─────────────+
                           │
                   intent classified
                           ▼
             +───────────────────────────+
             |     LangGraph Router      |
             +──┬──────────┬──────────┬──+
                │          │          │
                ▼          ▼          ▼
          [info_node]  [fees_node]  [sch_node] ...
                │          │          │
                +──────────┼──────────+
                           │
                   grounded context
                           ▼
             +───────────────────────────+
             |       Groq Explainer      |
             | (Llama-3.3-70b-versatile) |
             +───────────────────────────+
                           │
                    markdown response
                           ▼
                     [ User UI ]
```

### Key Architectural Pillars
1. **Hybrid Intent Routing**: Obvious queries bypass the LLM, whereas complex semantic requests are classified using the Groq router into domain-specific intents (`college_info`, `fees`, `scholarship`, `exam`).
2. **Deterministic Data Engine (Pandas)**: The node processing query uses vectorized Pandas boolean masks to handle comparisons, fee caps, placement thresholds, and spatial filtering.
3. **Structured Context Grounding**: Raw database query subsets are converted into structured markdown contexts and fed into the LLM alongside strict instructions prohibiting outside knowledge extrapolation.
4. **Context-Grounded Explainer (Groq)**: The explainer reads the structured context and compiles it into a human-friendly format, complete with matching metadata pills and official source citations.

---

## 📊 Jharkhand Dataset Overview

The system operates on an enriched, validated dataset of **30 engineering colleges** in Jharkhand:
- **IIT-Tier**: 1 Autonomous Institute (IIT ISM Dhanbad)
- **NIT-Tier**: 1 National Institute of Technology (NIT Jamshedpur)
- **IIIT-Tier**: 1 Indian Institute of Information Technology (IIIT Ranchi)
- **Government Engineering Colleges**: 7 regional institutions (including Birsa Institute of Technology Sindri, GEC Dumka, GEC Palamu, etc.)
- **State Universities**: 2 technical university hubs (Jharkhand University of Technology, Chhotanagpur Technical University)
- **Private Colleges**: 18 private engineering colleges (including Birla Institute of Technology Mesra, Cambridge Institute of Technology Ranchi, RVS Jamshedpur, etc.)

### Localized Features & Schema:
- **Exams Supported**: JEE Advanced, JEE Main, and **Jharkhand Combined Entrance Competitive Examination (JCECE)**.
- **Scholarships**: Integrated **e-Kalyan Jharkhand Post-Matric Scholarship**, Mukhyamantri Medha Chatravriti Yojana, and Birsa Munda Merit Scholarships.
- **Local Recruiters**: Curated regional recruiters including **TATA Steel Jamshedpur**, **SAIL Bokaro**, **BCCL Dhanbad**, **CCL Ranchi**, and **NTPC Patratu**.

---

## 📂 Project Structure

```
Campus_Assistant_Agent/
├── app.py                  # FastAPI server entrypoint & middleware config
├── graph.py                # LangGraph DAG workflow definition
├── nodes.py                # Graph nodes executing the Pandas query engine & Groq LLM
├── prompts.py              # System prompts for intent routing and grounded answering
├── state.py                # State schema (TypedDict) shared across nodes
├── requirements.txt        # Python package dependencies (featuring langchain-groq)
│
├── knowledge/              # Core Knowledge Base
│   ├── preprocess.py       # Data cleaning and deduplication utility
│   ├── validate_dataset.py # Validation constraints script (passes with 0 errors)
│   ├── generate_dataset.py # Deterministic synthetic ML dataset generator (Jharkhand-only)
│   ├── college_manifest.json# Manifest tracking all 30 colleges and official source links
│   ├── aliases.json        # 51 fuzzy/shorthand aliases for Jharkhand colleges
│   ├── college_info.csv    # Basic profiles, Scores, Types, and Cities
│   ├── fees.csv            # Tuition, hostel, and mess fee structures
│   ├── placements.csv      # Placement percentages, averages, and top recruiters
│   ├── hostel.csv          # Hostel availability, capacity, and room types
│   ├── admission.csv       # JCECE/JEE Main criteria and document checklists
│   ├── exam_rules.csv      # Attendance policies and midterm/final regulations
│   └── scholarship.csv     # 24,000+ historical student scholarship records
│
└── frontend/               # React Dashboard (Vite)
    ├── src/
    │   ├── App.jsx         # Chat layout, splash screens, and suggestions
    │   ├── App.css         # Modern glassmorphism dark-mode UI styles
    │   └── main.jsx        # Bootstrapper
    └── .env.local          # Frontend API connection config
```

---

## ⚡ Quickstart

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Groq API Key (stored securely in `.env`)

### 1. Configuration
Clone the repository and define your environment variables:
```bash
# Clone the repository
git clone https://github.com/TheyCallMeAnirban/Campus_Assistant_Agent.git
cd Campus_Assistant_Agent

# Configure Groq API Key
echo GROQ_API_KEY=gsk_your_api_key_here > .env
```

### 2. Launch Backend API
```bash
# Initialize and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux

# Install requirements
pip install -r requirements.txt

# Run FastAPI server
uvicorn app:app --reload
```
The backend starts at `http://127.0.0.1:8000`. API docs are auto-exposed at `http://127.0.0.1:8000/docs`.

### 3. Launch Frontend Client
```bash
cd frontend
npm install
npm run dev
```
The React Vite server launches at `http://localhost:5173/`.

---

## 📡 API Specification

### `POST /chat`
Submits a user message and returns a grounded response from the Graph.

#### Request Body
```json
{
  "question": "Compare NIT Jamshedpur and Birla Institute of Technology Mesra"
}
```

#### Response Body
```json
{
  "intent": "college_info",
  "matched_entity": "NIT Jamshedpur vs Birla Institute of Technology Mesra",
  "source": "Synthetic Benchmark Corpus v1.0 (generated)",
  "answer": "### Comparison Matrix\n\nMetric | NIT Jamshedpur | Birla Institute of Technology Mesra\n---|---|---\nCity | Jamshedpur | Ranchi\nType | nit_tier | private\nAcademic Score | 8.1 | 6.5\nAvg Fee | ₹196,000 | ₹261,000\nAvg Placement | 15.8 LPA | 8.8 LPA\n..."
}
```

---

## 🛡️ Robust Answering Rules

All Groq generation is bound by strict prompt directives:
1. **Source Grounding**: Never answer using outside knowledge. If a college or state is not present in the loaded dataset, the system explicitly states that the requested data is unavailable.
2. **Statistical Context**: Scholarship rates are evaluated as historical trends (e.g. *"Among matching historical student records in the database, 74% were eligible for scholarships..."*) rather than absolute university policy to ensure legal compliance.
