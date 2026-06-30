from __future__ import annotations

import requests
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EMBED_DIR = BASE_DIR / "data" / "embeddings"
EMBED_DIR.mkdir(parents=True, exist_ok=True)

LM_STUDIO_URL = "http://localhost:1234/v1/embeddings"


def embed_documents(docs):
    """
    Transforme une liste de textes en vecteurs via LM Studio (API embeddings locale).
    Retourne une liste de vecteurs.
    """
    payload = {
        "model": "text-embedding-3-small",
        "input": docs,
    }

    response = requests.post(LM_STUDIO_URL, json=payload)
    response.raise_for_status()
    data = response.json()

    vectors = [item["embedding"] for item in data["data"]]

    out_file = EMBED_DIR / "vectors.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(vectors, f, indent=2)

    return vectors
