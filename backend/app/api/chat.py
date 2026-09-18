from fastapi import APIRouter

from app.agents.graph import run_agent_graph
from app.schemas.chat import (
    AgentResponse,
    ChatRequest,
    ChatResponse,
    GraphResponse,
    PandasResponse,
    RAGResponse,
    SQLResponse,
)
from app.services.agent_service import ask_agent
from app.services.chat_service import RouteDecision, classify_question, generate_answer
from app.services.pandas_service import answer_with_pandas
from app.services.rag_service import answer_with_rag
from app.services.sql_service import answer_with_sql

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(answer=generate_answer(request.message))


@router.post("/classify", response_model=RouteDecision)
def chat_classify(request: ChatRequest) -> RouteDecision:
    """Démonstration du structured output (Phase 2) — répétition générale du routing Phase 7."""
    return classify_question(request.message)


# Les 3 outils individuels restent accessibles pour tester/débugger chacun isolément
rag_router = APIRouter(prefix="/rag", tags=["tools"])
sql_router = APIRouter(prefix="/sql", tags=["tools"])
pandas_router = APIRouter(prefix="/pandas", tags=["tools"])
agent_router = APIRouter(prefix="/agent", tags=["agent"])
graph_router = APIRouter(prefix="/graph", tags=["agent"])


@rag_router.post("/ask", response_model=RAGResponse)
def rag_ask(request: ChatRequest) -> RAGResponse:
    result = answer_with_rag(request.message)
    return RAGResponse(answer=result["answer"], sources=result["sources"])


@sql_router.post("/ask", response_model=SQLResponse)
def sql_ask(request: ChatRequest) -> SQLResponse:
    result = answer_with_sql(request.message)
    return SQLResponse(answer=result["answer"], sql=result["sql"], row_count=result["row_count"])


@pandas_router.post("/ask", response_model=PandasResponse)
def pandas_ask(request: ChatRequest) -> PandasResponse:
    result = answer_with_pandas(request.message)
    return PandasResponse(answer=result["answer"], raw_result=result["raw_result"])


@agent_router.post("/ask", response_model=AgentResponse)
def agent_ask(request: ChatRequest) -> AgentResponse:
    """Phase 6 : routing simple, un seul outil choisi."""
    return AgentResponse(**ask_agent(request.message))


@graph_router.post("/ask", response_model=GraphResponse)
def graph_ask(request: ChatRequest) -> GraphResponse:
    """Phase 7 : LangGraph, peut enchaîner plusieurs outils. C'est celui-ci qu'utilisent les conversations (Phase 8)."""
    return GraphResponse(**run_agent_graph(request.message))
