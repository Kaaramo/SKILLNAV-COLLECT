# LinkedIn Maroc — ma.linkedin.com/jobs

> **Statut** : ✅ Vérifiée · 🥇 **Tier T1** (Indispensable)
> **URL principale** : https://ma.linkedin.com/jobs/
> **Méthode officielle** : Apify · `number_one_scraper/cheap-advance-linkedin-jobs-scraper`
> **Date d'audit** : 2026-05-15

---

## 🇲🇦 Qu'est-ce que LinkedIn MA ?

**LinkedIn Jobs Maroc** = portail LinkedIn pour les offres au Maroc. **454+ Data Scientist** + 643+ Data Analyst + plusieurs centaines Data Engineer / ML Engineer actuellement actifs. C'est le job board #1 Maroc pour les profils tech qualifiés.

---

## 🎯 Pourquoi LinkedIn MA = source stratégique #1 SKILLNAV

| Critère | Pertinence |
|---|---|
| **Volume colossal** | 454+ DS + 643+ DA — 2nd après Indeed mais qualité supérieure |
| **Entreprises premium** | QuantumBlack/McKinsey, BCG X, Mistral AI, AXA, Stellantis, Artefact, Capgemini, Coface, Société Générale, Orange Business |
| **Données structurées** | Apify renvoie 23 champs propres (jobId, applicationsCount, contractType, experienceLevel, workType, salaryInfo, sector…) |
| **Couverture sectorielle** | Banques (CIH, BNP, AXA), ESN (ALTEN, BROME, Capgemini, Devoteam, SQLI), tech (Agoda, Mistral), conseil (Artefact, BCG, Deloitte) |
| **Géo** | Casablanca dominant + Rabat, Fès, Tanger, remote |

---

## 📦 Collecte — 5 runs Apify (initial + Niveau 1)

### 💰 Bilan budgétaire

| Run | Cible | Raw jobs | Coût |
|---|---|:-:|:-:|
| **#0 initial** | Data/IA générique | 500 | $0.65 |
| **#1A IA pointue** | NLP · CV · LLM · GenAI · Applied Scientist · Prompt | 394 | $0.45 |
| **#1B Big Data** | Snowflake · Databricks · Hadoop · Spark · Kafka · Airflow · ETL · Cloud Data | 500 | $0.63 |
| **#1C BI & Analytics** | Power BI · Tableau · BI Analyst · Reporting · Quant · Risk | 502 | $0.56 |
| **#1D Variantes FR** | Analyste · Ingénieur Data · Statisticien · Actuaire · Data Steward · Governance · Product Manager | 503 | $0.60 |
| **TOTAL** | | **2 399** | **$2.89** |

> Budget Apify restant : **$2.08** sur $4.97 alloué.

### 🧪 Pipeline de qualité

