"""
Service SQL : orchestre sql_tool (génération + exécution) puis demande au
LLM de résumer les résultats bruts en réponse lisible.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.tools.sql_tool import ask_database

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu résumes des résultats de requête SQL en une réponse claire "
            "et concise en français, pour un utilisateur non-technique. "
            "Ne mentionne pas le SQL lui-même dans ta réponse.",
        ),
        ("human", "Question : {question}\n\nRésultats (JSON) : {rows}"),
    ]
)

summary_chain = SUMMARY_PROMPT | llm | StrOutputParser()


def answer_with_sql(question: str) -> dict:
    result = ask_database(question)

    if result["row_count"] == 0:
        answer = "Aucun résultat trouvé pour cette question."
    else:
        answer = summary_chain.invoke(
            {"question": question, "rows": str(result["rows"][:50])}
        )

    return {
        "answer": answer,
        "sql": result["sql"],
        "row_count": result["row_count"],
    }
