"""
State du graphe LangGraph : partagé et modifié par chaque nœud.

Pourquoi TypedDict : LangGraph fusionne automatiquement ce que chaque nœud
retourne dans ce state global — pas besoin de le faire manuellement.
"""

from typing import Any, TypedDict


class AgentState(TypedDict):
    question: str
    evidence: list[dict[str, Any]]  # ce que chaque outil appelé a rapporté
    next_action: str
    reasoning: str
    iterations: int
    final_answer: str
