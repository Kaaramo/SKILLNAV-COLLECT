# BRIEFING_PROMPT — À coller au démarrage d'une nouvelle session Claude Code

> Karamo lance plusieurs sessions Claude Code en parallèle pour scraper différentes sources Data/IA.
> Cette fiche est un **prompt prêt-à-coller** : copie tout ce qui suit le séparateur `══════` et envoie-le comme premier message.
>
> Préciser à la fin du prompt **quelle source** et **quel(s) bloc(s) d'année** la session doit attaquer.

---

══════════════════════════════════════════════════════════════════════════

# Mission SKILLNAV — Collecte Data/IA (norme v1.0)

Tu rejoins le projet **SKILLNAV** (Skills Navigator — observatoire compétences IA/DS par Web Mining, M242 ENSA-Tétouan, soutenance 28 mai 2026, binôme Karamo Sylla + Bachirou Konaté).

## 🎯 Ce que tu dois faire

Scraper les offres d'emploi **Data Science + Intelligence Artificielle** sur une source assignée, dans la fenêtre **2023-01-01 → 2026-05-14**, et produire des fiches structurées JSON + Markdown selon le protocole versionné du repo.

## 📚 À lire IMMÉDIATEMENT (avant de scraper quoi que ce soit)

1. [`CLAUDE.md`](CLAUDE.md) — consignes globales projet + RGPD strict
2. [`sources/collected/COLLECTION_PROTOCOL.md`](sources/collected/COLLECTION_PROTOCOL.md) — **protocole versionné v1.0 — binding**
3. [`sources/collected/_schema/job_posting.schema.json`](sources/collected/_schema/job_posting.schema.json) — schéma JSON officiel
4. [`sources/collected/rekrute/`](sources/collected/rekrute/) — **référence pédagogique** (32 fiches, méthode hybride 3 phases validée)
5. [`sources/scraping_map/sources.json`](sources/scraping_map/sources.json) — registre des sources & URLs canoniques

## ⚠️ Scope inviolable

- ✅ Métiers : **Data Analyst, Data Scientist, Data Engineer, ML Engineer, MLOps, AI Engineer, NLP, CV, GenAI/LLM, Data Architect, Tech Lead Data, Research Scientist**
- ❌ EXCLURE : Full Stack Developer (même avec IA en bonus), Consultant IT généraliste, Technicien Info, FP&A Analyst, Support Analyst, Software Developer pur
- 📅 Période : **2023-01-01 à 2026-05-14** (post-ChatGPT) — toute fiche < 2023 → `archive_pre_2023/`
- 🌍 Géo : Maroc prioritaire (International en complément pour benchmark)
- 🛡️ RGPD : **AUCUNE donnée personnelle de candidat** (jamais de nom, email, téléphone, photo, LinkedIn perso). Entité morale + descriptions publiques uniquement.

## 🧰 Boîte à outils disponible — UTILISE TOUS LES MOYENS

| Outil | Quand l'utiliser |
|---|---|
| **Firecrawl MCP** ⭐ | Sites JS heavy / Cloudflare / PDF — `firecrawl_scrape`, `firecrawl_crawl`, `firecrawl_map`, `firecrawl_search`. Charger via `ToolSearch select:mcp__plugin_firecrawl_firecrawl__firecrawl-scrape` |
| **Playwright MCP** | Sites JS avec interactions (form fill, click, scroll) — `browser_navigate`, `browser_evaluate` |
| **curl + Python regex** | Sites HTML statique avec URLs connues (batch rapide) |
| **WebFetch (Claude)** | Single page summarization rapide |
| **Apify MCP** | LinkedIn spécifiquement (actor `linkedin-jobs-scraper`) |
| **WebSearch** | Découverte URLs via `site:<domain> "..." YYYY` |

> ⚠️ Firecrawl + Apify sont des MCPs **deferred** — il faut les charger en début de session via `ToolSearch query="select:..."`.

## 🔧 Méthode hybride OBLIGATOIRE (3 phases)

