"""
Recuperation Glassdoor MA via Apify actor `bebity/glassdoor-jobs-scraper`.

Usage :
  python _apify_recover.py --smoke   # 5 URLs test
  python _apify_recover.py           # toutes les URLs incompletes
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"F:\Web Mining Project\sources\collected\glassdoor-ma")
INCOMPLETE_FILE = ROOT / "raw" / "_incomplete_urls.json"
POSTINGS = ROOT / "postings"
APIFY_OUTPUT = ROOT / "raw" / "_apify_recovery_results.json"

ACTOR_ID = "memo23~glassdoor-scraper-ppr"
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
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def api_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def run_actor(token, urls):
    print(f"  Lancement {ACTOR_ID} sur {len(urls)} URLs...")
    body = {
        "startUrls": [{"url": u} for u in urls],
        "maxItems": len(urls) + 5,
    }
    res = api_post(f"{APIFY_API}/acts/{ACTOR_ID}/runs", body, token)
    return res.get("data", {})


def poll_run(token, run_id, max_wait=900):
    print(f"  Polling status...")
    waited = 0
    while waited < max_wait:
        data = api_get(f"{APIFY_API}/actor-runs/{run_id}", token).get("data", {})
        status = data.get("status")
        print(f"    [{waited:3d}s] status={status}", end="\r")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            print()
            return data
        time.sleep(15)
        waited += 15
    raise TimeoutError(f"Run {run_id} did not finish in {max_wait}s")


def fetch_items(token, dataset_id):
    items = api_get(f"{APIFY_API}/datasets/{dataset_id}/items", token)
    return items if isinstance(items, list) else []


def html_to_text(html):
    if not html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "- ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&agrave;", "à").replace("&eacute;", "é").replace("&egrave;", "è")
                 .replace("&ecirc;", "ê").replace("&ocirc;", "ô").replace("&icirc;", "î")
                 .replace("&acirc;", "â").replace("&ucirc;", "û").replace("&ccedil;", "ç")
                 .replace("&Eacute;", "É").replace("&nbsp;", " ").replace("&amp;", "&")
                 .replace("&quot;", '"').replace("&#39;", "'").replace("&rsquo;", "'")
                 .replace("&lsquo;", "'").replace("&laquo;", "«").replace("&raquo;", "»"))
    text = re.sub(r"&[a-z]+;", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def update_posting(posting_file_name, item):
    json_path = POSTINGS / posting_file_name
    md_path = POSTINGS / posting_file_name.replace(".json", ".md")
    if not json_path.exists():
        return False

    with json_path.open("r", encoding="utf-8") as f:
        rec = json.load(f)

    # Format memo23 : item.companyDetails.data.jobView.{job, header}
    cd = (item.get("companyDetails") or {}).get("data") or {}
    jv = cd.get("jobView") or {}
    job = jv.get("job") or {}
    header = jv.get("header") or {}

    # Description : peut être au top level OU dans job.description
    raw_desc = item.get("description") or job.get("description") or ""
    new_desc = html_to_text(raw_desc) if raw_desc else ""

    if not new_desc or len(new_desc) < len(rec.get("description") or ""):
        return False

    rec["description"] = new_desc

    title = header.get("jobTitleText") or job.get("jobTitleText") or rec.get("title")
    if title:
        rec["title"] = title

    company = header.get("employerNameFromSearch") or rec.get("company")
    if company:
        rec["company"] = company

    location = header.get("locationName") or rec.get("location")
    if location:
        rec["location"] = location

    # Salaire (rare sur Glassdoor MA)
    if header.get("payPercentile50"):
        cur = header.get("payCurrency", "")
        period = header.get("payPeriod", "")
        rec["salary_range"] = f"{header['payPercentile50']} {cur} ({period})".strip()

    # Posted_date depuis ageInDays
    age = header.get("ageInDays")
    if age is not None:
        from datetime import datetime, timedelta, timezone
        d = (datetime.now(timezone.utc).date() - timedelta(days=age))
        rec["posted_date"] = d.isoformat()

    rec["scraper"] = "skillnav-apify-glassdoor-recovery-v1.0"
    rec["extraction_confidence"] = 0.92
    rec["recovery_via"] = "apify_memo23_glassdoor_scraper_ppr"

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
    print("RECUPERATION Glassdoor MA via Apify")
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

    url_to_file = {r["source_url"]: r["posting_file"] for r in incomplete if r["source_url"]}
    urls = list(url_to_file.keys())

    print(f"\n[2/4] Lancement Apify...")
    run = run_actor(token, urls)
    run_id = run.get("id")
    print(f"  Run lance : {run_id}")

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
    print(f"  {len(items)} items recuperes")

    # Build {source_ref → posting_file}
    ref_to_file = {r["source_ref"]: r["posting_file"] for r in incomplete}

    n_updated = 0
    for item in items:
        # Match by listingId = source_ref
        cd = (item.get("companyDetails") or {}).get("data") or {}
        jv = cd.get("jobView") or {}
        job = jv.get("job") or {}
        listing_id = str(job.get("listingId") or "")
        match_file = ref_to_file.get(listing_id)
        if match_file and update_posting(match_file, item):
            n_updated += 1

    print(f"\n  Postings updates : {n_updated}")
    cu = final.get("stats", {}).get("computeUnits", 0)
    print(f"\n  Compute units : {cu:.4f} (~${cu * 0.20:.4f} a $0.20/CU)")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    smoke = "--smoke" in sys.argv
    main(smoke=smoke)
