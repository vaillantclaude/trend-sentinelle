from __future__ import annotations

import requests
import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "data" / "chroma"

LM_STUDIO_URL = "http://localhost:1234/v1/embeddings"


def embed_query(query: str):
    """
    Génère un embedding pour la requête via LM Studio (API locale).
    """
    payload = {
        "model": "text-embedding-3-small",
        "input": query
    }

    response = requests.post(LM_STUDIO_URL, json=payload)
    response.raise_for_status()
    data = response.json()

    return data["data"][0]["embedding"]


def retrieve_similar(query: str, n_results: int = 5):
    """
    Récupère les documents les plus proches du query via ChromaDB.
    Embeddings générés localement via LM Studio.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection("trend_clusters")

    query_vec = embed_query(query)

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=n_results
    )

    return results
