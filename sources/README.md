# Sources Collected — Données SKILLNAV collectées

> Stockage **structuré** des fiches de poste collectées site par site.
> Pipeline Pydantic-compatible : chaque posting = `NNN.json` + `NNN.md` validés contre [`_schema/job_posting.schema.json`](_schema/job_posting.schema.json).

---

## 📜 Protocole officiel — lecture obligatoire avant tout scraping

| Document | Rôle |
|---|---|
| [`COLLECTION_PROTOCOL.md`](COLLECTION_PROTOCOL.md) | **Protocole versionné v1.0 (binding)** — méthode hybride 3 phases · phasage par bloc d'années · RGPD · faux positifs |
| [`BRIEFING_PROMPT.md`](BRIEFING_PROMPT.md) | **Prompt prêt-à-coller** pour lancer une session Claude Code parallèle sur une nouvelle source |
| [`_schema/job_posting.schema.json`](_schema/job_posting.schema.json) | Schéma JSON officiel (Pydantic-compatible) |
| [`_schema/posting.template.md`](_schema/posting.template.md) | Template Markdown standardisé |
| [`rekrute/`](rekrute/) | **Référence pédagogique** — 32 fiches Data/IA 2023-2026 + 15 archive pre-2023 |

> 🚀 Pour lancer une session Claude Code sur une nouvelle source : ouvre [`BRIEFING_PROMPT.md`](BRIEFING_PROMPT.md), copie le bloc entre `══════`, complète la section "ASSIGNATION" et envoie.

---

## 📂 Structure standardisée

Pour chaque site source identifié dans [`sources/scraping_map/`](../scraping_map/) :

```
<source-id>/
├── README.md                      # Description du site + raison du choix dans SKILLNAV + méthode + notes RGPD
├── source.yaml                    # Métadonnées scraping (User-Agent, rate limit, dates de collecte, état)
├── postings/
│   ├── 001.json                   # Posting JSON valide schema
│   ├── 001.md                     # Posting Markdown lisible
│   ├── 002.json
│   ├── 002.md
│   └── ...
└── raw/                           # HTML brut (gitignored — re-dérivable depuis URL)
    └── *.html
```

---

## 🎯 Périmètre de collecte

- **Métiers** : tout Data Science + IA — Data Analyst → Data Scientist → Data Engineer → ML Engineer → MLOps → AI Engineer → NLP/CV/RS Engineer → LLM Engineer → Research Scientist
- **Géo** : Maroc prioritaire · International en complément
- **Période** : 2023 → 2026 (live scraping + Wayback Machine snapshots historiques)

---

## 🛡️ RGPD — Règles inviolables (CLAUDE.md §N4)

| Règle | Application |
|---|---|
| Aucune donnée personnelle de candidat | nom, email, téléphone, photo, profil LinkedIn personnel → **jamais** stockés |
| Entités morales uniquement | nom employeur, descriptions publiques d'offres |
| User-Agent identifié | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | ≥ 5s entre requêtes sur sources statiques |
| robots.txt | parsé + respecté, log de compliance |

---

## 📊 État de la collecte (mise à jour temps réel)

### 🇲🇦 Maroc (381 fiches 100% exploitables après recovery + cleanup 2026-05-16)

| Source | Tier | Statut | Postings | Date |
|---|---|---|---|---|
| ANAPEC | T1 | ✅ Sample done | **2** | 2026-05-14 |
| Rekrute | T1 | ✅ Collecte historique (5 incomplètes éliminées) | **27** (2023-2026) | 2026-05-16 |
| Indeed MA | T1 | ✅ **Recovery Apify** (12 expirées éliminées) | **67** (description full text) | 2026-05-16 |
| LinkedIn MA | T1 | ✅ Apify 8 runs SATURÉ ($3.83) | **207** | 2026-05-15 |
| Pages carrières MA | T1 | ✅ Phase 1+2 (Crédit du Maroc + Stellantis) | **6** premium | 2026-05-15 |
| Glassdoor MA | T1 | ✅ **Firecrawl + Recovery descriptions** | **72** (100% complètes) | 2026-05-16 |
| UM6P Ai Movement | T1 | ⚪ À venir | — | — |
| LinkedIn Casablanca | T1 | ⚪ À venir | — | — |

> EmploiTIC initialement listé a été **retiré** : c'est un job board **algérien** (emploitic.com), pas marocain. Hors scope priorité MA.

**Total Maroc = 381 fiches Data/IA strict 2022-2026, 100% descriptions exploitables (>= 200 chars).**

> 🔬 **Recovery 2026-05-16** : audit qualité initial révèle 133 fiches MA (33%) avec descriptions vides ou trop courtes. Pipeline de récupération exécuté :
> - **Indeed MA** : 73 URLs re-scrapées via Apify `misceres/indeed-scraper` (~$0.02) — 61 récupérées + 12 expirées éliminées
> - **Glassdoor MA** : 55 URLs re-scrapées via Firecrawl direct (free tier) — 55 récupérées avec descriptions complètes
> - **17 fiches incomplètes restantes éliminées** (12 Indeed expirées + 5 Rekrute courtes)
> - Bilan : passage de **265/398 (67%)** à **381/381 (100%) exploitables**

