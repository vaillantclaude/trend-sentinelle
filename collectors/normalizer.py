from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List


def strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(text: Any) -> str:
    if text is None:
        return ""
    text = str(text)
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2019", "'")
    text = text.replace("\u2018", "'")
    text = text.replace("\u201c", '"')
    text = text.replace("\u201d", '"')
    text = text.lower()
    text = strip_accents(text)
    text = normalize_whitespace(text)
    return text


def normalize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(item)
    normalized["title"] = normalize_text(item.get("title", ""))
    normalized["summary"] = normalize_text(item.get("summary", ""))
    normalized["source_name"] = normalize_text(item.get("source_name", ""))
    normalized["link"] = str(item.get("link", "")).strip()
    normalized["published"] = str(item.get("published", "")).strip()
    normalized["tags"] = [normalize_text(t) for t in item.get("tags", []) if t]
    normalized["authors"] = [normalize_text(a) for a in item.get("authors", []) if a]
    normalized["text"] = normalize_text(
        f"{normalized['title']} {normalized['summary']} {' '.join(normalized['tags'])}"
    )
    return normalized


def normalize_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [normalize_item(item) for item in items]