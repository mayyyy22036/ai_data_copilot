"""
SQL Tool — text-to-SQL sécurisé.

Trois couches de protection, dans l'ordre :
1. Validation du SQL généré AVANT exécution (ce fichier)
2. Connexion via un rôle PostgreSQL read-only (readonly_session.py)
3. default_transaction_read_only=on sur la connexion elle-même

Si une seule couche suffisait, on n'aurait pas besoin des deux autres —
c'est précisément parce qu'aucune protection n'est infaillible seule
qu'on empile ces trois niveaux.
"""

from sqlalchemy import text
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm import llm
from app.database.readonly_session import readonly_engine

# Description du schéma donnée au LLM — doit rester synchronisée avec
# app/database/models.py. Le LLM ne "connaît" la base QUE via ce texte.
SCHEMA_DESCRIPTION = """
Table "stores" (un magasin par ligne) :
  - store_id (integer, clé primaire)
  - store_type (text, valeurs possibles: 'a', 'b', 'c', 'd')
  - assortment (text, 'a'=basic, 'b'=extra, 'c'=extended)
  - competition_distance (float, distance en mètres au concurrent le plus proche, peut être NULL)
  - promo2 (boolean, participe à une promo continue)
  - promo_interval (text, mois de relance de la promo continue)

Table "sales" (une ligne par magasin par jour) :
  - id (integer, clé primaire)
  - store_id (integer, clé étrangère vers stores.store_id)
  - date (date)
  - day_of_week (integer, 1=lundi ... 7=dimanche)
  - sales (float, chiffre d'affaires du jour)
  - customers (integer, nombre de clients)
  - open (boolean)
  - promo (boolean, promo active ce jour)
  - state_holiday (text, 'a'/'b'/'c' ou '0' si aucun)
  - school_holiday (boolean)
"""

FORBIDDEN_KEYWORDS = [
    "drop", "delete", "update", "insert", "alter", "truncate",
    "grant", "revoke", "create", "--", "/*", "*/",
]


class SQLQuery(BaseModel):
    sql: str = Field(description="Une unique requête SQL SELECT valide en PostgreSQL")


sql_generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu es un expert PostgreSQL. Génère UNE SEULE requête SQL SELECT "
            "pour répondre à la question, en te basant STRICTEMENT sur ce "
            "schéma (n'invente jamais de colonne ou de table) :\n\n"
            f"{SCHEMA_DESCRIPTION}\n\n"
            "Règles : uniquement des requêtes SELECT, jamais de modification "
            "de données. Toujours utiliser un JOIN explicite si tu as besoin "
            "des deux tables.",
        ),
        ("human", "{question}"),
    ]
)

sql_generation_chain = sql_generation_prompt | llm.with_structured_output(SQLQuery)


def validate_sql(sql: str) -> str:
    """
    Lève une ValueError si la requête est jugée dangereuse.
    Retourne le SQL nettoyé (et complété d'un LIMIT) si elle est acceptée.
    """
    cleaned = sql.strip().rstrip(";")

    if ";" in cleaned:
        raise ValueError("Plusieurs instructions SQL détectées — refusé.")

    lowered = cleaned.lower()

    if not lowered.startswith("select"):
        raise ValueError("Seules les requêtes SELECT sont autorisées.")

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in lowered:
            raise ValueError(f"Mot-clé interdit détecté : '{keyword}'.")

    # Garde-fou perf/sécurité : jamais plus de 500 lignes retournées d'un coup.
    if "limit" not in lowered:
        cleaned += " LIMIT 500"

    return cleaned


def ask_database(question: str) -> dict:
    generated = sql_generation_chain.invoke({"question": question})
    validated_sql = validate_sql(generated.sql)

    with readonly_engine.connect() as conn:
        result = conn.execute(text(validated_sql))
        rows = [dict(row._mapping) for row in result]

    return {
        "sql": validated_sql,
        "row_count": len(rows),
        "rows": rows,
    }
