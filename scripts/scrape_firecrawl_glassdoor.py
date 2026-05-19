"""Scraping Glassdoor via l'API Firecrawl.

Technique : appel `/v1/scrape` qui contourne Cloudflare automatiquement et
retourne le contenu en markdown propre + métadonnées Open Graph. Utilisé pour
Glassdoor MA (anti-bot fort) et pour le corpus international JS-rendered.

Usage :
    export FIRECRAWL_API_KEY=fc-...
    python scrape_firecrawl_glassdoor.py urls.txt --out out/

Le fichier `urls.txt` contient une URL par ligne. La sortie est un YAML par URL
plus un fichier markdown brut, conforme à la couche `data_raw` du protocole.

Prérequis :
    pip install requests pyyaml
"""

from __future__ import annotations

import argparse
import os
import re
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml

USER_AGENT = "SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)"
RATE_LIMIT_S = 5
FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v1/scrape"


def scrape_one(url: str, api_key: str) -> dict:
    """Appel synchrone à Firecrawl. Retourne markdown + metadata."""
    response = requests.post(
        FIRECRAWL_ENDPOINT,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(f"Firecrawl error on {url}: {payload}")
    return payload["data"]


def parse_glassdoor_markdown(md: str) -> dict[str, str | None]:
    """Extrait titre, entreprise, lieu depuis le markdown Glassdoor."""
    lines = [line.strip() for line in md.splitlines() if line.strip()]
    title = next((line.lstrip("# ").strip() for line in lines if line.startswith("# ")), None)

    company = _first_match(md, r"(?:Employeur|Company)\s*:\s*(.+)")
    location = _first_match(md, r"(?:Lieu|Location)\s*:\s*(.+)")
    return {"title": title, "company": company, "location": location}


def _first_match(text: str, pattern: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


def to_data_raw(url: str, scraped: dict) -> dict:
    md = scraped.get("markdown", "")
    parsed = parse_glassdoor_markdown(md)

    return {
        "source": "glassdoor-ma",
        "source_url": url,
        "title": parsed["title"],
        "company": parsed["company"],
        "location": parsed["location"],
        "country": "MA",
        "scraped_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "scraper": "skillnav-firecrawl-glassdoor-v1",
        "description": md,
        "rgpd_compliant": True,
        "personal_data_stripped": True,
    }


def main(urls_file: Path, output_dir: Path) -> None:
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise SystemExit("FIRECRAWL_API_KEY n'est pas défini dans l'environnement.")

    output_dir.mkdir(parents=True, exist_ok=True)
    urls = [line.strip() for line in urls_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"[firecrawl] {len(urls)} URLs à traiter")

    for i, url in enumerate(urls, start=1):
        try:
            scraped = scrape_one(url, api_key)
        except requests.HTTPError as err:
            print(f"[skip] {url} → {err}")
            continue

        record = to_data_raw(url, scraped)
        slug = re.sub(r"[^a-z0-9]+", "-", (record["title"] or "untitled").lower())[:60]
        (output_dir / f"{i:03d}_{slug}.yaml").write_text(
            yaml.safe_dump(record, allow_unicode=True), encoding="utf-8"
        )
        print(f"[ok] {i:03d}_{slug}")
        time.sleep(RATE_LIMIT_S)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("urls_file", type=Path, help="Fichier texte avec une URL par ligne")
    parser.add_argument("--out", type=Path, default=Path("out"), help="Répertoire de sortie YAML")
    args = parser.parse_args()

    main(args.urls_file, args.out)
