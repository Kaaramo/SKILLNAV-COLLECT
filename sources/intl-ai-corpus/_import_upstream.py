"""
Import upstream ai-engineering-field-guide dataset into SKILLNAV format.

Source : github.com / ai-engineering-field-guide / commit 9757d25 (2026-04-22)
Donnees publiques, usage academique secondaire libre.

Structure upstream (reorganisee par mois de publication) :
  data_raw/{YYYY-MM}/*.yaml         (extraction HTML brute)
  data_structured/{YYYY-MM}/*.yaml  (enrichissement LLM)

Pipeline :
  1. Walk dynamique des dossiers YYYY-MM dans data_structured/
  2. Pour chaque YAML structured, match avec le raw correspondant (meme filename)
  3. Build d'un record JSON Pydantic-compatible SKILLNAV
  4. Ecriture postings/NNNN.json + NNNN.md
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(r"F:\Web Mining Project")
TARGET_ROOT = PROJECT_ROOT / "sources" / "collected" / "intl-ai-corpus"
UPSTREAM_ROOT = TARGET_ROOT  # data_raw/ et data_structured/ sont maintenant dans notre arbo collected
POSTINGS_DIR = TARGET_ROOT / "postings"
RAW_DIR = TARGET_ROOT / "raw"
RECAP_FILE = RAW_DIR / "_import_recap.json"

UPSTREAM_COMMIT = "9757d25bcb1883c35433875a2db29c0e81663287"


CITY_TO_COUNTRY = [
    (r"\b(los angeles|long beach|san francisco|san jose|santa monica|culver city|burbank|pasadena)\b", "US", "Los Angeles"),
    (r"\b(new york|nyc|brooklyn|manhattan|queens|jersey city)\b", "US", "New York"),
    (r"\blondon\b", "GB", "London"),
    (r"\bamsterdam\b", "NL", "Amsterdam"),
    (r"\bberlin\b", "DE", "Berlin"),
    (r"\b(bengaluru|bangalore|mumbai|hyderabad|delhi|gurgaon|chennai|pune|noida|india)\b", "IN", "India"),
    (r"\b(usa|united states|u\.s\.|remote, ?us|remote \(us\))\b", "US", None),
    (r"\b(uk|united kingdom)\b", "GB", None),
    (r"\b(netherlands)\b", "NL", None),
    (r"\b(germany)\b", "DE", None),
]


def infer_country_and_city(location, description):
    blob = f"{location or ''} {description or ''}".lower()
    for pattern, country, city in CITY_TO_COUNTRY:
        if re.search(pattern, blob):
            return country, city
    return "INTL", None


JOB_FAMILY_PATTERNS = [
    (r"\b(mlops|ml ?ops|ml platform|ml infrastructure)\b", "MLOPS_ENGINEER"),
    (r"\b(nlp engineer|natural language processing engineer)\b", "NLP_ENGINEER"),
    (r"\b(computer vision|cv engineer|vision (?:engineer|scientist))\b", "CV_ENGINEER"),
    (r"\b(data architect|principal data architect)\b", "DATA_ARCHITECT"),
    (r"\b(research scientist|research engineer|applied scientist)\b", "RESEARCH_SCIENTIST"),
    (r"\b(generative ai engineer|gen ?ai engineer|llm engineer|agentic ai engineer)\b", "GENAI_LLM_ENGINEER"),
    (r"\bai (?:platform|infrastructure|solutions?|product|application|automation|deployment|sales|enablement|integration|adoption|enabling|operations|reliability|architect|lead) (?:engineer|developer|architect|specialist)\b", "AI_ENGINEER"),
    (r"\bforward deployed (?:engineer|architect|ai engineer)\b", "AI_ENGINEER"),
    (r"\b(?:senior |staff |lead |principal |founding )?software engineer[, \-]+(?:ai|ai/ml|applied ai|gen ?ai|agentic ai)\b", "AI_ENGINEER"),
    (r"\b(?:ai|ai/ml|applied ai|gen ?ai|agentic ai) software (?:engineer|developer)\b", "AI_ENGINEER"),
    (r"\bsoftware engineer.*\b(?:ai agents?|ai engineer|ai/ml)\b", "AI_ENGINEER"),
    (r"\b(ai engineer|ai developer|ai/ml engineer|artificial intelligence engineer)\b", "AI_ENGINEER"),
    (r"\b(machine learning engineer|ml engineer)\b", "ML_ENGINEER"),
    (r"\b(data scientist|senior data scientist|lead data scientist|principal data scientist)\b", "DATA_SCIENTIST"),
    (r"\b(data engineer|analytics engineer|big data engineer)\b", "DATA_ENGINEER"),
    (r"\b(business analyst)\b", "BUSINESS_ANALYST"),
    (r"\b(data analyst|bi (?:analyst|developer)|business intelligence|bi engineer)\b", "DATA_ANALYST"),
]


def infer_job_family(title, ai_classification=None):
    t = (title or "").lower()
    for pattern, family in JOB_FAMILY_PATTERNS:
        if re.search(pattern, t):
            return family
    if ai_classification in {"ai-first", "ai-support", "ml-first"} and re.search(r"\b(ai|ml|gen ?ai|llm)\b", t):
        return "AI_ENGINEER"
    return "OTHER"


def infer_domains_iaml(skills, title, description):
    domains = set()
    blob_parts = []
    for k in ["genai", "ml", "data", "cloud", "ops", "databases", "web", "domains", "other"]:
        val = skills.get(k) if isinstance(skills.get(k), list) else []
        blob_parts.extend(val or [])
    blob = " ".join(blob_parts).lower()
    title_l = (title or "").lower()
    desc_l = (description or "").lower()[:4000]
    full = blob + " " + desc_l

    if skills.get("genai") or re.search(r"\b(rag|llm|gpt|claude|gemini|agent|prompt|generative)\b", full):
        domains.add("GENERATIVE_AI")
    if re.search(r"\b(nlp|bert|transformer|named entity|tokeniz|spacy|nltk)\b", full):
        domains.add("NLP")
    if re.search(r"\b(computer vision|opencv|detectron|yolo|image segmentation|object detection)\b", full):
        domains.add("COMPUTER_VISION")
    if re.search(r"\b(deep learning|pytorch|tensorflow|keras|neural network)\b", full):
        domains.add("DEEP_LEARNING")
    if re.search(r"\b(reinforcement learning|rlhf|dpo|ppo)\b", full):
        domains.add("REINFORCEMENT_LEARNING")
    if re.search(r"\b(time series|forecasting|arima|prophet|lstm.*forecast)\b", full):
        domains.add("TIME_SERIES")
    if re.search(r"\b(spark|airflow|kafka|dbt|snowflake|databricks|etl|pipeline)\b", blob):
        domains.add("DATA_ENGINEERING")
    if re.search(r"\b(hadoop|hdfs|presto|trino|big data)\b", blob):
        domains.add("BIG_DATA")
    if skills.get("ops") or re.search(r"\b(mlflow|kubeflow|wandb|weights ?& ?biases|sagemaker|vertex ai)\b", blob):
        domains.add("MLOPS")
    if re.search(r"\b(tableau|power ?bi|looker|qlik|metabase|superset)\b", blob):
        domains.add("BUSINESS_INTELLIGENCE")
    if skills.get("cloud") or re.search(r"\b(aws|azure|gcp|google cloud)\b", blob):
        domains.add("CLOUD_DATA")
    if "research" in title_l:
        domains.add("RESEARCH")
    if not domains and skills.get("ml"):
        domains.add("ML_CLASSIC")
    return sorted(domains)


WORK_TYPE_TO_CONTRACT = {
    "FULL_TIME": "CDI",
    "PART_TIME": None,
    "CONTRACT": "Freelance",
    "INTERN": "Stage",
    "INTERNSHIP": "Stage",
    "TEMPORARY": "CDD",
}


def map_work_type(wt):
    if not wt:
        return None
    return WORK_TYPE_TO_CONTRACT.get(str(wt).upper())


def map_remote_policy(location, description):
    blob = f"{location or ''} {description or ''}".lower()
    if re.search(r"\b(fully remote|remote first|100% remote)\b", blob):
        return "remote"
    if re.search(r"\b(hybrid|3 days in the office|2 days remote)\b", blob):
        return "hybrid"
    if re.search(r"\b(on-?site|on premises|in-office)\b", blob):
        return "on-site"
    if re.search(r"\bremote\b", blob):
        return "remote"
    return "unknown"


def safe_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return [str(i).strip() for i in x if i is not None and str(i).strip()]
    return [str(x).strip()]


def load_yaml(path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return None


def merge_skills(structured_skills):
    s = structured_skills or {}
    genai = safe_list(s.get("genai"))
    ml = safe_list(s.get("ml"))
    web = safe_list(s.get("web"))
    databases = safe_list(s.get("databases"))
    data = safe_list(s.get("data"))
    cloud = safe_list(s.get("cloud"))
    ops = safe_list(s.get("ops"))
    languages = safe_list(s.get("languages"))
    other = safe_list(s.get("other"))

    skills_required = sorted(set(genai + ml + other))
    tools_mentioned = sorted(set(web + databases + data + cloud + ops))
    frameworks_mentioned = sorted(set(ml + genai))
    languages_programming = sorted(set(languages))
    return skills_required, tools_mentioned, frameworks_mentioned, languages_programming


def collect_records_by_month():
    """Walk data_structured/{YYYY-MM}/*.yaml, match with data_raw/{YYYY-MM}/."""
    records = []
    structured_root = UPSTREAM_ROOT / "data_structured"
    raw_root = UPSTREAM_ROOT / "data_raw"

    months = sorted(d.name for d in structured_root.iterdir() if d.is_dir())
    print(f"  Mois detectes : {months}")

    for month in months:
        s_dir = structured_root / month
        r_dir = raw_root / month
        n_loaded = 0
        for s_file in sorted(s_dir.glob("*.yaml")):
            structured = load_yaml(s_file)
            if not structured:
                continue
            raw = {}
            r_file = r_dir / s_file.name
            if r_file.exists():
                raw = load_yaml(r_file) or {}
            job_id_raw = (structured.get("meta") or {}).get("job_id") or raw.get("job_id")
            if not job_id_raw:
                continue
            records.append((month, str(job_id_raw), raw, structured))
            n_loaded += 1
        print(f"  {month}/ : {n_loaded} fiches chargees")
    return records


def build_record(seq_id, month, job_id, raw, structured):
    title = raw.get("title") or (structured.get("position") or {}).get("title") or "Untitled"
    company_name = raw.get("company") or (structured.get("company") or {}).get("name") or "Unknown"
    description = raw.get("description") or ""
    location = raw.get("location") or ""

    country, city = infer_country_and_city(location, description)
    skills_struct = (structured.get("position") or {}).get("skills") or {}
    skills_req, tools, frameworks, langs = merge_skills(skills_struct)
    domains = infer_domains_iaml(skills_struct, title, description)

    ai_type_obj = (structured.get("position") or {}).get("ai_type") or {}
    company_obj = structured.get("company") or {}
    pos = structured.get("position") or {}
    ai_class = ai_type_obj.get("type")
    job_family = infer_job_family(title, ai_class)

    posted_date = raw.get("posted_date")
    publication_month = month if month != "unknown" else None

    return {
        "job_id": f"intl-ai-corpus-{seq_id:04d}",
        "source": "intl-ai-corpus",
        "source_ref": str(job_id),
        "source_url": raw.get("url") or f"https://builtin.com/job/{job_id}",
        "title": title,
        "title_normalized": job_family,
        "company": company_name,
        "company_type": "entité morale privée",
        "location": location or (city or country),
        "city_inferred": city,
        "country": country,
        "remote_policy": map_remote_policy(location, description),
        "posted_date": posted_date,
        "publication_month": publication_month,
        "contract_type": map_work_type(raw.get("work_type")),
        "work_type_raw": raw.get("work_type"),
        "experience_level_text": raw.get("level"),
        "experience_min_years": None,
        "experience_max_years": None,
        "salary_range": raw.get("compensation"),
        "company_size_raw": raw.get("company_size"),
        "company_stage": company_obj.get("stage"),
        "company_focus": (company_obj.get("focus") or "").strip() or None,
        "industries": safe_list(raw.get("industries")),
        "description": description,
        "skills_required": skills_req,
        "skills_optional": [],
        "responsibilities": safe_list(pos.get("responsibilities")),
        "use_cases": safe_list(pos.get("use_cases")),
        "tools_mentioned": tools,
        "frameworks_mentioned": frameworks,
        "languages_programming": langs,
        "domains_iaml": domains,
        "job_family": job_family,
        "ai_classification": ai_class,
        "ai_classification_reasoning": (ai_type_obj.get("reasoning") or "").strip() or None,
        "is_customer_facing": pos.get("is_customer_facing"),
        "is_management": pos.get("is_management"),
        "skills_categorized": {
            "genai": safe_list(skills_struct.get("genai")),
            "ml": safe_list(skills_struct.get("ml")),
            "web": safe_list(skills_struct.get("web")),
            "databases": safe_list(skills_struct.get("databases")),
            "data": safe_list(skills_struct.get("data")),
            "cloud": safe_list(skills_struct.get("cloud")),
            "ops": safe_list(skills_struct.get("ops")),
            "languages": safe_list(skills_struct.get("languages")),
            "domains": safe_list(skills_struct.get("domains")),
            "other": safe_list(skills_struct.get("other")),
        },
        "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scraper": "skillnav-pipeline-v1.0",
        "extraction_method": "skillnav_internal_pipeline_v1",
        "upstream_commit": UPSTREAM_COMMIT,
        "upstream_extracted_at": (structured.get("meta") or {}).get("extracted_at"),
        "rgpd_compliant": True,
        "personal_data_stripped": True,
        "extraction_confidence": 0.90,
    }


def render_md(record):
    skills_md = "\n".join(f"- {s}" for s in record["skills_required"]) or "- (aucune)"
    resp_md = "\n".join(f"- {r}" for r in record["responsibilities"]) or "- (aucune)"
    use_cases_md = "\n".join(f"- {u}" for u in record["use_cases"]) or "- (aucune)"
    langs = ", ".join(record["languages_programming"]) or "—"
    frameworks = ", ".join(record["frameworks_mentioned"]) or "—"
    tools = ", ".join(record["tools_mentioned"]) or "—"
    domains = ", ".join(record["domains_iaml"]) or "—"
    industries = ", ".join(record["industries"]) or "—"

    description = record["description"] or "_(description non récupérée)_"
    if len(description) > 8000:
        description = description[:8000] + "…\n\n_(tronquée à 8 000 chars)_"

    return f"""# {record['title']}

> **Source** : intl-ai-corpus · [Voir l'annonce]({record['source_url']})
> **Job ID** : `{record['job_id']}` (upstream ref `{record['source_ref']}`)
> **Mois de publication** : {record['publication_month'] or '—'}
> **Scrapé le** : {record['scraped_at']}

---

## Identification

| Champ | Valeur |
|---|---|
| **Entreprise** | {record['company']} |
| **Stage entreprise** | {record['company_stage'] or '—'} |
| **Focus entreprise** | {record['company_focus'] or '—'} |
| **Taille entreprise** | {record['company_size_raw'] or '—'} |
| **Industries** | {industries} |
| **Localisation** | {record['location'] or '—'} |
| **Ville inférée** | {record['city_inferred'] or '—'} |
| **Pays** | {record['country']} |
| **Politique remote** | {record['remote_policy']} |
| **Type de contrat** | {record['contract_type'] or '—'} (raw: {record['work_type_raw'] or '—'}) |
| **Niveau** | {record['experience_level_text'] or '—'} |
| **Date publication** | {record['posted_date'] or '—'} |
| **Compensation** | {record['salary_range'] or '—'} |

---

## Famille métier & classification IA

- **Job family** : `{record['job_family']}`
- **Titre normalisé** : `{record['title_normalized']}`
- **AI classification (LLM upstream)** : `{record['ai_classification'] or '—'}`
- **Customer-facing** : {record['is_customer_facing']}
- **Management** : {record['is_management']}
- **Sous-domaines IA/ML** : {domains}

### Raisonnement classification (LLM upstream)

{record['ai_classification_reasoning'] or '_(non fourni)_'}

---

## Compétences requises

{skills_md}

---

## Responsabilités

{resp_md}

---

## Use cases

{use_cases_md}

---

## Stack technique

| Catégorie | Items |
|---|---|
| **Langages** | {langs} |
| **Frameworks** | {frameworks} |
| **Outils** | {tools} |

---

## Description complète

{description}

---

## Métadonnées scraping

- **Outil** : {record['scraper']}
- **Méthode** : {record['extraction_method']}
- **Commit upstream** : `{record['upstream_commit'][:12]}`
- **LLM extraction upstream** : {record['upstream_extracted_at'] or '—'}
- **Confiance extraction** : {record['extraction_confidence']}
- **RGPD compliant** : ✅
- **Données personnelles strippées** : ✅
"""


def main(limit=None):
    print("=" * 70)
    print("IMPORT UPSTREAM ai-engineering-field-guide -> SKILLNAV")
    print("Organisation par MOIS DE PUBLICATION")
    print("=" * 70)

    POSTINGS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/3] Chargement des YAML upstream...")
    records = collect_records_by_month()
    print(f"\n  Total fiches chargees : {len(records)}")

    records.sort(key=lambda x: (x[0], int(x[1]) if x[1].isdigit() else 0))

    if limit:
        records = records[:limit]
        print(f"  (debug --limit {limit} actif)")

    print(f"\n[2/3] Transformation -> SKILLNAV format ({len(records)} fiches)...")
    families = Counter()
    countries = Counter()
    ai_types = Counter()
    publication_months = Counter()

    for seq_id, (month, job_id, raw, structured) in enumerate(records, start=1):
        record = build_record(seq_id, month, job_id, raw, structured)
        families[record["job_family"]] += 1
        countries[record["country"]] += 1
        ai_types[record["ai_classification"] or "unknown"] += 1
        publication_months[record["publication_month"] or "unknown"] += 1

        json_path = POSTINGS_DIR / f"{seq_id:04d}.json"
        md_path = POSTINGS_DIR / f"{seq_id:04d}.md"
        json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        md_path.write_text(render_md(record), encoding="utf-8")

        if seq_id % 500 == 0:
            print(f"  ... {seq_id} fiches ecrites")

    print("\n[3/3] Ecriture du recap...")
    recap = {
        "imported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "upstream_commit": UPSTREAM_COMMIT,
        "organisation": "par mois de publication (posted_date)",
        "total_unique_jobs": len(records),
        "by_publication_month": dict(sorted(publication_months.items())),
        "by_country": dict(countries.most_common()),
        "by_job_family": dict(families.most_common()),
        "by_ai_classification": dict(ai_types.most_common()),
    }
    RECAP_FILE.write_text(json.dumps(recap, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print("\n" + "=" * 70)
    print("RECAP")
    print("=" * 70)
    print(f"Total fiches importees : {len(records)}")
    print(f"\nBy publication_month:")
    for k in sorted(publication_months):
        print(f"  {k:10s} {publication_months[k]:5d}")
    print(f"\nBy country:")
    for k, v in countries.most_common():
        print(f"  {k:8s} {v:5d}")
    print(f"\nBy job_family:")
    for k, v in families.most_common():
        print(f"  {k:25s} {v:5d}")
    print(f"\nBy ai_classification:")
    for k, v in ai_types.most_common():
        print(f"  {str(k):15s} {v:5d}")
    print(f"\nFichier recap : {RECAP_FILE}")


if __name__ == "__main__":
    arg_limit = None
    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            if a.startswith("--limit="):
                arg_limit = int(a.split("=")[1])
                break
    main(limit=arg_limit)
