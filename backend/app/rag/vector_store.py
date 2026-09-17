"""
Vector store — ChromaDB persisté sur disque local.

Pourquoi ChromaDB : gratuit, tourne en local sans service externe (respecte
la contrainte budget 0€), suffisant pour un volume de documents portfolio.
Si le volume explosait (des millions de chunks), on migrerait vers un
vector store managé — mais ce n'est pas le cas ici, donc pas besoin de
sur-ingénierer.
"""

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2",
    google_api_key=settings.gemini_api_key,
)


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )
