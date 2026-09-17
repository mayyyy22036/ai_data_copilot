"""
Phase 2 — démonstration concrète de 3 briques LangChain :
1. PromptTemplate  : prompt réutilisable et paramétrable
2. Chain (LCEL)    : composition via l'opérateur |
3. Structured output : réponse typée (Pydantic), pas juste du texte libre

Le point 3 (classify_question) est une RÉPÉTITION GÉNÉRALE pour la Phase 7
(LangGraph) : c'est exactement ce mécanisme qui servira plus tard à décider
quel outil (RAG/SQL/Python) appeler. Ici on l'utilise juste pour l'observer
fonctionner, sans encore rien router réellement.
"""

from typing import Literal

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm import llm

# --- 1. PromptTemplate ---
# {question} est une variable : le même template sert pour n'importe quelle
# question, au lieu d'écrire un f-string différent à chaque fois.
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Tu es un assistant professionnel, clair et concis."),
        ("human", "{question}"),
    ]
)

# --- 2. Chain (LCEL) ---
# L'opérateur | connecte les étapes : prompt formate le message → llm génère
# → StrOutputParser extrait le texte brut (sinon on récupère un objet
# AIMessage avec des métadonnées qu'on n'a pas besoin de gérer nous-mêmes).
answer_chain = answer_prompt | llm | StrOutputParser()


def generate_answer(question: str) -> str:
    return answer_chain.invoke({"question": question})


# --- 3. Structured output ---
class RouteDecision(BaseModel):
    """Schéma typé que le LLM doit remplir — pas du texte libre à parser nous-même."""

    tool: Literal["rag", "sql", "python", "direct_answer"] = Field(
        description="L'outil le plus adapté pour répondre à la question"
    )
    reasoning: str = Field(description="Une phrase expliquant ce choix")


classification_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu classifies une question utilisateur pour un système de type "
            "entreprise avec 3 sources possibles : "
            "'rag' (documents internes/politiques), "
            "'sql' (données chiffrées structurées : ventes, magasins, régions), "
            "'python' (calculs statistiques : corrélations, tendances), "
            "'direct_answer' (question générale ne nécessitant aucune donnée interne).",
        ),
        ("human", "{question}"),
    ]
)

# .with_structured_output() force Gemini à répondre selon le schéma
# RouteDecision — LangChain gère le prompt engineering et le parsing JSON
# pour toi (c'est ce qu'on remplacerait par un json.loads() fragile sinon).
classification_chain = classification_prompt | llm.with_structured_output(RouteDecision)


def classify_question(question: str) -> RouteDecision:
    return classification_chain.invoke({"question": question})