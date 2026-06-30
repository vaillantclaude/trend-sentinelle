from __future__ import annotations

import chromadb
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "data" / "chroma"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

def index_vectors(vectors, metadata_list):
    """
    Indexe les vecteurs dans ChromaDB.
    metadata_list = liste de dicts (titre, cluster, etc.)
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection("trend_clusters")

    ids = [f"doc_{i}" for i in range(len(vectors))]

    collection.add(
        ids=ids,
        embeddings=vectors,
        metadatas=metadata_list
    )

    return True
