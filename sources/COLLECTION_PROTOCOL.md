# SKILLNAV — Protocole de collecte Data Science / IA

> Version 1.0 · 2026-05-14 · Karamo Sylla & Bachirou Konaté · ENSA-Tétouan

Ce document décrit la méthode utilisée pour constituer le corpus de 3 468 offres
d'emploi Data Science et Intelligence Artificielle qui alimente le projet SKILLNAV.
Il est rédigé pour qu'un tiers (étudiant, chercheur, jury) puisse reproduire la
collecte ou l'étendre à une nouvelle source sans information complémentaire.

---

## Sommaire

1. [Périmètre](#1-périmètre)
2. [Architecture 3 couches](#2-architecture-3-couches)
3. [Outils par type de source](#3-outils-par-type-de-source)
4. [Méthode hybride en 3 phases](#4-méthode-hybride-en-3-phases)
5. [Phasage par bloc d'années](#5-phasage-par-bloc-dannées)
6. [Schéma JSON officiel](#6-schéma-json-officiel)
7. [Détection des compétences](#7-détection-des-compétences)
8. [Mapping `job_family`](#8-mapping-job_family)
9. [Archive pré-2023](#9-archive-pré-2023)
10. [Quality gates](#10-quality-gates)
11. [Faux positifs à éliminer](#11-faux-positifs-à-éliminer)

---

## 1. Périmètre

### Métiers retenus

Data Analyst, Business Analyst, Data Scientist, Data Engineer, ML Engineer,
MLOps Engineer, AI Engineer, NLP Engineer, CV Engineer, Research Scientist,
Generative AI / LLM Engineer, Data Architect, Tech Lead Data, Quantitative
Engineer (si ML explicite).

### Métiers exclus

Full Stack Developer, Software Developer généraliste, DevOps Engineer (sans ML),
Consultant IT, Technicien Informatique, Web/Mobile Developer, Network Engineer,
Cybersecurity Analyst (sans data), Project Manager IT, FP&A Analyst, Support Analyst.

### Cas limites

| Titre | Décision |
|---|---|
| « Développeur IA / Machine Learning » | Inclure |
| « Analyste IT » | Exclure |
| « BI Analyst Power Platform » | Inclure si analytique prédictive mentionnée |
| « Architecte Cloud Data / Big Data » | Inclure (souvent MLOps / GenAI) |

### Géographie et période

* Maroc en priorité ; international en complément.
* Fenêtre temporelle : **2023-01-01 → 2026-05-14**.
  Le point d'ancrage est la sortie publique de ChatGPT en novembre 2022, qui
  marque l'inflexion grand public de l'IA générative. Toute fiche datée avant
  2023-01-01 part dans `archive_pre_2023/` (voir §9).

### RGPD

| Règle | Application |
|---|---|
| Aucune donnée personnelle de candidat | Pas de nom, email, téléphone, photo, profil LinkedIn personnel |
| Entités morales uniquement | Nom employeur (ou « Anonyme ») et descriptions publiques |
| User-Agent | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | ≥ 5 secondes entre requêtes |
| `robots.txt` | Vérifié pour chaque source avant collecte |

Chaque fiche extraite doit porter `"rgpd_compliant": true` et `"personal_data_stripped": true`.

---

## 2. Architecture 3 couches

```
<source-id>/
├── data_raw/{YYYY-MM}/<ref>_<co>_<title>.yaml         Couche 1 — texte brut
├── data_structured/{YYYY-MM}/<ref>_<co>_<title>.yaml  Couche 2 — enrichissement structuré
└── postings/NNN.{json,md}                             Couche 3 — pivot Pydantic
```

| Couche | Contenu | Source | Usage |
|---|---|---|---|
| `data_raw` | Texte brut, source de vérité textuelle | Extraction HTML / JSON-LD / markdown | NER, audit manuel |
| `data_structured` | Skills 10 dimensions, classification IA, niveau, contrat | Règles déterministes ou enrichissement structuré | Structure Mining, gap analysis |
| `postings` | Pivot Pydantic SKILLNAV | Fusion des deux couches précédentes | Ingestion DB, API, dashboard |

Les sous-dossiers `{YYYY-MM}/` représentent le **mois de publication** de l'offre,
pas la date de scraping. C'est ce qui permet de construire les séries temporelles
mensuelles utilisées en *Usage Mining*.

### Convention de naming des postings

* `001.json` à `999.json` numérotés par ordre de collecte (le plus récent en premier).
* Chaque `NNN.json` a toujours un `NNN.md` jumeau.
* `job_id` : `<source>-<YYYY>-<NNN>` où `YYYY` = année de publication.
  Exemples : `anapec-2026-001`, `rekrute-2025-026`, `linkedin-ma-2024-005`.

---

## 3. Outils par type de source

| Type de source | Outil retenu | Justification |
|---|---|---|
| Job board HTML statique | Playwright headless | Pagination JS, sélecteurs CSS stables |
| Site JS-heavy ou anti-bot Cloudflare | Firecrawl API | Bypass automatique, markdown propre en sortie |
| LinkedIn (auth wall) | Apify (`bebity/linkedin-jobs-scraper`) | Acteur officiel, sortie JSON structurée |
| Pages carrières (ATS modernes) | `requests` + BeautifulSoup + JSON-LD | Schema.org embedded, parsing déterministe |
| URLs expirées | Wayback Machine (`web.archive.org/web/<date>/<url>`) | Récupération de snapshots historiques |

L'arbre de décision implicite est : *si le HTML est statique → Playwright ; sinon
si JS lourd ou Cloudflare → Firecrawl ; sinon si LinkedIn → Apify*.

---

## 4. Méthode hybride en 3 phases

Validée empiriquement sur Rekrute (32 fiches Data/IA 2023-2026 collectées),
reproduite ensuite sur chaque nouvelle source.

### Phase 1 — Reconnaissance et listings actifs

Objectif : capturer toutes les offres actuellement actives sur la source.

1. Charger la page de recherche du site.
2. Inspecter le DOM pour identifier les sélecteurs et les patterns d'URL.
3. Lancer 4 à 6 requêtes clés :
   `data scientist`, `data engineer`, `data analyst`, `machine learning`,
   `ML engineer`, `AI engineer`.
4. Pour chaque résultat pertinent, naviguer sur la page détail et sauver le HTML brut.

Volume cible : **5 à 25 fiches** selon richesse de la source.

### Phase 2 — Historique via Google `site:`

Objectif : remonter aux fiches expirées mais dont les URLs restent valides
(la plupart des job boards conservent leurs URLs pendant plusieurs années).

1. **Découverte** : recherches Google ciblées par année.
   ```
   site:<domain> "data scientist" 2023
   site:<domain> "data scientist" 2024
   site:<domain> "data engineer" 2024 OR 2023
   site:<domain> "machine learning" engineer 2024 2025
   site:<domain> "data architect" 2024 2025
   ```
2. **Téléchargement** : `curl` direct si HTML statique, Firecrawl sinon.
   ```bash
   UA="Mozilla/5.0 ... SkillnavBot/1.0"
   curl -sL -A "$UA" --max-time 30 <url> -o raw/<id>.html
   ```
3. Respecter ≥ 5 s entre requêtes.

Volume cible : **10 à 50 fiches historiques** selon richesse de l'index Google.

### Phase 3 — Extraction Python et génération JSON+MD

Objectif : parser tous les HTML bruts pour produire les fichiers structurés.

Squelette type (à adapter au DOM de chaque source) :

```python
from datetime import datetime
from html.parser import HTMLParser

# 1. Parser HTML → texte
class TextExtractor(HTMLParser):
    ...

# 2. Extraire posted_date (chaque source a son format)
#    Rekrute   : "Publiée il y a N jours"
#    ANAPEC    : "Date : DD/MM/YYYY"
#    LinkedIn  : "Posted X days ago" / "Y weeks ago"
#    Indeed    : "Today" / "Yesterday" / "N days ago"

# 3. Filtrer par scope : posted_date >= 2023-01-01

# 4. Détecter compétences via regex (cf. §7).

# 5. Mapper job_family selon le titre (cf. §8).

# 6. Pour chaque fiche in-scope : générer NNN.json + NNN.md.
```

---

## 5. Phasage par bloc d'années

Plutôt que de scraper en bloc, le corpus a été construit en 4 vagues annuelles.
Cela évite de mélanger les époques et permet un suivi de progression simple.

```
Bloc 4 : 2026-01-01 → 2026-05-14   (Phase 1 en live)             ~15-30 fiches
Bloc 3 : 2025-01-01 → 2025-12-31   (Phase 2 Google + Phase 3)    ~20-50 fiches
Bloc 2 : 2024-01-01 → 2024-12-31   (Phase 2 Google + Phase 3)    ~20-40 fiches
Bloc 1 : 2023-01-01 → 2023-12-31   (Phase 2 Google + Phase 3)    ~10-30 fiches
```

L'ordre d'exécution conseillé est inverse du temps : commencer par Bloc 4
(données fraîches, valide la méthode sur la source) puis remonter vers Bloc 1
(URLs anciennes parfois retirées, plus difficile).

---

## 6. Schéma JSON officiel

Source de vérité : [`_schema/job_posting.schema.json`](_schema/job_posting.schema.json).

### Champs obligatoires

```json
{
  "job_id": "rekrute-2025-026",
  "source": "rekrute",
  "source_url": "https://...",
  "title": "Data Scientist H/F",
  "company": "Saham Bank",
  "location": "Casablanca",
  "country": "MA",
  "scraped_at": "2026-05-14T20:00:00Z",
  "scraper": "skillnav-curl-batch-v1.0",
  "rgpd_compliant": true,
  "personal_data_stripped": true
}
```

### Enums critiques

| Champ | Valeurs |
|---|---|
| `source` | `anapec`, `rekrute`, `linkedin-ma`, `indeed-ma`, `glassdoor-ma`, `pages-carrieres-ma`, `intl-ai-corpus`, ... |
| `job_family` | `DATA_ANALYST`, `BUSINESS_ANALYST`, `DATA_SCIENTIST`, `DATA_ENGINEER`, `ML_ENGINEER`, `MLOPS_ENGINEER`, `AI_ENGINEER`, `NLP_ENGINEER`, `CV_ENGINEER`, `RESEARCH_SCIENTIST`, `GENAI_LLM_ENGINEER`, `DATA_ARCHITECT`, `OTHER` |
| `domains_iaml` | `ML_CLASSIC`, `DEEP_LEARNING`, `NLP`, `COMPUTER_VISION`, `GENERATIVE_AI`, `REINFORCEMENT_LEARNING`, `TIME_SERIES`, `DATA_ENGINEERING`, `MLOPS`, `BUSINESS_INTELLIGENCE`, `BIG_DATA`, `CLOUD_DATA`, `RESEARCH` |
| `contract_type` | `CDI`, `CDD`, `Stage`, `Freelance`, `Alternance`, `Intérim`, `null` |
| `remote_policy` | `on-site`, `hybrid`, `remote`, `unknown` |
| `company_type` | `entité morale publique`, `entité morale privée`, `cabinet RH`, `anonyme`, `inconnu` |

Exemple complet, le plus richement renseigné du corpus :
[`rekrute/postings/016.json`](rekrute/postings/016.json) (Coface).

---

## 7. Détection des compétences

Patterns regex (insensibles à la casse) utilisés en Phase 3.

```python
SKILLS_PATTERNS = {
    "Python":          r"\bPython\b",
    "SQL":             r"\bSQL\b",
    "R":               r"\bR\b(?![a-zA-Z])",       # évite "Rabat" → "R"
    "Java":            r"\bJava\b",
    "Scala":           r"\bScala\b",
    "PySpark":         r"\bPySpark\b",
    "Spark":           r"\bSpark\b",
    "Hadoop":          r"\bHadoop\b",
    "Machine Learning": r"\bMachine Learning\b|\bapprentissage automatique\b",
    "Deep Learning":   r"\bDeep Learning\b|\bapprentissage profond\b",
    "NLP":             r"\bNLP\b|\bnatural language\b|\btraitement.{0,10}langage\b",
    "Computer Vision": r"\bcomputer vision\b|\bvision (par )?ordinateur\b",
    "TensorFlow":      r"\bTensorFlow\b",
    "PyTorch":         r"\bPyTorch\b",
    "Scikit-learn":    r"\bScikit[- ]?learn\b",
    "MLflow":          r"\bMLflow\b",
    "Databricks":      r"\bDatabricks\b",
    "Snowflake":       r"\bSnowflake\b",
    "BigQuery":        r"\bBigQuery\b",
    "PostgreSQL":      r"\bPostgreSQL\b",
    "MongoDB":         r"\bMongoDB\b",
    "Power BI":        r"\bPower\s*BI\b",
    "Tableau":         r"\bTableau\b(?!\sde)",      # évite "Tableau de bord"
    "Azure":           r"\bAzure\b",
    "AWS":             r"\bAWS\b",
    "GCP":             r"\bGCP\b|\bGoogle Cloud\b",
    "Docker":          r"\bDocker\b",
    "Kubernetes":      r"\bKubernetes\b|\bK8s\b",
    "Terraform":       r"\bTerraform\b",
    "Airflow":         r"\bAirflow\b",
    "Kafka":           r"\bKafka\b",
    "CI/CD":           r"\bCI/CD\b|\bGitHub Actions\b|\bAzure DevOps\b",
    "LLM":             r"\bLLMs?\b|\blarge language models?\b",
    "GenAI":           r"\bGenAI\b|\bGenerative AI\b",
    "MLOps":           r"\bMLOps\b",
    "SAS":             r"\bSAS\b",
}
```

La liste complète (50+ patterns) et l'implémentation de référence sont dans
les scripts de génération de chaque source.

---

## 8. Mapping `job_family`

Heuristique simple basée sur le titre. Si elle renvoie `OTHER`, vérifier
manuellement si la fiche est vraiment in-scope.

```python
def get_family(title: str) -> str:
    t = title.lower()
    if "machine learning" in t or "ml engineer" in t or "intelligence artificielle" in t:
        return "ML_ENGINEER"
    if "data scientist" in t:
        return "DATA_SCIENTIST"
    if "data engineer" in t:
        return "DATA_ENGINEER"
    if "data analyst" in t or "analyste data" in t:
        return "DATA_ANALYST"
    if "business analyst" in t:
        return "BUSINESS_ANALYST"
    if "architecte" in t or "tech lead" in t:
        return "DATA_ARCHITECT"
    if "mlops" in t:
        return "MLOPS_ENGINEER"
    if "nlp" in t:
        return "NLP_ENGINEER"
    if "computer vision" in t or "cv engineer" in t:
        return "CV_ENGINEER"
    if "llm" in t or "genai" in t or "generative ai" in t:
        return "GENAI_LLM_ENGINEER"
    if "research" in t and any(k in t for k in ("data", "ai", "ml")):
        return "RESEARCH_SCIENTIST"
    return "OTHER"
```

---

## 9. Archive pré-2023

Pour les fiches identifiées mais hors scope (date antérieure à 2023-01-01) :

```
<source-id>/archive_pre_2023/
├── INDEX.md          Récapitulatif manuel
└── <id>.html         HTML brut uniquement
```

On conserve le HTML brut sans le transformer en JSON / MD, pour deux raisons :
benchmark pré-ChatGPT si le scope est élargi un jour, et URLs souvent ré-dérivables
plus tard si nécessaire. Décision réversible.

Référence : [`rekrute/archive_pre_2023/INDEX.md`](rekrute/archive_pre_2023/INDEX.md).

---

## 10. Quality gates

Avant de considérer une fiche posting comme finalisée :

| Gate | Critère |
|---|---|
| `job_id` unique | Pas de duplicate dans la même source |
| `posted_date` valide | Format ISO `YYYY-MM-DD`, entre 2023-01-01 et aujourd'hui |
| `job_family != "OTHER"` | Sinon vérifier manuellement, archiver si hors scope |
| `skills_required` | Au moins une compétence détectée |
| `description` | ≥ 200 caractères |
| `rgpd_compliant: true` | Aucune donnée personnelle |
| `personal_data_stripped: true` | Vérifié à l'écriture |
| Markdown jumeau | `NNN.json` ↔ `NNN.md` toujours en paire |

### Validation finale par source

À la fin de la collecte d'une source :

1. `README.md` créé avec récap, justification, méthode.
2. `source.yaml` avec stats, URL patterns, conformité.
3. Tous les `.json` ont leur `.md` jumeau.
4. Tous les `raw/<id>.html` ont une fiche correspondante (sauf archive).

---

## 11. Faux positifs à éliminer

Le périmètre est strict Data Science / IA. Les titres suivants sont régulièrement
proposés par les sites mais hors scope :

* Full Stack Developer (avec IA mentionnée en simple « bonus »)
* Consultant IT généraliste (avec « appétences data »)
* Technicien Développement Informatique
* Project BOM Pilot (consolidation supply chain ≠ data science)
* Data Engineer Power Automate seul (Excel / VBA low-code, pas Big Data)
* FP&A Analyst (finance, pas data science)
* Support Analyst (support client)
* Genomics Scientist (bio-informatique pure)

### Pièges géographiques

* `emploitic.com` est un job board **algérien**, pas marocain.
  Vérifier systématiquement `country` et `location` sur chaque fiche.
