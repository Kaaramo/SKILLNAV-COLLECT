"""
Chantier MA Phase 1 — Restructuration des sources Maroc en 3 couches.

Avant : sources/collected/<source-ma>/postings/NNN.{json,md}
Apres : sources/collected/<source-ma>/data_raw/{YYYY-MM}/<ref>_<co>_<title>.yaml
        sources/collected/<source-ma>/postings/NNN.{json,md}              (couche pivot, intacte)
        sources/collected/<source-ma>/data_structured/{YYYY-MM}/...yaml   (Phase 2, plus tard)

Le YAML produit dans data_raw/ mime le format de la source intl-ai-corpus :
  job_id, title, company, location, work_type, level, skills,
  company_size, description, industries, posted_date, url, source.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(r"F:\Web Mining Project")
COLLECTED = PROJECT_ROOT / "sources" / "collected"
SOURCES_MA = ["anapec", "rekrute", "indeed-ma", "linkedin-ma", "pages-carrieres-ma", "glassdoor-ma"]


def _str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, _str_presenter)


def slug(s, maxlen=50):
    if not s:
        return "unknown"
    s = unicodedata.normalize("NFKD", str(s))
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    s = s.strip("_")
    s = s[:maxlen].strip("_")
    return s or "unknown"


WORK_TYPE_MAP = {
    "CDI": "FULL_TIME",
    "CDD": "TEMPORARY",
    "Stage": "INTERNSHIP",
    "Freelance": "CONTRACT",
    "Alternance": "INTERNSHIP",
    "Intérim": "TEMPORARY",
}


def infer_level(exp_min):
    if exp_min is None:
        return None
    if exp_min >= 7:
        return "Expert/Leader"
    if exp_min >= 3:
        return "Senior"
    if exp_min >= 1:
        return "Mid"
    return "Entry"


def build_raw_yaml(record):
    """Convert SKILLNAV posting record -> upstream-style raw YAML dict."""
    work_type = WORK_TYPE_MAP.get(record.get("contract_type"))
    level = record.get("experience_level_text") or infer_level(record.get("experience_min_years"))
    skills = list(dict.fromkeys((record.get("skills_required") or [])[:10]))

    return {
        "job_id": record.get("source_ref") or record.get("job_id"),
        "title": record.get("title"),
        "company": record.get("company"),
        "location": record.get("location"),
        "work_type": work_type,
        "level": level,
        "skills": skills,
        "company_size": record.get("company_size_raw"),
        "description": record.get("description") or "",
        "industries": record.get("industries") or [],
        "posted_date": record.get("posted_date"),
        "url": record.get("source_url"),
        "source": record.get("source"),
    }


def transform_source(source_id):
    src_root = COLLECTED / source_id
    postings_dir = src_root / "postings"
    raw_dir = src_root / "data_raw"

    if not postings_dir.exists():
        return None

    months = Counter()
    n_written = 0
    n_conflicts = 0
    seen_filenames = set()

    for json_file in sorted(postings_dir.glob("*.json")):
        try:
            with json_file.open("r", encoding="utf-8") as f:
                record = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ! Skip {json_file.name} (JSON error: {e})")
            continue

        raw_data = build_raw_yaml(record)

        posted = record.get("posted_date")
        month = str(posted)[:7] if posted else "unknown"
        months[month] += 1

        ref = slug(record.get("source_ref") or record.get("job_id") or "unknown", 30)
        co = slug(record.get("company") or "unknown", 30)
        title = slug(record.get("title") or "unknown", 50)
        base_name = f"{ref}_{co}_{title}"
        filename = f"{base_name}.yaml"

        target_dir = raw_dir / month
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / filename

        if target_file.exists():
            n_conflicts += 1
            continue

        if filename in seen_filenames:
            i = 1
            while True:
                candidate = target_dir / f"{base_name}_{i:02d}.yaml"
                if not candidate.exists() and candidate.name not in seen_filenames:
                    target_file = candidate
                    break
                i += 1

        seen_filenames.add(target_file.name)

        with target_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                raw_data,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=120,
            )
        n_written += 1

    return {"written": n_written, "conflicts": n_conflicts, "months": dict(months)}


def main():
    print("=" * 70)
    print("CHANTIER MA Phase 1 — Restructuration en 3 couches (data_raw + postings)")
    print("=" * 70)

    grand_total_written = 0
    grand_total_conflicts = 0
    global_months = Counter()

    for source in SOURCES_MA:
        print(f"\n[{source}]")
        result = transform_source(source)
        if result is None:
            print("  (source absente, skip)")
            continue
        print(f"  Total ecrit : {result['written']}")
        print(f"  Conflits resolus : {result['conflicts']}")
        print(f"  Par mois :")
        for m in sorted(result["months"]):
            print(f"    {m} : {result['months'][m]}")
        grand_total_written += result["written"]
        grand_total_conflicts += result["conflicts"]
        for m, n in result["months"].items():
            global_months[m] += n

    print("\n" + "=" * 70)
    print(f"TOTAL GLOBAL ECRIT : {grand_total_written}")
    print(f"TOTAL CONFLITS RESOLUS : {grand_total_conflicts}")
    print(f"\nDistribution GLOBALE par mois (toutes sources MA) :")
    for m in sorted(global_months):
        print(f"  {m} : {global_months[m]}")
    print("=" * 70)


if __name__ == "__main__":
    main()
