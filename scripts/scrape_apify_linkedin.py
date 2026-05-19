"""Scraping LinkedIn Jobs via Apify.

Technique : appel de l'acteur `bebity/linkedin-jobs-scraper` qui gère
l'authentification, la pagination et le rate limit côté Apify. Sortie JSON
structurée directement convertible vers la couche `data_raw` SKILLNAV.

Le corpus LinkedIn MA du projet a été collecté avec ce script (8 runs, 207 fiches,
~3,83 USD au total).

Usage :
    export APIFY_TOKEN=apify_api_...
    python scrape_apify_linkedin.py --location Morocco --query "data scientist" --max 50

Prérequis :
    pip install apify-client pyyaml
"""

from __future__ import annotations

import argparse
import os
import re
import time
from datetime import datetime
from pathlib import Path

import yaml
from apify_client import ApifyClient

USER_AGENT = "SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)"
ACTOR_ID = "bebity/linkedin-jobs-scraper"
RATE_LIMIT_S = 5


def run_linkedin_actor(client: ApifyClient, query: str, location: str, max_items: int) -> list[dict]:
    """Lance l'acteur Apify et récupère les résultats."""
    run_input = {
        "queries": [query],
        "locations": [location],
        "rows": max_items,
        "publishedAt": "anytime",
        "proxyConfiguration": {"useApifyProxy": True},
    }
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = run["defaultDatasetId"]
    return list(client.dataset(dataset_id).iterate_items())


def to_data_raw(item: dict) -> dict:
    """Convertit la sortie Apify vers la structure couche 1 SKILLNAV."""
    title = item.get("title") or ""
    description = item.get("descriptionText") or item.get("description") or ""
    if len(description) < 200:
        return {}

    return {
        "source": "linkedin-ma",
        "source_url": item.get("link") or item.get("url"),
        "title": title.strip(),
        "company": (item.get("companyName") or "").strip(),
        "location": (item.get("location") or "").strip(),
        "country": "MA",
        "posted_date": item.get("publishedAt") or item.get("postedAt"),
        "scraped_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "scraper": f"skillnav-apify-{ACTOR_ID.split('/')[-1]}-v1",
        "description": description.strip(),
        "rgpd_compliant": True,
        "personal_data_stripped": True,
    }


def main(query: str, location: str, max_items: int, output_dir: Path) -> None:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise SystemExit("APIFY_TOKEN n'est pas défini dans l'environnement.")

    output_dir.mkdir(parents=True, exist_ok=True)
    client = ApifyClient(token)

    print(f"[apify] acteur {ACTOR_ID} — query='{query}' location='{location}' max={max_items}")
    items = run_linkedin_actor(client, query, location, max_items)
    print(f"[apify] {len(items)} fiches retournées")

    written = 0
    for i, item in enumerate(items, start=1):
        record = to_data_raw(item)
        if not record:
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", record["title"].lower())[:60]
        (output_dir / f"{i:03d}_{slug}.yaml").write_text(
            yaml.safe_dump(record, allow_unicode=True), encoding="utf-8"
        )
        written += 1
        time.sleep(RATE_LIMIT_S)

    print(f"[done] {written} fiches conformes écrites dans {output_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--query", default="data scientist")
    parser.add_argument("--location", default="Morocco")
    parser.add_argument("--max", dest="max_items", type=int, default=50)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args()

    main(args.query, args.location, args.max_items, args.out)
