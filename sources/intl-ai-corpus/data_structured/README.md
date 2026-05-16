# `data_structured/` — enrichissement LLM par mois de publication

Couche 2 du stockage 3-couches. Chaque YAML correspond à **une offre d'emploi** déjà passée à un LLM (Z.ai GLM-4.7 chez l'auteur upstream) qui a transformé le texte brut en données analytiques structurées et catégorisées.

---

## Pourquoi cette couche existe ?

Le fichier `data_raw/{YYYY-MM}/<fiche>.yaml` contient **tout le texte de l'offre** (description complète, parfois 10 à 30 000 caractères), mais sa liste de compétences est très pauvre — 3 à 7 outils détectés via le widget Built In. Inutilisable pour des analyses statistiques.

**La vraie matière** est noyée dans la description : « We use Kubernetes for orchestration, MLflow for experiment tracking, Pinecone as vector store, FastAPI for serving… ». Un humain le voit, un script de stats ne le voit pas.

L'enrichissement LLM règle ce problème : on envoie chaque description au modèle qui en extrait des champs **propres, normalisés, analysables**. C'est cette couche qui permet de répondre à des questions comme :

- Quelle proportion d'AI Engineers utilise un vector store ?
- Quels skills cooccurrent avec LangChain ?
- Les rôles ai-support mentionnent-ils plus de cloud que les ai-first ?
- Combien de fiches mentionnent du fine-tuning vs du RAG ?

---

## Vision derrière ce choix

Le projet SKILLNAV s'inscrit dans un mémoire académique de **Web Mining** (M242 — ENSA-Tétouan). Le sujet impose une analyse rigoureuse en 3 axes : Content Mining, Structure Mining, Usage Mining.

Cette couche `data_structured/` alimente directement deux axes :

1. **Content Mining** — les skills classés en 10 dimensions servent de baseline pour évaluer notre propre NER (BERT-multi vs CamemBERT-NER vs DistilBERT) dans l'étude comparative §N2 du PRD.
2. **Structure Mining** — les 10 dimensions de skills + la classification IA permettent de construire un graphe Skill ↔ Job dense pour Neo4j (PageRank, communautés Louvain).

Sans cette couche structurée, le projet resterait bloqué au stade descriptif. Avec elle, on peut faire de la **science**.

---

## Champs présents dans chaque YAML

### `company`
- `name` — nom de l'entreprise (entité morale)
- `stage` — stade de maturité (Startup / Series A-B / Public)
- `focus` — courte description de l'activité

### `position`
- `title` — intitulé du poste
- `ai_type` — classification du rôle face à l'IA :
  - `type` parmi `ai-first` (construit l'IA), `ai-support` (gravite autour), `ml-first` (ML classique), `non-ai` (pas d'IA)
  - `reasoning` — phrase explicative justifiant la classification
- `responsibilities` — liste des missions principales extraites de la description
- `use_cases` — liste des cas d'usage business mentionnés (RAG, chatbot, forecasting…)
- `skills` — compétences réparties en **10 dimensions** :
  - `genai` — RAG, LangChain, prompt engineering, LLM, agents, fine-tuning
  - `ml` — PyTorch, TensorFlow, scikit-learn, deep learning, transformers
  - `web` — REST API, FastAPI, React, Next.js, GraphQL
  - `databases` — PostgreSQL, MongoDB, BigQuery, Snowflake
  - `data` — Spark, Airflow, dbt, Kafka, ETL, pandas
  - `cloud` — AWS, Azure, GCP, Sagemaker, Vertex AI
  - `ops` — Docker, Kubernetes, MLflow, CI/CD, Terraform
  - `languages` — Python, JavaScript, TypeScript, Java, Go
  - `domains` — NLP, Computer Vision, Time Series, Healthcare, Finance
  - `other` — Statistics, A/B testing, Solutions architecture
- `is_customer_facing` — booléen, indique si le rôle est en contact client
- `is_management` — booléen, indique si c'est un poste à responsabilités

### `meta`
- `job_id` — identifiant source-natif
- `extracted_at` — horodatage de l'extraction LLM

---

## Stockage par mois de publication

L'organisation `{YYYY-MM}/` reflète la date à laquelle l'offre a été **publiée** par l'entreprise (champ `posted_date` du data_raw), pas la date à laquelle elle a été scrapée. Ce choix aligne le stockage avec l'**axe Usage Mining** : forecasting de l'émergence des compétences sur une time-series mensuelle.

| Mois | Fiches |
|---|:-:|
| 2025-08 | 2 |
| 2025-11 | 2 |
| 2026-01 | 709 |
| 2026-02 | 1 055 |
| 2026-03 | 721 |
| 2026-04 | 597 |
| **Total** | **3 086** |

> Note : 1 fichier de moins que `data_raw/` (3 089 vs 3 086) car certains YAML upstream étaient mal formés et n'ont pas pu passer l'enrichissement LLM.

---

## Format de nommage

Identique à `data_raw/` pour garantir le pairage par filename :
`{job_id}_{company}_{title}.yaml`.

Le script `_import_upstream.py` exploite ce pairage : il lit le YAML structured et son équivalent raw pour produire le posting Pydantic final dans `postings/NNNN.json`.
