"""
LLM wrapper LangChain.

Une seule instance de ChatGoogleGenerativeAI, créée ici et importée partout
ailleurs (chat_service.py maintenant, puis les tools et l'agent plus tard).
Pourquoi centraliser : si demain tu changes de modèle ou de provider LLM,
tu modifies UN SEUL fichier, pas chaque endroit qui appelle le LLM.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    api_key=settings.gemini_api_key,
    temperature=0.3,  # relativement factuel ; on ajustera par tool plus tard
)