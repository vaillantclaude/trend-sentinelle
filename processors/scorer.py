from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RULES_FILE = BASE_DIR / "sources" / "rules.json"


def load_rules():
    """Charge les règles PRO depuis rules.json."""
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_date_safe(value: str):
    """Parse une date dans différents formats."""
    if not value:
        return None

    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value[:len(fmt.replace("%Z", ""))], fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            continue

    return None


def recency_score(published: str) -> float:
    """Score basé sur la fraîcheur."""
    dt = parse_date_safe(published)
    if dt is None:
        return 0.2

    now = datetime.now(timezone.utc)
    age_days = max((now - dt).days, 0)

    if age_days == 0:
        return 1.0
    if age_days <= 3:
        return 0.9
    if age_days <= 7:
        return 0.8
    if age_days <= 14:
        return 0.65
    if age_days <= 30:
        return 0.45
    if age_days <= 60:
        return 0.25
    return 0.1


def keyword_score(text: str, boost_keywords: List[str]) -> float:
    """Score basé sur les mots-clés orientés objets."""
    if not text:
        return 0.0

    text = text.lower()
    hits = sum(1 for kw in boost_keywords if kw.lower() in text)
    return min(hits / max(len(boost_keywords), 1), 1.0)


def source_quality_score(source: str) -> float:
    """Score basé sur la qualité de la source."""
    source = (source or "").lower()

    weights = {
        "techcrunch": 0.15,
        "wired": 0.15,
        "the verge": 0.12,
        "frandroid": 0.10,
        "les numeriques": 0.10,
        "gizmodo": 0.10,
        "engadget": 0.10,
        "yanko design": 0.12,
        "product hunt": 0.12,
    }

    return weights.get(source, 0.05)


def summary_richness_score(summary: str) -> float:
    """Score basé sur la richesse du résumé."""
    if not summary:
        return 0.0

    length = len(summary)

    if length < 120:
        return 0.0
    if length < 300:
        return 0.05
    if length < 600:
        return 0.10
    return 0.15


def title_boost(title: str) -> float:
    """Boost basé sur l'innovation dans le titre."""
    if not title:
        return 0.0

    score = 0.0
    title_lower = title.lower()

    if any(w in title_lower for w in ["new", "launch", "prototype", "concept", "robot", "smart"]):
        score += 0.2

    if any(c.isdigit() for c in title):
        score += 0.1

    if len(title) < 80:
        score += 0.05

    return min(score, 0.3)


def compute_score(item: Dict) -> Dict:
    """Calcule le score final PRO d'un item."""
    rules = load_rules()
    boost_keywords = rules.get("boost_keywords", [])

    summary = item.get("summary", "") or item.get("text", "")
    published = item.get("published", "")
    title = item.get("title", "")
    source = item.get("source_name", "")

    r = recency_score(published)
    k = keyword_score(summary, boost_keywords)
    s = source_quality_score(source)
    rich = summary_richness_score(summary)
    t = title_boost(title)

    final = round((0.40 * r) + (0.25 * k) + (0.15 * s) + (0.10 * rich) + (0.10 * t), 4)

    scored = dict(item)
    scored["score"] = final
    scored["score_parts"] = {
        "recency": round(r, 4),
        "keywords": round(k, 4),
        "source_quality": round(s, 4),
        "richness": round(rich, 4),
        "title_boost": round(t, 4),
    }

    return scored


def score_items(items: List[Dict]) -> List[Dict]:
    """Score tous les items et les trie par score décroissant."""
    scored = [compute_score(item) for item in items]
    return sorted(scored, key=lambda x: x.get("score", 0), reverse=True)
