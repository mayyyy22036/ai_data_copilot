"""
Agent (version simple, sans LangGraph) : classification puis dispatch
vers UN SEUL outil. Pas de boucle, pas de retry, pas d'enchaînement
multi-outils — voir Phase 7 (LangGraph) pour ces capacités.
"""

from app.services.chat_service import classify_question, generate_answer
from app.services.pandas_service import answer_with_pandas
from app.services.rag_service import answer_with_rag
from app.services.sql_service import answer_with_sql


def ask_agent(question: str) -> dict:
    decision = classify_question(question)

    if decision.tool == "rag":
        result = answer_with_rag(question)
        return {
            "answer": result["answer"],
            "tool_used": "rag",
            "reasoning": decision.reasoning,
            "details": {"sources": result["sources"]},
        }

    elif decision.tool == "sql":
        result = answer_with_sql(question)
        return {
            "answer": result["answer"],
            "tool_used": "sql",
            "reasoning": decision.reasoning,
            "details": {"sql": result["sql"], "row_count": result["row_count"]},
        }

    elif decision.tool == "python":
        result = answer_with_pandas(question)
        return {
            "answer": result["answer"],
            "tool_used": "python",
            "reasoning": decision.reasoning,
            "details": {"raw_result": result["raw_result"]},
        }

    else:  # direct_answer
        answer = generate_answer(question)
        return {
            "answer": answer,
            "tool_used": "direct_answer",
            "reasoning": decision.reasoning,
            "details": {},
        }
