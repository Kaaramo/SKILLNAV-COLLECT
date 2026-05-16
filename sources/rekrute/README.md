# Rekrute — Premier portail emploi du Maroc

> **Statut** : ✅ Vérifiée · 🥇 **Tier T1** (Indispensable)
> **URL principale** : https://www.rekrute.com/
> **Date d'audit** : 2026-05-14

---

## 🇲🇦 Qu'est-ce que Rekrute ?

**Rekrute.com** est le **premier portail emploi du Maroc** et de l'Afrique francophone. Il publie des annonces et offres d'emploi au Maroc, en Tunisie, en Algérie et dans plusieurs pays d'Afrique. Très orienté **cadres** et **profils tech**, c'est la référence pour la recherche d'emploi qualifié au Maroc.

---

## 🎯 Pourquoi Rekrute dans le scope SKILLNAV ?

### Atouts (justification du Tier T1)

| Critère | Pertinence |
|---|---|
| **Volume Data/IA très élevé** | 12 Data Scientists · 10 Data Engineers · 10 Data Analysts · 8 ML/AI roles — dans la même semaine |
| **Entreprises identifiées** | Coface · AXA · Sofrecom (Orange) · Cnexia (Bell Canada) · Leyton CognitX · CAT Assurance · ALTEN · Capgemini · ADM Value · IPANEMA — **brand-rich** |
| **Profils Senior + Lead + Expert** | 10-20 ans courants, niveaux explicites (Junior/Intermédiaire/Confirmé/Expert) |
| **Conditions précises** | Contrat, remote/hybride, deadline, traits personnalité, secteur, ville, code expérience |
| **HTML statique** | Pas d'anti-bot, scraping facile via Playwright + Crawl4AI |
| **Sectoriel large** | Assurance, Telecom, Industrie, ESN, Conseil, Cabinet — toutes les filières Data/IA présentes |
| **Niveau anglais explicite** | Important pour distinguer roles internationaux (Coface, AXA, Cnexia) |
| **Téléchargement annonce gratuit** | Pas de paywall sur les fiches publiques |

### Limites assumées

| Limite | Conséquence | Mitigation |
|---|---|---|
| **Salaire rarement publié** | Visibilité rémunération limitée vs ANAPEC | Croiser avec Glassdoor MA + LinkedIn Salary Insights |
| **Postings de cabinets de recrutement** | Mêmes profils dupliqués par plusieurs ESN/cabinets | Dédoublonnage SHA-256 (company+title+location) |
| **Trait personnalité « Kapacity Revealer »** | Marketing layer ajouté par Rekrute, à ignorer | Filtrer en extraction (regex sur "Recherche de nouveauté", etc.) |
| **Annonces internationales mélangées** | Quelques offres Tunisie/Algérie/Europe parmi les MA | Filtrer par `location.includes("Maroc")` |

---

## 🔧 Méthode de collecte

### Stack utilisée

| Outil | Rôle |
|---|---|
| **Playwright MCP** | Navigation + extraction DOM (utilisé pour ce batch) |
| **Crawl4AI** | Production pipeline (HTML statique propre) |
| **Firecrawl** | Fallback pour pages problématiques |

### URLs canoniques

```
Recherche  : https://www.rekrute.com/offres.html?keyword=<terme>&s=1
Détail     : https://www.rekrute.com/offre-emploi-<slug>-<ID>.html
```

### Termes de recherche utilisés (sprint 1)

| Mot-clé | Résultats bruts | Pertinents Data/IA |
|---|:-:|:-:|
| `data scientist` | 12 (6 uniques) | 6 |
| `data engineer` | 10 | 4 nouveaux |
| `data analyst` | 10 | 7 nouveaux |
| `machine learning` | 8 | 5 nouveaux (dont 4 déjà) |
| `ml engineer` | 4 | 0 nouveaux |

**Couverture totale unique** : 22 fiches Data/IA actives — 20 retenues après filtre strict.

### Sélecteurs DOM clés

- Résultats liste : `a[href*="/offre-emploi-"]` (parent `.holder` contient titre + lieu + niveau + date + entreprise)
- Détail : `document.body.innerText` (structure très uniforme · regex pour Niveau, Date, Contrat, Télétravail)
- Compteur total : non visible mais comptage côté JS

---

## 🛡️ Conformité RGPD & robots.txt (CLAUDE.md §N4)

| Règle | Application Rekrute |
|---|---|
| Aucune donnée personnelle | ✅ Rekrute ne publie jamais d'info contact candidat — uniquement entreprise (souvent identifiée) |
| robots.txt | ✅ Vérifié — aucune restriction sur les pages d'offres |
| User-Agent | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | 5-10 s entre requêtes (Playwright naturel) |

---

## 📦 Échantillon collecté (sprint 1 — 2026-05-14)

