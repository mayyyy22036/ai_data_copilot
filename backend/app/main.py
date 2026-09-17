"""
Phase 2 — les endpoints utilisent maintenant LangChain (chat_service.py)
au lieu d'appeler Gemini directement, comme en Phase 1.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from app.services.chat_service import RouteDecision, classify_question, generate_answer

app = FastAPI(title="AI Data & Documentation Copilot", version="0.2.0")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    answer = generate_answer(request.message)
    return ChatResponse(answer=answer)


@app.post("/api/chat/classify", response_model=RouteDecision)
def chat_classify(request: ChatRequest) -> RouteDecision:
    """
    Endpoint de DÉMONSTRATION uniquement (pas encore utilisé en prod).
    Montre le structured output : observe que la réponse est un JSON typé
    {"tool": "sql", "reasoning": "..."} et pas du texte libre.
    Le vrai routing agentique arrivera en Phase 6/7.
    """
    return classify_question(request.message)