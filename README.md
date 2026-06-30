# TREND-SENTINELLE  

## Système de veille automatisée, détection d’objets et synthèse IA locale

TREND‑SENTINELLE est un pipeline de veille automatisée conçu pour détecter des objets, signaux faibles et tendances émergentes à partir de flux d’informations technologiques.  
L’architecture est hybride :  
- la **collecte** peut s’appuyer sur des flux externes (RSS, Atom, HTML) et nécessite alors une connexion Internet ;  
- toute la **chaîne d’analyse IA** (normalisation, filtrage, scoring, clustering, RAG local, génération du rapport) fonctionne **entièrement hors‑ligne**.

Le système transforme des contenus hétérogènes en objets structurés, scorés, regroupés en clusters, puis synthétisés via une IA locale.

### Phases du pipeline

**A. Collecte des sources externes (mode connecté ou local)**  
- RSS, Atom, HTML statique  
- Normalisation des contenus  
- Extraction des objets et métadonnées  

**B. Analyse locale hors‑ligne**  
- Filtrage des objets  
- Scoring multi‑facteurs  
- Clustering thématique  
- Détection de familles d’objets  
- Synthèse IA locale (RAG)

Ce README documente l’architecture réelle du projet, son pipeline exact et les modules effectivement utilisés.

---

## . Contexte & Problématique

Le projet TREND‑SENTINELLE part d’un constat métier : en 2026, il devient extrêmement difficile d’anticiper les futurs objets à commercialiser en se basant uniquement sur le scraping frontal de sites web.  
Les plateformes renforcent leurs protections, les contenus sont dynamiques, et les signaux réellement intéressants apparaissent bien avant que les produits ne soient listés sur les marketplaces.

Pour répondre à cette problématique, nous avons adopté une approche plus **transversale** :  
plutôt que de scraper des pages produits, TREND‑SENTINELLE analyse des **flux d’informations technologiques**, détecte des **objets émergents**, identifie des **signaux faibles**, regroupe les contenus en **clusters thématiques**, puis génère une **synthèse IA locale** permettant d’entrevoir les tendances à venir.

Cette approche permet de repérer des objets avant leur apparition commerciale, en s’appuyant sur des signaux précurseurs plutôt que sur des listings produits.

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

## 12. Exemple de sortie du pipeline (anonymisé)

TREND‑SENTINELLE a analysé **142 items** provenant de plusieurs sources technologiques.  
Après filtrage, **37 objets** ont été retenus et regroupés en **6 clusters**.  
Ce tableau est un exemple anonymisé, représentatif du fonctionnement réel du pipeline.

---

### Top 5 objets détectés (exemple anonymisé)

#### 1. Assistant vocal embarqué pour seniors  
- Score : **0.92**  
- Cluster : Autonomie & Assistance  
- Résumé : assistant vocal embarqué permettant de déclencher des actions sans connexion internet.  
- Analyse IA : tendance forte vers des interfaces vocales locales pour l’autonomie des personnes âgées.

#### 2. Capteur de chute autonome  
- Score : **0.89**  
- Cluster : Sécurité & Détection  
- Résumé : capteur embarqué détectant les chutes sans transmission cloud.  
- Analyse IA : montée des dispositifs de sécurité autonomes, embarqués et respectueux de la vie privée.

#### 3. Module de navigation intérieure  
- Score : **0.87**  
- Cluster : Mobilité & Indoor  
- Résumé : navigation en intérieur sans GPS via capteurs inertiels.  
- Analyse IA : forte tendance dans les bâtiments publics, hôpitaux et centres commerciaux.

#### 4. Outil de transcription hors‑ligne  
- Score : **0.84**  
- Cluster : Productivité Locale  
- Résumé : transcription audio locale garantissant la confidentialité.  
- Analyse IA : demande croissante pour des outils souverains et hors‑ligne.

#### 5. Micro‑service de synchronisation locale  
- Score : **0.81**  
- Cluster : Infrastructure Locale  
- Résumé : synchronisation de données entre appareils sans serveur central.  
- Analyse IA : tendance vers des architectures distribuées locales pour réduire les dépendances externes.

---

### Synthèse des clusters détectés

- Autonomie & Assistance  
- Sécurité & Détection  
- Mobilité & Indoor  
- Productivité Locale  
- Infrastructure Locale  
- Habitat & Monitoring  

Ce tableau est un exemple anonymisé, représentatif du fonctionnement réel du pipeline TREND‑SENTINELLE.

# 13. Licence

Projet open-source, réutilisable dans un cadre professionnel ou académique.
