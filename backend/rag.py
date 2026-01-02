import os
from pathlib import Path

import chromadb
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions


# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
CHROMA_DIR = DATA_DIR / "chroma"

CHROMA_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# Chroma Initialization
# =========================
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

client = Client(
    Settings(
        persist_directory=str(CHROMA_DIR)
    )
)

collection = client.get_or_create_collection(
    name="starbucks_docs",
    embedding_function=embedding_fn
)


# =========================
# Ingestion (RUN ONCE)
# =========================
def ingest_documents():
    """
    Ingest documents from data/docs/*.txt into Chroma.
    Runs only if Chroma directory is empty.
    """

    # Idempotency check
    if any(CHROMA_DIR.iterdir()):
        print("📦 Chroma already exists. Skipping document ingestion.")
        return

    if not DOCS_DIR.exists():
        print("⚠️ Docs directory not found. Skipping RAG ingestion.")
        return

    documents = []
    ids = []

    for idx, filename in enumerate(sorted(DOCS_DIR.iterdir())):
        if filename.suffix.lower() == ".txt":
            with open(filename, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    documents.append(text)
                    ids.append(f"doc_{idx}")

    if not documents:
        print("⚠️ No documents found for ingestion.")
        return

    collection.add(documents=documents, ids=ids)

    print(f"✅ Ingested {len(documents)} documents into Chroma RAG store.")


# =========================
# Retrieval
# =========================
def retrieve_documents(question: str, k: int = 3):
    """
    Retrieve top-k relevant documents for a question.
    Returns a list of document strings.
    """

    if not question:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=k
    )

    docs = results.get("documents", [])

    if not docs or not docs[0]:
        return []

    return docs[0]
