# Campus Agent

Jharkhand Campus Agent is a LangGraph-powered college information and discovery assistant. It is a demonstration project that orchestrates a FastAPI backend, a React frontend, and a Pandas-driven deterministic data engine to serve context-grounded queries about engineering colleges in Jharkhand.

---

## Features

- **LangGraph Routing**: Dynamic intent routing using a fast-path keyword parser and Groq LLM semantic classifier.
- **FastAPI Backend**: Exposes endpoints for processing natural language queries.
- **React Frontend**: Clean dark-mode interface with conversational history and auto-complete suggestion chips.
- **Pandas Deterministic Retrieval**: Fetches tabular metadata (fees, placements, admission, scholarships) directly from CSVs.
- **Structured Context Grounding**: Merges retrieved CSV rows and Markdown directories to compile accurate facts for the LLM.
- **Gemini Response Generation**: Serves human-friendly answers strictly grounded in the context to eliminate hallucinations.

---

## Tech Stack

- **Backend**: FastAPI, LangGraph, Python 3.10+, Pandas, python-dotenv
- **Frontend**: React (Vite), JavaScript, Vanilla CSS
- **LLM**: ChatGroq (Llama-3.3-70b-versatile or Gemini-compatible API)
- **Knowledge Base**: Structured CSVs and Markdown corpus

---

## Architecture

```
User Query
   │
   ▼
[ FastAPI ]
   │
   ▼
[ LangGraph Orchestration ]
   │
   ├─► [ Intent Node ] (Keyword Fast-Path + Groq Router)
   │
   ├─► [ Specialized Nodes ]
   │      │
   │      ▼
   │   [ Pandas Retrieval ] ◄──► [ Knowledge Base (CSV/MD) ]
   │      │
   │      ▼
   ├─► [ Gemini Explainer ]
   │
   ▼
Response JSON
```

---

## Project Structure

```
Campus_Assistant_Agent/
├── app.py                  # FastAPI server entrypoint
├── graph.py                # LangGraph DAG workflow definition
├── nodes.py                # Graph nodes executing the Pandas engine and LLM call
├── prompts.py              # System prompts for intent routing and answering
├── state.py                # TypedDict state schema shared across nodes
├── requirements.txt        # Python package dependencies
│
├── knowledge/              # Core Knowledge Base
│   ├── corpus/             # Markdown directories per college
│   ├── *.csv               # Datasets (fees, placements, admissions, scholarships)
│   ├── aliases.json        # Fuzzy name lookup aliases
│   ├── context_map.json    # Intent-to-file mappings
│   ├── generate_dataset.py # Deterministic synthetic dataset generator
│   └── validate_dataset.py # Validation constraints script
│
└── frontend/               # React Dashboard (Vite)
    ├── src/
    │   ├── App.jsx         # Chat interface and state
    │   ├── App.css         # UI styles and animations
    │   └── main.jsx        # Bootstrapper
    └── public/             # Static assets (logo, video background)
```

---

## Dataset

This project operates on a deterministic **synthetic benchmark corpus** inspired by the Jharkhand engineering education ecosystem. It features 30 engineering colleges (IIT-tier, NIT-tier, IIIT-tier, government, private, and state university) containing:
- Annual tuition, hostel, and mess fee structures.
- Fictionalized placement averages and top recruiters (e.g. TATA Steel, SAIL, BCCL, BCCL Dhanbad).
- Scholarship records for board percentage evaluation (e.g., e-Kalyan portal, Birsa Munda scholarship).

No official institutional statistics are claimed. The architecture is modular and supports replacing the synthetic corpus with verified real-world data.

---

## Running the Application

### Backend
1. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env` in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node packages and start Vite:
   ```bash
   npm install
   npm run dev
   ```

---

## Example Queries

1. "Tell me about BIT Sindri."
2. "Compare BIT Sindri and GEC Dumka."
3. "Hostel fees at RTC Institute of Technology."
4. "Government engineering colleges in Jharkhand."
5. "Colleges with placements above 8 LPA."
6. "Scholarship eligibility for 85% score."
7. "Admission requirements for NIT Jamshedpur."
8. "What are the campus facilities at IIIT Ranchi?"

---

## License

MIT
