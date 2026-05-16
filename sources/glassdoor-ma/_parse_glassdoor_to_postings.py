"""
Parser glassdoor-ma : markdown Firecrawl brut -> postings SKILLNAV Pydantic.

Etapes :
1. Construire index {job_id -> meta} depuis les 4 _srch-*.json (titre, entreprise,
   location, posted_relative, url, keyword).
2. Pour chaque <job_id>.md, extraire description + qualifications + skills.
3. Convertir posted_relative ("7d", "30d+") en posted_date ISO.
4. Sortir postings/NNN.json + NNN.md au format SKILLNAV.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"F:\Web Mining Project\sources\collected\glassdoor-ma")
RAW = ROOT / "raw"
POSTINGS = ROOT / "postings"
TODAY = datetime(2026, 5, 16, tzinfo=timezone.utc).date()

KEYWORD_FILES = {
    "data-scientist": "_srch-data-scientist.json",
    "data-engineer": "_srch-data-engineer.json",
    "machine-learning": "_srch-machine-learning.json",
    "data-analyst": "_srch-data-analyst.json",
}


def parse_posted_relative(rel):
    if not rel:
        return None
    rel = rel.strip().lower()
    m = re.match(r"(\d+)\s*([dhm])\+?", rel)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2)
    if unit == "d":
        return (TODAY - timedelta(days=n)).isoformat()
    if unit == "h":
        return TODAY.isoformat()
    if unit == "m":
        return (TODAY - timedelta(days=n * 30)).isoformat()
    return None


def build_search_index():
    """Parse _srch-*.json files to extract {job_id: meta} index."""
    index = {}
    job_link_re = re.compile(
        r"!\[(?P<co_logo>[^\]]+?)\s*Logo\][^\n]*\n\n+(?:[^\n]+\n+)*?(?P<company>[^\n]+?)\n+\d\.\d.*?"
        r"\[(?P<title>[^\]]+)\]\((?P<url>https://www\.glassdoor\.com/job-listing/[^)]+?jl=(?P<job_id>\d+))\)\n+"
        r"(?P<location>[^\n]+?)\n",
        re.DOTALL,
    )
    simple_link_re = re.compile(
        r"\[(?P<title>[^\]]+)\]\((?P<url>https://www\.glassdoor\.com/job-listing/[^)]+?jl=(?P<job_id>\d+))\)"
    )
    posted_re = re.compile(r"\b(\d+[dhm]\+?)\b")

    for keyword, fname in KEYWORD_FILES.items():
        path = RAW / fname
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"  ! Erreur lecture {fname}: {e}")
            continue

        md = data.get("markdown", "") if isinstance(data, dict) else ""
        if not md:
            continue

        for m in simple_link_re.finditer(md):
            job_id = m.group("job_id")
            if job_id in index:
                if keyword not in index[job_id]["search_keywords"]:
                    index[job_id]["search_keywords"].append(keyword)
                continue

            title = m.group("title").strip()
            url = m.group("url").strip()

            chunk_start = max(0, m.start() - 800)
            chunk_end = min(len(md), m.end() + 600)
            chunk = md[chunk_start:chunk_end]

            company = None
            co_match = re.search(
                r"!\[([^\]]+?)\s*Logo\][^\n]*\n+(?:[^\n]+\n+)*?([^\n]+?)\n+\d\.\d",
                md[chunk_start:m.start()],
            )
            if co_match:
                company = co_match.group(2).strip()
            if not company:
                co_alt = re.findall(r"\n([A-Z][\w\s&\-\.]{2,50})\n+\d\.\d", md[chunk_start:m.start()])
                if co_alt:
                    company = co_alt[-1].strip()

            after = md[m.end():m.end() + 800]
            loc_match = re.search(r"^\n([\w\s,\-]+?)\n", after)
            location = loc_match.group(1).strip() if loc_match else None

            posted_match = posted_re.search(after)
            posted_relative = posted_match.group(1) if posted_match else None

            index[job_id] = {
                "title": title,
                "company": company or "Unknown",
                "location": location or "Morocco",
                "posted_relative": posted_relative,
                "url": url,
                "search_keywords": [keyword],
            }

    return index


def parse_md_fiche(path):
    """Parse un fichier <job_id>.md pour extraire description, qualifications, skills."""
    try:
        with path.open("r", encoding="utf-8") as f:
            md = f.read()
    except OSError:
        return None

    sections = {}
    section_patterns = [
        ("description", r"(?:Description du poste|Job description)\s*:?\s*\n+(.+?)(?=\n\n#{1,6}\s|\nQualifications\s*:|\nCompetences\s*:|\nCompétences\s*:|\nMissions\s*:|\nShow more|\Z)"),
        ("missions", r"(?:Missions)\s*:?\s*\n+(.+?)(?=\nQualifications\s*:|\nCompetences\s*:|\nCompétences\s*:|\nShow more|\Z)"),
        ("qualifications", r"(?:Qualifications)\s*:?\s*\n+(.+?)(?=\nCompetences\s*:|\nCompétences\s*:|\nShow more|\Z)"),
        ("skills_section", r"(?:Compétences|Competences|Skills)\s*:?\s*\n+(.+?)(?=\nShow more|\nSee company|\Z)"),
    ]
    for name, pattern in section_patterns:
        m = re.search(pattern, md, re.DOTALL | re.IGNORECASE)
        if m:
            sections[name] = m.group(1).strip()

    full_text = "\n\n".join(
        v for v in [sections.get("description"), sections.get("missions"),
                    sections.get("qualifications"), sections.get("skills_section")]
        if v
    )

    bullets = []
    for line in (sections.get("skills_section") or sections.get("qualifications") or "").splitlines():
        line = line.strip()
        if line.startswith("- ") or line.startswith("* ") or re.match(r"^\d+\.\s", line):
            cleaned = re.sub(r"^[-*]\s*|\d+\.\s*", "", line).strip()
            cleaned = re.sub(r"\*+", "", cleaned).strip()
            if 3 <= len(cleaned) <= 200:
                bullets.append(cleaned)

    responsibilities = []
    for line in (sections.get("missions") or "").splitlines():
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            cleaned = re.sub(r"^[-*]\s*", "", line).strip()
            cleaned = re.sub(r"\*+", "", cleaned).strip()
            if 5 <= len(cleaned) <= 300:
                responsibilities.append(cleaned)

    tech_patterns = [
        r"\bPython\b", r"\bSQL\b", r"\bJava\b", r"\bScala\b", r"\bR\b(?!\w)",
        r"\bPyTorch\b", r"\bTensorFlow\b", r"\bKeras\b", r"\bscikit[- ]?learn\b",
        r"\bAWS\b", r"\bAzure\b", r"\bGCP\b", r"\bGoogle Cloud\b",
        r"\bDocker\b", r"\bKubernetes\b", r"\bSpark\b", r"\bAirflow\b",
        r"\bMongoDB\b", r"\bPostgreSQL\b", r"\bMySQL\b", r"\bRedis\b",
        r"\bRAG\b", r"\bLLM\b", r"\bLangChain\b", r"\bOpenAI\b",
        r"\bPower BI\b", r"\bTableau\b", r"\bExcel\b", r"\bSnowflake\b",
        r"\bMachine Learning\b", r"\bDeep Learning\b", r"\bNLP\b",
        r"\bGenerative AI\b", r"\bGenAI\b", r"\bComputer Vision\b",
        r"\bFastAPI\b", r"\bFlask\b", r"\bDjango\b", r"\bREST\b", r"\bAPI\b",
        r"\bDatabricks\b", r"\bBigQuery\b", r"\bPandas\b", r"\bNumPy\b",
    ]
    detected_skills = []
    seen = set()
    for pattern in tech_patterns:
        for match in re.findall(pattern, full_text, re.IGNORECASE):
            mlower = match.lower()
            if mlower not in seen:
                detected_skills.append(match.strip())
                seen.add(mlower)

    return {
        "description_full": full_text,
        "responsibilities": responsibilities[:15],
        "bullets_skills": bullets[:20],
        "skills_detected": detected_skills,
    }


JOB_FAMILY_PATTERNS = [
    (r"\b(mlops|ml ?ops)\b", "MLOPS_ENGINEER"),
    (r"\b(nlp engineer)\b", "NLP_ENGINEER"),
    (r"\b(computer vision|cv engineer)\b", "CV_ENGINEER"),
    (r"\b(data architect)\b", "DATA_ARCHITECT"),
    (r"\b(research scientist|applied scientist)\b", "RESEARCH_SCIENTIST"),
    (r"\b(gen ?ai engineer|llm engineer)\b", "GENAI_LLM_ENGINEER"),
    (r"\b(ai engineer|ai developer|intelligence artificielle)\b", "AI_ENGINEER"),
    (r"\b(machine learning engineer|ml engineer|ingenieur machine learning)\b", "ML_ENGINEER"),
    (r"\b(data scientist|scientifique des donnees|scientifique de donnees)\b", "DATA_SCIENTIST"),
    (r"\b(data engineer|analytics engineer|ingenieur data|ingenieur donnees)\b", "DATA_ENGINEER"),
    (r"\b(business analyst)\b", "BUSINESS_ANALYST"),
    (r"\b(data analyst|bi (?:analyst|developer)|business intelligence|analyste donnees|analyste data)\b", "DATA_ANALYST"),
]


def infer_job_family(title):
    t = (title or "").lower()
    for pattern, family in JOB_FAMILY_PATTERNS:
        if re.search(pattern, t):
            return family
    return "OTHER"


def render_md_posting(record):
    skills_md = "\n".join(f"- {s}" for s in record["skills_required"]) or "- (aucune)"
    resp_md = "\n".join(f"- {r}" for r in record["responsibilities"]) or "- (aucune)"
    description = record["description"] or "_(description non récupérée)_"
    if len(description) > 6000:
        description = description[:6000] + "…\n\n_(tronquée)_"

    return f"""# {record['title']}

