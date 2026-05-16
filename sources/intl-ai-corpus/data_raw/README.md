# `data_raw/` — extraction brute par mois de publication

Couche 1 du stockage 3-couches. Chaque YAML correspond à **une offre d'emploi** scrapée sur builtin.com, dans son état brut tel qu'extrait du HTML via JSON-LD + BeautifulSoup. Pas d'enrichissement, pas de classification — juste les champs natifs de l'annonce.

## Vue d'ensemble — fiches par mois de publication

| Mois | Fiches |
|---|:-:|
| 2025-08 | 2 |
| 2025-11 | 2 |
| 2026-01 | 709 |
| 2026-02 | **1 055** (pic) |
| 2026-03 | 724 |
| 2026-04 | 597 |
| **Total** | **3 089** |

Format de nommage : `{job_id}_{company}_{title}.yaml`.
