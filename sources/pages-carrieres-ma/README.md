# Pages carrières directes — entreprises Maroc

> **Statut** : ✅ Phase 1 + 2 complètes — **6 fiches premium** récupérées (2026-05-15)
> **Sources actives** : Crédit du Maroc · Stellantis Morocco
> **Outils** : Firecrawl · curl · Python (TalentSoft + TeamTailor + Workday parsers)
> **Date d'audit** : 2026-05-15

---

## 🎯 Pourquoi cibler les pages carrières directes ?

Après 8 runs Apify LinkedIn MA ($3.83 dépensés, 207 fiches retenues), nous avons identifié que **LinkedIn search live est saturé** pour le marché Data/IA marocain. Notre Niveau 3 LinkedIn (top-down par entreprise) a confirmé que les grandes banques et industriels MA postent peu Data/IA en direct sur LinkedIn.

→ Cette source `pages-carrieres-ma` est conçue pour capturer les offres invisibles + l'historique 2023-2024 (souvent conservé 6-12 mois sur les pages carrières d'entreprise).

---

## 📊 Résultats Phase 1 + 2

### 🔬 Reconnaissance Phase 1 (14 entreprises auditées)

L'agent général a identifié **4 plateformes ATS principales** couvrant 11/14 entreprises MA :

| ATS | Entreprises MA | Statut Phase 2 |
|---|---|---|
| **TalentSoft** | BCP · Crédit du Maroc · Stellantis | ✅ Scrapé (6/237 fiches Data/IA) |
| **Cornerstone OnDemand** | Attijariwafa · BMCE Bank of Africa | ⏳ API à reverse-engineer |
| **Workday CXS** | OCP Group | ⚠️ Endpoint vide (1 spontaneous app) |
| **TeamTailor** | INWI | ✅ Scrapé (0 Data/IA actives) |
| **Phenom People** | Société Générale · Orange Maroc | ⏳ JS rendering — Playwright requis |
| **SharePoint** | Maroc Telecom | ❌ HTTP 403 — anti-bot strict |
| **Custom HTML** | CIH Bank (507 offres !) | ❌ HTTP 403 — anti-bot strict |

### 📦 Phase 2 — Scraping (V2 corrigé)

**Total scrapé** : 257 offres · **Data/IA retenu** : 6 (signal 2.3 %)

| Entreprise | URL | Offres totales | Data/IA |
|---|---|:-:|:-:|
| **Crédit du Maroc** | carriere.creditdumaroc.ma | 196 | **4** ⭐ |
| **Stellantis Morocco** | jobs.groupe-psa.com (?facet_JobCountry=128) | 34 | **2** |
| BCP | bcp-cand.talent-soft.com | 7 | 0 |
| INWI | jobs.inwi.ma | 20 | 0 |

### 🌟 Les 6 fiches premium récupérées

| ID | Entreprise | Titre | Date | Famille | Skills |
|:-:|---|---|---|---|---|
| 001 | **Crédit du Maroc** | Data Scientist (H/F) | 2026-01-13 | DATA_SCIENTIST | Python · TensorFlow · Scikit-learn · ML · MLflow · Stats |
| 002 | **Crédit du Maroc** | Lead Data Engineer | **2025-12-10** | DATA_ENGINEER | SQL · R |
| 003 | **Crédit du Maroc** | Data Manager | 2026-02-16 | DATA_MANAGER | — |
| 004 | **Crédit du Maroc** | Data Scientist | 2026-02-19 | DATA_SCIENTIST | Python · ML |
| 005 | **Stellantis Morocco** | Senior SW Engineer Perception/Radar/ML H/F | 2026-05-15 | ML_ENGINEER | TensorFlow · PyTorch · Computer Vision · Deep Learning · MLOps · ROS |
| 006 | **Stellantis Morocco** | AI ML Optimization Engineer H/F | 2026-05-15 | ML_ENGINEER | TensorFlow · ML |

---

## 🛡️ RGPD & robots.txt

| Règle | Application |
|---|---|
| robots.txt | ✅ Vérifié pour TalentSoft + TeamTailor (pas de disallow sur /offre-de-emploi/) |
| User-Agent | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | 1 s entre fetch · ≥ 5 s pour pages anti-bot |
| Personal data | ✅ Aucune donnée candidat — entité morale + descriptions publiques |

---

## 📅 Roadmap

| Phase | Statut | Action |
|---|---|---|
| ✅ **1. Reconnaissance** | Done 2026-05-15 | 14 entreprises auditées, 4 ATS identifiés |
| ✅ **2. Scraping** | Done 2026-05-15 | 6 fiches retenues, parsers TalentSoft + TeamTailor + Workday opérationnels |
| ⏳ **3. Wayback historique** | Prévu | Snapshots Crédit du Maroc 2024-2025 → +5-15 fiches historiques |
| ⏳ **4. Sources débloquées** | Prévu | CIH/IAM via Playwright · Phenom (SG, Orange) · CSOD (AWB, BoA) |
| ⏳ **5. Dédup cross-sources** | Prévu | SHA-256 vs LinkedIn + Indeed + Rekrute |

---

## 💎 Insight observatoire

Sur 257 offres scrapées sur 4 pages carrière → **6 vraies fiches Data/IA (signal 2.3 %)**. Le constat :
- **Le marché Data/IA marocain est extrêmement concentré** chez quelques employeurs (Crédit du Maroc, Stellantis)
- Les fiches récupérées sont **denses** (descriptions 700-3200 chars, skills explicites, dates fiables)
- **BCP** poste exclusivement des agents commerciaux sur sa page carrière (le tech passe par LinkedIn ou ESN)
- **INWI** poste 20 offres dont 0 Data/IA — la cellule data INWI doit recruter par cooptation/ESN

→ **Décision** : continuer à scraper page par page rapporte ~1-2 fiches par site. Plus rentable d'attaquer **Wayback Machine** sur les sites validés (Crédit du Maroc) pour récupérer 2023-2024.

---

## 🔗 Liens

- [Schéma JSON](../_schema/job_posting.schema.json)
- [Protocole de collecte](../COLLECTION_PROTOCOL.md)
- [LinkedIn MA — source précédente saturée](../linkedin-ma/README.md)
- [Recap Phase 2 v2](raw/_pages_carrieres_recap_v2.json)

---

**Mai 2026 · SKILLNAV · M242 ENSA-Tétouan · Pr. Imad Sassi · Karamo Sylla & Bachirou Konaté**
