# Corpus Tech International — scraping multi-villes (USA + Europe + Inde)

> **Statut** : ✅ Phase A complète + réorganisation par mois de publication — **3 087 fiches** (2026-05-15)
> **Période publication** : Août 2025 → Avril 2026 (6 mois actifs)
> **Villes** : Los Angeles · New York · London · Amsterdam · Berlin · India
> **Organisation** : `data_raw/{YYYY-MM}/` et `data_structured/{YYYY-MM}/` — **par mois de publication**

---

## 🎯 Pourquoi cette source ?

Après saturation du marché Data/IA marocain, SKILLNAV étend sa collecte à l'**international** pour benchmarker les compétences IA observées au Maroc vs celles demandées sur le marché mondial.

builtin.com est un agrégateur tech US/EU/IN avec un excellent rendement de fiches AI Engineer. Le scraping cible **5 grandes villes** (Los Angeles, New York, London, Amsterdam, Berlin + Inde nationale) sur **Q1 2026**.

Les données sont structurées sur 3 couches :
- Couche 1 (`data_raw/`) — extraction brute HTML→YAML via JSON-LD + BeautifulSoup
- Couche 2 (`data_structured/`) — enrichissement LLM (classification ai-first/ai-support/ml-first, skills catégorisés en 10 dimensions, responsibilities, use_cases)
- Couche 3 (`postings/`) — pivot Pydantic SKILLNAV (DB-ready)

---

## 📊 Résultats

### Distribution géographique (3 087 fiches)

| Pays | Fiches | % |
|---|:-:|:-:|
| 🇺🇸 USA | 1 381 | 44.7 % |
| 🇮🇳 Inde | 835 | 27.0 % |
| 🌍 INTL non classifié | 495 | 16.0 % |
| 🇬🇧 UK | 283 | 9.2 % |
| 🇩🇪 Allemagne | 53 | 1.7 % |
| 🇳🇱 Pays-Bas | 40 | 1.3 % |

### Distribution familles métiers SKILLNAV

| Famille | Fiches | % |
|---|:-:|:-:|
| AI_ENGINEER | 2 760 | 89.4 % |
| ML_ENGINEER | 116 | 3.8 % |
| DATA_ENGINEER | 68 | 2.2 % |
| RESEARCH_SCIENTIST | 52 | 1.7 % |
| GENAI_LLM_ENGINEER | 40 | 1.3 % |
| MLOPS_ENGINEER | 26 | 0.8 % |
| CV_ENGINEER | 8 | 0.3 % |
| OTHER | 16 | 0.5 % |
| DATA_ANALYST | 1 | 0.03 % |

> 🔎 **Note** : La concentration sur AI_ENGINEER (89%) reflète le focus du keyword utilisé pour le scraping initial.

### Classification AI

| Type | Fiches | % |
|---|:-:|:-:|
| ai-first | 2 258 | 73.2 % |
| ai-support | 742 | 24.0 % |
| ml-first | 66 | 2.1 % |
| unknown | 21 | 0.7 % |

---

## 🔬 Méthode de collecte (5 étapes)

1. **Scrape listings** — Firecrawl + proxy sur builtin.com (5 villes)
2. **Dedup** — par `(title, company)` + spam filter
3. **Download HTML** — parallélisé
4. **Extract YAML raw** — JSON-LD primary + BeautifulSoup fallback
5. **Enrichissement LLM** — classification + skills catégorisés en 10 dimensions

Stack : Python 3.13 · Pydantic v2 · BeautifulSoup4 · Firecrawl · PyYAML · `anthropic` SDK.

Le **dédoublonnage est fait à la source** : pas de re-scraping des jobs déjà vus dans le CSV global. Conséquence : chaque YAML représente une fiche unique avec un `first_seen_date`.

---

## 🔄 Structure SKILLNAV — 3 couches de stockage

```
sources/collected/intl-ai-corpus/
├── data_raw/<YYYY-MM>/<id>_<co>_<title>.yaml         ← Couche 1 : extraction brute (HTML→JSON-LD)
├── data_structured/<YYYY-MM>/<id>_<co>_<title>.yaml  ← Couche 2 : enrichissement LLM (skills 10D + classif)
└── postings/NNNN.{json,md}                            ← Couche 3 : pivot Pydantic SKILLNAV (DB-ready)
```

**Pipeline de transformation** (`_import_upstream.py`) :

```
data_raw/<YYYY-MM>/*.yaml + data_structured/<YYYY-MM>/*.yaml
        │
        ▼  Merge par job_id, dossiers par mois de publication
postings/NNNN.json (Pydantic + publication_month + tous champs SKILLNAV)
postings/NNNN.md   (version humaine lisible)
```

> **Réorganisation 2026-05-15** : YAML regroupés par **mois de publication** (`posted_date`). Plus aligné avec l'axe Usage Mining (forecasting d'émergence des skills). Script : `_reorg_by_publication_month.py` · Zéro perte.

Champs disponibles depuis data_raw + data_structured :
- `description` (full text) — depuis `data_raw`
- `skills_categorized` (10 dimensions) — depuis `data_structured.position.skills`
- `responsibilities`, `use_cases` — extraction LLM
- `ai_classification` + `ai_classification_reasoning` — sortie LLM
- `is_customer_facing`, `is_management` — flags binaires
- `company_stage`, `company_focus` — depuis `data_structured.company`

Champs inférés par SKILLNAV :
- `country` + `city_inferred` — regex sur location
- `job_family` — taxonomie SKILLNAV (13 familles)
- `domains_iaml` — heuristique sur skills_categorized + description
- `remote_policy` — regex sur description
- `contract_type` — mapping work_type → CDI/CDD/Stage/Freelance

---

## 🛡️ RGPD

| Règle | Application |
|---|---|
| **Personal data** | ✅ Aucune donnée candidat — entité morale + description publique uniquement |
| **User-Agent** | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| **Rate limit** | 5 s entre requêtes |
| **robots.txt** | Vérifié |

---

## 🔗 Liens

- [Schéma JSON SKILLNAV](../_schema/job_posting.schema.json)
- [Recap d'import (machine-lisible)](raw/_import_recap.json)
- [LinkedIn MA — source MA principale](../linkedin-ma/README.md) (207 fiches)

---

**Mai 2026 · SKILLNAV · M242 ENSA-Tétouan · Pr. Imad Sassi · Karamo Sylla & Bachirou Konaté**
