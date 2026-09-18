"""
Pandas Tool — sécurisé par conception : AUCUNE exécution de code généré
par le LLM. Le LLM choisit uniquement parmi ces fonctions prédéfinies, avec
des colonnes validées contre une liste blanche.
"""

from functools import lru_cache
from typing import Literal, Optional

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm import llm
from app.database.readonly_session import readonly_engine

# Liste blanche : seules ces colonnes peuvent être manipulées, quoi que le
# LLM demande. Empêche toute tentative d'accéder à une colonne inattendue.
ALLOWED_NUMERIC_COLUMNS = {"sales", "customers", "competition_distance", "day_of_week"}
ALLOWED_GROUP_COLUMNS = {"store_type", "assortment", "promo", "state_holiday", "day_of_week"}
ALLOWED_AGG_FUNCS = {"mean", "sum", "count", "std", "median"}


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """
    Charge sales+stores en mémoire une seule fois (cache), via le rôle
    read-only. Recharger à chaque requête serait beaucoup trop lent sur
    ~1 million de lignes.
    """
    query = """
        SELECT s.date, s.store_id, s.sales, s.customers, s.promo,
               s.day_of_week, s.state_holiday,
               st.store_type, st.assortment, st.competition_distance
        FROM sales s
        JOIN stores st ON s.store_id = st.store_id
    """
    return pd.read_sql(query, readonly_engine)


# --- Fonctions d'analyse, écrites par nous, jamais par le LLM ---

def compute_correlation(column_x: str, column_y: str) -> dict:
    if column_x not in ALLOWED_NUMERIC_COLUMNS or column_y not in ALLOWED_NUMERIC_COLUMNS:
        raise ValueError("Colonne non autorisée pour une corrélation.")
    df = load_data()
    coefficient = df[column_x].corr(df[column_y])
    return {"column_x": column_x, "column_y": column_y, "correlation": round(coefficient, 4)}


def compute_groupby_stats(group_by: str, agg_column: str, agg_func: str) -> dict:
    if group_by not in ALLOWED_GROUP_COLUMNS:
        raise ValueError("Colonne de groupement non autorisée.")
    if agg_column not in ALLOWED_NUMERIC_COLUMNS:
        raise ValueError("Colonne d'agrégation non autorisée.")
    if agg_func not in ALLOWED_AGG_FUNCS:
        raise ValueError("Fonction d'agrégation non autorisée.")
    df = load_data()
    result = df.groupby(group_by)[agg_column].agg(agg_func).round(2)
    return {"group_by": group_by, "agg_column": agg_column, "agg_func": agg_func, "result": result.to_dict()}


def compute_trend() -> dict:
    """Tendance des ventes moyennes par mois, toutes régions confondues."""
    df = load_data()
    df = df.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    result = df.groupby("month")["sales"].mean().round(2)
    return {"result": result.to_dict()}


# --- Sélection de la fonction par le LLM (structured output) ---

class AnalysisRequest(BaseModel):
    function: Literal["correlation", "groupby_stats", "trend"] = Field(
        description="La fonction d'analyse la plus adaptée à la question"
    )
    column_x: Optional[str] = Field(None, description=f"Pour 'correlation' — parmi {ALLOWED_NUMERIC_COLUMNS}")
    column_y: Optional[str] = Field(None, description=f"Pour 'correlation' — parmi {ALLOWED_NUMERIC_COLUMNS}")
    group_by: Optional[str] = Field(None, description=f"Pour 'groupby_stats' — parmi {ALLOWED_GROUP_COLUMNS}")
    agg_column: Optional[str] = Field(None, description=f"Pour 'groupby_stats' — parmi {ALLOWED_NUMERIC_COLUMNS}")
    agg_func: Optional[str] = Field(None, description=f"Pour 'groupby_stats' — parmi {ALLOWED_AGG_FUNCS}")


selection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu choisis quelle fonction d'analyse statistique utiliser pour "
            "répondre à la question, parmi : 'correlation' (lien entre deux "
            "variables numériques), 'groupby_stats' (statistique agrégée "
            "par catégorie), 'trend' (évolution mensuelle des ventes, sans "
            "paramètre).\n\n"
            f"Colonnes numériques valides : "
            f"{', '.join(sorted(ALLOWED_NUMERIC_COLUMNS))}.\n"
            f"Colonnes de groupement valides : "
            f"{', '.join(sorted(ALLOWED_GROUP_COLUMNS))}.\n"
            f"Fonctions d'agrégation valides : "
            f"{', '.join(sorted(ALLOWED_AGG_FUNCS))}.",
        ),
        ("human", "{question}"),
    ]
)
selection_chain = selection_prompt | llm.with_structured_output(AnalysisRequest)


def run_analysis(question: str) -> dict:
    request = selection_chain.invoke({"question": question})

    if request.function == "correlation":
        return compute_correlation(request.column_x, request.column_y)
    elif request.function == "groupby_stats":
        return compute_groupby_stats(request.group_by, request.agg_column, request.agg_func)
    elif request.function == "trend":
        return compute_trend()
    else:
        raise ValueError(f"Fonction inconnue : {request.function}")
