from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph import graph

app = FastAPI(title="College Analytics & Information Assistant API")

# Add CORS middleware to support local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    intent: str
    matched_entity: str
    source: str
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Run the query through the compiled graph
    initial_state = {"question": request.question}
    result = graph.invoke(initial_state)
    return {
        "intent": result.get("intent", "unknown"),
        "matched_entity": result.get("matched_entity", "Unknown"),
        "source": result.get("source", "Official Sources"),
        "answer": result.get("answer", "No answer generated."),
    }