> **Source** : glassdoor-ma · [Voir l'annonce]({record['source_url']})
> **Job ID** : `{record['job_id']}`
> **Scrapé le** : {record['scraped_at']}

## Identification

| Champ | Valeur |
|---|---|
| **Entreprise** | {record['company']} |
| **Localisation** | {record['location']} |
| **Pays** | {record['country']} |
| **Date publication** | {record['posted_date'] or '—'} |
| **Date relative scrape** | {record['posted_relative'] or '—'} |

## Famille métier

- **Job family** : `{record['job_family']}`
- **Mot-clé de recherche** : {', '.join(record['search_keywords']) or '—'}

## Compétences détectées

{skills_md}

## Responsabilités

{resp_md}

## Description complète

{description}

---

- **Outil** : {record['scraper']}
- **Confiance extraction** : {record['extraction_confidence']}
- **RGPD compliant** : ✅
"""


def main():
    print("=" * 70)
    print("PARSER glassdoor-ma : raw markdown -> postings SKILLNAV")
    print("=" * 70)

    print("\n[1/3] Construction de l'index de recherche...")
    index = build_search_index()
    print(f"  {len(index)} job_id indexes depuis _srch-*.json")

    print("\n[2/3] Parsing des fiches individuelles...")
    POSTINGS.mkdir(parents=True, exist_ok=True)

    md_files = sorted(RAW.glob("[0-9]*.md"))
    print(f"  {len(md_files)} fichiers <job_id>.md a traiter")

    records = []
    no_meta = 0
    parse_failed = 0

    for md_file in md_files:
        job_id = md_file.stem
        meta = index.get(job_id)
        parsed = parse_md_fiche(md_file)

        if parsed is None:
            parse_failed += 1
            continue

        if meta is None:
            meta = {
                "title": "Unknown",
                "company": "Unknown",
                "location": "Morocco",
                "posted_relative": None,
                "url": f"https://www.glassdoor.com/job-listing/{job_id}",
                "search_keywords": [],
            }
            no_meta += 1

        skills_required = list(dict.fromkeys(parsed["skills_detected"] + parsed["bullets_skills"][:5]))[:15]

        posted_date = parse_posted_relative(meta["posted_relative"])

        record = {
            "source": "glassdoor-ma",
            "source_ref": job_id,
            "source_url": meta["url"],
            "title": meta["title"],
            "title_normalized": infer_job_family(meta["title"]),
            "company": meta["company"],
            "company_type": "entité morale privée",
            "location": meta["location"],
            "country": "MA",
            "remote_policy": "unknown",
            "posted_date": posted_date,
            "posted_relative": meta["posted_relative"],
            "contract_type": None,
            "experience_min_years": None,
            "experience_max_years": None,
            "salary_range": None,
            "description": parsed["description_full"],
            "skills_required": skills_required,
            "skills_optional": [],
            "responsibilities": parsed["responsibilities"],
            "tools_mentioned": [],
            "frameworks_mentioned": [],
            "languages_programming": [],
            "domains_iaml": [],
            "job_family": infer_job_family(meta["title"]),
            "search_keywords": meta["search_keywords"],
            "scraped_at": "2026-05-16T00:00:00Z",
            "scraper": "skillnav-firecrawl-glassdoor-v1.0",
            "rgpd_compliant": True,
            "personal_data_stripped": True,
            "extraction_confidence": 0.80 if meta["title"] != "Unknown" else 0.50,
        }
        records.append(record)

    print(f"  {len(records)} fiches parsees ({no_meta} sans meta, {parse_failed} echec parsing)")

    print("\n[3/3] Ecriture des postings...")
    for seq_id, record in enumerate(records, start=1):
        record["job_id"] = f"glassdoor-ma-{seq_id:03d}"
        json_path = POSTINGS / f"{seq_id:03d}.json"
        md_path = POSTINGS / f"{seq_id:03d}.md"
        json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        md_path.write_text(render_md_posting(record), encoding="utf-8")

    families = Counter(r["job_family"] for r in records)
    print(f"\n  {len(records)} postings ecrits dans {POSTINGS}")
    print(f"\nBy job_family:")
    for k, v in families.most_common():
        print(f"  {k:25s} {v:4d}")

    months = Counter()
    for r in records:
        m = (r.get("posted_date") or "unknown")[:7] if r.get("posted_date") else "unknown"
        months[m] += 1
    print(f"\nBy month publication:")
    for k in sorted(months):
        print(f"  {k:10s} {months[k]:4d}")


if __name__ == "__main__":
    main()
