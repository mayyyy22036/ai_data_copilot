"""
Le graphe agentique : peut enchaîner plusieurs outils avant de répondre.

C'est le cœur de la Phase 7 — compare ce fichier à agent_service.py
(Phase 6) pour voir précisément ce que LangGraph ajoute : une boucle
contrôlée au lieu d'un choix unique.
"""

from typing import Literal

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from app.agents.state import AgentState
from app.core.llm import llm
from app.services.pandas_service import answer_with_pandas
from app.services.rag_service import answer_with_rag
from app.services.sql_service import answer_with_sql

# Garde-fou anti-boucle infinie : si le LLM n'arrive jamais à décider qu'il
# a assez d'éléments, on force l'arrêt après ce nombre de tours. C'est le
# "Retry" avec limite mentionné dans le diagramme de la section 8.
MAX_ITERATIONS = 4


# --- Nœud "analyze" : décide du prochain outil, ou "generate" si assez d'éléments ---

class NextAction(BaseModel):
    next_action: Literal["rag", "sql", "python", "generate"] = Field(
        description="Le prochain outil à utiliser, ou 'generate' si assez "
        "d'éléments ont été rassemblés pour répondre complètement"
    )
    reasoning: str = Field(description="Justification courte de ce choix")


analyze_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu diriges un système agentique qui peut appeler plusieurs "
            "outils avant de répondre. Question de l'utilisateur : "
            "{question}\n\n"
            "Éléments déjà rassemblés :\n{evidence_summary}\n\n"
            "Outils disponibles :\n"
            "- 'rag' : documents internes (politiques, procédures)\n"
            "- 'sql' : données chiffrées structurées (ventes, magasins, régions)\n"
            "- 'python' : calculs statistiques (corrélations, tendances)\n"
            "- 'generate' : les éléments rassemblés suffisent pour répondre\n\n"
            "Choisis 'generate' dès que tu as assez d'éléments. N'appelle "
            "jamais deux fois le même outil pour la même sous-question.",
        ),
        ("human", "Quelle est la prochaine action ?"),
    ]
)

analyze_chain = analyze_prompt | llm.with_structured_output(NextAction)


def analyze_node(state: AgentState) -> dict:
    evidence_summary = (
        "\n".join(f"- [{e['tool']}] {e['summary']}" for e in state["evidence"])
        or "(aucun élément rassemblé pour l'instant)"
    )

    iterations = state["iterations"] + 1

    if iterations > MAX_ITERATIONS:
        return {
            "next_action": "generate",
            "reasoning": "Limite d'itérations atteinte — génération forcée.",
            "iterations": iterations,
        }

    decision = analyze_chain.invoke(
        {"question": state["question"], "evidence_summary": evidence_summary}
    )
    return {
        "next_action": decision.next_action,
        "reasoning": decision.reasoning,
        "iterations": iterations,
    }


# --- Nœuds "outil" : chacun ajoute son résultat à evidence, sans jamais l'écraser ---

def call_rag_node(state: AgentState) -> dict:
    result = answer_with_rag(state["question"])
    evidence = state["evidence"] + [
        {"tool": "rag", "summary": result["answer"], "details": {"sources": result["sources"]}}
    ]
    return {"evidence": evidence}


def call_sql_node(state: AgentState) -> dict:
    result = answer_with_sql(state["question"])
    evidence = state["evidence"] + [
        {"tool": "sql", "summary": result["answer"], "details": {"sql": result["sql"]}}
    ]
    return {"evidence": evidence}


def call_python_node(state: AgentState) -> dict:
    result = answer_with_pandas(state["question"])
    evidence = state["evidence"] + [
        {"tool": "python", "summary": result["answer"], "details": {"raw_result": result["raw_result"]}}
    ]
    return {"evidence": evidence}


# --- Nœud "generate" : synthétise TOUS les éléments rassemblés ---

GENERATE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu rédiges la réponse finale à partir des éléments rassemblés "
            "par différents outils. Synthétise TOUS les éléments "
            "pertinents, ne te contente pas d'en recopier un seul si "
            "plusieurs ont été rassemblés.",
        ),
        ("human", "Question : {question}\n\nÉléments rassemblés :\n{evidence_summary}"),
    ]
)

generate_chain = GENERATE_PROMPT | llm | StrOutputParser()


def generate_node(state: AgentState) -> dict:
    evidence_summary = (
        "\n".join(f"- [{e['tool']}] {e['summary']}" for e in state["evidence"])
        or "(aucun élément — réponds du mieux possible avec tes connaissances générales)"
    )
    final_answer = generate_chain.invoke(
        {"question": state["question"], "evidence_summary": evidence_summary}
    )
    return {"final_answer": final_answer}


def route_after_analyze(state: AgentState) -> str:
    return state["next_action"]


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze", analyze_node)
    graph.add_node("call_rag", call_rag_node)
    graph.add_node("call_sql", call_sql_node)
    graph.add_node("call_python", call_python_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("analyze")

    graph.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {"rag": "call_rag", "sql": "call_sql", "python": "call_python", "generate": "generate"},
    )

    # La BOUCLE : après chaque outil, on repasse par analyze. C'est ce qui
    # permet l'enchaînement multi-outils (ex: SQL puis Python).
    graph.add_edge("call_rag", "analyze")
    graph.add_edge("call_sql", "analyze")
    graph.add_edge("call_python", "analyze")

    graph.add_edge("generate", END)

    return graph.compile()


agent_graph = build_graph()


def run_agent_graph(question: str) -> dict:
    initial_state: AgentState = {
        "question": question,
        "evidence": [],
        "next_action": "",
        "reasoning": "",
        "iterations": 0,
        "final_answer": "",
    }
    final_state = agent_graph.invoke(initial_state)
    return {
        "answer": final_state["final_answer"],
        "evidence": final_state["evidence"],
        "iterations": final_state["iterations"],
    }
