# SKILLNAV : Corpus de collecte Data Science & IA

> Volet **Collecte de données** du projet **SKILLNAV**
>
> Observatoire des compétences IA & Data Science par Web Mining.
>
> Module **M242 · Analyse de Web** · ENSA-Tétouan · Pr. Imad Sassi.
>
> Soutenance : 28 mai 2026.
>
> Auteurs : Karamo Sylla & Bachirou Konaté.

---

## Sommaire

1. [Contenu du dépôt](#1-contenu-du-dépôt)
2. [Volumes et qualité](#2-volumes-et-qualité)
3. [Architecture 3 couches](#3-architecture-3-couches)
4. [Outils de collecte](#4-outils-de-collecte)
5. [Reproductibilité](#5-reproductibilité)
6. [Conformité RGPD](#6-conformité-rgpd)
7. [Structure du dépôt](#7-structure-du-dépôt)
8. [Note pour le jury](#8-note-pour-le-jury)

---

## 1. Contenu du dépôt

Ce dépôt contient le volet collecte de données du projet SKILLNAV :

* **3 468 fiches d'offres d'emploi Data Science / IA** (381 Maroc, 3 087 International),
  100 % avec description ≥ 200 caractères, organisées selon l'architecture 3 couches
  (`data_raw`, `data_structured`, `postings`).
* **Les scripts utilisés** pour la collecte, l'enrichissement, le contrôle qualité
  et l'export (dossier `scripts/` à la racine, et scripts spécifiques par source
  dans `sources/<source>/`).

Les autres livrables du projet (modèles NER, base NoSQL hybride, pipelines d'analyse,
dashboard Next.js, rapport L5) sont dans des dépôts séparés.

---

## 2. Volumes et qualité

| Indicateur | Valeur |
|---|:-:|
| Total fiches | **3 468** |
| Maroc | 381 |
| International | 3 087 |
| Fiches avec description ≥ 200 caractères | **100 %** |
| Sources Maroc | 6 |
| Sources International | 1 (corpus multi-pays) |
| Période de publication couverte | 25 mois (août 2022 → mai 2026) |
| Familles métier représentées | 13 |

### Distribution par source

| Source | Pays | Postings | Outil de collecte |
|---|:-:|:-:|---|
| ANAPEC | MA | 2 | Playwright |
| Rekrute | MA | 27 | Playwright |
| Indeed MA | MA | 67 | Playwright + recovery Apify |
| LinkedIn MA | MA | 207 | Apify (8 runs, $3.83) |
| Pages carrières MA | MA | 6 | JSON-LD + BeautifulSoup |
| Glassdoor MA | MA | 72 | Firecrawl + recovery |
| Corpus Tech INTL | 6 pays | 3 087 | Firecrawl + parsing JSON-LD |
| **Total** | | **3 468** | |

---

## 3. Architecture 3 couches

Toutes les sources adoptent la même structure de stockage :

```text
sources/<source>/
├── data_raw/{YYYY-MM}/<id>_<co>_<title>.yaml         (Couche 1 : extraction brute)
├── data_structured/{YYYY-MM}/<id>_<co>_<title>.yaml  (Couche 2 : enrichissement LLM)
└── postings/NNN.{json,md}                            (Couche 3 : pivot Pydantic)
```

### Rôle de chaque couche

| Couche | Rôle | Origine | Cible d'utilisation |
|---|---|---|---|
| `data_raw` | Texte brut, source de vérité textuelle | Extraction HTML / JSON-LD | NER, audit manuel |
| `data_structured` | Analyse LLM (skills 10 dimensions, classification IA) | Enrichissement déterministe ou LLM | Études comparatives, Structure Mining |
| `postings` | Pivot Pydantic SKILLNAV (DB-ready) | Fusion raw + structured + inférence SKILLNAV | Ingestion MongoDB, API, dashboard |

### Comptage par source et par couche

| Source | data_raw | data_structured | postings |
|---|:-:|:-:|:-:|
| anapec | 2 | 2 | 2 |
| rekrute | 27 | 27 | 27 |
| indeed-ma | 67 | 67 | 67 |
| linkedin-ma | 207 | 207 | 207 |
| pages-carrieres-ma | 6 | 6 | 6 |
| glassdoor-ma | 72 | 72 | 72 |
| intl-ai-corpus | 3 089 | 3 086 | 3 087 |
| **Total** | **3 470** | **3 467** | **3 468** |

### Organisation temporelle

L'organisation `{YYYY-MM}/` reflète la date à laquelle l'offre a été **publiée** (champ `posted_date`), pas la date de scraping. Ce choix aligne le stockage avec l'**axe Usage Mining** du sujet (forecasting d'émergence des compétences sur une time-series mensuelle).

---

## 4. Outils de collecte

| Outil | Sources concernées | Justification du choix |
|---|---|---|
| **Apify** | LinkedIn MA, Indeed MA (recovery) | Anti-bot robuste, acteurs managés, sortie JSON structurée |
| **Firecrawl** | Glassdoor MA, Corpus Tech INTL | Pages JS-rendered, contournement Cloudflare, markdown propre en sortie |
| **Playwright headless** | ANAPEC, Rekrute | Pagination JS, sélecteurs CSS stables, interactions formulaire |
| **JSON-LD + BeautifulSoup** | Pages carrières MA (TalentSoft, TeamTailor) | ATS modernes embarquant schema.org, parsing déterministe |

L'arbre de décision implicite est documenté dans [`sources/COLLECTION_PROTOCOL.md §3`](sources/COLLECTION_PROTOCOL.md#3-outils-par-type-de-source).

---

## 5. Reproductibilité

### Prérequis

```bash
python --version   # 3.12 ou supérieur
pip install -r requirements.txt
```

### Variables d'environnement (`.env`)

```env
APIFY_TOKEN=apify_api_xxx          # console.apify.com/account/integrations
FIRECRAWL_API_KEY=fc-xxx           # firecrawl.dev/app/api-keys
```

### Scripts disponibles

Scripts transverses (à la racine de `sources/`) :

| Script | Rôle |
|---|---|
| `sources/_restructure_ma_to_3_layers.py` | Convertit `postings/` vers `data_raw/{YYYY-MM}/` |
| `sources/_enrich_ma_structured.py` | Génère `data_structured/{YYYY-MM}/` via règles déterministes |
| `sources/_audit_ma_quality.py` | Mesure le taux de descriptions exploitables par source |
| `sources/_eliminate_incomplete_postings.py` | Élimine les postings < 200 caractères et renumérote |

Scripts spécifiques aux sources (recovery, parsing, import) :

| Script | Rôle |
|---|---|
| `sources/indeed-ma/_apify_recover.py` | Re-scrape via Apify actor `misceres/indeed-scraper` |
| `sources/glassdoor-ma/_apify_recover.py` | Re-scrape via Apify actor `memo23/glassdoor-scraper-ppr` |
| `sources/glassdoor-ma/_firecrawl_recover.py` | Re-scrape via API Firecrawl |
| `sources/glassdoor-ma/_parse_glassdoor_to_postings.py` | Parse markdown Glassdoor vers `postings/` |
| `sources/intl-ai-corpus/_import_upstream.py` | Pipeline complet `data_raw` + `data_structured` → `postings/` |
| `sources/intl-ai-corpus/_reorg_by_publication_month.py` | Réorganise les YAML par mois de publication |

Templates reproductibles (dossier `scripts/`) :

| Script | Technique illustrée |
|---|---|
| `scripts/scrape_playwright_rekrute.py` | Playwright headless sur job board statique |
| `scripts/scrape_firecrawl_glassdoor.py` | API Firecrawl pour pages JS-rendered + Cloudflare |
| `scripts/scrape_apify_linkedin.py` | Apify acteur LinkedIn jobs |
| `scripts/scrape_jsonld_career_page.py` | Parse JSON-LD embarqué (TalentSoft, TeamTailor, Workday) |
| `scripts/scrape_wayback_archive.py` | Récupération via Wayback Machine pour URLs expirées |

### Exemples d'usage

Auditer la qualité globale du corpus :

```bash
python sources/_audit_ma_quality.py
```

Récupérer les fiches Indeed incomplètes via Apify :

```bash
python sources/indeed-ma/_apify_recover.py --smoke   # test sur 5 URLs
python sources/indeed-ma/_apify_recover.py           # run complet
```

Restructurer après ajout de nouvelles fiches `postings/` :

```bash
python sources/_restructure_ma_to_3_layers.py
python sources/_enrich_ma_structured.py
```

---

## 6. Conformité RGPD

| Règle | Application |
|---|---|
| Données personnelles de candidat | Aucune : pas de nom, email, téléphone, photo, profil LinkedIn personnel |
| Entités morales uniquement | Nom employeur et descriptions publiques d'offres |
| User-Agent | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | ≥ 5 secondes entre requêtes sur sources statiques |
| `robots.txt` | Vérifié pour chaque source avant collecte |
| Schéma JSON officiel | `sources/_schema/job_posting.schema.json` (Pydantic-compatible) |

---

## 7. Structure du dépôt

```text
SKILLNAV-DELIVERY/
├── README.md                              (ce fichier)
├── requirements.txt                       (dépendances Python)
├── data/                                  (exports consolidés)
│   ├── jobs.jsonl                         (corpus pivot, 3 467 lignes)
│   ├── graph_nodes.csv                    (export graphe Skill ↔ Skill)
│   └── graph_edges.csv
├── scripts/                               (templates Python par technique)
│   ├── scrape_playwright_rekrute.py
│   ├── scrape_firecrawl_glassdoor.py
│   ├── scrape_apify_linkedin.py
│   ├── scrape_jsonld_career_page.py
│   └── scrape_wayback_archive.py
└── sources/
    ├── README.md                          (récap par source + RGPD)
    ├── COLLECTION_PROTOCOL.md             (protocole détaillé v1.0)
    ├── _schema/
    │   ├── job_posting.schema.json        (schéma JSON officiel)
    │   └── posting.template.md            (gabarit Markdown)
    ├── _restructure_ma_to_3_layers.py
    ├── _enrich_ma_structured.py
    ├── _audit_ma_quality.py
    ├── _eliminate_incomplete_postings.py
    ├── anapec/
    ├── rekrute/
    ├── indeed-ma/
    ├── linkedin-ma/
    ├── pages-carrieres-ma/
    ├── glassdoor-ma/
    └── intl-ai-corpus/
```

---

## 8. Note méthodologique

Ce volet répond à l'exigence n°1 du sujet :

> « Scripts de Collecte : Code documenté pour le scraping et l'appel aux API. »

La qualité du corpus conditionne directement les volets aval (base NoSQL hybride,
pipelines NER / graphe / forecasting, dashboard).

### Effort de récupération qualité

L'audit qualité initial a relevé 133 fiches sur 398 (33 %) côté Maroc avec
descriptions vides ou trop courtes. Un second passage a été lancé :

* **Indeed MA** : 73 URLs re-scrapées via l'acteur Apify `misceres/indeed-scraper`
  (~0,02 USD). 61 fiches récupérées, 12 URLs expirées définitivement.
* **Glassdoor MA** : 55 URLs re-scrapées via Firecrawl (free tier).
  55 fiches récupérées avec descriptions complètes.
* **17 fiches définitivement éliminées** (12 Indeed expirées + 5 Rekrute < 200 caractères),
  traces dans `sources/<source>/raw/_eliminated_incomplete.json`.

Bilan : passage de 265/398 (67 %) à 381/381 (100 %) fiches exploitables côté Maroc.

### Corpus International

Le `intl-ai-corpus` regroupe des offres collectées sur Q1 2026 dans six pays
(US, IN, GB, DE, NL, autres), avec un focus AI Engineer. Le pipeline 3 couches
identique aux sources Maroc garantit que les deux marchés peuvent être analysés
avec les mêmes outils.

---

**Mai 2026 · ENSA-Tétouan · Karamo Sylla & Bachirou Konaté**
