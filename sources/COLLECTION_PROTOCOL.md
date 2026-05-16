# SKILLNAV — Protocole de Collecte Data/IA — v1.0

> **Norme officielle** pour scraper les offres d'emploi Data Science / IA sur les sources marocaines + internationales du registre SKILLNAV.
>
> Toute session Claude Code lancée pour étendre la collecte **doit suivre ce protocole**.
>
> **Version** : 1.0 · **Date** : 2026-05-14 · **Auteur** : Karamo Sylla · **Statut** : binding

---

## 0. À lire AVANT d'agir (ordre obligatoire)

| Ordre | Fichier | Pourquoi |
|:-:|---|---|
| 1 | [`CLAUDE.md`](../../CLAUDE.md) | Consignes globales projet · RGPD · stack · conventions |
| 2 | [`docs/PRD_CONDENSE.md`](../../docs/PRD_CONDENSE.md) | Vision SKILLNAV en ASCII + schémas |
| 3 | [`sources/collected/README.md`](README.md) | Statut actuel de la collecte par source |
| 4 | Ce fichier (`COLLECTION_PROTOCOL.md`) | Protocole opérationnel |
| 5 | [`sources/collected/_schema/job_posting.schema.json`](_schema/job_posting.schema.json) | Schéma JSON officiel (Pydantic-compatible) |
| 6 | [`sources/collected/_schema/posting.template.md`](_schema/posting.template.md) | Template Markdown standardisé |
| 7 | [`sources/collected/rekrute/`](rekrute/) | Exemple complet (32 fiches, méthode hybride 3 phases) |
| 8 | [`sources/scraping_map/sources.json`](../scraping_map/sources.json) | Registre des sources à attaquer (tier, URL, MCP tool) |

---

## 1. Scope inviolable

### Périmètre métiers — STRICT Data Science + Intelligence Artificielle

✅ **Inclure** : Data Analyst · Business Analyst · Business Intelligence Analyst · Data Scientist · Data Engineer · ML Engineer · MLOps Engineer · AI Engineer · NLP Engineer · CV Engineer · Generative AI Engineer · LLM Engineer · Data Architect · Tech Lead Data · Research Scientist (Data) · Quantitative Engineer (avec ML)

❌ **Exclure** : Full Stack Developer, Software Developer, DevOps Engineer (sans ML), Consultant IT généraliste, Technicien Informatique, Web Developer, Mobile Developer, Network Engineer, Cybersecurity Analyst (sans data), Project Manager IT, FP&A Analyst, Support Analyst

🟡 **Cas borderline (à juger)** :
- "Developpeur IA / Machine Learning Engineer" → ✅ inclure (IA explicite)
- "Analyste IT" → ❌ exclure (pas Data spécifique)
- "BI Analyst Power Platform" → ✅ inclure si AI predictive mentionné
- "Architecte Cloud Data/Big Data" → ✅ inclure (ML/MLOps/GenAI/LLMs)

### Périmètre géographique

- **Priorité 1** : Maroc 🇲🇦
- **Priorité 2** : International (LinkedIn, builtin, WTTJ, Otta, AI labs) — pour le benchmark

### Période d'observation : **2023-01-01 → 2026-05-14** (≈ aujourd'hui)

> Période ancrée sur la sortie de ChatGPT (nov. 2022, démocratisation IA générative).
> Tout posting avec `posted_date < 2023-01-01` → archive séparée (voir §10).

### RGPD inviolable (CLAUDE.md §N4)

| Règle | Application |
|---|---|
| **Aucune donnée personnelle de candidat** | nom, email, téléphone, photo, profil LinkedIn personnel → **jamais stockés** |
| Entité morale uniquement | nom employeur (ou "Anonyme" / "Confidentiel") + descriptions publiques |
| User-Agent identifié | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | ≥ **5 s** entre requêtes sur sources statiques |
| robots.txt | vérifié + respecté · log de compliance |

Toute fiche extraite **DOIT** avoir `"rgpd_compliant": true` et `"personal_data_stripped": true`.

