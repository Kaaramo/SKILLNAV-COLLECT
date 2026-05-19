"""Parsing JSON-LD sur pages carrières.

Beaucoup d'ATS modernes (TalentSoft, TeamTailor, Workday, Smart Recruiters,
Greenhouse, Lever) embarquent du Schema.org `JobPosting` directement dans le HTML.
C'est la méthode la plus fiable et la plus rapide pour ces sources, car elle ne
dépend pas du markup visuel.

Le corpus pages-carrieres-ma (6 fiches Crédit du Maroc + Stellantis) a été
constitué avec ce script.

Usage :
    python scrape_jsonld_career_page.py https://careers.example.com/jobs/123 \\
                                        https://careers.example.com/jobs/456

Prérequis :
    pip install requests beautifulsoup4 pyyaml
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

USER_AGENT = "SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)"
RATE_LIMIT_S = 5


def fetch_jsonld(url: str) -> list[dict]:
    """Récupère et parse tous les blocs JSON-LD d'une page."""
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    blocks: list[dict] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        if not tag.string:
            continue
        try:
            data = json.loads(tag.string)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            blocks.extend(d for d in data if isinstance(d, dict))
        elif isinstance(data, dict):
            blocks.append(data)
    return blocks


def find_job_posting(blocks: list[dict]) -> dict | None:
    """Retourne le premier bloc dont @type == JobPosting (incluant @graph)."""
    for block in blocks:
        if block.get("@type") == "JobPosting":
            return block
        for child in block.get("@graph", []) or []:
            if isinstance(child, dict) and child.get("@type") == "JobPosting":
                return child
    return None


def to_data_raw(url: str, posting: dict) -> dict | None:
    """Mappe JobPosting schema.org → couche 1 SKILLNAV."""
    description = posting.get("description") or ""
    if isinstance(description, list):
        description = " ".join(str(x) for x in description)
    description = re.sub(r"<[^>]+>", " ", description).strip()
    if len(description) < 200:
        return None

    hiring = posting.get("hiringOrganization") or {}
    company = hiring.get("name") if isinstance(hiring, dict) else None

    location = posting.get("jobLocation") or {}
    if isinstance(location, list) and location:
        location = location[0]
    address = location.get("address") if isinstance(location, dict) else {}
    country_code = (address or {}).get("addressCountry") or "MA"

    return {
        "source": "pages-carrieres-ma",
        "source_url": url,
        "title": (posting.get("title") or "").strip(),
        "company": (company or "").strip(),
        "location": (address or {}).get("addressLocality"),
        "country": country_code if isinstance(country_code, str) else "MA",
        "posted_date": posting.get("datePosted"),
        "scraped_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "scraper": "skillnav-jsonld-careers-v1",
        "employment_type": posting.get("employmentType"),
        "description": description,
        "rgpd_compliant": True,
        "personal_data_stripped": True,
    }


def main(urls: list[str], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, url in enumerate(urls, start=1):
        try:
            blocks = fetch_jsonld(url)
        except requests.RequestException as err:
            print(f"[skip] {url} → {err}")
            continue

        posting = find_job_posting(blocks)
        if posting is None:
            print(f"[skip] {url} → aucun JobPosting JSON-LD trouvé")
            continue

        record = to_data_raw(url, posting)
        if record is None:
            print(f"[skip] {url} → description < 200 caractères")
            continue

        slug = re.sub(r"[^a-z0-9]+", "-", record["title"].lower())[:60]
        outfile = output_dir / f"{i:03d}_{slug}.yaml"
        outfile.write_text(yaml.safe_dump(record, allow_unicode=True), encoding="utf-8")
        print(f"[ok] {outfile.name}")
        time.sleep(RATE_LIMIT_S)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("urls", nargs="+", help="URLs de fiches à parser")
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args()

    main(args.urls, args.out)