**32 fiches Data/IA strict** dans la fenêtre **2023-01-01 → 2026-05-14** :
- 20 via Playwright sur les listings live actifs
- **12 via Google search `site:rekrute.com` + curl direct** (Rekrute préserve l'historique HTTP 200)

➕ **15 fiches pre-2023** archivées dans `archive_pre_2023/` pour benchmark pré-ChatGPT (voir [`INDEX.md`](archive_pre_2023/INDEX.md)).

### 📅 Distribution temporelle finale

| Année | Postings | Couverture |
|:-:|:-:|---|
| **2026** | 23 | Janvier → Mai (riche) |
| **2025** | 4 | Février, Avril, Juin, Juillet |
| **2024** | 3 | Janvier, Mars (2) |
| **2023** | 2 | Septembre, Novembre |
| **TOTAL** | **32** | scope SKILLNAV complet |

### 🛠️ Méthode hybride utilisée

```
PHASE 1 : Playwright live search (Rekrute search interface)
  ├── data scientist (12 → 6 retenues)
  ├── data engineer (10 → 4)
  ├── data analyst (10 → 7)
  ├── machine learning (8 → 5)
  └── ml engineer (4 → 0)
                ↓ Postings 001-020 (live 2026)

PHASE 2 : Google "site:rekrute.com" recherche historique
  ├── data scientist 2023/2024/2025
  ├── data engineer 2024 OR 2023
  ├── data analyst 2023/2024
  └── machine learning engineer 2025
                ↓ 27 URLs uniques découvertes

PHASE 3 : curl direct (Rekrute conserve les URLs expirées)
  ├── 27/27 répondent HTTP 200 ✅
  ├── Téléchargement HTML brut
  └── Python regex extraction (date pub, niveau, skills...)
                ↓ Postings 021-032 (2023-2026) · 15 archivés pre-2023
```

### Top 5 par pertinence Data/IA

| # | Job ID | Titre | Famille | Entreprise | Niveau | Lieu | Date |
|:-:|---|---|---|---|---|---|---|
| **001** | `rekrute-2026-001` | **Data Scientist** | DATA_SCIENTIST | Cnexia Tech | 5-10 ans | Rabat (remote 100%) | 2026-05-14 |
| **016** | `rekrute-2026-016` | **Data Scientist / ML Engineer** | ML_ENGINEER | **Coface** Data Lab international | 3-5 ans | Casablanca (hybride) | 2026-03-23 |
| **018** | `rekrute-2026-018` | **Sr Machine Learning Engineer** | MLOPS_ENGINEER | AXA GBS Morocco | 5-10 ans | Rabat (hybride) | 2026-03-19 |
| **012** | `rekrute-2026-012` | **Architecte Cloud DATA/BIG DATA** | DATA_ARCHITECT | Confidentiel | 10-20 ans | Casablanca | 2026-04-13 |
| **017** | `rekrute-2026-017` | **Data Engineer Senior Databricks** | DATA_ENGINEER | Confidentiel | 5-10 ans | Casablanca | 2026-04-22 |

### Liste complète des 20 postings

| # | Job ID | Titre | Famille | Entreprise | Lieu |
|:-:|---|---|---|---|---|
| 001 | `rekrute-2026-001` | Data Scientist | DATA_SCIENTIST | Cnexia Tech | Rabat |
| 002 | `rekrute-2026-002` | Business Data Analyst | BUSINESS_ANALYST | Cnexia Tech | Maroc |
| 003 | `rekrute-2026-003` | Data Scientist | DATA_SCIENTIST | Cnexia Tech | Rabat |
| 004 | `rekrute-2026-004` | Data Analyst RH | DATA_ANALYST | ALTEN Maroc | Fès |
| 005 | `rekrute-2026-005` | Data Analyst Telecom | DATA_ANALYST | Sofrecom (Orange) | Rabat |
| 006 | `rekrute-2026-006` | BI Analyst (Power Platform + AI) | DATA_ANALYST | ALTEN Maroc | Rabat |
| 007 | `rekrute-2026-007` | Associate Data Science Manager | DATA_SCIENTIST | Leyton CognitX | Casablanca |
| 008 | `rekrute-2026-008` | Senior Data Scientist | DATA_SCIENTIST | Leyton CognitX | Casablanca |
| 009 | `rekrute-2026-009` | Data Analyste confirmé | DATA_ANALYST | BTECHNOLOGIE | Rabat |
| 010 | `rekrute-2026-010` | Data Analyst (Retail/RH) | DATA_ANALYST | LABELVIE/Carrefour | Skhirat |
| 011 | `rekrute-2026-011` | Tech Lead Data | DATA_ARCHITECT | IPANEMA Consulting | Casablanca |
| 012 | `rekrute-2026-012` | Architecte Cloud DATA/BIG DATA | DATA_ARCHITECT | Confidentiel (GCP) | Casablanca |
| 013 | `rekrute-2026-013` | Data Scientist | DATA_SCIENTIST | CAT Assurance | Casablanca |
| 014 | `rekrute-2026-014` | Data Engineer | DATA_ENGINEER | ADM Value | Rabat |
| 015 | `rekrute-2026-015` | Data Analyst | DATA_ANALYST | ADM Value | Rabat |
| 016 | `rekrute-2026-016` | Data Scientist / ML Engineer | ML_ENGINEER | Coface | Casablanca |
| 017 | `rekrute-2026-017` | Data Engineer Senior Databricks | DATA_ENGINEER | Confidentiel | Casablanca |
| 018 | `rekrute-2026-018` | Sr ML Engineer | MLOPS_ENGINEER | AXA GBS Morocco | Rabat |
| 019 | `rekrute-2026-019` | Data & AI Engineering Team Leader | DATA_ARCHITECT | AXA GBS Morocco | Rabat |
| 020 | `rekrute-2026-020` | Architecte Cloud DATA/BIG DATA | DATA_ARCHITECT | Sofrecom (Orange) | Casablanca |

### Postings éliminés (hors scope Data/IA strict)

| Réf. | Titre | Raison |
|---|---|---|
| 180858 | Scientist Population Genomics (UM6P) | Bioinformatique pure, hors Data Science marché |
| 182133 | Data Engineer PowerAutomate (ALTEN) | Stack Microsoft Power Platform / Excel / VBA — technicien low-code |

### Compétences agrégées (20 postings)

| Catégorie | Fréquence | Top tools/skills |
|---|:--:|---|
| **Langages** | 20/20 | **Python** (15) · SQL (13) · R (4) · Java (3) · PySpark (3) · SAS (3) |
| **ML / DL** | 14/20 | Machine Learning · Deep Learning · TensorFlow · PyTorch · scikit-learn |
| **MLOps** | 6/20 | MLflow · Kubeflow · Docker · Kubernetes · CI/CD · Azure DevOps |
| **Big Data** | 11/20 | **Databricks** (6) · Spark · Hadoop · Delta Lake · Snowflake · BigQuery |
| **Cloud** | 9/20 | Azure (Azure ML, ADF, ADLS) · GCP (BigQuery, Pub/Sub) · AWS (S3, Glue, Redshift) |
| **BI** | 13/20 | **Power BI** (7) · Tableau · Looker · SSAS · Power Apps · Power Automate |
| **NLP** | 4/20 | NLP · LLMs · Knowledge graphs |
| **GenAI** | 3/20 | Generative AI · LLMs · MLOps GenAI |
| **Database** | 12/20 | SQL · NoSQL · Oracle · PostgreSQL · BigQuery · Snowflake |

### Entreprises identifiées

**Top employeurs Data/IA Maroc identifiés via Rekrute** :

| Entreprise | Nb postings | Secteur |
|---|:-:|---|
| **Cnexia Tech** | 3 | Telecom (subsidiary Bell Canada) |
| **AXA GBS Morocco** | 2 | Assurance (offshoring) |
| **Leyton CognitX** | 2 | AI & Tech Advisory |
| **Sofrecom** | 2 | Telecom (filiale Orange) |
| **ADM Value** | 2 | Relation client (filiale TESSI) |
| **ALTEN Maroc** | 2 | ESN ingénierie |
| **Coface** | 1 | Assurance-crédit (Data Lab international) |
| **CAT Assurance** | 1 | Assurance MA |
| **IPANEMA Consulting** | 1 | Conseil transformation numérique |
| **LABELVIE / Carrefour** | 1 | Distribution retail |
| **BTECHNOLOGIE** | 1 | Tech MA |
| **Confidentiel** | 2 | Conseil/ESN |

---

## 📅 Roadmap pour Rekrute

| Sprint | Action |
|---|---|
| **S1 J5** (aujourd'hui) | ✅ Sample 20 postings + structure validée |
| **S1 J6** | Élargir à 50 postings (paginations + cabinet RH dédoublonnage) |
| **S2 J7-J12** | Production pipeline `skillnav.scrapers.rekrute` + persistence MongoDB raw_jobs |
| **S2 J10** | Wayback Machine snapshots Rekrute 2023, 2024, 2025 |
| **S3** | Monitoring continu hebdomadaire |

---

## 🔗 Liens

- [Site officiel Rekrute](https://www.rekrute.com/)
- [Filtres Métiers IT](https://www.rekrute.com/offres-emploi-metiers-de-l-it.html)
- [Schéma JSON](../_schema/job_posting.schema.json)
- [Cartographie complète des sources](../../scraping_map/index.html)

---

**Mai 2026 · SKILLNAV · M242 ENSA-Tétouan · Pr. Imad Sassi · Karamo Sylla & Bachirou Konaté**