---

## 2. Structure de dossier — STANDARD INVIOLABLE

Pour chaque nouvelle source `<source-id>` (e.g. `indeed-ma`, `linkedin-ma`, `glassdoor-ma`, `um6p-aim`, `builtin`, `wttj`) :

```
sources/collected/<source-id>/
├── README.md                  # Description source + justification tier + méthode
├── source.yaml                # Métadonnées scraping (URL patterns, conformité, stats)
├── postings/
│   ├── 001.json               # Schéma JobPosting Pydantic-compatible
│   ├── 001.md                 # Vue Markdown lisible
│   ├── 002.json
│   ├── 002.md
│   └── ...
├── raw/                       # HTML/PDF brut (gitignored sauf .gitkeep)
│   ├── .gitkeep
│   └── <id>.html
└── archive_pre_2023/          # OPTIONNEL — fiches hors scope mais conservées
    ├── INDEX.md
    └── <id>.html
```

### Convention de naming des postings

- `001.json` à `999.json` — numérotation **par ordre de collecte** (chronologie inverse, plus récent = 001)
- `001.md` doit toujours exister à côté de `001.json` (paire indissociable)

### `job_id` dans chaque JSON

Format : `<source>-<YYYY>-<NNN>` où `YYYY` = année de publication, `NNN` = numéro posting.

Exemples valides :
- `anapec-2026-001`
- `rekrute-2025-026`
- `linkedin-ma-2024-005`

---

## 3. Boîte à outils MCP — Tout l'arsenal disponible

> **Règle d'or** : utiliser **tous les moyens** à disposition. Choisir l'outil le plus adapté à la source.

### Inventaire des MCPs scraping

| Outil | Quand l'utiliser | Avantages | Limites |
|---|---|---|---|
| **Firecrawl MCP** ⭐ | Sites avec **JS dynamique** + PDFs + sites avec rate limit géré · scraping batch + extraction structurée IA-native | API managée · markdown propre · gère Cloudflare et anti-bot · supporte PDF · `firecrawl_scrape` / `firecrawl_crawl` / `firecrawl_map` / `firecrawl_search` | Quota mensuel · clé API requise (`FIRECRAWL_API_KEY`) |
| **Playwright MCP** | Sites **JS heavy** + besoin d'interactions (clics, scrolls, formulaires) + Cloudshield challenge automatique | Vrai navigateur Chromium · contourne anti-bot · DOM exploration interactive via `browser_evaluate` | Lent (~5-10s/page) · pas de batch · 1 onglet à la fois |
| **curl + Python regex** | Sites **HTML statique** + URLs connues (post Phase 2 Google) + besoin scraping ultra-rapide à grande échelle | Très rapide · pas de quota · parallélisable · adapté au batch de centaines d'URLs | Aucun support JS · faux UA si anti-bot · regex fragiles |
| **WebFetch (Claude)** | Single page · fetch one-off + summarization automatique LLM | Pas besoin de parser HTML soi-même · auto-résumé pertinent | Bloque sur certains sites (anti-bot, SSL self-signed) · pas de batch |
| **Apify MCP** | **LinkedIn** spécifiquement · sites où Firecrawl/Playwright échouent | Actor `linkedin-jobs-scraper` officiel · sortie structurée JSON | Payant ($5-10/run) · plafond ~200 fiches/session · token requis |
| **Context7 MCP** | Docs de librairie (pas pertinent pour scraping mais utile pour debug code Python) | Docs à jour | Hors scope scraping direct |

### Recommandation par type de source

