import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import RateLimitError

from graph import graph

app = FastAPI(title="College Analytics & Information Assistant API")

# Add CORS middleware to support local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    intent: str
    matched_entity: str
    source: str
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        initial_state = {"question": request.question}
        result = graph.invoke(initial_state)
        return {
            "intent": result.get("intent", "unknown"),
            "matched_entity": result.get("matched_entity", "Unknown"),
            "source": result.get("source", "Official Sources"),
            "answer": result.get("answer", "No answer generated."),
        }
    except RateLimitError as e:
        # Groq error message contains "try again in 1m2.34s" or "try again in 5.2s"
        msg = str(e)
        seconds = 60  # sensible default
        m = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", msg)
        if m:
            minutes = int(m.group(1) or 0)
            secs = float(m.group(2) or 0)
            seconds = minutes * 60 + int(secs) + 1
        raise HTTPException(status_code=429, detail={"retry_after": seconds})
