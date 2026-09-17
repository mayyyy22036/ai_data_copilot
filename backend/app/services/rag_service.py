"""
Service RAG : retrouve les chunks pertinents, les injecte dans le prompt,
génère une réponse, et retourne les sources utilisées pour vérification.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm import llm
from app.rag.vector_store import get_vector_store

# Instruction explicite de ne pas halluciner si le contexte est insuffisant —
# c'est la principale mitigation qu'on peut faire côté prompt (section 9).
RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Tu es un assistant d'entreprise. Réponds à la question "
            "UNIQUEMENT à partir du contexte fourni ci-dessous. Si le "
            "contexte ne contient pas l'information nécessaire pour "
            "répondre, dis clairement que tu ne sais pas — n'invente "
            "jamais de réponse.\n\nContexte:\n{context}",
        ),
        ("human", "{question}"),
    ]
)

rag_chain = RAG_PROMPT | llm | StrOutputParser()


def answer_with_rag(question: str, top_k: int = 4) -> dict:
    store = get_vector_store()
    retriever = store.as_retriever(search_kwargs={"k": top_k})
    relevant_docs = retriever.invoke(question)

    context = "\n\n---\n\n".join(doc.page_content for doc in relevant_docs)
    answer = rag_chain.invoke({"context": context, "question": question})

    sources = sorted({doc.metadata.get("source", "inconnu") for doc in relevant_docs})

    return {"answer": answer, "sources": sources}