```
┌─────────────────────────────────────────────────────────────┐
│  Job board statique (Rekrute, Bayt, Talents.ma)             │
│     → Phase 1 Playwright (interaction) + Phase 2 curl       │
│                                                             │
│  Job board JS-heavy (EmploiTIC, WTTJ, builtin)              │
│     → Firecrawl scrape ⭐ (markdown propre) ou Playwright    │
│                                                             │
│  Site avec Cloudflare (ENSAF découvert)                     │
│     → Firecrawl ⭐ (gère automatique) ou Playwright          │
│                                                             │
│  Site avec PDFs (brochures ENSA, plaquettes)                │
│     → Firecrawl scrape format=pdf ⭐                          │
│                                                             │
│  LinkedIn (auth wall)                                       │
│     → Apify actor linkedin-jobs-scraper                     │
│                                                             │
│  ANAPEC, agences gouvernementales (HTML legacy)             │
│     → curl + Python regex (rapide + suffisant)              │
└─────────────────────────────────────────────────────────────┘
```

### Firecrawl MCP — Commandes clés

Le plugin Firecrawl est déjà installé (cf. `~/.claude/plugins/cache/firecrawl/`). Outils disponibles :

| Outil MCP | Usage type |
|---|---|
| `mcp__plugin_firecrawl_firecrawl__firecrawl-scrape` | Scraper une URL → markdown propre |
| `mcp__plugin_firecrawl_firecrawl__firecrawl-crawl` | Crawler un site entier (avec dépth) |
| `mcp__plugin_firecrawl_firecrawl__firecrawl-map` | Lister toutes les URLs d'un domaine |
| `mcp__plugin_firecrawl_firecrawl__firecrawl-search` | Recherche web + scraping en une étape |
| `mcp__plugin_firecrawl_firecrawl__firecrawl-extract` | Extraction structurée via LLM (schema-based) |
| `mcp__plugin_firecrawl_firecrawl__firecrawl-instruct` | Skill agentique : décrit le but, Firecrawl orchestre |

⚠️ Ces outils sont **deferred** dans Claude Code — ils doivent être chargés via `ToolSearch` avant utilisation :
```
ToolSearch query="select:mcp__plugin_firecrawl_firecrawl__firecrawl-scrape,mcp__plugin_firecrawl_firecrawl__firecrawl-map"
```

---

## 4. Méthode hybride — 3 phases obligatoires (NORME)

> Validée empiriquement sur Rekrute (32 fiches 2023-2026 collectées). À reproduire sur chaque nouvelle source.

### PHASE 1 — Reconnaissance & Listings actifs (Playwright MCP ou Firecrawl MCP)

Objectif : capturer toutes les offres **actuellement actives** sur la source.

**Option A — Playwright MCP** (interaction riche, anti-bot challenges)

```text
1. mcp__plugin_playwright_playwright__browser_navigate → page d'accueil ou search
2. mcp__plugin_playwright_playwright__browser_evaluate → extraire la structure DOM
   (sélecteurs CSS, formulaire de recherche, URL patterns, anti-bot ?)
3. Identifier URL search & URL détail
4. Lancer 4-6 queries clés
5. Pour chaque résultat pertinent → navigate sur détail + extract content
6. Sauver raw HTML dans raw/<id>.html
```

**Option B — Firecrawl MCP** ⭐ (rapide, gère JS + Cloudflare automatique)

```text
1. ToolSearch select:mcp__plugin_firecrawl_firecrawl__firecrawl-map → lister toutes URLs
2. ToolSearch select:mcp__plugin_firecrawl_firecrawl__firecrawl-scrape → scraper chaque URL
   → reçoit du markdown propre + metadata structurées
3. Sauver markdown dans raw/<id>.md (au lieu de .html)
```

**Quand choisir** :
- Site JS lourd, Cloudflare, ou structure inconnue → Firecrawl ⭐
- Site qui nécessite click/scroll/form fill → Playwright
- Site HTML statique simple → curl + Python regex direct

Queries clés (toutes options) :
- "data scientist"
- "data engineer"
- "data analyst"
- "machine learning"
- "ML engineer" / "AI engineer"
- "business intelligence" (BI hybride)

Volume cible Phase 1 : **5-25 fiches** selon richesse de la source.

### PHASE 2 — Historique via Google `site:<source>` (WebSearch + curl OU Firecrawl)

