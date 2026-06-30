# TREND-SENTINELLE  
Système de veille automatisée, analyse de tendances et synthèse IA locale

TREND-SENTINELLE est un pipeline complet de collecte, traitement, scoring, clustering et analyse IA locale appliqué à des flux d’actualités technologiques.  
Le système fonctionne en deux phases :  
1. Collecte automatique des sources externes (RSS, Atom, HTML).  
2. Analyse locale hors-ligne (normalisation, filtrage, scoring, clustering, RAG).

Ce README documente l’architecture réelle du projet, son pipeline exact et les modules effectivement utilisés.

---

# 1. Objectifs

- Automatiser la collecte de signaux technologiques.  
- Normaliser et filtrer les contenus.  
- Détecter les tendances via scoring et clustering.  
- Générer un rapport Markdown complet.  
- Ajouter une analyse IA locale par cluster via un RAG interne.  
- Fonctionner hors-ligne pour toutes les étapes IA.

---

# 2. Architecture générale

Pipeline réel :

Collecte → Normalisation → Filtrage → Scoring → Clustering → Analyse IA (RAG) → Rapport Markdown

---

# 3. Collecte automatique

La collecte est entièrement automatisée via `collect.py`.

Sources configurées dans :

`sources/feeds.json`

Formats supportés :

- RSS standard  
- Atom  
- HTML (fallback)

Étapes :

1. Téléchargement des flux (requests)
2. Parsing multi-format (BeautifulSoup)
3. Déduplication via SHA-256
4. Sauvegarde dans :

`data/raw/<source>.json`  
`data/raw/all_sources.json`

La collecte nécessite une connexion internet.  
Toutes les étapes suivantes fonctionnent hors-ligne.

---

# 4. Normalisation

Module : `collectors/normalizer.py`

Fonctions :

- suppression des accents  
- uniformisation des apostrophes et guillemets  
- passage en minuscules  
- nettoyage des espaces  
- normalisation des champs (title, summary, tags, authors)  
- création du champ `text` (title + summary + tags)

Sortie : liste d’items normalisés.

---

# 5. Filtrage, scoring, clustering

Module principal : `analyze.py`

Modules appelés :

- `processors/filter.py`  
- `processors/scorer.py`  
- `processors/clusterer.py`

Étapes :

1. Normalisation  
2. Filtrage des items non pertinents  
3. Calcul du score global et des sous-scores  
4. Attribution d’un cluster (`cluster_id`, `cluster_name`)  
5. Tri final par score  
6. Sauvegarde dans :

`data/processed/scored_items.json`

---

# 6. Analyse IA locale (RAG)

Module : `report.py`

Modules IA utilisés :

- `rag/retriever.py`  
- `rag/summarizer.py`

Fonctionnement :

1. Chargement des items scorés  
2. Génération du rapport Markdown  
3. Pour chaque cluster :
- recherche sémantique locale (RAG)  
- résumé IA du cluster  
4. Export dans :

`reports/last_report.md`

Le RAG est réellement utilisé dans le pipeline.

---

# 7. Structure du rapport

Le rapport contient :

- date de génération  
- nombre total d’items  
- Top 10 tendances  
- score détaillé  
- résumé brut  
- analyse IA locale par cluster (RAG)

---

# 8. Arborescence réelle du projet

```text
TREND-SENTINELLE/
│
├── collectors/
│   ├── normalizer.py
│   ├── rss_collector.py
│   ├── web_collector.py
│
├── processors/
│   ├── filter.py
│   ├── scorer.py
│   ├── clusterer.py
│   ├── family_detector.py
│   ├── keyword_extractor.py
│
├── rag/
│   ├── embedder.py
│   ├── indexer.py
│   ├── retriever.py
│   ├── summarizer.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── chroma/
│
├── reports/
│   ├── templates/
│   └── last_report.md
│
├── scripts/
│   ├── collect.py
│   ├── analyze.py
│   ├── report.py
│   ├── ingest.py (vide)
│   └── run_all.py (vide)
│
├── sources/
│   ├── feeds.json
│   ├── rules.json
│   └── sites.json
│
└── tests/
```

---

# 9. Exécution du pipeline

Étape 1 : collecte  

```bash
python3 -m scripts.collect
```

Étape 2 : analyse  

```bash
python3 -m scripts.analyze
```

Étape 3 : rapport  

```bash
python3 -m scripts.report
```

---

# 10. Limitations actuelles

- `ingest.py` est présent mais non utilisé.  
- `run_all.py` est vide.  
- Le RAG est utilisé uniquement dans `report.py`.  
- Pas d’embeddings dans le pipeline principal (embeddings présents dans `rag/` mais non utilisés dans `analyze.py`).

---

# 11. Améliorations possibles

- Intégration des embeddings dans `analyze.py`.  
- Utilisation de ChromaDB dans le pipeline principal.  
- Orchestration complète via `run_all.py`.  
- Interface Streamlit pour visualiser les clusters.  
- Détection automatique de familles d’objets (module existant mais non utilisé).

---

# 12. Licence

Projet open-source, réutilisable dans un cadre professionnel ou académique.