- **Raw jobs scrapés** : 2 399
- **Après dédup par `jobId` LinkedIn** : 852 jobs uniques (65 % d'overlap entre runs = normal)
- **Filtre Data/IA strict** (whitelist 50+ patterns + blacklist 25) : **206 retenus** (24 % de signal)
- **RGPD strippé** : 136 champs `posterFullName` + `posterProfileUrl` supprimés

### 📅 Fenêtre temporelle des publications

| Année | Fiches | Visualisation |
|:-:|:-:|---|
| **2026** | **176** (85 %) | ████████████████████████████████████████████████████████ |
| **2025** | **28** (14 %) | █████████ |
| **2024** | **2** (1 %) | ▏ |
| 2023 | 0 | _LinkedIn search live n'expose pas <2024_ |

### 🎓 Distribution par famille de métier (13 familles désormais)

| Famille | Fiches | Part |
|---|:-:|:-:|
| **DATA_ANALYST** | 61 | 30 % |
| **DATA_ENGINEER** | 58 | 28 % |
| **DATA_SCIENTIST** | 41 | 20 % |
| **BI_DEVELOPER** ⭐ | 9 | 4 % |
| **AI_ENGINEER** ⭐ | 8 | 4 % |
| **QUANT_ANALYST** ⭐ | 7 | 3 % |
| **DATA_OTHER** | 7 | 3 % |
| **ML_ENGINEER** | 4 | 2 % |
| **DATA_MANAGER** ⭐ | 3 | 1 % |
| **DATA_ARCHITECT** ⭐ | 3 | 1 % |
| **MLOPS_ENGINEER** | 2 | 1 % |
| **ACTUARY** ⭐ | 2 | 1 % |
| **CV_ENGINEER** ⭐ | 1 | 0.5 % |
| **TOTAL** | **206** | **100 %** |

> ⭐ = familles nouvellement détectées grâce au Niveau 1 (7 familles supplémentaires)

### 🏆 Top employeurs cumulés (75 uniques)

**Top 5 cumulé** : ALTEN (14) · BROME (12) · Agoda (12) · Capgemini (14 = 5 initial + 9 level1) · CIH BANK (7)

**Nouveaux employeurs Niveau 1** (19) : Capgemini (+9), Exclusive Networks (+3), Phi Partners, CGI, Scania Group, AKWEL, MAROC FER, Inetum, Atos, RED TIC, ProgressSoft, Mirage Metrics, La Marocaine Vie, A2MAC1, Collective.work, AGC Glass Europe, Smile, Concentrix, Hexagone Digitale

### 🛠️ Top 15 skills détectés sur les 60 nouvelles fiches (Niveau 1)

| Rang | Skill | Occurrences | Cluster |
|:-:|---|:-:|---|
| 1 | **SQL** | 29 | Data fondation |
| 2 | **Python** | 25 | Data fondation |
| 3 | **Azure** | 23 | Cloud |
| 4 | **AWS** | 17 | Cloud |
| 5 | **GCP** | 16 | Cloud |
| 6 | **R** | 14 | Data fondation |
| 7 | **Power BI** | 13 | BI |
| 8 | **Machine Learning** | 12 | IA |
| 9 | **Java** | 10 | Programmation |
| 10 | **CI/CD** | 10 | DevOps |
| 11 | **Spark** | 9 | Big Data |
| 12 | **Statistics** | 9 | Data fondation |
| 13 | **Excel** | 8 | BI |
| 14 | **Git** | 8 | DevOps |
| 15 | **Docker** | 8 | DevOps |

**Skills émergents détectés** : LLM (5), MLOps (5), RAG (3), LangChain (4), Snowflake (5), Databricks (6), dbt, Looker (3)

---

## 🛡️ Conformité RGPD & robots.txt (CLAUDE.md §N4)

| Règle | Application |
|---|---|
| robots.txt | ⚠️ LinkedIn interdit scraping général. Usage académique M242 limité + UA SkillnavBot identifié + rate limit Apify natif |
| Aucune donnée personnelle | ✅ 136 champs `posterFullName` + `posterProfileUrl` strippés sur 5 runs. Uniquement entreprise + description publique |
| Mode guest | ✅ Aucune authentification utilisée |
| Rate limit | ≥ 5 s (Apify proxy résidentiel) |

---

## 📅 Roadmap LinkedIn MA

| Sprint | Action | Coût | Fiches attendues |
|---|---|:-:|:-:|
| ✅ **S1 J5** | Apify run #0 initial + Niveau 1 (4 runs thématiques) | $2.89 | **206 fiches** Data/IA 2024-2026 ↑ |
| 🔄 **S2 — Niveau 2** | 5 runs géographiques (Tanger/Fès/Marrakech/Agadir/Oujda) | ~$1.70 | +200-400 régionales |
| 🔄 **S2 — Niveau 3** | Top-down 30 entreprises via bebity actor | ~$1.00 | +250-500 historiques 2023-2024 |
| 🔄 **S2 — Niveau 4** | Pages carrières directes + Glassdoor MA | ~$0.50 | +500-1000 hors-LinkedIn |
| **S3** | Pipeline `skillnav.scrapers.linkedin_ma_apify` automatisé hebdo | — | — |

---

## 🔗 Liens

- [Site officiel LinkedIn Jobs Morocco](https://ma.linkedin.com/jobs/search?location=Morocco)
- [Schéma JSON](../_schema/job_posting.schema.json)
- [Protocole de collecte](../COLLECTION_PROTOCOL.md)
- [Apify actor](https://apify.com/number_one_scraper/cheap-advance-linkedin-jobs-scraper)

---

**Mai 2026 · SKILLNAV · M242 ENSA-Tétouan · Pr. Imad Sassi · Karamo Sylla & Bachirou Konaté**