Objectif : remonter aux fiches **expirées mais URLs toujours valides** (la plupart des job boards conservent leurs URLs des années).

**Étape 2a — Découverte d'URLs (WebSearch)**

```text
1. WebSearch site:<domain> "data scientist" 2023
2. WebSearch site:<domain> "data scientist" 2024
3. WebSearch site:<domain> "data scientist" 2025
4. WebSearch site:<domain> "data engineer" 2024 OR 2023
5. WebSearch site:<domain> "data analyst" 2023
6. WebSearch site:<domain> "machine learning" engineer 2024 2025
7. WebSearch site:<domain> "data architect" 2024 2025
```

**Étape 2b — Téléchargement de chaque URL** (deux options)

**Option A — curl direct** (rapide, HTML statique)

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# Pour chaque URL :
curl -sL -A "$UA" --max-time 15 -o /dev/null -w "%{http_code}" <url>  # check HTTP 200
curl -sL -A "$UA" --max-time 30 <url> -o raw/<id>.html               # télécharger
```

**Option B — Firecrawl MCP** ⭐ (recommandé si le site bloque curl/UA)

```text
mcp__plugin_firecrawl_firecrawl__firecrawl-scrape url=<url> formats=markdown
   → retourne markdown propre + metadata (auteur, date publication, OG tags)
   → sauver dans raw/<id>.md
```

**Quand choisir** :
- Si curl HTTP 200 + HTML lisible → curl ⭐ (rapide, gratuit)
- Si curl bloqué / Cloudflare / contenu JS-rendered → Firecrawl ⭐
- Si beaucoup d'URLs (50+) → curl en batch puis Firecrawl pour échecs

Rate limit : ≥ **5 s** entre requêtes (Karamo a 5s minimum dans `SCRAPER_RATE_LIMIT_SECONDS`).

Volume cible Phase 2 : **10-50 fiches historiques** selon richesse de l'index Google.

### PHASE 3 — Extraction Python + Génération JSON+MD

Objectif : parser tous les HTML bruts → produire les fichiers structurés.

Script type (à adapter au DOM de la source) :

```python
import os, re, json
from html.parser import HTMLParser
from datetime import datetime, timedelta

# 1. Parser HTML → texte
class TE(HTMLParser): ...

# 2. Extraire date publication (chaque source a son format)
#    Rekrute : "Publiée il y a N jours"
#    ANAPEC : "Date : DD/MM/YYYY"
#    LinkedIn : "Posted X days ago" / "Y weeks ago"
#    Indeed : "Today" / "Yesterday" / "N days ago"

# 3. Filtrer par scope : posted_date >= 2023-01-01

# 4. Détecter compétences via regex (cf. SKILLS_PATTERNS dans rekrute/_generate_postings.py)

# 5. Mapper job_family selon titre (enum dans le schéma JSON)

