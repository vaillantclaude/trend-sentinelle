import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCES_FILE = BASE_DIR / "sources" / "feeds.json"
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_rss(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text


# -----------------------------
# PARSE RSS (standard)
# -----------------------------
def parse_rss(xml: str, source_name: str, source_url: str):
    soup = BeautifulSoup(xml, "lxml-xml")
    items = []

    for entry in soup.find_all("item"):
        title = entry.title.text if entry.title else ""
        link = entry.link.text if entry.link else ""
        summary = entry.description.text if entry.description else ""
        published = entry.pubDate.text if entry.pubDate else ""

        fingerprint_src = f"{title}|{link}|{published}|{source_name}"
        fingerprint = hashlib.sha256(fingerprint_src.encode("utf-8")).hexdigest()

        items.append({
            "id": fingerprint,
            "fingerprint": fingerprint,
            "source_name": source_name,
            "source_url": source_url,
            "title": title,
            "link": link,
            "summary": summary,
            "published": published,
            "tags": [],
            "authors": [],
            "collected_at": datetime.now(timezone.utc).isoformat(),
        })

    return items


# -----------------------------
# PARSE ATOM (The Verge)
# -----------------------------
def parse_atom(xml: str, source_name: str, source_url: str):
    soup = BeautifulSoup(xml, "lxml-xml")
    items = []

    for entry in soup.find_all("entry"):
        title = entry.title.text if entry.title else ""

        link_tag = entry.find("link", {"rel": "alternate"})
        link = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""

        summary = entry.summary.text if entry.summary else ""
        published = entry.published.text if entry.published else ""

        fingerprint_src = f"{title}|{link}|{published}|{source_name}"
        fingerprint = hashlib.sha256(fingerprint_src.encode("utf-8")).hexdigest()

        items.append({
            "id": fingerprint,
            "fingerprint": fingerprint,
            "source_name": source_name,
            "source_url": source_url,
            "title": title,
            "link": link,
            "summary": summary,
            "published": published,
            "tags": [],
            "authors": [],
            "collected_at": datetime.now(timezone.utc).isoformat(),
        })

    return items


# -----------------------------
# PARSE HTML (Les Numériques)
# -----------------------------
def parse_html_feed(xml: str, source_name: str, source_url: str):
    soup = BeautifulSoup(xml, "html.parser")
    items = []

    for article in soup.find_all("article"):
        title_tag = article.find("h2")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        link_tag = article.find("a")
        link = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""

        summary_tag = article.find("p")
        summary = summary_tag.get_text(strip=True) if summary_tag else ""

        published = ""

        fingerprint_src = f"{title}|{link}|{published}|{source_name}"
        fingerprint = hashlib.sha256(fingerprint_src.encode("utf-8")).hexdigest()

        items.append({
            "id": fingerprint,
            "fingerprint": fingerprint,
            "source_name": source_name,
            "source_url": source_url,
            "title": title,
            "link": link,
            "summary": summary,
            "published": published,
            "tags": [],
            "authors": [],
            "collected_at": datetime.now(timezone.utc).isoformat(),
        })

    return items


# -----------------------------
# LOAD SOURCES
# -----------------------------
def load_sources():
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# SAVE RAW
# -----------------------------
def save_raw(name: str, items):
    out_file = RAW_DIR / f"{name}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def main():
    sources = load_sources()
    all_items = []

    for src in sources:
        name = src["name"]
        url = src["url"]

        try:
            xml = fetch_rss(url)

            # 1) RSS standard
            items = parse_rss(xml, name, url)

            # 2) Fallback Atom
            if len(items) == 0:
                items = parse_atom(xml, name, url)

            # 3) Fallback HTML
            if len(items) == 0:
                items = parse_html_feed(xml, name, url)

            print(f"[OK] {name} -> {len(items)} entrées")

            save_raw(name, items)
            all_items.extend(items)

        except Exception as e:
            print(f"[ERREUR] {name} : {e}")

    print(f"\nCollecte terminée : {len(all_items)} entrées récupérées")

    # Déduplication
    fingerprints = set()
    deduped = []
    for item in all_items:
        if item["fingerprint"] not in fingerprints:
            fingerprints.add(item["fingerprint"])
            deduped.append(item)

    print(f"Après déduplication : {len(deduped)} entrées conservées")

    save_raw("all_sources", deduped)


if __name__ == "__main__":
    main()
