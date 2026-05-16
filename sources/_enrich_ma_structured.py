"""
Chantier MA Phase 2 — Enrichissement LLM-style pour les sources MA.

Genere des YAML data_structured/{YYYY-MM}/<ref>_<co>_<title>.yaml conformes au
schema upstream intl-ai-corpus :

  company:
    name, stage, focus
  position:
    title
    ai_type: { type: ai-first|ai-support|ml-first|non-ai, reasoning }
    responsibilities: [...]
    use_cases: [...]
    skills:
      genai, ml, web, databases, data, cloud, ops, languages, domains, other
    is_customer_facing: bool
    is_management: bool
  meta:
    job_id, extracted_at

Les regles de classification ont ete calibrees par Claude Opus 4.7 a partir
de la méthode interne SKILLNAV + des 3 087 exemples intl-ai-corpus.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
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


# ─── 10-DIMENSION SKILLS CATEGORIZATION ────────────────────────────────────
SKILL_DIMENSIONS = {
    "genai": {
        r"\b(rag|retrieval[- ]augmented)\b", r"\blangchain\b", r"\blangraph\b", r"\bllamaindex\b",
        r"\bvector\s*(store|db|database)\b", r"\bpinecone\b", r"\bweaviate\b", r"\bchroma\b",
        r"\bqdrant\b", r"\bfaiss\b", r"\bpgvector\b",
        r"\b(gpt|chatgpt|gpt-4|gpt-5)\b", r"\bclaude\b", r"\bgemini\b", r"\bllama\b",
        r"\bllm\b", r"\bllms\b", r"\bgenerative\s*ai\b", r"\bgenai\b",
        r"\bprompt\s*engineering\b", r"\bprompting\b", r"\bagent[s]?\b", r"\bmulti[- ]?agent\b",
        r"\bfine[- ]?tun(?:e|ing)\b", r"\blora\b", r"\bpeft\b", r"\brlhf\b", r"\bdpo\b",
        r"\bopenai\s*api\b", r"\banthropic\s*api\b", r"\bmcp\b", r"\bfunction\s*calling\b",
        r"\bembeddings?\b", r"\bsemantic\s*search\b", r"\bllmops\b", r"\bdspy\b", r"\bhaystack\b",
        r"\bcrewai\b", r"\bautogen\b", r"\bragas\b",
    },
    "ml": {
        r"\bpytorch\b", r"\btensorflow\b", r"\bkeras\b", r"\bscikit[- ]?learn\b", r"\bxgboost\b",
        r"\blightgbm\b", r"\bcatboost\b", r"\bjax\b", r"\bhugging\s*face\b",
        r"\btransformers\b", r"\bbert\b", r"\bdeep\s*learning\b",
        r"\bneural\s*network[s]?\b", r"\bmachine\s*learning\b", r"\bml\b",
        r"\bspacy\b", r"\bnltk\b", r"\bopencv\b", r"\bdetectron\b", r"\byolo\b",
    },
    "web": {
        r"\brest\s*api[s]?\b", r"\bgraphql\b", r"\bfastapi\b", r"\bflask\b", r"\bdjango\b",
        r"\bexpress(?:\.js)?\b", r"\bnext(?:\.js)?\b", r"\bnuxt\b", r"\bvue(?:\.js)?\b",
        r"\breact(?:\.js)?\b", r"\bangular\b", r"\bsvelte\b", r"\bnode(?:\.js)?\b",
        r"\bgrpc\b", r"\bhtml[5]?\b", r"\bcss[3]?\b", r"\btailwind\b",
    },
    "databases": {
        r"\bpostgresql\b", r"\bpostgres\b", r"\bmysql\b", r"\bmongodb\b", r"\bmongo\b",
        r"\bredis\b", r"\bsqlserver\b", r"\boracle\b", r"\bbigquery\b", r"\bsnowflake\b",
        r"\bcassandra\b", r"\bdynamodb\b", r"\bcosmos\s*db\b", r"\bcouchbase\b", r"\bneo4j\b",
        r"\belasticsearch\b", r"\bsqlite\b",
    },
    "data": {
        r"\bspark\b", r"\bairflow\b", r"\bdbt\b", r"\bdatabricks\b", r"\betl\b",
        r"\bkafka\b", r"\bflink\b", r"\bpandas\b", r"\bnumpy\b", r"\bdata\s*warehouse\b",
        r"\bredshift\b", r"\bdataflow\b", r"\bdata\s*lake\b", r"\bpresto\b", r"\btrino\b",
        r"\bhadoop\b", r"\bhdfs\b", r"\bpipeline\b", r"\bbeam\b", r"\bprefect\b", r"\bdagster\b",
        r"\bsql\b",
    },
    "cloud": {
        r"\baws\b", r"\bazure\b", r"\bgcp\b", r"\bgoogle\s*cloud\b",
        r"\bs3\b", r"\bec2\b", r"\blambda\b", r"\beks\b", r"\bekm\b", r"\bsagemaker\b",
        r"\bvertex\s*ai\b", r"\bbedrock\b", r"\bcloudwatch\b",
    },
    "ops": {
        r"\bdocker\b", r"\bkubernetes\b", r"\bk8s\b", r"\bci/?cd\b",
        r"\bmlflow\b", r"\bkubeflow\b", r"\bwandb\b", r"\bweights\s*&\s*biases\b",
        r"\bterraform\b", r"\bansible\b", r"\bprometheus\b", r"\bgrafana\b", r"\bdatadog\b",
        r"\bjenkins\b", r"\bgithub\s*actions\b", r"\bgitlab\s*ci\b",
    },
    "languages": {
        r"\bpython\b", r"\bjavascript\b", r"\btypescript\b", r"\bjava\b", r"\bgo(?:\s|lang)\b",
        r"\brust\b", r"\bc\+\+\b", r"\bscala\b", r"\br\b", r"\bphp\b", r"\bruby\b",
        r"\bswift\b", r"\bkotlin\b", r"\bmatlab\b",
    },
    "domains": {
        r"\bnlp\b", r"\bnatural\s*language\s*processing\b", r"\bcomputer\s*vision\b",
        r"\btime\s*series\b", r"\bforecasting\b", r"\brecommendation\b",
        r"\bhealthcare\b", r"\bfinance\b", r"\bfintech\b", r"\bautomotive\b",
        r"\bcybersecurity\b", r"\binsurance\b", r"\bretail\b", r"\binsurtech\b",
        r"\brobotics\b", r"\bbiomedical\b", r"\bgenomics\b",
    },
    "other": {
        r"\bstatistics\b", r"\bbiostatistics\b", r"\ba/b\s*testing\b",
        r"\bdata\s*visualization\b", r"\bdashboard\b", r"\bpower\s*bi\b", r"\btableau\b",
        r"\blooker\b", r"\bqlik\b", r"\bproduct\s*management\b", r"\bstakeholder\b",
        r"\bsolutions\s*architecture\b", r"\bconsulting\b", r"\bagile\b", r"\bscrum\b",
    },
}


def categorize_skills(skills_list, description=""):
    """Dispatch flat skills into 10 dimensions + scan description for additional hits."""
    cats = {k: [] for k in SKILL_DIMENSIONS}
    seen = set()
    text = (" ".join(skills_list) + " " + description[:3000]).lower()

    for dim, patterns in SKILL_DIMENSIONS.items():
        for pattern in patterns:
            for match in re.findall(pattern, text):
                m = match.strip() if isinstance(match, str) else str(match)
                if not m or m.lower() in seen:
                    continue
                if len(m) < 2:
                    continue
                cats[dim].append(m)
                seen.add(m.lower())

    for skill in skills_list:
        sl = skill.lower()
        if sl in seen:
            continue
        placed = False
        for dim, patterns in SKILL_DIMENSIONS.items():
            for pattern in patterns:
                if re.search(pattern, sl):
                    cats[dim].append(skill)
                    seen.add(sl)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            cats["other"].append(skill)
            seen.add(sl)

    return {k: sorted(set(v), key=str.lower) for k, v in cats.items()}


# ─── AI TYPE CLASSIFICATION (calibrated rules) ─────────────────────────────
AI_FIRST_TITLE_PATTERNS = re.compile(
    r"\b(ai engineer|ai developer|ml engineer|machine learning engineer|"
    r"applied ai|gen ?ai engineer|llm engineer|agentic|nlp engineer|"
    r"computer vision engineer|cv engineer|research scientist|applied scientist|"
    r"deep learning|prompt engineer)\b",
    re.IGNORECASE,
)
AI_SUPPORT_TITLE_PATTERNS = re.compile(
    r"\b(ai solutions|ai sales|ai account|ai customer|ai forward deployed|"
    r"ai enablement|ai product engineer|ai infrastructure engineer|"
    r"ai platform engineer)\b",
    re.IGNORECASE,
)
ML_FIRST_TITLE_PATTERNS = re.compile(
    r"\b(data scientist|research scientist)\b",
    re.IGNORECASE,
)
NON_AI_TITLE_PATTERNS = re.compile(
    r"\b(data analyst|business analyst|bi developer|bi engineer|"
    r"business intelligence|data engineer|data architect|data manager|"
    r"actuary|quantitative analyst|quant analyst)\b",
    re.IGNORECASE,
)


def classify_ai_type(title, skills_cat, description=""):
    title = title or ""
    has_genai = bool(skills_cat.get("genai"))
    has_ml = bool(skills_cat.get("ml"))
    desc_l = (description or "").lower()
    has_genai_desc = bool(re.search(r"\b(rag|llm|agent|gpt|prompt|fine[- ]?tun|generative ai)\b", desc_l))

    if AI_SUPPORT_TITLE_PATTERNS.search(title):
        return ("ai-support",
                "Customer-facing or platform-supporting role around AI products "
                "(detected via title pattern)")

    if AI_FIRST_TITLE_PATTERNS.search(title) or has_genai or has_genai_desc:
        if has_genai or has_genai_desc:
            return ("ai-first",
                    "Role builds GenAI / LLM / agent systems "
                    "(GenAI skills or LLM/RAG keywords in description)")
        return ("ai-first",
                "Title explicitly indicates AI/ML engineering role")

    if ML_FIRST_TITLE_PATTERNS.search(title) or has_ml:
        return ("ml-first",
                "Traditional ML role focused on model building "
                "(scikit/pytorch/tensorflow without GenAI emphasis)")

    if NON_AI_TITLE_PATTERNS.search(title):
        return ("non-ai",
                "Data role without direct ML/AI model building "
                "(analyst, BI, data engineering)")

    return ("non-ai", "No strong AI/ML signal detected; defaulted to non-ai")


# ─── is_customer_facing / is_management ────────────────────────────────────
CUSTOMER_FACING = re.compile(
    r"\b(solutions?\s*architect|customer|sales\s*engineer|account|client[- ]facing|"
    r"forward\s*deployed|consultant|advisor|presales)\b",
    re.IGNORECASE,
)
MANAGEMENT = re.compile(
    r"\b(lead|head|principal|director|manager|chief|founding|cto|vp|chief\s*data|"
    r"chief\s*technology|chief\s*ai)\b",
    re.IGNORECASE,
)


def detect_customer_facing(title, description):
    blob = f"{title or ''} {(description or '')[:2000]}"
    return bool(CUSTOMER_FACING.search(blob))


def detect_management(title):
    return bool(MANAGEMENT.search(title or ""))


# ─── use_cases extraction (heuristique) ────────────────────────────────────
def extract_use_cases(description):
    if not description:
        return []
    text = description[:6000]
    cases = []
    patterns = [
        (r"customer\s*service\s*automation", "Customer service automation"),
        (r"content\s*generation", "Content generation"),
        (r"chatbot", "Chatbot / conversational AI"),
        (r"document\s*understanding|document\s*processing", "Document understanding"),
        (r"fraud\s*detection", "Fraud detection"),
        (r"recommendation\s*system", "Recommendation systems"),
        (r"forecasting|demand\s*forecast", "Forecasting"),
        (r"anomaly\s*detection", "Anomaly detection"),
        (r"churn\s*prediction", "Churn prediction"),
        (r"personalization", "Personalization"),
        (r"computer\s*vision", "Computer vision"),
        (r"sentiment\s*analysis", "Sentiment analysis"),
        (r"named\s*entity\s*recognition|\bner\b", "NER / entity extraction"),
        (r"summari[zs]ation", "Summarization"),
        (r"translation", "Translation"),
        (r"voice\s*assistant|speech\s*recognition", "Voice / speech AI"),
        (r"predictive\s*model", "Predictive modeling"),
        (r"a/b\s*test", "A/B testing"),
        (r"data\s*pipeline", "Data pipeline engineering"),
        (r"dashboard|reporting", "Dashboarding & reporting"),
        (r"risk\s*management|risk\s*scoring", "Risk management"),
    ]
    seen = set()
    for pattern, label in patterns:
        if re.search(pattern, text, re.IGNORECASE) and label not in seen:
            cases.append(label)
            seen.add(label)
    return cases


# ─── Pipeline ──────────────────────────────────────────────────────────────
def build_structured(record):
    title = record.get("title") or "Untitled"
    company = record.get("company") or "Unknown"
    description = record.get("description") or ""

    skills_flat = list(set(
        (record.get("skills_required") or [])
        + (record.get("tools_mentioned") or [])
        + (record.get("frameworks_mentioned") or [])
        + (record.get("languages_programming") or [])
    ))

    skills_cat = categorize_skills(skills_flat, description)
    ai_type, reasoning = classify_ai_type(title, skills_cat, description)
    responsibilities = record.get("responsibilities") or []
    use_cases = extract_use_cases(description)
    is_cf = detect_customer_facing(title, description)
    is_mgmt = detect_management(title)

    return {
        "company": {
            "name": company,
            "stage": None,
            "focus": record.get("company_description") or None,
        },
        "position": {
            "title": title,
            "ai_type": {
                "type": ai_type,
                "reasoning": reasoning,
            },
            "responsibilities": responsibilities,
            "use_cases": use_cases,
            "skills": skills_cat,
            "is_customer_facing": is_cf,
            "is_management": is_mgmt,
        },
        "meta": {
            "job_id": record.get("source_ref") or record.get("job_id"),
            "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "extraction_method": "skillnav-claude-opus-4-7-rule-based-v1",
        },
    }


def transform_source(source_id):
    src_root = COLLECTED / source_id
    postings_dir = src_root / "postings"
    struct_dir = src_root / "data_structured"

    if not postings_dir.exists():
        return None

    months = Counter()
    ai_types = Counter()
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

        structured = build_structured(record)
        ai_types[structured["position"]["ai_type"]["type"]] += 1

        posted = record.get("posted_date")
        month = str(posted)[:7] if posted else "unknown"
        months[month] += 1

        ref = slug(record.get("source_ref") or record.get("job_id") or "unknown", 30)
        co = slug(record.get("company") or "unknown", 30)
        title = slug(record.get("title") or "unknown", 50)
        base_name = f"{ref}_{co}_{title}"
        filename = f"{base_name}.yaml"

        target_dir = struct_dir / month
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
                structured,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=120,
            )
        n_written += 1

    return {"written": n_written, "conflicts": n_conflicts, "months": dict(months), "ai_types": dict(ai_types)}


def main():
    print("=" * 70)
    print("CHANTIER MA Phase 2 — Enrichissement structured")
    print("(regles calibrees par Claude Opus 4.7, deterministe sur 326 fiches)")
    print("=" * 70)

    grand_total = 0
    global_ai_types = Counter()
    global_months = Counter()

    for source in SOURCES_MA:
        print(f"\n[{source}]")
        result = transform_source(source)
        if result is None:
            print("  (source absente, skip)")
            continue
        print(f"  Total ecrit : {result['written']}")
        print(f"  ai_type :")
        for k, v in sorted(result["ai_types"].items()):
            print(f"    {k} : {v}")
        grand_total += result["written"]
        for k, v in result["ai_types"].items():
            global_ai_types[k] += v
        for m, n in result["months"].items():
            global_months[m] += n

    print("\n" + "=" * 70)
    print(f"TOTAL GLOBAL ECRIT : {grand_total}")
    print(f"\nDistribution AI_TYPE globale (MA) :")
    for k in ["ai-first", "ai-support", "ml-first", "non-ai"]:
        print(f"  {k:12s} : {global_ai_types.get(k, 0)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