# 6. Pour chaque fiche in-scope : générer NNN.json + NNN.md
```

**Code de référence** : [`sources/collected/rekrute/_generate_postings.py`](rekrute/_generate_postings.py) (gitignored après usage, mais référence solide).

---

## 4. Stratégie de phasage par année (NOUVELLE NORME)

> Demandée par Karamo le 2026-05-14 : organiser la collecte par **blocs d'années** pour éviter de tout mélanger.

### Découpage temporel recommandé

```
┌──────────────────────────────────────────────────────────────────┐
│  BLOC 4 : 2026-01-01 → 2026-05-14  (actuel · 4-5 mois)           │
│           Méthode : Phase 1 Playwright live                       │
│           Cible volume : 15-30 fiches                             │
├──────────────────────────────────────────────────────────────────┤
│  BLOC 3 : 2025-01-01 → 2025-12-31  (année pleine)                │
│           Méthode : Phase 2 Google + Phase 3 Python              │
│           Cible volume : 20-50 fiches                             │
├──────────────────────────────────────────────────────────────────┤
│  BLOC 2 : 2024-01-01 → 2024-12-31  (année pleine)                │
│           Méthode : Phase 2 Google + Phase 3 Python              │
│           Cible volume : 20-40 fiches                             │
├──────────────────────────────────────────────────────────────────┤
│  BLOC 1 : 2023-01-01 → 2023-12-31  (année pleine post-ChatGPT)   │
│           Méthode : Phase 2 Google + Phase 3 Python              │
│           Cible volume : 10-30 fiches                             │
└──────────────────────────────────────────────────────────────────┘
```

### Ordre d'exécution conseillé

1. **D'abord BLOC 4 (2026)** — facile, données live, valide la méthode sur la source
2. **Puis BLOC 3 (2025)** — Google search ciblé `site:domain "data" 2025`
3. **Puis BLOC 2 (2024)** — idem
4. **Enfin BLOC 1 (2023)** — souvent le plus difficile (URLs anciennes parfois retirées)

### Rationale du phasage

- **Évite la surcharge cognitive** : 4 blocs de 20 fiches = plus gérable que 1 bloc de 80 fiches
- **Permet le suivi de progression** : `source.yaml` documente `bloc_4_done: true` etc.
- **Permet la parallélisation** : plusieurs sessions Claude Code peuvent attaquer différents blocs d'une même source si conflit Git évité (cf. §11)

---

## 5. Source IDs disponibles (registre)

Le registre officiel est dans [`sources/scraping_map/sources.json`](../scraping_map/sources.json).

### Sources T1 (Indispensables) — 8 cibles

| Source ID | Nom | URL | MCP Tool | Statut actuel |
|---|---|---|---|---|
| `anapec` | ANAPEC | https://www.anapec.org/ | firecrawl | ✅ 2 fiches |
| `rekrute` | Rekrute | https://www.rekrute.com/ | crawl4ai | ✅ 32 fiches |
| `indeed-ma` | Indeed Maroc | https://ma.indeed.com/ | firecrawl | ⚪ À faire |
| `linkedin-ma` | LinkedIn Jobs Maroc | https://ma.linkedin.com/jobs/jobs-in-morocco | apify | ⚪ À faire |
| `linkedin-cas` | LinkedIn Jobs Casablanca | https://ma.linkedin.com/jobs/jobs-in-casablanca | apify | ⚪ À faire |
| `glassdoor-ma` | Glassdoor Maroc | https://www.glassdoor.com/Job/morocco-data-scientist-jobs.htm | apify | ⚪ À faire |
| `um6p-aim` | UM6P Ai Movement | https://aim.um6p.ma/en/job-offers/ | firecrawl | ⚪ À faire |

### Sources T2 (Stratégiques) — voir registre complet

Tous les sources T2-T4 dans [`sources/scraping_map/sources.json`](../scraping_map/sources.json).

---

## 6. Schéma JSON officiel (Pydantic-compatible)

Source de vérité : [`sources/collected/_schema/job_posting.schema.json`](_schema/job_posting.schema.json)

### Champs OBLIGATOIRES

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

### Champs ENUMS critiques

#### `source` (liste évolutive)
`"anapec" | "rekrute" | "linkedin-ma" | "linkedin-cas" | "indeed-ma" | "glassdoor-ma" | "um6p-aim" | "builtin" | "wttj" | "otta" | "wellfound" | "aijobs-net" | ...`

#### `job_family`
`"DATA_ANALYST" | "BUSINESS_ANALYST" | "DATA_SCIENTIST" | "DATA_ENGINEER" | "ML_ENGINEER" | "MLOPS_ENGINEER" | "AI_ENGINEER" | "NLP_ENGINEER" | "CV_ENGINEER" | "RESEARCH_SCIENTIST" | "GENAI_LLM_ENGINEER" | "DATA_ARCHITECT" | "OTHER"`

#### `domains_iaml`
`"ML_CLASSIC" | "DEEP_LEARNING" | "NLP" | "COMPUTER_VISION" | "GENERATIVE_AI" | "REINFORCEMENT_LEARNING" | "TIME_SERIES" | "DATA_ENGINEERING" | "MLOPS" | "BUSINESS_INTELLIGENCE" | "BIG_DATA" | "CLOUD_DATA" | "RESEARCH"`

#### `contract_type`
`"CDI" | "CDD" | "Stage" | "Freelance" | "Alternance" | "Intérim" | null`

#### `remote_policy`
`"on-site" | "hybrid" | "remote" | "unknown"`

#### `company_type`
`"entité morale publique" | "entité morale privée" | "cabinet RH" | "anonyme" | "inconnu"`

### Exemple complet

Voir [`sources/collected/rekrute/postings/016.json`](rekrute/postings/016.json) (Coface) — la plus complète, à utiliser comme **référence pédagogique**.

---

## 7. Markdown — Template standardisé

Source de vérité : [`sources/collected/_schema/posting.template.md`](_schema/posting.template.md)

### Structure attendue

```markdown
# {title} — {company}

