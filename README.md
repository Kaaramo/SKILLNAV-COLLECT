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

Ce dépôt contient **uniquement** le volet collecte de données du projet SKILLNAV :

* **3 468 fiches d'offres d'emploi Data/IA** (381 Maroc et 3 087 International), 100 % exploitables, organisées en pipeline 3 couches.
* **Tous les scripts de collecte** (Apify, Firecrawl, Playwright, restructure, enrichissement, audit qualité).

Les autres livrables du projet (modèles IA, base NoSQL hybride, dashboard Next.js, rapport méthodologique L5) sont dans des dépôts séparés.

---

## 2. Volumes et qualité

| Indicateur | Valeur |
|---|:-:|
| Total fiches | **3 468** |
| Maroc | 381 (100 % exploitables) |
| International | 3 087 (100 % exploitables) |
| Description longue ($\geq$ 200 caractères) | **100 %** |
| Sources Maroc | 6 |
| Sources International | 1 |
| Période publication couverte | 25 mois (août 2022 à mai 2026) |
| Familles métiers couvertes | 13 |

### Distribution par source

| Source | Pays | Postings | Outil de collecte |
|---|:-:|:-:|---|
| ANAPEC | MA | 2 | Playwright MCP |
| Rekrute | MA | 27 | Playwright MCP |
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
| **Apify** | LinkedIn MA, Indeed MA (recovery) | Anti-bot fort, actors managés pay-per-result, infrastructure rentable |
| **Firecrawl** | Glassdoor MA, Corpus Tech INTL | Pages JS-rendered, proxies intégrés, parser markdown propre |
| **Playwright** | ANAPEC, Rekrute | Interactions complexes (formulaires, pagination JS, login optionnel) |
| **JSON-LD + BeautifulSoup** | Pages carrières MA (TalentSoft, TeamTailor) | ATS modernes avec schema.org embedded, parsing déterministe |

> La justification approfondie de ces choix (avec arbre de décision, coûts, alternatives écartées) est dans la documentation projet complète, hors de ce dépôt.

---

## 5. Reproductibilité

### Prérequis

```bash
python --version   # 3.12 ou supérieur
pip install -r requirements.txt
npm install -g firecrawl-cli   # pour les scripts Firecrawl
```

### Variables d'environnement (`.env`)

```env
APIFY_TOKEN=apify_api_xxx       # depuis console.apify.com/account/integrations
# FIRECRAWL : CLI installé via npm, pas de clé API requise pour le mode local
```

### Scripts disponibles

| Script | Rôle |
|---|---|
| `sources/_restructure_ma_to_3_layers.py` | Convertit `postings/` vers `data_raw/{YYYY-MM}/` |
| `sources/_enrich_ma_structured.py` | Génère `data_structured/{YYYY-MM}/` via règles déterministes |
| `sources/_audit_ma_quality.py` | Audit qualité (taux descriptions exploitables par source) |
| `sources/_eliminate_incomplete_postings.py` | Élimine les postings < 200 chars et renumérote |
| `sources/indeed-ma/_apify_recover.py` | Recovery via Apify actor `misceres/indeed-scraper` |
| `sources/glassdoor-ma/_apify_recover.py` | Recovery via Apify actor `memo23/glassdoor-scraper-ppr` |
| `sources/glassdoor-ma/_firecrawl_recover.py` | Recovery via Firecrawl CLI direct |
| `sources/glassdoor-ma/_parse_glassdoor_to_postings.py` | Parse markdown Glassdoor vers `postings/` |
| `sources/intl-ai-corpus/_import_upstream.py` | Pipeline `data_raw` + `data_structured` vers `postings/` |
| `sources/intl-ai-corpus/_reorg_by_publication_month.py` | Réorganise les YAML par mois de publication |

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
| Données personnelles de candidat | **Aucune** : pas de noms, emails, téléphones, photos, profils LinkedIn personnels |
| Entités morales uniquement | Noms d'entreprise et descriptions publiques d'offres |
| User-Agent identifié | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | $\geq$ 5 secondes entre requêtes sur sources statiques |
| robots.txt | Vérifié pour chaque source avant collecte |
| Schéma JSON officiel | `sources/_schema/job_posting.schema.json` (Pydantic-compatible, validation stricte) |

---

## 7. Structure du dépôt

```text
SKILLNAV-COLLECT/
├── README.md                              (ce fichier)
├── .gitignore                              (exclusions Git, raw HTML/MD)
├── requirements.txt                        (dépendances Python minimales)
└── sources/
    ├── README.md                           (description du protocole de collecte)
    ├── COLLECTION_PROTOCOL.md              (protocole versionné v1.0)
    ├── BRIEFING_PROMPT.md                  (prompt prêt à coller pour scraping)
    ├── _schema/
    │   ├── job_posting.schema.json         (schéma JSON officiel SKILLNAV)
    │   └── posting.template.md             (template Markdown standardisé)
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

## 8. Note pour le jury

Ce volet collecte est un **livrable indépendant** qui satisfait l'exigence n°1 du sujet :

> « Scripts de Collecte : Code documenté pour le scraping et l'appel aux API. »

La qualité des données ici alimente directement les volets aval (base NoSQL hybride, pipeline IA, dashboard).

### Effort de récupération qualité documenté

Un audit qualité initial a révélé que 133 fiches sur 398 (33 %) côté Maroc avaient des descriptions vides ou trop courtes (moins de 200 caractères). Un pipeline de récupération a été exécuté :

* **Indeed MA** : 73 URLs re-scrapées via Apify `misceres/indeed-scraper` pour environ 0,02 USD. 61 fiches récupérées, 12 expirées définitivement.
* **Glassdoor MA** : 55 URLs re-scrapées via Firecrawl direct (free tier). 55 fiches récupérées avec descriptions complètes.
* **17 fiches définitivement éliminées** (12 Indeed expirées et 5 Rekrute trop courtes), traçabilité dans `sources/<source>/raw/_eliminated_incomplete.json`.

Bilan : passage de **265/398 (67 %)** à **381/381 (100 %)** fiches exploitables.

### Architecture inspirée de Built In

Le Corpus Tech INTL adopte une structure de scraping multi-villes (Los Angeles, New York, London, Amsterdam, Berlin, Inde) sur Q1 2026. Le pipeline 3 couches (raw, structured, postings) garantit la **traçabilité scientifique** exigée par le sujet (Data Quality Framework, point 3 des Spécifications Techniques).

---

**Mai 2026** · SKILLNAV · M242 ENSA-Tétouan · Pr. Imad Sassi · Karamo Sylla & Bachirou Konaté
