from __future__ import annotations

from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np


CLUSTER_COUNT = 10  # Granularité moyenne (Option A)


def extract_text(item: Dict) -> str:
    """Récupère le texte pertinent pour le clustering."""
    title = item.get("title", "") or ""
    summary = item.get("summary", "") or ""
    return f"{title} {summary}".strip()


def cluster_items(items: List[Dict]) -> List[Dict]:
    """Clusterisation PRO des items."""
    if not items:
        return items

    texts = [extract_text(item) for item in items]

    # Vectorisation TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=3000,
        stop_words="english",
        ngram_range=(1, 2)
    )
    X = vectorizer.fit_transform(texts)

    # Clustering KMeans
    model = KMeans(
        n_clusters=CLUSTER_COUNT,
        random_state=42,
        n_init=10
    )
    labels = model.fit_predict(X)

    # Extraction des mots dominants pour nommer les clusters
    terms = vectorizer.get_feature_names_out()
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]

    cluster_names = []
    for i in range(CLUSTER_COUNT):
        top_terms = [terms[ind] for ind in order_centroids[i, :5]]
        cluster_names.append(", ".join(top_terms))

    # Attribution des clusters aux items
    clustered = []
    for item, label in zip(items, labels):
        new_item = dict(item)
        new_item["cluster_id"] = int(label)
        new_item["cluster_name"] = cluster_names[label]
        clustered.append(new_item)

    return clustered