> **Source** : {source} · [Voir l'annonce]({source_url})
> **Job ID** : `{job_id}` · Réf. {source_ref}
> **Date publication** : **{posted_date}** · Deadline {deadline_date}

## Identification

| Champ | Valeur |
|---|---|
| Entreprise | **{company}** |
| Lieu | {location} ({country}) |
| Remote | {remote_policy} |
| Contrat | **{contract_type}** |
| Niveau | {niveau} |
| Diplôme | {education} |

## Famille

- Job family : `{job_family}`
- Domaines : {domains_iaml}

## Skills détectés ({count})

{skills_required}

## Description

{description}
```

---

## 8. Détection automatique des compétences (Skills Patterns)

Liste de regex `(case-insensitive)` à utiliser dans Phase 3 :

```python
SKILLS_PATTERNS = {
    "Python": r"\bPython\b",
    "SQL": r"\bSQL\b",
    "R": r"\bR\b(?![a-zA-Z])",   # éviter "Rabat" → "R" false positive
    "Java": r"\bJava\b",
    "Scala": r"\bScala\b",
    "PySpark": r"\bPySpark\b",
    "Spark": r"\bSpark\b",
    "Hadoop": r"\bHadoop\b",
    "Machine Learning": r"\bMachine Learning\b|\bapprentissage automatique\b",
    "Deep Learning": r"\bDeep Learning\b|\bapprentissage profond\b",
    "NLP": r"\bNLP\b|\bnatural language\b|\btraitement.{0,10}langage\b",
    "Computer Vision": r"\bcomputer vision\b|\bvision (par )?ordinateur\b",
    "TensorFlow": r"\bTensorFlow\b",
    "PyTorch": r"\bPyTorch\b",
    "Scikit-learn": r"\bScikit[- ]?learn\b",
    "MLflow": r"\bMLflow\b",
    "Kubeflow": r"\bKubeflow\b",
    "Databricks": r"\bDatabricks\b",
    "Snowflake": r"\bSnowflake\b",
    "BigQuery": r"\bBigQuery\b",
    "PostgreSQL": r"\bPostgreSQL\b",
    "MongoDB": r"\bMongoDB\b",
    "NoSQL": r"\bNoSQL\b",
    "Power BI": r"\bPower\s*BI\b",
    "Tableau": r"\bTableau\b(?!\sde)",
    "Excel": r"\bExcel\b",
    "Power Apps": r"\bPower\s*Apps?\b",
    "Power Automate": r"\bPower\s*Automate\b",
    "Azure": r"\bAzure\b",
    "AWS": r"\bAWS\b",
    "GCP": r"\bGCP\b|\bGoogle Cloud\b",
    "Docker": r"\bDocker\b",
    "Kubernetes": r"\bKubernetes\b|\bK8s\b",
    "Terraform": r"\bTerraform\b",
    "Git": r"\bGit\b",
    "Linux": r"\bLinux\b",
    "Airflow": r"\bAirflow\b",
    "Kafka": r"\bKafka\b",
    "Hive": r"\bHive\b",
    "CI/CD": r"\bCI/CD\b|\bGitHub Actions\b|\bAzure DevOps\b",
    "Big Data": r"\bBig Data\b",
    "Data Warehouse": r"\bdata\s*warehouse\b",
    "Data Lake": r"\bdata\s*lake\b|\bDelta Lake\b",
    "Statistics": r"\bstatistiques?\b|\bstatistics\b",
    "LLM": r"\bLLMs?\b|\blarge language models?\b",
    "GenAI": r"\bGenAI\b|\bGenerative AI\b",
    "MLOps": r"\bMLOps\b",
    "SAS": r"\bSAS\b",
    "Spring Boot": r"\bSpring\s*Boot\b",
    "Angular": r"\bAngular\b",
    "React": r"\bReact\b",
}
```

**Référence implémentation** : [`sources/collected/rekrute/_generate_postings.py`](rekrute/_generate_postings.py).

---

## 9. Mapping `job_family` (heuristique)

```python
def get_family(title):
    t = title.lower()
    if "machine learning" in t or "ml engineer" in t or "developpeur ia" in t or "intelligence artificielle" in t:
        return "ML_ENGINEER"
    if "data scientist" in t:
        return "DATA_SCIENTIST"
    if "data engineer" in t:
        return "DATA_ENGINEER"
    if "data analyst" in t or "analyste data" in t:
        return "DATA_ANALYST"
    if "business analyst" in t or "business data" in t:
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
    if "research" in t and ("data" in t or "ai" in t or "ml" in t):
        return "RESEARCH_SCIENTIST"
    return "OTHER"  # Si OTHER → vérifier si vraiment in-scope
```

---

## 10. Archive pre-2023 — Gestion

Pour les fiches identifiées **mais hors scope 2023-2026** :

```
sources/collected/<source-id>/archive_pre_2023/
├── INDEX.md                   # tableau récapitulatif
├── <id>.html                  # HTML brut
└── ...
```

**Garder** ces fiches en archive (raw HTML uniquement, pas de JSON+MD) parce que :
1. Benchmark pré-ChatGPT pour rapport L5 §N2.3
2. URLs souvent rederivables → si on veut élargir le scope plus tard
3. Décision réversible

**Référence** : [`sources/collected/rekrute/archive_pre_2023/INDEX.md`](rekrute/archive_pre_2023/INDEX.md).

---

## 11. Coordination entre sessions parallèles (Git)

### Stratégie recommandée

- Chaque session **travaille sur sa propre branche** : `Karamo-<source-id>` (ex: `Karamo-indeed-ma`, `Karamo-linkedin-ma`)
- À la fin, merger toutes les branches dans `Karamo` puis push

### Workflow type

```bash
# Au début d'une nouvelle session
git checkout Karamo
git pull
git checkout -b Karamo-<source-id>

# Pendant la session
# ... scraper + générer fichiers ...

# À la fin
git add sources/collected/<source-id>/
git commit -m "feat(scraping): collecte <source-id> bloc 4 (2026) — N fiches"
git push -u origin Karamo-<source-id>

# Karamo merge plus tard manuellement sur Karamo
```

### Pas de conflit possible si

- Chaque session reste **strictement** dans son `sources/collected/<source-id>/`
- Aucune session ne modifie `sources/collected/README.md` ou `sources/scraping_map/*` (sauf demande explicite)

### Si modification d'un fichier partagé nécessaire

- Demander d'abord à Karamo qui orchestre
- Ou faire un PR vers `Karamo` plutôt que push direct

---

## 12. Quality Gates — Validation avant push

Avant de considérer une fiche posting comme finalisée :

| Gate | Critère |
|---|---|
| `job_id` unique | Pas de duplicate dans la même source |
| `posted_date` valide | Format ISO YYYY-MM-DD · entre 2023-01-01 et today |
| `job_family != "OTHER"` | Sinon vérifier si vraiment in-scope ; sinon archiver |
| `skills_required.length >= 1` | Au moins une compétence détectée |
| `rgpd_compliant: true` | Aucune donnée personnelle |
| `personal_data_stripped: true` | Vérifié manuellement |
| `extraction_confidence >= 0.5` | Sinon flag comme `partial` |
| Markdown jumeau existe | `NNN.json` ↔ `NNN.md` toujours en paire |

### Validation finale source

À la fin de la collecte d'une source :

1. README.md créé avec tableau récap + justification tier
2. source.yaml avec stats, URL patterns, conformité
3. `sources/collected/README.md` mis à jour (ligne pour la source)
4. Tous les `.json` ont un `.md` jumeau
5. Tous les `raw/<id>.html` ont leur posting JSON+MD correspondant (sauf archive)
6. Branche `Karamo-<source-id>` créée et push

---

## 13. Pitfalls connus

### Anti-bot

| Bloqueur | Source | Contournement |
|---|---|---|
| Cloudflare "Un instant…" | ENSAF (vu précédemment) | **Firecrawl MCP ⭐** (auto-bypass) ou Playwright (vrai navigateur) |
| LinkedIn auth wall | linkedin.com | Apify actor `linkedin-jobs-scraper` |
| Indeed scrolling JS | indeed.com | **Firecrawl MCP ⭐** ou Playwright pour pagination |
| Captcha Google | site:queries massives | Espacer 5+ s + UA chrome desktop |
| 403 sur curl | ENSAF, sites Cloudflare | **Firecrawl MCP ⭐** (managé) |
| ECONNREFUSED | ensa-tetouan.ac.ma (DNS down) | Wayback Machine via curl `web.archive.org/web/<date>/<url>` |
| PDF binaire | Brochures ENSA, plaquettes | `pdftotext -layout` ou **Firecrawl scrape format=pdf** |

### Faux positifs à éliminer (Data/IA strict)

❌ Full Stack Developer (avec IA en simple "bonus")
❌ Consultant IT généraliste (avec "appétences data")
❌ Technicien Développement Informatique (généraliste)
❌ Project BOM Pilot (data consolidation supply chain ≠ data science)
❌ Data Engineer PowerAutomate seul (Excel/VBA low-code, pas Big Data)
❌ FP&A Analyst (finance, pas data science)
❌ Support Analyst (support client, pas data)
❌ Genomics Scientist (bioinformatique pure, pas data science marché)

### Sources Algériennes / Tunisiennes mélangées

- `emploitic.com` → **Algérie**, pas Maroc
- Vérifier toujours le `.country` et `.location` de chaque fiche

---

## 14. Checklist de fin de collecte (par source)

```
□ Phase 1 (Playwright live) exécutée                  → N fiches récentes
□ Phase 2 (Google + curl) exécutée par bloc :
   □ Bloc 4 (2026) → N₄ fiches
   □ Bloc 3 (2025) → N₃ fiches
   □ Bloc 2 (2024) → N₂ fiches
   □ Bloc 1 (2023) → N₁ fiches
□ Phase 3 (Python extraction) exécutée                → Total = N₁+N₂+N₃+N₄
□ Archive pre-2023 créée si fiches hors scope
□ postings/ contient NNN.json + NNN.md (paires)
□ raw/ contient les HTML bruts (.gitkeep préservé)
□ README.md écrit avec récap + tableau + justification tier
□ source.yaml écrit avec stats + URL patterns + conformité
□ Quality gates passés (RGPD, schema, confidence)
□ sources/collected/README.md mis à jour (ligne source)
□ Branche Karamo-<source-id> créée + commit + push
□ Communication à Karamo : "Source <id> done — N fiches"
```

---

## 15. Évolution du protocole

Ce protocole est **versionné** (v1.0). Si une session découvre une amélioration :
- Ne pas modifier directement
- Documenter dans le commit message + dans le README de la source concernée
- Karamo décide d'intégrer ou non en v1.1

---

**v1.0 · 2026-05-14 · SKILLNAV · Karamo Sylla & Bachirou Konaté · M242 ENSA-Tétouan · Pr. Imad Sassi**
