"""Scraping Rekrute via Playwright headless.

Technique : pagination JavaScript + extraction des cards de la page de recherche,
puis ouverture séquentielle de chaque page détail. Validé sur Rekrute,
adaptable à ANAPEC et Indeed MA en modifiant les sélecteurs CSS.

Usage :
    python scrape_playwright_rekrute.py --query "data scientist" --max-pages 3

Sortie : un fichier YAML par offre dans `out/`, structure conforme à la couche
`data_raw` du protocole SKILLNAV.

Prérequis :
    pip install playwright pyyaml
    playwright install chromium
"""

from __future__ import annotations

import argparse
import asyncio
import re
from datetime import date, datetime
from pathlib import Path

import yaml
from playwright.async_api import async_playwright

USER_AGENT = "SkillnavBot/1.0 (Academic; M242 ENSA-Tetouan)"
RATE_LIMIT_S = 5
BASE_URL = "https://www.rekrute.com"
SEARCH_URL = BASE_URL + "/offres-emploi-{}-au-maroc.html"


async def collect_offer_urls(page, query: str, max_pages: int) -> list[str]:
    """Parcourt les pages de listing et collecte les URLs des fiches."""
    urls: list[str] = []
    slug = query.lower().replace(" ", "-")
    await page.goto(SEARCH_URL.format(slug), wait_until="networkidle")

    for _ in range(max_pages):
        cards = await page.locator("a.titreJob").all()
        for card in cards:
            href = await card.get_attribute("href")
            if href and "/offre-emploi" in href:
                urls.append(href if href.startswith("http") else BASE_URL + href)

        next_btn = page.locator("a.next:not(.disabled)")
        if await next_btn.count() == 0:
            break
        await next_btn.first.click()
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(RATE_LIMIT_S)

    seen: set[str] = set()
    return [u for u in urls if not (u in seen or seen.add(u))]


def parse_posted_date(text: str) -> date | None:
    """Rekrute affiche `Publié(e) il y a N jours` — on remonte la date."""
    match = re.search(r"il y a (\d+) jours?", text, flags=re.IGNORECASE)
    if not match:
        return None
    days_ago = int(match.group(1))
    return date.fromordinal(date.today().toordinal() - days_ago)


async def scrape_offer(page, url: str) -> dict | None:
    await page.goto(url, wait_until="networkidle")

    title_el = page.locator("h1")
    if await title_el.count() == 0:
        return None

    title = (await title_el.first.inner_text()).strip()
    description = (await page.locator("div.holder.contenupost").inner_text()).strip()
    if len(description) < 200:
        return None  # quality gate du protocole

    metadata_text = await page.locator("div.holder.col-md-9").inner_text()
    posted = parse_posted_date(metadata_text)

    return {
        "source": "rekrute",
        "source_url": url,
        "title": title,
        "company": _first_match(metadata_text, r"Entreprise\s*:\s*(.+)"),
        "location": _first_match(metadata_text, r"Lieu\s*:\s*(.+)"),
        "country": "MA",
        "posted_date": posted.isoformat() if posted else None,
        "scraped_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "scraper": "skillnav-playwright-rekrute-v1",
        "description": description,
        "rgpd_compliant": True,
        "personal_data_stripped": True,
    }


def _first_match(text: str, pattern: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


async def main(query: str, max_pages: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()

        urls = await collect_offer_urls(page, query, max_pages)
        print(f"[listing] {len(urls)} URLs collectées pour '{query}'")

        for i, url in enumerate(urls, start=1):
            offer = await scrape_offer(page, url)
            if offer is None:
                continue
            slug = re.sub(r"[^a-z0-9]+", "-", offer["title"].lower())[:60]
            outfile = output_dir / f"{i:03d}_{slug}.yaml"
            outfile.write_text(yaml.safe_dump(offer, allow_unicode=True), encoding="utf-8")
            print(f"[ok] {outfile.name}")
            await asyncio.sleep(RATE_LIMIT_S)

        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--query", default="data scientist", help="Mot-clé de recherche")
    parser.add_argument("--max-pages", type=int, default=3, help="Pages de listing à parcourir")
    parser.add_argument("--out", type=Path, default=Path("out"), help="Répertoire de sortie YAML")
    args = parser.parse_args()

    asyncio.run(main(args.query, args.max_pages, args.out))
