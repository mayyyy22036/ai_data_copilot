"""
Service Pandas : orchestre pandas_tool (sélection + calcul) puis demande au
LLM de résumer le résultat numérique en réponse lisible.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.tools.pandas_tool import run_analysis

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu résumes un résultat d'analyse statistique en une réponse "
            "claire en français, pour un utilisateur non-technique. "
            "Si c'est une corrélation, explique le sens du coefficient "
            "(proche de 1 = forte corrélation positive, proche de -1 = "
            "forte corrélation négative, proche de 0 = pas de lien "
            "linéaire clair).",
        ),
        ("human", "Question : {question}\n\nRésultat (JSON) : {result}"),
    ]
)

summary_chain = SUMMARY_PROMPT | llm | StrOutputParser()


def answer_with_pandas(question: str) -> dict:
    result = run_analysis(question)
    answer = summary_chain.invoke({"question": question, "result": str(result)})
    return {"answer": answer, "raw_result": result}
