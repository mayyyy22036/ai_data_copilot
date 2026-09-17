"""
Chunking.

chunk_size=600, chunk_overlap=100 : point de départ raisonnable pour des
documents de politique d'entreprise (paragraphes denses, pas des romans).
`separators` priorise la coupe sur les titres de section (## ) puis les
paragraphes, pour éviter de couper une phrase en plein milieu autant que
possible.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n## ", "\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(documents)
