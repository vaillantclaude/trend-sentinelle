import json
from pathlib import Path
from datetime import datetime

from collectors.normalizer import normalize_items
from processors.filter import filter_items
from processors.scorer import score_items
from processors.clusterer import cluster_items


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "all_sources.json"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = PROCESSED_DIR / "scored_items.json"


def load_raw_items():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Fichier introuvable : {RAW_FILE}")

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_scored(items):
    out = {
        "generated_at": datetime.now().isoformat(),
        "total_items": len(items),
        "items": items,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)


def main():
    raw_items = load_raw_items()

    print(f"[INFO] Normalisation de {len(raw_items)} items...")
    normalized = normalize_items(raw_items)

    print("[INFO] Filtrage...")
    filtered = filter_items(normalized)
    print(f"[INFO] {len(filtered)} items après filtrage")

    print("[INFO] Scoring...")
    scored = score_items(filtered)

    print("[INFO] Clustering...")
    clustered = cluster_items(scored)

    # Tri final sur les items clusterisés
    final_items = sorted(clustered, key=lambda x: x["score"], reverse=True)

    save_scored(final_items)

    print(f"[OK] {len(final_items)} items analysés, scorés et clusterisés")
    print(f"[TOP] {final_items[0]['title']} | score={final_items[0]['score']}")


if __name__ == "__main__":
    main()
