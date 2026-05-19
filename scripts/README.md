# Templates de collecte

Cinq scripts Python qui documentent, sous forme reproductible, chaque technique
utilisée pour constituer le corpus SKILLNAV. Chaque template est volontairement
court et concentré sur une technique : pagination Playwright, API Firecrawl,
acteur Apify, parse JSON-LD, fallback Wayback Machine.

Pour le mode opératoire complet (phasing, quality gates, scope), voir
[`../sources/COLLECTION_PROTOCOL.md`](../sources/COLLECTION_PROTOCOL.md).

| Script | Technique | Sources couvertes dans le corpus |
|---|---|---|
| `scrape_playwright_rekrute.py` | Playwright headless, pagination + détail | Rekrute, ANAPEC, Indeed MA (Phase 1) |
| `scrape_firecrawl_glassdoor.py` | API Firecrawl (`/v1/scrape`) | Glassdoor MA, Corpus Tech INTL |
| `scrape_apify_linkedin.py` | Apify SDK, acteur `bebity/linkedin-jobs-scraper` | LinkedIn MA |
| `scrape_jsonld_career_page.py` | `requests` + BeautifulSoup + `JobPosting` schema.org | Pages carrières MA (Crédit du Maroc, Stellantis, autres ATS) |
| `scrape_wayback_archive.py` | Wayback Machine pour URLs expirées | Recovery historique 2023-2024 |

## Variables d'environnement attendues

```env
APIFY_TOKEN=apify_api_xxx
FIRECRAWL_API_KEY=fc-xxx
```

Pas de clé API pour Playwright (utilise un navigateur Chromium local) ni pour
Wayback Machine (API publique).

## Prérequis

```bash
pip install -r ../requirements.txt
playwright install chromium    # uniquement pour Playwright
```

## Conformité

Tous les templates respectent les règles RGPD du projet : User-Agent identifié
`SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)`, rate limit de 5 secondes,
zéro donnée personnelle collectée.
