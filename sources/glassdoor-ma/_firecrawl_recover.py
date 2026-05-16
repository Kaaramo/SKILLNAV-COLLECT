"""
Recuperation Glassdoor MA via Firecrawl CLI.

Usage:
  python _firecrawl_recover.py --smoke   # 3 URLs test
  python _firecrawl_recover.py           # toutes les URLs incompletes
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"F:\Web Mining Project\sources\collected\glassdoor-ma")
INCOMPLETE_FILE = ROOT / "raw" / "_incomplete_urls.json"
POSTINGS = ROOT / "postings"
DETAILS_DIR = ROOT / "raw" / "_firecrawl_details"

FIRECRAWL_BIN = r"C:\Users\ksthe\AppData\Roaming\npm\firecrawl.cmd"
SLEEP_BETWEEN = 2.0


def firecrawl_scrape(url, output_path):
    if output_path.exists() and output_path.stat().st_size > 1000:
        return True
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        res = subprocess.run(
            f'"{FIRECRAWL_BIN}" scrape "{url}" -o "{output_path}"',
            capture_output=True, text=True, timeout=120, shell=True,
        )
        return res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000
    except subprocess.TimeoutExpired:
        return False


def parse_glassdoor_md(md_text):
    """Extract title, company, location, description from Glassdoor markdown."""
    result = {"title": None, "company": None, "location": None, "description": ""}

    # Find main content : right after "Apply on employer site" marker
    apply_idx = md_text.find("Apply on employer siteApply now")
    if apply_idx < 0:
        apply_idx = md_text.find("Apply on employer site")
    main_text = md_text[apply_idx:] if apply_idx >= 0 else md_text

    # End marker : "Is my resume a good match" or "Conversations @"
    end_markers = ["Is my resume a good match", "Conversations @", "## Working here doesn"]
    end_idx = len(main_text)
    for em in end_markers:
        idx = main_text.find(em)
        if 0 < idx < end_idx:
            end_idx = idx
    main_text = main_text[:end_idx]

    # Sections variantes possibles
    sections = {}
    section_patterns = [
        ("description", r"(?:####\s*\*?\*?)?(?:Description (?:du poste|emploi|de l'offre)|Job description|Description :|Détails du poste)\s*\*?\*?\s*:?\s*\n+(.+?)(?=\n#{1,6}\s|\nMissions\s*:|\nQualifications\s*:|\nCompetences\s*:|\nCompétences\s*:|\nProfil\s*:|\nShow more|\Z)"),
        ("missions", r"(?:####\s*\*?\*?)?Missions\s*\*?\*?\s*:?\s*\n+(.+?)(?=\n#{1,6}|\nQualifications|\nCompetences|\nCompétences|\nProfil|\nShow more|\Z)"),
        ("qualifications", r"(?:####\s*\*?\*?)?(?:Qualifications|Profil recherché|Profil)\s*\*?\*?\s*:?\s*\n+(.+?)(?=\n#{1,6}|\nCompetences|\nCompétences|\nShow more|\Z)"),
        ("skills", r"(?:####\s*\*?\*?)?(?:Compétences|Competences|Skills)\s*\*?\*?\s*:?\s*\n+(.+?)(?=\n#{1,6}|\nShow more|\nSee company|\Z)"),
    ]
    for name, pattern in section_patterns:
        m = re.search(pattern, md_text, re.DOTALL | re.IGNORECASE)
        if m:
            sections[name] = m.group(1).strip()

    full_desc = "\n\n".join(v for v in [
        sections.get("description"), sections.get("missions"),
        sections.get("qualifications"), sections.get("skills"),
    ] if v)

    # Fallback robuste : tout le texte entre "Apply on employer site" et "Is my resume"
    if not full_desc or len(full_desc) < 200:
        # Take main_text minus the very first lines (title, location, apply links)
        lines = main_text.split("\n")
        # Skip header noise
        start = 0
        for i, line in enumerate(lines):
            ll = line.strip().lower()
            if not ll or ll.startswith("apply on") or ll.startswith("upload your resume") \
               or "use ai to find out" in ll or "is your resume a good match" in ll:
                continue
            start = i
            break
        body = "\n".join(lines[start:])
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        # Drop very short body or pure navigation
        if len(body) > 300:
            full_desc = body[:8000]

    result["description"] = full_desc

    # Title : 1er H1 dans main_text
    title_m = re.search(r"^#\s+(.+?)$", main_text, re.MULTILINE)
    if title_m:
        result["title"] = title_m.group(1).strip()

    # Company : link [NOM](url employeur) après le H1
    if title_m:
        after_title = main_text[title_m.end():title_m.end() + 1500]
        co_m = re.search(r"\[([^\]]+?)\]\(https?://[^)]*?Employer/[^)]+\)", after_title)
        if not co_m:
            co_m = re.search(r"\[([^\]]+?)\]\(https?://www\.glassdoor\.com/Reviews/[^)]+\)", after_title)
        if co_m:
            result["company"] = co_m.group(1).strip()

    # Location : ligne avec ville/pays après company
    loc_m = re.search(r"\b(Casablanca|Rabat|Marrakech|Tanger|Fes|Fès|Agadir|Oujda|Tetouan|Tétouan|Kenitra|Settat|Salé|Mohammedia|Maroc|Morocco)[\w\s,\-]*\n", md_text)
    if loc_m:
        result["location"] = loc_m.group(0).strip()

    return result


def update_posting(posting_file_name, parsed):
    json_path = POSTINGS / posting_file_name
    md_path = POSTINGS / posting_file_name.replace(".json", ".md")
    if not json_path.exists():
        return False

    with json_path.open("r", encoding="utf-8") as f:
        rec = json.load(f)

    new_desc = parsed.get("description") or ""
    if not new_desc or len(new_desc) < len(rec.get("description") or ""):
        return False
    if len(new_desc) < 200:
        return False

    rec["description"] = new_desc
    if parsed.get("title"):
        rec["title"] = parsed["title"]
    if parsed.get("company") and parsed["company"] not in ("Unknown", ""):
        rec["company"] = parsed["company"]
    if parsed.get("location"):
        rec["location"] = parsed["location"]

    rec["scraper"] = "skillnav-firecrawl-glassdoor-recovery-v1.0"
    rec["extraction_confidence"] = 0.85
    rec["recovery_via"] = "firecrawl_direct_scrape"

    json_path.write_text(json.dumps(rec, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    if md_path.exists():
        md_text = md_path.read_text(encoding="utf-8")
        md_text = re.sub(
            r"(## Description complète\n\n)(.*?)(\n\n---\n)",
            lambda m: m.group(1) + new_desc[:6000] + m.group(3),
            md_text,
            flags=re.DOTALL,
        )
        md_path.write_text(md_text, encoding="utf-8")
    return True


def main(smoke=False):
    print("=" * 70)
    print("RECUPERATION Glassdoor MA via Firecrawl")
    print("=" * 70)

    incomplete = json.loads(INCOMPLETE_FILE.read_text(encoding="utf-8"))
    if smoke:
        incomplete = incomplete[:3]
        print(f"  [SMOKE] Limit a {len(incomplete)} URLs")
    else:
        print(f"\n[1/3] {len(incomplete)} URLs a recuperer")

    DETAILS_DIR.mkdir(parents=True, exist_ok=True)

    n_scraped = 0
    n_updated = 0
    n_failed = 0
    for i, inc in enumerate(incomplete, 1):
        url = inc["source_url"]
        ref = inc["source_ref"]
        md_path = DETAILS_DIR / f"{ref}.md"
        print(f"  [{i:2d}/{len(incomplete)}] {ref} ...", end=" ", flush=True)

        if firecrawl_scrape(url, md_path):
            n_scraped += 1
            md_text = md_path.read_text(encoding="utf-8", errors="ignore")
            parsed = parse_glassdoor_md(md_text)
            if update_posting(inc["posting_file"], parsed):
                n_updated += 1
                print(f"OK desc={len(parsed['description'])} chars")
            else:
                print(f"PARSE FAIL (desc={len(parsed.get('description') or '')})")
        else:
            n_failed += 1
            print("SCRAPE FAIL")
        time.sleep(SLEEP_BETWEEN)

    print(f"\n{'=' * 70}")
    print(f"  Scrape OK : {n_scraped}/{len(incomplete)}")
    print(f"  Postings updates : {n_updated}/{len(incomplete)}")
    print(f"  Echecs scrape : {n_failed}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    smoke = "--smoke" in sys.argv
    main(smoke=smoke)
