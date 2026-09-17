"""
Construit l'index RAG à partir des documents dans data/documents/.

Usage (depuis backend/, venv activé) :
    python -m scripts.build_rag_index

Idempotent : supprime et reconstruit la collection à chaque exécution.
"""

from app.rag.loader import load_documents
from app.rag.splitter import split_documents
from app.rag.vector_store import get_vector_store

DOCS_DIR = "data/documents"


def main():
    print("Chargement des documents...")
    documents = load_documents(DOCS_DIR)
    print(f"  {len(documents)} documents trouvés")

    print("Découpage en chunks...")
    chunks = split_documents(documents)
    print(f"  {len(chunks)} chunks créés")

    print("Génération des embeddings + indexation dans ChromaDB...")
    store = get_vector_store()
    store.delete_collection()  # idempotence : on repart propre
    store = get_vector_store()
    store.add_documents(chunks)

    print("Index RAG construit avec succès.")


if __name__ == "__main__":
    main()
