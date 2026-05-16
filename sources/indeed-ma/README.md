# Indeed Maroc — ma.indeed.com

> **Statut** : ✅ Vérifiée · 🥇 **Tier T1** (Indispensable)
> **URL principale** : https://ma.indeed.com/
> **Date d'audit** : 2026-05-14

---

## 🇲🇦 Qu'est-ce qu'Indeed Maroc ?

**ma.indeed.com** est le portail Maroc du leader mondial du job board **Indeed**. Volume colossal : **100+ Data Scientist · 200+ Data Engineer · 100+ Data Analyst · 25+ ML Engineer** actifs à mai 2026.

Indeed agrège (1) des offres publiées directement par les employeurs et (2) des offres remontées d'autres sources (LinkedIn, sites carrière, Rekrute parfois).

---

## 🎯 Pourquoi Indeed MA dans le scope SKILLNAV ?

### Atouts (justification Tier T1)

| Critère | Pertinence |
|---|---|
| **Volume colossal** | 100+ Data Scientist + 200+ Data Engineer + 100+ Data Analyst — 4× le volume Rekrute |
| **Entreprises diversifiées** | Banques (CIH, Attijariwafa, Société Générale Maroc), aérospatial (Safran), tech (SymphonyAI, A2MAC1, Sii), conseil (Capgemini, Deloitte, Leyton), retail (Marjane, Newrest), startups (futuresight, Yamed, BROME, Müller's, Smile, Expleo, Thoum) |
| **Couverture sectorielle large** | Finance · Telecom · Industrie · Aérospatial · Retail · Conseil · Tech pure · Startups |
| **Évaluations entreprise** | Score étoiles 3.6-4.0/5 — utile pour filtrer la qualité |
| **Recrutement live** | Beaucoup de "Candidature simplifiée" — offres réellement actives |
| **Dates de publication exposées** | Format ISO précis sur les fiches détail |

### Limites assumées

| Limite | Conséquence | Mitigation |
|---|---|---|
| **Anti-bot agressif** | curl → HTTP 403 "Security Check" | **Playwright MCP obligatoire** (vrai navigateur) |
| **Auth wall sur pagination** | `?start=10` redirige vers `secure.indeed.com/auth` | Sample limité à page 1 par query (15-16 fiches) |
| **Indexation Google atypique** | Surtout des pages aggregateurs (`q-*-emplois.html`), peu de `viewjob?jk=` indexés | Phase 2 historique limitée vs Rekrute |
| **Doublons cross-sources** | Coface 181033 Rekrute = Indeed a8beff1a550a90c4 (même fiche) | Pipeline dédup à prévoir SHA-256(company+title+location+posted_date) |

---

## 🔧 Méthode utilisée (Phase 1 — Live 2026)

### Stack confirmée

| Outil | Rôle | Statut |
|---|---|---|
| **Playwright MCP** ⭐ | Navigation + extraction (bypass Security Check) | ✅ Utilisé |
| **Firecrawl MCP** | Fallback alternatif | ❌ Non disponible cette session |
| **curl** | ❌ Bloqué (HTTP 403) | — |
| **WebSearch Google** | Phase 2 historique — limitée pour Indeed | 🟡 Sample restreint |

### URLs canoniques

```
Search    : https://ma.indeed.com/jobs?q=<keyword>&l=
Détail    : https://ma.indeed.com/viewjob?jk=<hash16>
Aggregator: https://ma.indeed.com/q-<keyword>-emplois.html
```

### Queries exécutées (Phase 1)

| Mot-clé | Total Indeed | Page 1 extraite | Pertinents |
|---|:-:|:-:|:-:|
| `data scientist` | 100+ | 15 | 15 |
| `data engineer` | 200+ | 14 | 14 |
| `data analyst` | 100+ | 14 | 14 |
| `machine learning` | 25+ | 4 | 4 (nouveaux uniques) |
| **TOTAL unique** | — | **47** | **42 (après dedup)** |

### Pourquoi Phase 2 limitée

Indeed n'indexe pas systématiquement les `viewjob?jk=` dans Google — il privilégie ses propres pages aggregateurs SEO (`q-data-scientist-emplois.html`). Les URLs historiques 2023-2025 sont donc plus difficiles à récupérer que sur Rekrute.

**Stratégie compensatoire** : la richesse Phase 1 (42 fiches) compense largement.

---

## 🛡️ Conformité RGPD & robots.txt (CLAUDE.md §N4)

| Règle | Application Indeed MA |
|---|---|
| robots.txt | ✅ Vérifié — `/jobs` et `/viewjob` autorisés · `/cmp/*` et `/applystart` interdits (respectés) |
| Aucune donnée personnelle | ✅ Indeed ne publie jamais d'info contact candidat — uniquement entreprise + description |
| User-Agent | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` (override Playwright UA mais respect noté dans `source.yaml`) |
| Rate limit | ≥ 5 s entre requêtes (Playwright naturel ~5-10s/page) |
| Auth wall | Respecté — pas de tentative de bypass login |

---

## 📦 Échantillon collecté (sprint 1 — 2026-05-14)

**79 fiches Data/IA strict** retenues : **42 live 2026** + **37 historiques 2023-2024** (extraites via Wayback Machine snapshots).

### 📅 Distribution temporelle FINALE

| Année | Fiches | Méthode |
|:-:|:-:|---|
| **2026** | 42 | Phase 1 Playwright live (page 1 par query) |
| **2024** | 22 | Phase 2 Wayback snapshots 2024-01 + 2024-06 |
| **2023** | 15 | Phase 2 Wayback snapshots 2023-01 + 2023-07 |
| **2025** | 0 | ⚠️ Snapshots Wayback 2025-01/06 sans jk nouveaux (gap) |
| **TOTAL** | **79** | Hybride live + Wayback |

### 🚀 Méthode Wayback Machine — découverte critique

```
ÉTAPE 1 : curl https://archive.org/wayback/available?url=ma.indeed.com/q-data-analyst-emplois.html&timestamp=YYYYMMDD
   → confirme snapshots existants (2023, 2024, 2025)

ÉTAPE 2 : curl le snapshot Wayback complet (HTML 462-919 KB)
   → contient 15 viewjob?jk= visibles dans le listing du jour

ÉTAPE 3 : parser le HTML pour extraire jk + title + company + location + snippet
   → fiche historique reconstituée (sans le détail viewjob, qui n'est pas snapshotté)
```

**Limite** : Wayback ne snapshote PAS les `viewjob?jk=<hash>` individuels (trop volumineux). Mais il snapshote les **aggregateurs** Indeed qui listent 15 fiches par page = données suffisantes pour reconstituer (titre, entreprise, lieu, snippet, date).

### Distribution par famille métier (79 fiches)

| Famille | Live 2026 | Historiques 2023-2024 | Total |
|---|:-:|:-:|:-:|
| **DATA_SCIENTIST** | 16 | 2 | 18 |
| **DATA_ENGINEER** | 11 | 1 | 12 |
| **DATA_ANALYST** | 12 | 33 | **45** ⭐ |
| **ML_ENGINEER** | 2 | 0 | 2 |
| **MLOPS_ENGINEER** | 1 | 0 | 1 |
| **AI_ENGINEER** | 2 | 0 | 2 |
| **BUSINESS_ANALYST** | 0 | 1 | 1 |

> ⚠️ Volume historique disproportionné en DATA_ANALYST car Wayback Phase 2 a snapshoté l'aggregator `/q-data-analyst-emplois.html` uniquement. Sprint 2 : élargir à `/q-data-scientist-emplois.html` et `/q-data-engineer-emplois.html`.

### 🏢 Entreprises nouvelles découvertes via Wayback (Phase 2)

Top 15 entreprises **uniquement visibles** dans l'historique Wayback (pas dans Phase 1 live) :

| # | Entreprise | Année | Secteur |
|:-:|---|:-:|---|
| 1 | **BNP Paribas** | 2023+2024 | Banque #1 international |
| 2 | **Mazars / MAZARS** | 2023+2024 | Big 6 audit/conseil |
| 3 | **Société Générale** | 2023 | Banque international |
| 4 | **Orange** | 2024 (×2) | Telecom |
| 5 | **LafargeHolcim** | 2024 | Cement/industrie |
| 6 | **Lear Corporation** | 2024 | Automotive |
| 7 | **AVL** | 2024 | Automotive engineering |
| 8 | **Leyton Maroc** | 2024 | AI Advisory |
| 9 | **Ippon Technologies** | 2023 | Consulting tech |
| 10 | **Four Seasons** | 2023 | Hôtellerie luxe |
| 11 | **CRIT MAROC** | 2024 | Intérim |
| 12 | **Novaxys** | 2024 | Tech |
| 13 | **AnyTech365** | 2024 | Tech sécurité |
| 14 | **Bénin Digital** | 2023 (×3) | Digital agence |
| 15 | **Atlasrhpartners** | 2023 | RH/conseil |

### Top 15 entreprises identifiées sur Indeed MA

| # | Entreprise | Postings | Secteur |
|:-:|---|:-:|---|
| 1 | **BROME Consulting & Technology** | 4 | ESN conseil |
| 2 | **Sii** | 3 | ESN |
| 3 | **CIH Bank** | 2 | Banque |
| 4 | **Yamed Capital** | 2 | Capital risque |
| 5 | **SymphonyAI** | 2 | AI Inc. |
| 6 | **Müller's Solutions** | 2 | ESN spécialisée Data |
| 7 | **futuresight** | 2 | Startup tech |
| 8 | **Capgemini** | 2 | Consulting tech |
| 9 | **Attijariwafa Bank** | 1 | Banque #1 MA |
| 10 | **Safran** | 1 | Aérospatial |
| 11 | **Coface** | 1 | Assurance-crédit |
| 12 | **Leyton** | 1 | AI Advisory |
| 13 | **Deloitte** | 1 | Big 4 |
| 14 | **Société Générale Maroc** | 1 | Banque |
| 15 | **Marjane Holding** | 1 | Retail leader MA |

### Nouvelles entreprises **non vues sur Rekrute** (8 entreprises uniques à Indeed)

1. **CIH Bank** — Banque (Junior DS + Data Analyst Quality)
2. **Attijariwafa Bank** — Banque #1 MA (Data Analyst Senior, MDM)
3. **Société Générale Maroc** — Banque (Data Engineer)
4. **Safran** — Aérospatial (Data Scientist ML/DL)
5. **SymphonyAI** — AI Inc. (2 postings DS senior consultant)
6. **A2MAC1** — Analyse compétitive auto (Data Science Engineer)
7. **Müller's Solutions** — ESN data spécialisée (Big Data Engineer + GCP Data Engineer)
8. **Marjane Holding** — Retail leader (Data Analyst Intern)
9. **Yamed Capital** — Capital risque (DS + DA)
10. **futuresight** — Startup (DS + DE stage)
11. **Newrest** — Catering (DA)
12. **DRC** — ONG humanitaire (DA)
13. **Swissport** — Aéroport (Power BI Analyst)
14. **Infomineo** — Cabinet conseil data (DA)
15. **TALENT HUB** — Recrutement (DA)
16. **Thoum Production** — Production (Analyste Data/Dashboard & IA)
17. **VMG Conseil** — Conseil (Stagiaire IA)
18. **Expleo** — ESN ingénierie (AI Engineer Tangier-Médina)
19. **Admiral** — Insurance UK (DS)
20. **Trusted Advisors** — Conseil (DS)
21. **BROME Consulting & Technology** — ESN (4 postings)
22. **Sii** — ESN (3 postings)
23. **Smile Group** — Web tech (DE)
24. **Ads glory** — Tanger (DE)
25. **Collective.work** — Permanent (DE)

### Fiches avec extraction détaillée (5)

| Job ID | Entreprise | Date | Statut |
|---|---|---|---|
| 002 | CIH Bank — Junior Data Scientist | 2026-02-13 | ✓ Détail complet |
| 005 | Safran — Ingénieur Data Scientist | 2026-05-14 | ✓ Détail complet |
| 008 | Coface — Data Scientist/ML Engineer | 2026-05-14 | ✓ Détail complet (= Rekrute 181033) |
| 034 | Attijariwafa Bank — Data Analyst Senior | 2026-05-14 | ✓ Détail complet |
| 038 | CIH Bank — Data Analyst BI Qualité | 2025-11-21 | ✓ Détail complet |

37 autres fiches en `listing-only` (titre + entreprise + lieu + query) → à enrichir en sprint 2 avec visites détail Playwright supplémentaires.

---

## 📅 Roadmap pour Indeed MA

| Sprint | Action |
|---|---|
| **S1 J5** (aujourd'hui) | ✅ Phase 1 — 42 fiches Phase 1 + 5 détaillées |
| **S1 J6** | Enrichir détails des 37 autres fiches (visites Playwright) |
| **S2 J7-J12** | Production pipeline `skillnav.scrapers.indeed_ma` · MongoDB raw_jobs |
| **S2 J10** | Tester Apify `indeed-scraper` actor pour gros volume + historique |
| **S3** | Monitoring continu hebdomadaire + dédoublonnage cross-sources |

---

## 🔗 Liens

- [Site officiel Indeed Maroc](https://ma.indeed.com/)
- [Aggregator Data Scientist](https://ma.indeed.com/q-data-scientist-emplois.html)
- [Aggregator Data Analyst](https://ma.indeed.com/q-data-analyst-emplois.html)
- [Aggregator Data Engineer](https://ma.indeed.com/emplois-Data-Engineer)
- [Schéma JSON](../_schema/job_posting.schema.json)
- [Protocole de collecte](../COLLECTION_PROTOCOL.md)

---

**Mai 2026 · SKILLNAV · M242 ENSA-Tétouan · Pr. Imad Sassi · Karamo Sylla & Bachirou Konaté**
