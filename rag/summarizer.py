from __future__ import annotations

import requests
import json

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

def summarize_cluster(results):
    """
    Résume un cluster avec Gemma 4 (LM Studio).
    Style professionnel (Option A).
    """
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    context = ""
    for doc, meta in zip(docs, metas):
        context += f"- {meta.get('title', 'item')} : {doc}\n"

    prompt = f"""
Tu es un analyste professionnel des tendances produits.
Voici un ensemble d'objets appartenant à un même cluster :

{context}

Produis un résumé professionnel contenant :
1. Description du cluster
2. Signaux faibles détectés
3. Tendances émergentes
4. Recommandations d'objets à surveiller
"""

    payload = {
        "model": "gemma-4-12b-qat",
        "messages": [
            {"role": "system", "content": "Tu es un expert en analyse de tendances produits."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(LM_STUDIO_URL, json=payload)
    data = response.json()

    return data["choices"][0]["message"]["content"]
