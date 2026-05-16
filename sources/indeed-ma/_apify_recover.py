"""
Recuperation Indeed MA via Apify actor `misceres/indeed-scraper`.

Etapes :
1. Charge la liste des 73 URLs incompletes
2. POST start un run Apify avec startUrls = ces URLs
3. Polling jusqu'a SUCCEEDED
4. Recupere les items (descriptions completes)
5. Update les postings JSON + MD existants

Usage :
  python _apify_recover.py --smoke   # 5 URLs test
  python _apify_recover.py           # toutes les URLs incompletes
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"F:\Web Mining Project\sources\collected\indeed-ma")
INCOMPLETE_FILE = ROOT / "raw" / "_incomplete_urls.json"
POSTINGS = ROOT / "postings"
APIFY_OUTPUT = ROOT / "raw" / "_apify_recovery_results.json"

ACTOR_ID = "misceres~indeed-scraper"
APIFY_API = "https://api.apify.com/v2"


def get_token():
    env_path = Path(r"F:\Web Mining Project\.env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("APIFY_TOKEN="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("APIFY_TOKEN", "")


def api_post(url, body, token):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def api_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def run_actor(token, urls, country="MA"):
    print(f"  Lancement actor {ACTOR_ID} sur {len(urls)} URLs...")
    body = {
        "startUrls": [{"url": u} for u in urls],
        "country": country,
        "maxItems": len(urls) + 5,
        "saveOnlyUniqueItems": True,
    }
    res = api_post(f"{APIFY_API}/acts/{ACTOR_ID}/runs", body, token)
    run = res.get("data", {})
    run_id = run.get("id")
    print(f"  Run lance : {run_id}")
    return run


def poll_run(token, run_id, max_wait=600):
    print(f"  Polling status...")
    waited = 0
    while waited < max_wait:
        data = api_get(f"{APIFY_API}/actor-runs/{run_id}", token).get("data", {})
        status = data.get("status")
        print(f"    [{waited:3d}s] status={status}", end="\r")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            print()
            return data
        time.sleep(10)
        waited += 10
    raise TimeoutError(f"Run {run_id} did not finish in {max_wait}s")


def fetch_items(token, dataset_id):
    items = api_get(f"{APIFY_API}/datasets/{dataset_id}/items", token)
    return items if isinstance(items, list) else []


def update_posting(posting_file_name, item):
    """Update existing JSON + MD posting with recovered data."""
    json_path = POSTINGS / posting_file_name
    md_path = POSTINGS / posting_file_name.replace(".json", ".md")
    if not json_path.exists():
        return False

    with json_path.open("r", encoding="utf-8") as f:
        rec = json.load(f)

    # Apify Indeed scraper returns: positionName, company, location, salary,
    # jobType, description, url, scrapedAt, etc.
    new_desc = item.get("description") or item.get("descriptionText") or ""
    if not new_desc or len(new_desc) < len(rec.get("description") or ""):
        return False  # pas mieux que ce qu'on avait

    rec["description"] = new_desc
    rec["title"] = item.get("positionName") or rec["title"]
    rec["company"] = item.get("company") or rec["company"]
    rec["location"] = item.get("location") or rec["location"]
    rec["salary_range"] = item.get("salary") or rec.get("salary_range")
    if item.get("jobType"):
        jt = item["jobType"][0] if isinstance(item["jobType"], list) else item["jobType"]
        ct_map = {
            "Temps plein": "CDI", "Full-time": "CDI", "Permanent": "CDI",
            "CDD": "CDD", "Stage": "Stage", "Internship": "Stage",
            "Freelance": "Freelance", "Contract": "Freelance",
        }
        rec["contract_type"] = ct_map.get(jt) or rec.get("contract_type")
    if item.get("postingDateParsed") or item.get("postedDate"):
        rec["posted_date"] = item.get("postingDateParsed") or item.get("postedDate")
    rec["scraper"] = "skillnav-apify-indeed-recovery-v1.0"
    rec["extraction_confidence"] = 0.92
    rec["recovery_via"] = "apify_misceres_indeed_scraper"

    json_path.write_text(json.dumps(rec, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # Mettre a jour le MD : on regenere la section description
    if md_path.exists():
        md_text = md_path.read_text(encoding="utf-8")
        # Replace description section
        import re
        md_text = re.sub(
            r"(## Description complète\n\n)(.+?)(\n\n---\n)",
            lambda m: m.group(1) + new_desc[:6000] + m.group(3),
            md_text,
            flags=re.DOTALL,
        )
        md_path.write_text(md_text, encoding="utf-8")
    return True


def main(smoke=False):
    print("=" * 70)
    print("RECUPERATION Indeed MA via Apify")
    print("=" * 70)

    token = get_token()
    if not token:
        print("! APIFY_TOKEN absent")
        return

    incomplete = json.loads(INCOMPLETE_FILE.read_text(encoding="utf-8"))
    print(f"\n[1/4] {len(incomplete)} URLs incompletes chargees")

    if smoke:
        incomplete = incomplete[:5]
        print(f"  [SMOKE] Limit a {len(incomplete)} URLs")

    # Build URL → posting_file map
    url_to_file = {r["source_url"]: r["posting_file"] for r in incomplete if r["source_url"]}
    urls = list(url_to_file.keys())

    print(f"\n[2/4] Lancement Apify actor...")
    run = run_actor(token, urls)
    run_id = run.get("id")
    if not run_id:
        print(f"! Erreur: pas de run_id retourne")
        return

    print(f"\n[3/4] Attente fin du run...")
    final = poll_run(token, run_id)
    if final.get("status") != "SUCCEEDED":
        print(f"! Run {final.get('status')} — abort")
        print(f"  details: {final.get('statusMessage', '')}")
        return

    dataset_id = final.get("defaultDatasetId")
    print(f"  Dataset : {dataset_id}")

    print(f"\n[4/4] Recuperation items + update postings...")
    items = fetch_items(token, dataset_id)
    APIFY_OUTPUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  {len(items)} items recuperes (sauve dans {APIFY_OUTPUT.name})")

    n_updated = 0
    n_skipped = 0
    for item in items:
        url = item.get("url") or item.get("externalApplyLink") or ""
        # match by source_ref / jobkey
        jk = ""
        if "jk=" in url:
            jk = url.split("jk=")[1].split("&")[0]
        # find matching posting
        match_file = None
        for inc in incomplete:
            if inc["source_ref"] == jk or inc["source_url"] == url:
                match_file = inc["posting_file"]
                break
        if match_file:
            if update_posting(match_file, item):
                n_updated += 1
            else:
                n_skipped += 1
        else:
            n_skipped += 1

    print(f"\n  Postings updates : {n_updated}")
    print(f"  Items sans match : {n_skipped}")

    print(f"\n{'=' * 70}")
    print(f"Recuperation terminee.")
    print(f"  Stats Apify : compute units = {final.get('stats', {}).get('computeUnits', '?'):.4f}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    smoke = "--smoke" in sys.argv
    main(smoke=smoke)
