"""
Reorganise les YAML upstream par MOIS DE PUBLICATION (posted_date)
au lieu de date de scrape.

Avant : data_raw/{2026-02-04|2026-02-27|2026-03-27|2026-04-22}/*.yaml
Apres : data_raw/{YYYY-MM}/*.yaml  (ex: 2026-01/, 2026-02/, ...)

Meme logique pour data_structured/. Aucun fichier n'est perdu : si posted_date
est absent/illisible, le fichier va dans un dossier 'unknown/'.
"""
from __future__ import annotations

import shutil
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"F:\Web Mining Project\sources\external\ai-engineering-field-guide\job-market")
RAW = ROOT / "data_raw"
STRUCT = ROOT / "data_structured"
OLD_DATES = ["2026-02-04", "2026-02-27", "2026-03-27", "2026-04-22"]


def get_posted_month(yaml_path: Path) -> str:
    try:
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        pd = (data or {}).get("posted_date") if data else None
        if pd:
            return str(pd)[:7]
    except Exception:
        pass
    return "unknown"


def main() -> None:
    print("=" * 70)
    print("REORGANISATION upstream par MOIS DE PUBLICATION")
    print("=" * 70)

    print("\n[1/4] Lecture posted_date de chaque data_raw/*.yaml ...")
    fname_to_month: dict[str, str] = {}
    counts_per_month: Counter = Counter()
    n_total_raw = 0
    for old_date in OLD_DATES:
        d = RAW / old_date
        if not d.exists():
            print(f"  ! Dossier source absent : {old_date}/ (deja reorganise ?)")
            continue
        local = 0
        for f in d.glob("*.yaml"):
            m = get_posted_month(f)
            fname_to_month[f.name] = m
            counts_per_month[m] += 1
            local += 1
            n_total_raw += 1
        print(f"  {old_date}/ : {local} fichiers analyses")
    print(f"\n  Total raw analyses : {n_total_raw}")
    print(f"  Mois detectes : {sorted(counts_per_month.keys())}")
    for m in sorted(counts_per_month):
        print(f"    {m}: {counts_per_month[m]}")

    print("\n[2/4] Deplacement des fichiers data_raw/ ...")
    moved_raw, skipped_raw = 0, 0
    for old_date in OLD_DATES:
        d = RAW / old_date
        if not d.exists():
            continue
        for f in list(d.glob("*.yaml")):
            month = fname_to_month.get(f.name, "unknown")
            target_dir = RAW / month
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / f.name
            if target_file.exists():
                print(f"  ! Conflit (skip) : {f.name} existe deja dans {month}/")
                skipped_raw += 1
                continue
            shutil.move(str(f), str(target_file))
            moved_raw += 1
        try:
            d.rmdir()
            print(f"  Dossier vide retire : {old_date}/")
        except OSError as e:
            print(f"  ! Impossible de retirer {old_date}/ : {e}")
    print(f"  Deplaces : {moved_raw} | Conflits skip : {skipped_raw}")

    print("\n[3/4] Deplacement des fichiers data_structured/ ...")
    moved_st, skipped_st, no_match_st = 0, 0, 0
    for old_date in OLD_DATES:
        d = STRUCT / old_date
        if not d.exists():
            continue
        for f in list(d.glob("*.yaml")):
            month = fname_to_month.get(f.name)
            if month is None:
                month = "unknown"
                no_match_st += 1
            target_dir = STRUCT / month
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / f.name
            if target_file.exists():
                print(f"  ! Conflit (skip) : {f.name} existe deja dans {month}/")
                skipped_st += 1
                continue
            shutil.move(str(f), str(target_file))
            moved_st += 1
        try:
            d.rmdir()
            print(f"  Dossier vide retire : {old_date}/")
        except OSError as e:
            print(f"  ! Impossible de retirer {old_date}/ : {e}")
    print(f"  Deplaces : {moved_st} | Conflits skip : {skipped_st} | Sans match raw : {no_match_st}")

    print("\n[4/4] Structure finale :")
    for base, label in [(RAW, "data_raw/"), (STRUCT, "data_structured/")]:
        print(f"\n  {label}")
        if not base.exists():
            print("    (dossier absent)")
            continue
        total = 0
        for sub in sorted(base.iterdir(), key=lambda x: x.name):
            if sub.is_dir():
                n = sum(1 for _ in sub.glob("*.yaml"))
                total += n
                print(f"    {sub.name}/  -> {n} fichiers")
        print(f"    TOTAL {label} = {total} fichiers")

    print("\n" + "=" * 70)
    print("Reorganisation terminee. Aucun fichier n'est perdu.")
    print("=" * 70)


if __name__ == "__main__":
    main()
