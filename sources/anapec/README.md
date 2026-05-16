# ANAPEC — Agence Nationale de Promotion de l'Emploi et des Compétences

> **Statut** : ✅ Vérifiée · 🥇 **Tier T1** (Indispensable)
> **URL principale** : https://www.anapec.org/
> **Date d'audit** : 2026-05-14

---

## 🇲🇦 Qu'est-ce qu'ANAPEC ?

**ANAPEC** (Agence Nationale de Promotion de l'Emploi et des Compétences) est l'**agence publique d'État marocaine** chargée de la promotion de l'emploi et de l'intermédiation entre demandeurs d'emploi et employeurs. Créée en 2000 et placée sous la tutelle du Ministère de l'Économie et des Finances, elle opère sur tout le territoire à travers son réseau d'agences régionales.

Son rôle est triple :
1. **Mise en relation** entre chercheurs d'emploi et employeurs
2. **Accompagnement** des chercheurs (CV, entretiens, formations)
3. **Recrutement institutionnel** — l'ANAPEC publie aussi des offres pour le compte d'entreprises (mention "L'ANAPEC RECRUTE POUR LE COMPTE DE...")

---

## 🎯 Pourquoi ANAPEC dans le scope SKILLNAV ?

### Atouts (justification du Tier T1)

| Critère | Pertinence |
|---|---|
| **Source officielle** | Agence d'État — référence légale du marché du travail marocain |
| **Couverture territoriale** | 12 régions du Maroc (Casablanca-Settat, Rabat-Salé-Kénitra, Fès-Meknès, Tanger-Tétouan-Al Hoceima, etc.) |
| **Données structurées** | Format uniforme : référence, date, titre, contrat, salaire, formation, compétences |
| **Salaires explicites** | ~60 % des offres précisent un salaire (7 000 à 19 000 DHS observés) — rare sur le marché MA |
| **Compliance RGPD** | Publication officielle d'État · transparence assumée · données publiques |
| **Couverture historique** | Annonces 2021-2026 accessibles · idéal pour la dimension temporelle 2023-2026 SKILLNAV |
| **robots.txt** | Pas de restriction sur `/sigec-app-rv/fr/chercheurs/` ni `/sigec-app-rv/fr/entreprises/bloc_offre_home/` |

### Limites assumées

| Limite | Conséquence | Mitigation |
|---|---|---|
| **Volume Data/IA très faible** | "data scientist"=0 · "data analyst"=5 · "machine learning"=3 · "intelligence artificielle"=5 | Croiser avec Indeed MA + Rekrute + EmploiTIC pour volumes |
| **Employeurs anonymisés** | La majorité des offres masquent le nom de l'entreprise ("Description de l'entreprise" vide ou générique) | Acceptable — on cible les compétences requises, pas l'employeur identifié |
| **Profils plutôt junior/mid** | ANAPEC publie surtout des roles d'entrée (techniciens, juniors) — peu de Senior / Lead Data | Compléter par LinkedIn + cabinets RH pour Senior+ |
| **Recherche peu précise** | Le filtre `motclee` matche le texte entier — beaucoup de faux positifs | Filtrage Pydantic AI en aval + scope tagging par job_family |

---

## 🔧 Méthode de collecte

### Stack utilisée (cohérent avec [`sources/scraping_map/sources.json`](../../scraping_map/sources.json))

| Outil | Rôle |
|---|---|
| **Playwright MCP** | Navigation + extraction DOM (utilisé pour ce sample) |
| **Firecrawl** | Production pipeline (fallback HTML statique) |
| **Crawl4AI** | Alternative pour conversion HTML → markdown propre |

### URLs canoniques

```
Recherche  : https://www.anapec.org/sigec-app-rv/chercheurs/resultat_recherche/motclee:<terme>/appcle:toutlesmot
Détail     : https://www.anapec.org/sigec-app-rv/fr/entreprises/bloc_offre_home/<ID>/display
```

### Termes de recherche utilisés (sprint 1)

- `data analyst` → 5 résultats
- `data scientist` → 0 résultats
- `machine learning` → 3 résultats
- `intelligence artificielle` → 5 résultats
- `data` (large) → 129 résultats (à filtrer en aval)

### Sélecteurs DOM clés

- Résultats liste : `a[href*="bloc_offre"]` (parent `tr` → titre + date + entreprise + lieu)
- Détail : `document.body.innerText` (mise en forme libre — extraction par regex/heuristique)
- Compteur total : regex `Nombre d'offres emploi\s*:\s*(\d+)`

---

## 🛡️ Conformité RGPD & robots.txt (CLAUDE.md §N4)

| Règle | Application ANAPEC |
|---|---|
| Aucune donnée personnelle | ✅ ANAPEC ne publie jamais d'info contact candidat — uniquement employeur (souvent anonyme) |
| robots.txt | ✅ Vérifié — aucune restriction sur les pages d'offres |
| User-Agent | `SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)` |
| Rate limit | ≥ 5 s entre requêtes (sprint 1 : ~10 s par défaut Playwright) |
| Crawl-delay | Pas spécifié dans robots.txt — on applique 5s prudent |

---

## 📦 Échantillon collecté (sprint 1 — 2026-05-14)

**Scope strict Data / IA** — uniquement les fiches du cœur métier Data Science / IA. Les profils généralistes (Full-stack, Technicien Info, Consultant IT) ont été éliminés.

2 fiches structurées dans [`postings/`](postings/) :

| # | Job ID | Titre | Famille | Date | Lieu | Salaire | Score |
|:--:|---|---|---|---|---|---|:--:|
| 001 | `anapec-2026-001` | **Data Analyst** | DATA_ANALYST | 2026-03-13 | Casablanca-Anfa | 12 344 DHS | ⭐⭐⭐⭐⭐ |
| 002 | `anapec-2026-002` | Analyste Data Center Pharma | DATA_ANALYST | 2022-12-16 | Bouskoura | 11-13K DHS | ⭐⭐⭐⭐⭐ |

### Compétences agrégées (2/2 postings)

| Catégorie | Fréquence | Mots clés |
|---|:--:|---|
| **BI / Dashboards** | 2/2 | data warehouse, KPIs, reporting, dashboards |
| **Machine Learning** | 1/2 | algorithmes d'apprentissage automatique |
| **Data Engineering** | 2/2 | extraction, traitement, intégration data warehouse |
| **Veille technologique** | 1/2 | nouveaux outils d'analyse de données |

### Postings éliminés (hors scope Data/IA strict)

| Réf. | Raison |
|---|---|
| ET1306251014879 | Consultant IT — conseil généraliste avec data en simple "appétence" |
| ET2002261088985 | Développeur Full-stack — IA mentionnée comme bonus uniquement |
| EL0605261117324 | Technicien Développement Informatique — généraliste hors scope |

---

## 📅 Roadmap pour ANAPEC

| Sprint | Action |
|---|---|
| **S1 J5** (aujourd'hui) | ✅ Sample 5 postings + structure validée |
| **S1 J6** | Élargir à 30 postings (queries combinées + dédoublonnage SHA-256) |
| **S2 J7-J12** | Production pipeline `skillnav.scrapers.anapec` + persistence MongoDB raw_jobs |
| **S2 J10** | Wayback Machine snapshots ANAPEC 2023, 2024, 2025 |
| **S3** | Monitoring continu hebdomadaire |

---

## 🔗 Liens

- [Annonce officielle ANAPEC — accueil offres](https://www.anapec.org/sigec-app-rv/fr/chercheurs/resultat_recherche/tout:all)
- [Schéma JSON](../_schema/job_posting.schema.json)
- [Template Markdown](../_schema/posting.template.md)
- [Cartographie complète des sources](../../scraping_map/index.html)

---

**Mai 2026 · SKILLNAV · M242 ENSA-Tétouan · Pr. Imad Sassi · Karamo Sylla & Bachirou Konaté**
