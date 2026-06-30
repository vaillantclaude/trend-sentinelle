import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RULES_FILE = BASE_DIR / "sources" / "rules.json"


def load_rules():
    if not RULES_FILE.exists():
        return {"block_keywords": [], "block_sources": []}

    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_items(items):
    rules = load_rules()
    blocked_keywords = rules.get("block_keywords", [])
    blocked_sources = rules.get("block_sources", [])

    filtered = []

    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        source = item.get("source_name", "")

        # Filtrage par source
        if source in blocked_sources:
            continue

        # Filtrage par mots-clés
        blocked = False
        for kw in blocked_keywords:
            if kw in title or kw in summary:
                blocked = True
                break

        if not blocked:
            filtered.append(item)

    return filtered
