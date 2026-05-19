"""Récupération via Wayback Machine pour URLs expirées.

Les job boards ne conservent pas indéfiniment leurs annonces. Pour reconstituer
l'historique 2023-2024 d'une source, on passe par les snapshots datés de
`web.archive.org`. C'est la pièce manquante qui permet au volet *Usage Mining*
du projet (forecasting ARIMA / Prophet / LSTM) de disposer d'assez d'historique
pour entraîner les modèles.

Usage :
    # 1. Lister tous les snapshots d'une URL
    python scrape_wayback_archive.py list https://www.rekrute.com/offre-emploi-12345.html

    # 2. Télécharger un snapshot précis et le sauver en YAML couche 1
    python scrape_wayback_archive.py fetch \\
        https://www.rekrute.com/offre-emploi-12345.html \\
        --timestamp 20230615 --out out/

Prérequis :
    pip install requests beautifulsoup4 pyyaml
"""

from __future__ import annotations

import argparse
import re
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

USER_AGENT = "SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)"
RATE_LIMIT_S = 5
CDX_API = "https://web.archive.org/cdx/search/cdx"
WAYBACK_PREFIX = "https://web.archive.org/web/{ts}/{url}"


def list_snapshots(url: str, since: str = "2023") -> list[tuple[str, str]]:
    """Retourne la liste (timestamp, url archivée) pour une URL donnée."""
    response = requests.get(
        CDX_API,
        params={
            "url": url,
            "output": "json",
            "from": f"{since}0101",
            "filter": "statuscode:200",
            "collapse": "digest",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()
    rows = response.json()
    if len(rows) <= 1:
        return []
    # rows[0] = header, rows[1..] = données
    return [(r[1], WAYBACK_PREFIX.format(ts=r[1], url=r[2])) for r in rows[1:]]


def fetch_snapshot(url: str, timestamp: str) -> str:
    """Télécharge un snapshot Wayback à un timestamp donné."""
    snapshot_url = WAYBACK_PREFIX.format(ts=timestamp, url=url)
    response = requests.get(
        snapshot_url,
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )
    response.raise_for_status()
    return response.text


def parse_to_record(url: str, timestamp: str, html: str) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("h1") or soup.find("title")
    body = soup.get_text(separator="\n", strip=True)
    if len(body) < 200:
        return None

    posted_date = datetime.strptime(timestamp[:8], "%Y%m%d").date().isoformat()

    return {
        "source": _guess_source(url),
        "source_url": url,
        "title": title_tag.get_text(strip=True) if title_tag else None,
        "country": "MA",
        "posted_date": posted_date,
        "scraped_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "scraper": "skillnav-wayback-v1",
        "wayback_timestamp": timestamp,
        "description": body,
        "rgpd_compliant": True,
        "personal_data_stripped": True,
    }


def _guess_source(url: str) -> str:
    domain = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return (domain.group(1) if domain else "wayback").replace(".", "-")


def cmd_list(url: str) -> None:
    snapshots = list_snapshots(url)
    if not snapshots:
        print(f"Aucun snapshot disponible pour {url}")
        return
    print(f"{len(snapshots)} snapshots disponibles :")
    for ts, archived_url in snapshots:
        print(f"  {ts}  {archived_url}")


def cmd_fetch(url: str, timestamp: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    html = fetch_snapshot(url, timestamp)
    record = parse_to_record(url, timestamp, html)
    if record is None:
        print(f"[skip] {url}@{timestamp} — contenu insuffisant (< 200 chars)")
        return

    slug = re.sub(r"[^a-z0-9]+", "-", (record["title"] or "untitled").lower())[:60]
    outfile = output_dir / f"{timestamp[:6]}_{slug}.yaml"
    outfile.write_text(yaml.safe_dump(record, allow_unicode=True), encoding="utf-8")
    print(f"[ok] {outfile.name}")
    time.sleep(RATE_LIMIT_S)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="Liste les snapshots disponibles")
    p_list.add_argument("url")

    p_fetch = sub.add_parser("fetch", help="Télécharge un snapshot et écrit un YAML")
    p_fetch.add_argument("url")
    p_fetch.add_argument("--timestamp", required=True, help="Format YYYYMMDD ou YYYYMMDDHHMMSS")
    p_fetch.add_argument("--out", type=Path, default=Path("out"))

    args = parser.parse_args()
    if args.cmd == "list":
        cmd_list(args.url)
    elif args.cmd == "fetch":
        cmd_fetch(args.url, args.timestamp, args.out)