### Phase 1 — Reconnaissance + Listings actifs (offres récentes 2026)

**Option A — Playwright** (sites avec interactions)
- `mcp__plugin_playwright_playwright__browser_navigate` + `browser_evaluate`
- Form fill + clicks + scroll si nécessaire

**Option B — Firecrawl** ⭐ (sites JS + Cloudflare)
- `firecrawl_map` pour découvrir URLs
- `firecrawl_scrape` pour chaque URL → markdown propre

Queries : "data scientist", "data engineer", "data analyst", "machine learning", "ML engineer"
Sauver raw/<id>.html (Playwright) ou raw/<id>.md (Firecrawl)

### Phase 2 — Historique 2023-2025 (Google + curl OU Firecrawl)

- `WebSearch` avec `site:<domain> "data scientist" 2024`, `2025`, `2023` (par bloc d'année)
- `WebSearch` aussi pour `"data engineer"`, `"data analyst"`, `"machine learning engineer"`, `"data architect"`
- Pour chaque URL trouvée :
  - **Option A** : `curl -sL -A "$UA" --max-time 30 <url> -o raw/<id>.html` (rapide, gratuit)
  - **Option B** : `firecrawl_scrape url=<url>` ⭐ (si curl bloqué)
- UA : `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
- Rate limit : ≥ 5 s entre requêtes
- robots.txt vérifié

### Phase 3 — Python extraction → JSON + MD
- Voir [`sources/collected/rekrute/_generate_postings.py`](sources/collected/rekrute/_generate_postings.py) (référence)
- Pour chaque raw HTML/MD : parser texte, extraire (date, niveau, contrat, lieu, skills via regex), détecter `job_family`
- Générer `postings/NNN.json` (schéma Pydantic) + `postings/NNN.md` (template README)
- Filtrer scope 2023+, archiver pre-2023 dans `archive_pre_2023/`

## 📂 Structure à produire

```
sources/collected/<SOURCE_ID>/
├── README.md                  # description source + justification tier + méthode hybride
├── source.yaml                # URL patterns + conformité + stats + bloc completion
├── postings/
│   ├── 001.json + 001.md      # paires obligatoires
│   ├── 002.json + 002.md
│   └── ...
├── raw/                       # HTML bruts (gitignored)
└── archive_pre_2023/          # fiches hors scope si découvertes
```

## 🗓️ Phasage par bloc d'année (NORME)

Découpe ta collecte en blocs séquentiels, ne pas mélanger :

```
BLOC 4 : 2026-01 → 2026-05  → Phase 1 Playwright live
BLOC 3 : 2025-01 → 2025-12  → Phase 2 Google "site:... 2025"
BLOC 2 : 2024-01 → 2024-12  → Phase 2 Google "site:... 2024"
BLOC 1 : 2023-01 → 2023-12  → Phase 2 Google "site:... 2023"
```

À chaque bloc terminé, mettre à jour `source.yaml` avec `bloc_N_done: true`.

## 🌿 Git — Branche dédiée

- Sois sur la branche `Karamo-<source-id>` (ex: `Karamo-indeed-ma`, `Karamo-linkedin-ma`)
- Conventional commits : `feat(scraping): <source-id> bloc N — N fiches`
- Pas de modification de `sources/collected/README.md` ou `sources/scraping_map/*` sans demande explicite (éviter conflits avec autres sessions)

## ✅ Quality gates avant de considérer ton travail fini

- `job_id` unique format `<source>-<YYYY>-<NNN>`
- `posted_date` ISO YYYY-MM-DD entre 2023-01-01 et aujourd'hui
- `job_family != "OTHER"` (sinon vérifier ou archiver)
- `skills_required.length >= 1` (au moins une compétence détectée)
- `rgpd_compliant: true` + `personal_data_stripped: true`
- Chaque `NNN.json` a son jumeau `NNN.md`
- README.md + source.yaml renseignés
- `sources/collected/README.md` mis à jour avec une ligne pour ta source

## 🚫 Pièges à éviter (faux positifs déjà identifiés)

- Full Stack Developer + IA en bonus → ❌ pas Data/IA strict
- Consultant IT avec "appétences data" → ❌ généraliste
- Technicien Développement Informatique → ❌ pas Data
- Power Platform / VBA technicien → ❌ low-code
- Genomics Scientist → ❌ bioinformatique pure
- emploitic.com → ❌ **Algérien**, pas Maroc
- FP&A Analyst, Support Analyst → ❌ finance / support, pas data

## 📝 Ce que je te demande maintenant

1. **Lis dans l'ordre** les 5 fichiers de la section "À lire IMMÉDIATEMENT"
2. **Charge tes outils MCP** via `ToolSearch` (Firecrawl, Playwright, Apify si LinkedIn)
   ```
   ToolSearch query="select:mcp__plugin_firecrawl_firecrawl__firecrawl-scrape,mcp__plugin_firecrawl_firecrawl__firecrawl-map,mcp__plugin_firecrawl_firecrawl__firecrawl-search"
   ```
3. **Confirme par un récap de 5 lignes** que tu as compris : (a) le scope, (b) la source assignée, (c) les blocs à traiter, (d) la méthode hybride choisie, (e) le format de sortie
4. **Crée la branche** `Karamo-<source-id>` à partir de `Karamo`
5. **Crée le dossier** `sources/collected/<source-id>/` avec sous-dossiers `postings/`, `raw/`, `archive_pre_2023/`
6. **Exécute la collecte** bloc par bloc dans l'ordre (Bloc 4 → 3 → 2 → 1)
7. **Génère un récap final** : nombre de fiches par bloc + distribution famille + entreprises identifiées + outil principal utilisé

---

# 🎯 ASSIGNATION (à compléter par Karamo avant d'envoyer le prompt)

- **Source à scraper** : `___________` (ex: `indeed-ma`, `linkedin-ma`, `glassdoor-ma`, `um6p-aim`, `builtin`, `wttj`, etc. — voir [`sources/scraping_map/sources.json`](sources/scraping_map/sources.json))
- **Blocs à traiter** : `___________` (ex: "tous les blocs 1-4" / "uniquement 2024 et 2025" / "seulement 2026 d'abord")
- **Volume cible** : `___________` (ex: "≥ 20 fiches par bloc" / "tout ce qui est trouvable")
- **Branche Git** : `Karamo-<source-id>`
- **Contraintes spécifiques** : `___________` (ex: "Apify requis pour LinkedIn", "robots.txt strict sur ce site")

══════════════════════════════════════════════════════════════════════════

## 📋 Notes pour Karamo (orchestrateur)

### Comment lancer une session

1. Ouvre une nouvelle fenêtre Claude Code dans `F:\Web Mining Project`
2. Copie le bloc entre `══════` ci-dessus
3. Remplis la section "ASSIGNATION" avec la source + blocs + volume
4. Envoie comme premier message

### Sessions parallèles recommandées (sprint 2)

| Session | Source | Blocs | Notes |
|---|---|---|---|
| #1 | `indeed-ma` | 1-4 | Gros volume probable (4000+ data scientist) |
| #2 | `linkedin-ma` | 4 d'abord | Apify requis, plafond ~200 fiches/session |
| #3 | `glassdoor-ma` | 1-4 | Apify aussi, salaires utiles |
| #4 | `um6p-aim` | 1-4 | Petit volume, ciblé recherche |
| #5 | `builtin` (T2) | 4 | Tech US pour benchmark international |

### Coordination

- Chaque session sur sa branche `Karamo-<source-id>` (pas de conflit Git)
- Toi (Karamo) merges les branches dans `Karamo` quand elles sont prêtes
- Si une session découvre une amélioration au protocole → bumper en v1.1

### Suivi temps réel

- Après chaque session : update `sources/collected/README.md` pour refléter le nouveau total
- Une PR review entre Karamo et Bachirou avant merge sur `main`

---

**v1.0 · 2026-05-14 · SKILLNAV**
