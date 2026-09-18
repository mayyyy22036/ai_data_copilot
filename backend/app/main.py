"""
Point d'entrée FastAPI — ne contient plus de logique métier, uniquement
le montage des routers. Voir app/api/ pour les endpoints.
"""

from fastapi import FastAPI

from app.api import chat, conversations, health

app = FastAPI(title="AI Data & Documentation Copilot", version="0.8.0")

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(chat.rag_router, prefix="/api")
app.include_router(chat.sql_router, prefix="/api")
app.include_router(chat.pandas_router, prefix="/api")
app.include_router(chat.agent_router, prefix="/api")
app.include_router(chat.graph_router, prefix="/api")
app.include_router(conversations.router, prefix="/api")