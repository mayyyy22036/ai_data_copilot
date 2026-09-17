"""
Chargement des documents.

Aujourd'hui : lecture de fichiers .md sur le filesystem local.
Plus tard (GCS) : cette fonction sera la SEULE à changer — le reste du
pipeline (splitter, vector store) n'a aucune idée d'où viennent les documents.
C'est exactement le principe d'abstraction storage de la section 19.
"""

from pathlib import Path

from langchain_core.documents import Document


def load_documents(directory: str) -> list[Document]:
    docs = []
    for path in Path(directory).glob("*.md"):
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs
