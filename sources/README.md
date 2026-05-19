# Sources — corpus collecté

Chaque dossier `<source>/` contient les offres Data Science / IA récupérées sur ce
site, organisées en architecture 3 couches (`data_raw`, `data_structured`, `postings`)
et validées contre [`_schema/job_posting.schema.json`](_schema/job_posting.schema.json).

Pour comprendre la méthode de collecte (phases, outils, critères qualité), lire
[`COLLECTION_PROTOCOL.md`](COLLECTION_PROTOCOL.md).

---

## Structure d'une source

```
<source-id>/
├── README.md                      Description du site, justification du choix
├── source.yaml                    Métadonnées (User-Agent, rate limit, dates de collecte)
├── data_raw/{YYYY-MM}/            Couche 1 : extraction brute (HTML→YAML)
├── data_structured/{YYYY-MM}/     Couche 2 : enrichissement structuré
├── postings/NNN.{json,md}         Couche 3 : pivot Pydantic (DB-ready)
└── raw/                           HTML/MD brut (gitignoré sauf .gitkeep)
```

`data_raw` et `data_structured` sont organisés par **mois de publication**
(champ `posted_date`), pas par date de scraping. Cela permet de construire
directement les séries temporelles utilisées par le volet *Usage Mining* du projet.

---

## Périmètre de collecte

* **Métiers** : Data Analyst, Business Analyst, Data Scientist, Data Engineer,
  ML Engineer, MLOps Engineer, AI Engineer, NLP Engineer, CV Engineer,
  Research Scientist, Generative AI / LLM Engineer, Data Architect.
* **Géographie** : Maroc en priorité, International en complément (benchmark).
* **Période** : 2023-01-01 → 2026-05-14.
  Point d'ancrage : sortie publique de ChatGPT (novembre 2022). Les fiches
  antérieures sont conservées en `archive_pre_2023/` mais hors corpus de travail.

---

## RGPD

| Règle | Application |
|---|---|
| Aucune donnée personnelle de candidat | Aucun nom, email, téléphone, photo, profil LinkedIn personnel n'est stocké |
| Entités morales uniquement | Nom employeur (ou "Anonyme") et descriptions publiques d'offres |
| User-Agent | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | ≥ 5 secondes entre requêtes sur les sources statiques |
| `robots.txt` | Vérifié pour chaque source avant la collecte |

Chaque fiche posting porte `"rgpd_compliant": true` et `"personal_data_stripped": true`.

---

## État de la collecte au 2026-05-16

### Maroc — 381 fiches

| Source | Postings | Outil principal | Notes |
|---|:-:|---|---|
| ANAPEC | 2 | Playwright | Échantillon (site faiblement indexé pour Data/IA) |
| Rekrute | 27 | Playwright | Collecte historique 2023-2026 ; 5 fiches éliminées (descriptions < 200 caractères) |
| Indeed MA | 67 | Playwright + Apify (recovery) | 12 URLs définitivement expirées |
| LinkedIn MA | 207 | Apify (8 runs, ~3,83 USD) | Plafond saturé |
| Pages carrières MA | 6 | Parse JSON-LD + BeautifulSoup | Crédit du Maroc, Stellantis |
| Glassdoor MA | 72 | Firecrawl + recovery | 100 % descriptions complètes après second passage |

### International — 3 087 fiches

| Source | Postings | Outil principal | Notes |
|---|:-:|---|---|
| Corpus Tech INTL | 3 087 | Firecrawl + JSON-LD | Q1 2026, 6 pays (US, IN, GB, DE, NL, autres) |

Total : **3 468 fiches Data/IA, 100 % avec description ≥ 200 caractères.**

---

## Pipeline de récupération (audit qualité 2026-05-16)

Un audit initial avait remonté 133 fiches Maroc (33 %) avec descriptions vides ou
trop courtes. Un second passage a été lancé :

* **Indeed MA** : 73 URLs re-scrapées via Apify (`misceres/indeed-scraper`, ~0,02 USD).
  61 fiches récupérées, 12 URLs expirées éliminées.
* **Glassdoor MA** : 55 URLs re-scrapées via Firecrawl (free tier).
  55 fiches récupérées avec descriptions complètes.
* **17 fiches définitivement supprimées** (12 Indeed expirées + 5 Rekrute trop courtes),
  traces dans `<source>/raw/_eliminated_incomplete.json`.

Bilan : passage de **265/398 (67 %)** à **381/381 (100 %)** fiches exploitables.

---

## Comparaison initiale Maroc ↔ International

Classification IA appliquée au corpus complet (`ai-first`, `ai-support`, `ml-first`,
`non-ai` selon la méthodologie du corpus upstream) :

| Type IA | INTL (3 087) | MA (398, avant cleanup) |
|---|:-:|:-:|
| `ai-first` | 73,2 % | 10 % |
| `ai-support` | 24,0 % | 0 % |
| `ml-first` | 2,1 % | 28 % |
| `non-ai` | 0,7 % | 62 % |

Le marché marocain reste dominé par le ML classique et l'analytique BI/Power
Platform. Aucune offre `ai-support` (typiquement Solutions Architect AI,
Customer Engineer AI) n'apparaît côté MA. Cet écart est précisément l'objet
de la mesure quantitative que mène le projet SKILLNAV.

---

## Liens internes

* [`COLLECTION_PROTOCOL.md`](COLLECTION_PROTOCOL.md) — protocole détaillé (méthode, phases, quality gates).
* [`_schema/job_posting.schema.json`](_schema/job_posting.schema.json) — schéma JSON officiel (Pydantic-compatible).
* [`_schema/posting.template.md`](_schema/posting.template.md) — gabarit Markdown standardisé.
* [`rekrute/`](rekrute/) — exemple complet, utilisable comme référence pédagogique.
