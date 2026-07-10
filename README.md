# Campus Agent — AI-Powered College Discovery Assistant

Campus Agent is a high-performance, production-grade college analytics and discovery assistant built on **FastAPI**, **LangGraph**, **Google Gemini 2.5 Flash**, and **React**. Designed to resolve the complex discovery and filtering constraints faced by prospective college students, it grounds large language models in structured CSV databases, avoiding hallucination and offering transparent, source-cited responses.

---

## 🏛️ System Architecture

Campus Agent implements a hybrid routing pipeline that combines zero-latency deterministic routing with advanced LLM semantic classification, feeding into a single-pass graph workflow.

```
                   [ User Query ]
                          │
                          ▼
            +───────────────────────────+
            |        Intent Node        |
            |  (Keyword Fast-Path +     |
            |   Gemini Semantic Fallback|
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
            |      Gemini Explainer     |
            +───────────────────────────+
                          │
                   markdown response
                          ▼
                    [ User UI ]
```

### Routing & Node Execution Cycle
1. **Hybrid Intent Routing**: The system parses the query. Obvious queries (e.g. including terms like `fees`, `scholarship`) bypass the LLM entirely, executing in **<2ms**. Ambiguous phrases trigger a semantic call to **Gemini 2.5 Flash** for intent classification.
2. **Deterministic Data Query Engine (Python/Pandas)**: Once the intent is routed to a specific graph node, the system queries the corresponding CSV files. It handles complex sorting, top-N slicing, range filters, and comparison joins in memory using Pandas.
3. **Structured Context Injection**: The output is compiled into a highly descriptive context header (detailing active filters, sort orders, and matching counts) followed by formatted CSV subset records.
4. **Context-Grounded Explanation (LLM Answering)**: Gemini reads the user's question alongside the generated context. It runs under strict constraints: it can only format, explain, and summarize the data provided, eliminating hallucination.

---

## 💻 Tech Stack

| Layer | Component | Description |
|---|---|---|
| **AI Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) | Single-pass DAG workflow orchestration with conditional routing. |
| **Generative LLM** | Google Gemini 2.5 Flash | Handles intent fallback and grounded natural language explanations. |
| **API Backend** | FastAPI + Uvicorn | Asynchronous HTTP service with automatic OpenAPI generation. |
| **Data Engine** | Pandas (Python) | High-speed, in-memory query, comparison, and constraint-filtering engine. |
| **Frontend UI** | React + Vite | Fluid dark-mode layout utilizing glassmorphic aesthetics and smooth custom micro-animations. |

---

## 📂 Project Structure

```
Campus_Assistant_Agent/
├── app.py                  # FastAPI application entrypoint & API middleware configuration
├── graph.py                # LangGraph workflow builder and execution state definitions
├── nodes.py                # Graph node functions containing the Pandas filtering engine
├── prompts.py              # Answering guidelines and intent classification prompts
├── state.py                # Type-safe state context (TypedDict) passed between nodes
├── requirements.txt        # Python package dependencies
│
├── knowledge/              # Core Knowledge Base
│   ├── preprocess.py       # Flat preprocessing script (drops duplicates, cleans schemas)
│   ├── college_info.csv    # Directory of 1,203 colleges with ratings, city, state, types
│   ├── fees.csv            # Tuition, hostel, mess, and one-time fee breakdowns
│   ├── placements.csv      # Package averages (LPA), highest packages, placement ratios
│   ├── hostel.csv          # Room types, mess requirements, and hostel details
│   ├── admission.csv       # Document checklists and admission criteria
│   ├── exam_rules.csv      # Academic policies and attendance requirements
│   └── scholarship.csv     # 24,000+ historical student scholarship records
│
└── frontend/               # Single Page Application
    ├── src/
    │   ├── App.jsx         # ChatGPT-style multi-conversation manager and UI layout
    │   ├── App.css         # Modern styling rules (glassmorphic panels, animated glows)
    │   └── main.jsx        # App bootstrapper
    └── .env.local          # Frontend environment variables
```

---

## 🔍 Data-Grounding & Constraint Logic

Unlike traditional RAG systems that rely on vector similarity (which frequently returns irrelevant chunks for quantitative constraints), Campus Agent uses a **deterministic query pipeline** inside `nodes.py`:

*   **Comparison Queries**: When parsing `Compare A and B` or `A vs B`, the engine matches both colleges, performs a column-wise join across the directory, fee, and placement sheets, and produces a side-by-side metric matrix.
*   **Quantitative Thresholds**: Recognizes fee limits (`under 2 lakh`) and placement minimums (`above 15 LPA`) using regex, applies corresponding boolean masks to Pandas dataframes, and sorts by rating.
*   **Top-N Lists**: If the query includes `top 10` or `top 5`, the engine slices the sorted dataframe in Python *before* passing the text context to Gemini.
*   **Fuzzy Matching Safeguards**: To prevent generic terms (like the word `"colleges"`) from triggering false positives against college names, the single-college lookup node uses discovery checks to skip the fuzzy matches for list/search requests.

---

## ⚡ Quickstart

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Google Gemini API Key

### 1. Configuration
Clone the repository and set up your backend environment:

```bash
# Clone
git clone https://github.com/TheyCallMeAnirban/Campus_Assistant_Agent.git
cd Campus_Assistant_Agent

# Configure Gemini key
echo GOOGLE_API_KEY=your_gemini_api_key_here > .env
```

### 2. Launch Backend Server
```bash
# Initialize virtual env
python -m venv .venv
.venv\Scripts\activate      # On Windows
# source .venv/bin/activate # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run FastAPI reload server
uvicorn app:app --reload
```
The server starts at `http://127.0.0.1:8000`. You can inspect endpoints via the Swagger docs at `http://127.0.0.1:8000/docs`.

### 3. Launch Frontend Client
```bash
cd frontend
npm install
npm run dev
```
The UI dashboard opens automatically at `http://localhost:5173`.

---

## 📡 API Spec

### `POST /chat`
Submits a user message and returns a grounded response from the graph.

**Request Body:**
```json
{
  "question": "Compare NIT Jamshedpur and NIT Rourkela"
}
```

**Response Body:**
```json
{
  "intent": "college_info",
  "matched_entity": "NIT Jamshedpur vs NIT Rourkela",
  "source": "NIRF / Official College Data 2025",
  "answer": "### Comparison Matrix\n\nMetric | NIT Jamshedpur | NIT Rourkela\n---|---|---\nNIRF Rank | #101 | #37\nRating | 7.8 | 8.2\nAvg Fee | ₹186,000 | ₹191,000\nAvg Package | 14.65 LPA | 15.0 LPA\n..."
}
```

---

## 🛡️ Robust Answering Rules (Strict Grounding)

The Gemini generation is bound by strict prompt directives:
1. **Never Invent Facts**: If a college is missing from the database (e.g. `BIT Sindri`), the system explicitly responds stating that the data is not available.
2. **Context-Only Framing**: The explainer translates raw database logs into markdown paragraphs, bullet points, or lists without extrapolating information.
3. **Statistical Framing**: When answering scholarship or admission chance questions based on historical records, the model presents the findings as a trend (e.g. *"Among comparable student profiles in the database, 82% were eligible..."*) to avoid representing it as an official university rule.

---

## 📜 License
This project is licensed under the MIT License.
