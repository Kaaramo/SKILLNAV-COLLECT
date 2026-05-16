"""
Audit qualité des fiches MA : description vide, courte, exploitable.

Pour chaque source MA, calcule :
- Total fiches
- Description vide (len == 0)
- Description courte (1-200 chars) — quasi inutile pour NER
- Description moyenne (201-500 chars) — pauvre
- Description correcte (501-1500 chars) — exploitable
- Description riche (>1500 chars) — top
- Salary range present
- Skills_required count moyen
- Posted_date present
"""
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

COLLECTED = Path(r"F:\Web Mining Project\sources\collected")
SOURCES_MA = ["anapec", "rekrute", "indeed-ma", "linkedin-ma", "pages-carrieres-ma", "glassdoor-ma"]


def bucket_desc(n):
    if n == 0:
        return "0_vide"
    if n <= 200:
        return "1_courte_200"
    if n <= 500:
        return "2_moyenne_500"
    if n <= 1500:
        return "3_correcte_1500"
    return "4_riche_1500plus"


def audit_source(source_id):
    p = COLLECTED / source_id / "postings"
    if not p.exists():
        return None
    files = sorted(p.glob("*.json"))
    n = len(files)
    desc_buckets = Counter()
    n_with_salary = 0
    n_with_posted_date = 0
    n_with_company = 0
    skill_counts = []
    incomplete_files = []  # description < 200 chars

    for f in files:
        try:
            with f.open("r", encoding="utf-8") as fh:
                rec = json.load(fh)
        except Exception:
            continue
        desc = rec.get("description") or ""
        bucket = bucket_desc(len(desc))
        desc_buckets[bucket] += 1
        if len(desc) < 200:
            incomplete_files.append({
                "file": f.name,
                "title": rec.get("title", "?")[:60],
                "company": rec.get("company", "?")[:30],
                "desc_len": len(desc),
                "url": rec.get("source_url", ""),
            })
        if rec.get("salary_range"):
            n_with_salary += 1
        if rec.get("posted_date"):
            n_with_posted_date += 1
        if rec.get("company") and rec.get("company") not in ("Unknown", "Anonyme", ""):
            n_with_company += 1
        skill_counts.append(len(rec.get("skills_required") or []))

    avg_skills = sum(skill_counts) / max(len(skill_counts), 1)
    return {
        "total": n,
        "desc_buckets": dict(desc_buckets),
        "n_incomplete_lt_200": sum(1 for x in incomplete_files),
        "n_with_salary": n_with_salary,
        "n_with_posted_date": n_with_posted_date,
        "n_with_company": n_with_company,
        "avg_skills_required": round(avg_skills, 1),
        "incomplete_sample": incomplete_files[:10],
    }


def main():
    print("=" * 80)
    print("AUDIT QUALITE — Postings MA")
    print("=" * 80)

    grand_total = 0
    grand_incomplete = 0

    for src in SOURCES_MA:
        r = audit_source(src)
        if r is None:
            continue
        print(f"\n┌─ {src.upper()} ────────────────────────────────")
        print(f"│ Total fiches              : {r['total']}")
        print(f"│ Avec description >= 200   : {r['total'] - r['n_incomplete_lt_200']:4d}  ({100*(r['total']-r['n_incomplete_lt_200'])/max(r['total'],1):.0f}%)")
        print(f"│ Avec description < 200    : {r['n_incomplete_lt_200']:4d}  ← À RÉCUPÉRER OU ÉLIMINER")
        print(f"│")
        print(f"│ Distribution longueur desc :")
        for b in sorted(r['desc_buckets']):
            n = r['desc_buckets'][b]
            label = {
                "0_vide": "VIDE                     ",
                "1_courte_200": "courte (1-200 chars)     ",
                "2_moyenne_500": "moyenne (201-500)        ",
                "3_correcte_1500": "correcte (501-1500)      ",
                "4_riche_1500plus": "riche (1500+ chars)      ",
            }[b]
            pct = 100 * n / max(r['total'], 1)
            print(f"│   {label} : {n:4d} ({pct:.0f}%)")
        print(f"│")
        print(f"│ Avec salaire             : {r['n_with_salary']:4d}  ({100*r['n_with_salary']/max(r['total'],1):.0f}%)")
        print(f"│ Avec posted_date         : {r['n_with_posted_date']:4d}  ({100*r['n_with_posted_date']/max(r['total'],1):.0f}%)")
        print(f"│ Avec company identifiée  : {r['n_with_company']:4d}  ({100*r['n_with_company']/max(r['total'],1):.0f}%)")
        print(f"│ Skills_required moyen    : {r['avg_skills_required']}")
        if r['incomplete_sample']:
            print(f"│")
            print(f"│ Exemples de fiches incomplètes (top 5) :")
            for f in r['incomplete_sample'][:5]:
                print(f"│   {f['file']}  desc={f['desc_len']:3d}  {f['title']}")
        grand_total += r['total']
        grand_incomplete += r['n_incomplete_lt_200']

    print(f"\n{'=' * 80}")
    print(f"GRAND TOTAL : {grand_total} fiches MA")
    print(f"  Avec description exploitable (>= 200 chars) : {grand_total - grand_incomplete} ({100*(grand_total-grand_incomplete)/max(grand_total,1):.0f}%)")
    print(f"  À récupérer ou éliminer (< 200 chars)      : {grand_incomplete} ({100*grand_incomplete/max(grand_total,1):.0f}%)")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
