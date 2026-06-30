from pathlib import Path
import json
from datetime import datetime

# IA locale (RAG)
from rag.retriever import retrieve_similar
from rag.summarizer import summarize_cluster

BASE_DIR = Path(__file__).resolve().parent.parent
SCORED_FILE = BASE_DIR / "data" / "processed" / "scored_items.json"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = REPORTS_DIR / "last_report.md"


def load_scored():
    if not SCORED_FILE.exists():
        raise FileNotFoundError(f"Fichier introuvable: {SCORED_FILE}")
    with open(SCORED_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("items", [])


def generate_markdown(items):
    now = datetime.now().isoformat()
    lines = []
    lines.append(f"# Rapport de veille — {now}\n")
    lines.append(f"Total items : **{len(items)}**\n")
    lines.append("---\n")
    lines.append("## Top 10 tendances\n")

    top = items[:10]
    for i, item in enumerate(top, 1):
        title = item.get("title", "")
        score = item.get("score", 0)
        source = item.get("source_name", "")
        link = item.get("link", "")
        summary = item.get("summary", "")
        tags = ", ".join(item.get("tags", []))

        cluster_id = item.get("cluster_id", "N/A")
        cluster_name = item.get("cluster_name", "N/A")

        score_parts = item.get("score_parts", {})

        lines.append(f"### {i}. {title}")
        lines.append(f"- Score : **{score}**")
        lines.append(f"- Source : {source}")
        lines.append(f"- Lien : [{link}]({link})")
        lines.append(f"- Tags : {tags}")
        lines.append(f"- Cluster : **{cluster_id} — {cluster_name}**")

        # Scores détaillés
        lines.append("#### Détails du score")
        for k, v in score_parts.items():
            lines.append(f"- {k} : {v}")

        # Résumé brut
        lines.append("\n#### Résumé")
        lines.append(summary + "\n")

        # IA locale — résumé du cluster
        lines.append("#### Analyse IA du cluster")

        try:
            # On utilise le nom du cluster comme requête RAG
            query = cluster_name

            results = retrieve_similar(query)
            summary_ai = summarize_cluster(results)

            lines.append(summary_ai)
            lines.append("\n---\n")

        except Exception as e:
            lines.append(f"*Erreur IA locale : {e}*")
            lines.append("\n---\n")

    return "\n".join(lines)


def save_report(content):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    items = load_scored()
    md = generate_markdown(items)
    save_report(md)
    print(f"[OK] Rapport généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
