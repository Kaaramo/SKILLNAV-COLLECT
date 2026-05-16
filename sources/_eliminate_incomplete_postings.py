"""
Elimine les postings MA dont la description est < 200 chars.
Renumerote les postings restants en sequence propre.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

COLLECTED = Path(r"F:\Web Mining Project\sources\collected")
SOURCES_MA = ["anapec", "rekrute", "indeed-ma", "linkedin-ma", "pages-carrieres-ma", "glassdoor-ma"]
THRESHOLD = 200


def process_source(source_id):
    p = COLLECTED / source_id / "postings"
    if not p.exists():
        return None

    files = sorted(p.glob("*.json"))
    keep = []  # records that pass the threshold
    eliminated = []

    for j in files:
        try:
            with j.open("r", encoding="utf-8") as f:
                rec = json.load(f)
        except json.JSONDecodeError:
            continue
        desc_len = len(rec.get("description") or "")
        if desc_len >= THRESHOLD:
            keep.append((j, rec))
        else:
            eliminated.append({
                "file": j.name,
                "title": (rec.get("title") or "")[:60],
                "company": (rec.get("company") or "")[:40],
                "desc_len": desc_len,
                "url": rec.get("source_url"),
            })

    n_eliminated = len(eliminated)
    if n_eliminated == 0:
        return {"source": source_id, "kept": len(keep), "eliminated": 0}

    # Suppression des incompletes
    for inc in eliminated:
        json_path = p / inc["file"]
        md_path = p / inc["file"].replace(".json", ".md")
        json_path.unlink(missing_ok=True)
        md_path.unlink(missing_ok=True)

    # Renumeroter les restants
    # On determine le format de numerotation : 3 ou 4 chiffres selon source
    n_total = len(keep)
    digits = max(3, len(str(n_total)))

    # Strategy : ecriture en deux passes pour eviter conflits de noms
    # Pass 1 : rename to .tmp_NNN
    for i, (old_path, rec) in enumerate(keep, start=1):
        new_seq = f"{i:0{digits}d}"
        tmp_json = p / f".tmp_{new_seq}.json"
        tmp_md = p / f".tmp_{new_seq}.md"
        old_md = p / old_path.name.replace(".json", ".md")
        old_path.rename(tmp_json)
        if old_md.exists():
            old_md.rename(tmp_md)

    # Pass 2 : rename .tmp_NNN -> NNN + maj job_id dans JSON + MD
    for i, (_, rec) in enumerate(keep, start=1):
        new_seq = f"{i:0{digits}d}"
        tmp_json = p / f".tmp_{new_seq}.json"
        tmp_md = p / f".tmp_{new_seq}.md"
        final_json = p / f"{new_seq}.json"
        final_md = p / f"{new_seq}.md"

        # Read tmp, update job_id, write final
        with tmp_json.open("r", encoding="utf-8") as f:
            r = json.load(f)
        # Build new job_id with same source prefix
        old_id = r.get("job_id", "")
        if old_id and "-" in old_id:
            prefix = "-".join(old_id.split("-")[:-1])
            r["job_id"] = f"{prefix}-{new_seq}"
        with final_json.open("w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2, default=str)
        tmp_json.unlink()
        if tmp_md.exists():
            tmp_md.rename(final_md)

    # Save log
    log_path = COLLECTED / source_id / "raw" / "_eliminated_incomplete.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(eliminated, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"source": source_id, "kept": n_total, "eliminated": n_eliminated, "log": str(log_path)}


def main():
    print("=" * 70)
    print("ELIMINATION POSTINGS INCOMPLETS (desc < 200 chars)")
    print("=" * 70)

    grand_kept = 0
    grand_eliminated = 0
    for src in SOURCES_MA:
        r = process_source(src)
        if r is None:
            continue
        print(f"\n[{src}]  garde={r['kept']}  elimine={r['eliminated']}")
        if r["eliminated"] > 0:
            print(f"  log : {r.get('log', '')}")
        grand_kept += r["kept"]
        grand_eliminated += r["eliminated"]

    print(f"\n{'=' * 70}")
    print(f"TOTAL : {grand_kept} fiches gardees | {grand_eliminated} eliminees")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