### 🌍 International (Bascule observatoire — Phase Mvt A complétée)

| Source | Tier | Statut | Postings | Date |
|---|---|---|---|---|
| **Corpus Tech INTL** | T1 | ✅ **Mvt A complet — 6 pays, snapshots Q1 2026** | **3 087** (1381 US + 835 IN + 283 GB + 53 DE + 40 NL + 495 INTL) | 2026-05-15 |
| Corpus Tech INTL — scope élargi Data/Engineer/Analyst | T1 | ⏳ Mvt B planifié | — | — |
| LinkedIn US/UK/DE via Apify | T1 | ⏳ Mvt C planifié | — | — |
| WTTJ Europe (FR/DE/UK/ES) | T2 | ⏳ Mvt C planifié | — | — |
| HN "Who is hiring" monthly | T2 | ⏳ Mvt C planifié | — | — |

**Total International = 3 087 fiches Data/IA (focus AI Engineer, Q1 2026).**

---

### 🎯 Total global SKILLNAV : **3 468 fiches Data/IA** (381 MA + 3 087 INTL) — 100% exploitables

> Source : scraping interne SKILLNAV de **builtin.com** (Q1 2026, 6 pays). Détails dans [intl-ai-corpus/README.md](intl-ai-corpus/README.md).

---

## 🏛 Architecture 3-couches uniforme (2026-05-15)

Toutes les sources adoptent la **structure 3-couches SKILLNAV** :

```
<source>/
├── data_raw/{YYYY-MM}/<ref>_<co>_<title>.yaml         ← Couche 1 — extraction brute (HTML→YAML)
├── data_structured/{YYYY-MM}/<ref>_<co>_<title>.yaml  ← Couche 2 — enrichissement LLM (skills 10D + classif IA)
└── postings/NNNN.{json,md}                            ← Couche 3 — pivot Pydantic SKILLNAV (DB-ready)
```

| Source | data_raw | data_structured | postings |
|---|:-:|:-:|:-:|
| anapec | 2 | 2 | 2 |
| rekrute | 27 | 27 | 27 |
| indeed-ma | 67 | 67 | 67 |
| linkedin-ma | 207 | 207 | 207 |
| pages-carrieres-ma | 6 | 6 | 6 |
| glassdoor-ma | 72 | 72 | 72 |
| intl-ai-corpus | 3 089 | 3 086 | 3 087 |
| **TOTAL** | **3 470** | **3 467** | **3 468** |

**Pourquoi cette structure ?**
1. **Symétrie scientifique** — MA et INTL exploitables avec les mêmes scripts d'analyse
2. **Traçabilité** — raw (signal brut) → structured (analyse LLM) → postings (DB-ready)
3. **Mois de publication** — organisation alignée avec l'axe Usage Mining (forecasting d'émergence)
4. **Pédagogie M242** — les 3 couches s'alignent sur les 3 axes Web Mining (Content / Structure / Usage)

**Scripts de production** :
- [`_restructure_ma_to_3_layers.py`](_restructure_ma_to_3_layers.py) — Phase 1 MA : postings → data_raw/{YYYY-MM}/
- [`_enrich_ma_structured.py`](_enrich_ma_structured.py) — Phase 2 MA : structured (règles Claude Opus 4.7 déterministes)
- [`intl-ai-corpus/_import_upstream.py`](intl-ai-corpus/_import_upstream.py) — Import upstream → postings/

---

## 🔬 Premier insight comparatif MA ↔ INTL

Classification AI calibrée selon la méthodologie upstream :

| Type IA | INTL (3 087) | MA (398) | Écart |
|---|:-:|:-:|---|
| `ai-first` | **73.2%** (2 258) | **10%** (40) | 🔴 **−63 pts** |
| `ai-support` | 24.0% (742) | **0%** (0) | 🔴 −24 pts |
| `ml-first` | 2.1% (66) | **28%** (110) | 🟢 +26 pts |
| `non-ai` | 0% | **62%** (248) | 🟢 +62 pts |

**Insight scientifique majeur pour le rapport L5** : le marché Maroc n'a pas encore basculé sur GenAI/LLM. Il fait encore majoritairement du ML classique + Data Analytics traditionnel. Aucun rôle « ai-support » (Solutions Architect AI, Customer Engineer AI) n'existe en MA. C'est précisément le type de **gap mesuré** que le projet M242 cherche à révéler.

---

## 🔗 Liens

- [Schéma JSON officiel](_schema/job_posting.schema.json)
- [Template Markdown](_schema/posting.template.md)
- [Cartographie sources complète](../scraping_map/index.html) (dashboard)
- [Registre conformité](../registry.yaml) (robots.txt + TOS)
- [Curricula ENSA Maroc](../curricula/REGISTRY.md) (volet B)
