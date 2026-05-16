"""Identifie les URLs Indeed MA dont la description est < 200 chars."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

POSTINGS = Path(r"F:\Web Mining Project\sources\collected\indeed-ma\postings")
OUTPUT = Path(r"F:\Web Mining Project\sources\collected\indeed-ma\raw\_incomplete_urls.json")

incomplete = []
complete = 0
for j in sorted(POSTINGS.glob("*.json")):
    with j.open("r", encoding="utf-8") as f:
        rec = json.load(f)
    desc_len = len(rec.get("description") or "")
    if desc_len < 200:
        incomplete.append({
            "posting_file": j.name,
            "job_id": rec.get("job_id"),
            "source_ref": rec.get("source_ref"),
            "source_url": rec.get("source_url"),
            "title": (rec.get("title") or "")[:80],
            "company": (rec.get("company") or "")[:50],
            "current_desc_len": desc_len,
        })
    else:
        complete += 1

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(incomplete, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"Total postings indeed-ma : {len(incomplete) + complete}")
print(f"  Complets (>= 200 chars) : {complete}")
print(f"  Incomplets (< 200 chars) : {len(incomplete)}")
print(f"\nSauvegarde : {OUTPUT}")
print(f"\nApercu (5 premiers) :")
for r in incomplete[:5]:
    print(f"  {r['posting_file']} | ref={r['source_ref']} | desc={r['current_desc_len']:3d} | {r['title'][:60]}")

n_with_url = sum(1 for r in incomplete if r['source_url'] and 'indeed' in (r['source_url'] or '').lower())
print(f"\nURLs Indeed valides pour Apify : {n_with_url}/{len(incomplete)}")
