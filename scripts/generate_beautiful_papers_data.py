#!/usr/bin/env python3
"""
Generate precomputed data for 'Beautiful Papers' section:
- Spans the complete decade of ISLS scholarship (2016–2026, 4,100+ papers).
- Ingests both modern proceedings (2023–2026) and pre-2023 section datasets (2016–2022).
- Distinguishes and separates:
  1. Full Papers (Empirical Full / Long Papers)
  2. Short Papers (Empirical Short Papers)
  3. Others / Symposia (Symposia, Chaired Sessions, Workshops, Keynotes)
- Multi-Year Cohort Buckets:
  - '2016-2018': Early Repository Era
  - '2019-2020': Virtual & Transition Era
  - '2021-2022': Hybrid Re-emergence Era
  - '2023-2024': Modern Unified ISLS Era
  - '2025-2026': GenAI & Contemporary Frontier
  Also provides individual year distributions ('2016' through '2026') and 'All'.
- Precomputes distributions (KDE, median, Q1, Q3, IQR, min, max, p95) partitioned by group and era.
- Extracts section length outliers (Max & Min) for Full Papers, Short Papers, and Others/Symposia.
"""

import os
import json
import re
import numpy as np
from collections import defaultdict
from scipy.stats import gaussian_kde

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED_DIR = os.path.join(BASE_DIR, "data", "derived")
WEB_DIR = os.path.join(BASE_DIR, "web")
PRE2023_PATH = os.path.join(DERIVED_DIR, "pre2023_sections.json")
REGISTRY_PATH = os.path.join(DERIVED_DIR, "ground_truth_registry.json")

SECTIONS_ORDER = [
    "Abstract & Introduction",
    "Methodology & Context",
    "Results & Findings",
    "Discussion & Conclusion",
    "References & Back Matter"
]

CORE_SECTIONS = [
    "Abstract & Introduction",
    "Methodology & Context",
    "Results & Findings",
    "Discussion & Conclusion"
]

COHORT_BUCKETS = [
    ("2016-2018", lambda y: 2016 <= y <= 2018, "Early Repository Era (2016–2018)"),
    ("2019-2020", lambda y: 2019 <= y <= 2020, "Virtual & Transition Era (2019–2020)"),
    ("2021-2022", lambda y: 2021 <= y <= 2022, "Hybrid Re-emergence (2021–2022)"),
    ("2023-2024", lambda y: 2023 <= y <= 2024, "Modern Unified Era (2023–2024)"),
    ("2025-2026", lambda y: 2025 <= y <= 2026, "GenAI & Contemporary Frontier (2025–2026)")
]

SECTION_DESCRIPTIONS = {
    "Abstract & Introduction": "Front-matter distillation, theoretical framing, problem statement, research questions, and literature grounding.",
    "Methodology & Context": "Research design, participant demographics, study contexts, and analytical protocols.",
    "Results & Findings": "Empirical evidence, qualitative interaction transcripts, statistical models, and case findings.",
    "Discussion & Conclusion": "Theoretical synthesis, design/pedagogical implications, limitations, and future directions.",
    "References & Back Matter": "Complete scholarly bibliographies, citations, acknowledgments, and appendices."
}

OUTLIER_CONTEXTS = {
    ("Abstract & Introduction", "high"): "Extensive theoretical grounding and front-matter distillation dedicating comprehensive framing and foundational literature.",
    ("Abstract & Introduction", "low"): "Concise, rapid problem statement that transitions immediately into experimental or pedagogical design.",
    ("Methodology & Context", "high"): "Comprehensive multi-framework methodological architecture detailing mechanisms, empirical data pipelines, and analytical rubrics.",
    ("Methodology & Context", "low"): "Highly condensed, minimalist design brief that summarizes iterative methodology in under two paragraphs.",
    ("Results & Findings", "high"): "In-depth qualitative and quantitative empirical findings presenting extensive interaction transcripts and multi-case observations.",
    ("Results & Findings", "low"): "Short conceptual piece that embeds preliminary findings directly into theoretical arguments, leaving a minimal standalone results section.",
    ("Discussion & Conclusion", "high"): "Broad theoretical discussion synthesizing systemic implications, relational ontologies, and educational justice.",
    ("Discussion & Conclusion", "low"): "Laser-focused concluding remarks delivering immediate takeaways in a single summary paragraph.",
    ("References & Back Matter", "high"): "Massive interdisciplinary bibliography consolidating scholarship across learning sciences and cognitive psychology.",
    ("References & Back Matter", "low"): "Lean, highly selective reference list prioritizing only immediate foundational sources to stay within strict page bounds."
}

AFFILIATIONS_AND_NON_NAMES = {
    'university', 'college', 'school', 'institute', 'department', 'laboratory', 'lab',
    'united states', 'los angeles', 'new york', 'california', 'boston', 'chicago',
    'germany', 'canada', 'china', 'uk', 'netherlands', 'spain', 'france', 'australia',
    'japan', 'korea', 'gmbh', 'inc', 'llc', 'corp', 'foundation', 'center', 'centre',
    'faculty', 'council', 'educational testing service', 'learnology labs', 'mindset copilot',
    'district', 'drexel', 'ucla', 'mit', 'stanford', 'harvard', 'carnegie mellon',
    'georgia institute of technology', 'raspberry pi foundation', 'google research',
    'google deepmind', 'impact accelerator', 'phantom llc', 'massachusetts institute of technology',
    'new york jobs ceo council', 'digital promise', 'hadassah academic college jerusalem'
}

def is_title_spillover(author_str: str, title_str: str) -> bool:
    if not author_str or not title_str:
        return False
    a = author_str.strip()
    t = title_str.strip()
    if len(a) < 3 or len(t) < 5:
        return False

    a_norm = re.sub(r'[^a-z0-9 ]', '', a.lower()).strip()
    t_norm = re.sub(r'[^a-z0-9 ]', '', t.lower()).strip()

    if not a_norm or not t_norm:
        return False

    if t_norm.endswith(a_norm):
        return True

    a_words = a_norm.split()
    t_words = t_norm.split()
    if len(a_words) >= 2 and len(t_words) >= 2:
        for k in range(min(len(a_words), len(t_words)), 1, -1):
            if a_words[-k:] == t_words[-k:]:
                return True

    if re.match(r'^(and|in|the|of|for|with|through|to|from|by|on|at|during|across|within|towards|toward|into)\b', a, re.I):
        if a_norm in t_norm:
            return True

    if len(a_words) >= 3 and a_norm in t_norm:
        return True

    return False

def is_affiliation_or_invalid(author_str: str) -> bool:
    if not author_str:
        return True
    a_lower = author_str.lower().strip()
    if len(a_lower) < 2:
        return True
    if '@' in a_lower or 'http' in a_lower or any(char.isdigit() for char in a_lower):
        return True
    if any(aff in a_lower for aff in AFFILIATIONS_AND_NON_NAMES):
        return True
    return False

def clean_author_name(author_str: str) -> str:
    a = author_str.strip()
    # Strip role markers like (co-chair), (chair), (discussant), (organizer)
    a = re.sub(r'\s*\((?:co-)?chair[s]?\)', '', a, flags=re.IGNORECASE).strip()
    a = re.sub(r'\s*\((?:organizer|discussant|session chair)[s]?\)', '', a, flags=re.IGNORECASE).strip()
    a = re.sub(r'^(?:and|&)\s+', '', a, flags=re.IGNORECASE).strip()
    a = re.sub(r'[;,.]+$', '', a).strip()
    return a

def to_first_last(name: str) -> str:
    name = clean_author_name(name)
    name = re.sub(r'\s*\([^)]*\)', '', name).strip()
    name = re.sub(r'\*+$', '', name).strip()
    if ',' in name:
        parts = [p.strip() for p in name.split(',') if p.strip()]
        if len(parts) == 2 and not any(w in parts[1].lower() for w in ['inc', 'llc', 'jr', 'sr', 'iii', 'iv', 'ltd', 'dept', 'lab', 'group']):
            return f"{parts[1]} {parts[0]}"
    return name

def sanitize_author_names(raw_authors: list, title: str) -> list:
    extracted = []
    for item in raw_authors:
        if isinstance(item, dict):
            disp = (item.get("display_name") or item.get("name") or "").strip()
            given = (item.get("given_name") or "").strip()
            family = (item.get("family_name") or "").strip()
            if given and family and not is_title_spillover(f"{given} {family}", title) and not is_affiliation_or_invalid(f"{given} {family}"):
                name = f"{given} {family}"
            else:
                name = disp
        else:
            name = str(item).strip()

        name = to_first_last(name)
        for part in re.split(r'[;]', name):
            part = clean_author_name(part)
            part = to_first_last(part)
            if part and part not in extracted:
                extracted.append(part)

    clean_list = []
    for a in extracted:
        if is_title_spillover(a, title):
            continue
        if is_affiliation_or_invalid(a):
            continue
        if a not in clean_list:
            clean_list.append(a)

    return clean_list

def categorize_section(heading, canonical_roles, sec_idx, total_secs):
    h = (heading or '').lower().strip()
    roles = [r.lower() for r in canonical_roles]
    
    # 1. References & Back Matter
    if 'reference' in h or 'bibliography' in h or 'works cited' in h or 'acknowledg' in h or 'appendi' in h:
        return 'References & Back Matter'
    if sec_idx == total_secs - 1 and ('ref' in h or len(h) == 0):
        return 'References & Back Matter'
        
    # 2. Discussion & Conclusion
    if 'conclusion' in h or 'concluding' in h or 'future work' in h or 'summary' in h or 'conclusion' in roles:
        return 'Discussion & Conclusion'
    if 'discussion' in h or 'implication' in h or 'limitation' in h or 'discussion' in roles:
        return 'Discussion & Conclusion'
        
    # 3. Results & Findings
    if 'finding' in h or 'result' in h or 'results' in roles or 'case study' in h or 'empirical' in h:
        return 'Results & Findings'
        
    # 4. Methodology & Context
    if 'method' in h or 'methodology' in h or 'data collection' in h or 'participants' in h or 'context' in h or 'procedure' in h or 'design' in h or 'method' in roles:
        return 'Methodology & Context'
    if 'analysis' in h or 'analysis' in roles:
        return 'Methodology & Context' if sec_idx < total_secs / 2 else 'Results & Findings'

    # 5. Abstract & Introduction
    if 'abstract' in h or 'intro' in h or 'background' in h or 'theoretical' in h or 'literature' in h or 'framework' in h or 'overview' in h or 'motivation' in h or 'introduction' in roles:
        return 'Abstract & Introduction'
    if sec_idx == 0:
        return 'Abstract & Introduction'
        
    # Positional fallback guarantees 100% token attribution
    ratio = sec_idx / max(1, total_secs - 1)
    if ratio < 0.25:
        return 'Abstract & Introduction'
    elif ratio < 0.50:
        return 'Methodology & Context'
    elif ratio < 0.75:
        return 'Results & Findings'
    else:
        return 'Discussion & Conclusion'

def compute_dist_dict(arr_dict):
    dist_res = {}
    for sec in SECTIONS_ORDER:
        arr = np.array(arr_dict.get(sec, []))
        if len(arr) == 0:
            continue
            
        median_val = float(np.median(arr))
        mean_val = float(np.mean(arr))
        q1 = float(np.percentile(arr, 25))
        q3 = float(np.percentile(arr, 75))
        iqr = q3 - q1
        min_val = float(np.min(arr))
        max_val = float(np.max(arr))
        p95_val = float(np.percentile(arr, 95))
        
        upper_limit = max(p95_val, q3 + 1.5 * iqr, 300)
        x_eval = np.linspace(0, upper_limit, 25)
        
        pos_arr = arr[arr > 0]
        if len(pos_arr) > 5:
            try:
                kde = gaussian_kde(pos_arr)
                density = kde(x_eval)
                max_d = np.max(density) if np.max(density) > 0 else 1.0
                norm_density = [round(float(d / max_d), 4) for d in density]
            except Exception:
                norm_density = [round(float(max(0.05, 1.0 - abs(x - median_val)/upper_limit)), 4) for x in x_eval]
        else:
            norm_density = [0.1] * len(x_eval)

        kde_points = [{"x": round(float(x_val), 1), "y": d_val} for x_val, d_val in zip(x_eval, norm_density)]

        dist_res[sec] = {
            "section": sec,
            "median": round(median_val, 1),
            "mean": round(mean_val, 1),
            "q1": round(q1, 1),
            "q3": round(q3, 1),
            "iqr": round(iqr, 1),
            "min": round(min_val, 1),
            "max": round(max_val, 1),
            "p95": round(p95_val, 1),
            "sample_count": len(arr),
            "kde": kde_points
        }
    return dist_res

def get_bucket_for_year(year: int) -> str:
    for b_name, b_fn, _ in COHORT_BUCKETS:
        if b_fn(year):
            return b_name
    return "2025-2026"

def generate_data():
    print("=== Generating 'Beautiful Papers' Token Data Across the Decade (2016–2026) ===")

    # Setup storage for groups: all (core empirical), full, short, other (symposia/workshops)
    groups = ["all", "full", "short", "other"]
    tokens_store = {g: defaultdict(lambda: defaultdict(list)) for g in groups}
    paper_records_by_type = {g: defaultdict(list) for g in groups}
    counts = {g: {"total": 0, "by_year": defaultdict(int), "by_bucket": defaultdict(int), "tokens": 0} for g in groups}

    # Load verified authors from proceedings.db
    db_path = os.path.join(BASE_DIR, "proceedings.db")
    db_authors_by_id = {}
    db_authors_by_title = {}
    db_paper_types = {}
    if os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''
                SELECT p.id, p.title, p.paper_type, GROUP_CONCAT(a.display_name, '; ')
                FROM papers p
                LEFT JOIN paper_authors pa ON p.id = pa.paper_id
                LEFT JOIN authors a ON pa.author_id = a.id
                GROUP BY p.id
            ''')
            for row in c.fetchall():
                p_id, p_title, p_ptype, p_auths = row
                if p_id:
                    db_authors_by_id[p_id] = p_auths
                    db_paper_types[p_id] = p_ptype
                if p_title:
                    norm_t = re.sub(r'[^a-z0-9]', '', p_title.lower())
                    db_authors_by_title[norm_t] = p_auths
            conn.close()
        except Exception as e:
            print(f"Warning: Could not read proceedings.db: {e}")

    # 1. Ingest Modern Proceedings (2023–2026)
    vol_dirs = sorted([d for d in os.listdir(DERIVED_DIR) if os.path.isdir(os.path.join(DERIVED_DIR, d)) and d.endswith("-proceedings")])
    for v in vol_dirs:
        json_path = os.path.join(DERIVED_DIR, v, f"{v}.json")
        if not os.path.exists(json_path):
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            d = json.load(f)

        conf_year = d.get("conference", {}).get("year", 2024)
        conf_acronym = d.get("conference", {}).get("acronym", "ISLS")
        bucket = get_bucket_for_year(conf_year)

        for p in d.get("papers", []):
            pid = p.get("id")
            title = (p.get("title") or "").strip()
            norm_t = re.sub(r'[^a-z0-9]', '', title.lower())
            p_sec = (p.get("proceedings_section") or "").strip()
            db_type = db_paper_types.get(pid, p.get("paper_type", ""))

            # Classify into full, short, or other
            if p_sec == "Symposia" or db_type == "Symposium" or "symposi" in title.lower():
                ptype = "other"
                display_type = "Symposium"
            elif p_sec in ["Special Session", "Pre-Conference Workshops", "Keynotes", "Community Workshops", "Early Career Workshops"]:
                ptype = "other"
                display_type = p_sec
            elif p_sec in ['Long Papers', 'Full Papers', 'Long Paper', 'Full Paper'] or db_type == 'Full Paper':
                ptype = "full"
                display_type = "Full Paper"
            elif p_sec in ['Short Papers', 'Short Paper'] or db_type == 'Short Paper':
                ptype = "short"
                display_type = "Short Paper"
            else:
                ptype = "other"
                display_type = p_sec or "Other"

            # Check clean author from proceedings.db
            db_auth = db_authors_by_id.get(pid) or db_authors_by_title.get(norm_t)
            if db_auth:
                db_auth_list = [a.strip() for a in db_auth.split(';') if a.strip() and not is_title_spillover(a.strip(), title) and not is_affiliation_or_invalid(a.strip())]
                if db_auth_list:
                    authors = "; ".join(db_auth_list)
                else:
                    clean_auth_list = sanitize_author_names(p.get("authors", []), title)
                    authors = "; ".join(clean_auth_list).strip()
            else:
                clean_auth_list = sanitize_author_names(p.get("authors", []), title)
                authors = "; ".join(clean_auth_list).strip()

            is_clean_paper = (
                title and len(title) >= 15 and title[0].isupper() and 
                not title.startswith('leading to') and '...' not in title and
                authors and len(authors) >= 3
            )

            secs = p.get("sections", [])
            total_secs = len(secs)

            paper_tokens = defaultdict(int)
            sec_texts = defaultdict(list)
            paper_total_tokens = 0

            for idx, sec in enumerate(secs):
                h = sec.get("heading_original") or sec.get("heading_normalized") or ""
                roles = sec.get("canonical_roles", [])
                text = sec.get("text") or ""
                tokens = len(text.split())
                cat = categorize_section(h, roles, idx, total_secs)
                paper_tokens[cat] += tokens
                sec_texts[cat].append(text)
                paper_total_tokens += tokens

            if paper_total_tokens < 80:
                continue

            # Record in assigned partition
            target_groups = [ptype]
            if ptype in ["full", "short"]:
                target_groups.append("all")  # all represents all core empirical scholarship papers

            for grp in target_groups:
                counts[grp]["total"] += 1
                counts[grp]["tokens"] += paper_total_tokens
                counts[grp]["by_year"][conf_year] += 1
                counts[grp]["by_bucket"][bucket] += 1
                for sec_name in SECTIONS_ORDER:
                    tok = paper_tokens[sec_name]
                    tokens_store[grp][conf_year][sec_name].append(tok)
                    tokens_store[grp][str(conf_year)][sec_name].append(tok)
                    tokens_store[grp][bucket][sec_name].append(tok)
                    tokens_store[grp]["All"][sec_name].append(tok)

            # Outlier bounds check
            is_valid_outlier = (
                is_clean_paper and (
                    (ptype == "full" and 1800 <= paper_total_tokens <= 12000) or
                    (ptype == "short" and 900 <= paper_total_tokens <= 5500) or
                    (ptype == "other" and 1500 <= paper_total_tokens <= 15000)
                )
            )

            if is_valid_outlier:
                for sec_name in CORE_SECTIONS:
                    tok = paper_tokens[sec_name]
                    raw_text = " ".join(sec_texts[sec_name])
                    clean_excerpt = re.sub(r'\s+', ' ', raw_text).strip()
                    if len(clean_excerpt) > 280:
                        clean_excerpt = clean_excerpt[:277] + "..."
                    raw_ab = (p.get("abstract") or clean_excerpt).strip()
                    if len(raw_ab) > 1800:
                        paragraphs = [para.strip() for para in raw_ab.split("\n\n") if para.strip()]
                        if len(paragraphs) > 1:
                            raw_ab = "\n\n".join(paragraphs[:2]).strip()
                        if len(raw_ab) > 1800:
                            raw_ab = raw_ab[:1797] + "..."

                    rec_item = {
                        "id": pid,
                        "title": title,
                        "authors": authors,
                        "year": conf_year,
                        "conference": conf_acronym,
                        "paper_type": display_type,
                        "tokens": tok,
                        "pct": round((tok / paper_total_tokens * 100), 1) if paper_total_tokens > 0 else 0.0,
                        "total_tokens": paper_total_tokens,
                        "section_tokens": {s: paper_tokens[s] for s in CORE_SECTIONS},
                        "abstract": raw_ab,
                        "excerpt": clean_excerpt
                    }
                    paper_records_by_type[ptype][sec_name].append(rec_item)
                    if ptype in ["full", "short"]:
                        paper_records_by_type["all"][sec_name].append(rec_item)

    # 2. Ingest Pre-2023 Parsed Dataset (2016–2022)
    if os.path.exists(PRE2023_PATH):
        print(f"Ingesting pre-2023 parsed section data from {PRE2023_PATH}...")
        try:
            with open(PRE2023_PATH, "r", encoding="utf-8") as f:
                pre_data = json.load(f)

            for pid, p in pre_data.items():
                title = p.get("title", "")
                conf_year = p.get("year", 2020)
                conf_acronym = p.get("conference", "ISLS")
                bucket = get_bucket_for_year(conf_year)
                raw_type = p.get("paper_type", "Full Paper")

                if raw_type == "Symposium":
                    ptype = "other"
                    display_type = "Symposium"
                elif raw_type == "Full Paper":
                    ptype = "full"
                    display_type = "Full Paper"
                elif raw_type == "Short Paper":
                    ptype = "short"
                    display_type = "Short Paper"
                else:
                    ptype = "other"
                    display_type = raw_type

                # Authors from DB
                db_auth = db_authors_by_id.get(pid)
                if db_auth:
                    db_auth_list = [a.strip() for a in db_auth.split(';') if a.strip() and not is_title_spillover(a.strip(), title) and not is_affiliation_or_invalid(a.strip())]
                    authors = "; ".join(db_auth_list) if db_auth_list else "Unknown Authors"
                else:
                    authors = "Unknown Authors"

                is_clean_paper = title and len(title) >= 15 and authors != "Unknown Authors"
                paper_tokens = p.get("tokens", {})
                paper_total_tokens = sum(paper_tokens.values())

                if paper_total_tokens < 80:
                    continue

                target_groups = [ptype]
                if ptype in ["full", "short"]:
                    target_groups.append("all")

                for grp in target_groups:
                    counts[grp]["total"] += 1
                    counts[grp]["tokens"] += paper_total_tokens
                    counts[grp]["by_year"][conf_year] += 1
                    counts[grp]["by_bucket"][bucket] += 1
                    for sec_name in SECTIONS_ORDER:
                        tok = paper_tokens.get(sec_name, 0)
                        tokens_store[grp][conf_year][sec_name].append(tok)
                        tokens_store[grp][str(conf_year)][sec_name].append(tok)
                        tokens_store[grp][bucket][sec_name].append(tok)
                        tokens_store[grp]["All"][sec_name].append(tok)

                is_valid_outlier = (
                    is_clean_paper and (
                        (ptype == "full" and 1800 <= paper_total_tokens <= 12000) or
                        (ptype == "short" and 900 <= paper_total_tokens <= 5500) or
                        (ptype == "other" and 1500 <= paper_total_tokens <= 15000)
                    )
                )

                if is_valid_outlier:
                    for sec_name in CORE_SECTIONS:
                        tok = paper_tokens.get(sec_name, 0)
                        rec_item = {
                            "id": pid,
                            "title": title,
                            "authors": authors,
                            "year": conf_year,
                            "conference": conf_acronym,
                            "paper_type": display_type,
                            "tokens": tok,
                            "pct": round((tok / paper_total_tokens * 100), 1) if paper_total_tokens > 0 else 0.0,
                            "total_tokens": paper_total_tokens,
                            "section_tokens": {s: paper_tokens.get(s, 0) for s in CORE_SECTIONS},
                            "abstract": p.get("abstract", ""),
                            "excerpt": p.get("abstract", "")[:280]
                        }
                        paper_records_by_type[ptype][sec_name].append(rec_item)
                        if ptype in ["full", "short"]:
                            paper_records_by_type["all"][sec_name].append(rec_item)
        except Exception as e:
            print(f"Warning loading pre2023_sections: {e}")

    years = sorted([y for y in counts["all"]["by_year"].keys() if isinstance(y, int)])
    bucket_keys = [b[0] for b in COHORT_BUCKETS]
    all_keys = ["All"] + bucket_keys + [str(y) for y in years]

    print(f"Total Scholarship Papers across Decade: {counts['all']['total']} (Full: {counts['full']['total']}, Short: {counts['short']['total']})")
    print(f"Total Others / Symposia / Workshops: {counts['other']['total']}")
    print(f"Total Attributed Tokens: {counts['all']['tokens']:,}")

    # Build Distributions
    distributions_by_type = {g: {} for g in groups}
    for group in groups:
        for k in all_keys:
            dist = compute_dist_dict(tokens_store[group][k])
            if dist:
                distributions_by_type[group][str(k)] = dist

    # Extract Outliers for Full, Short, Other, and All
    outliers_data = {}
    for group in groups:
        outliers_data[group] = {}
        for sec_name in CORE_SECTIONS:
            recs = paper_records_by_type[group][sec_name]
            if not recs:
                continue
            # Very High Outlier
            high_rec = sorted(recs, key=lambda x: x["tokens"], reverse=True)[0]
            # Very Low Outlier (min >= 25 tokens)
            low_cands = [r for r in recs if r["tokens"] >= 25]
            low_rec = sorted(low_cands, key=lambda x: x["tokens"])[0] if low_cands else recs[-1]

            badge_label = "Symposium Outlier" if group == "other" else "Outlier"

            outliers_data[group][sec_name] = [
                {
                    "outlier_type": "Very High",
                    "badge_label": f"Very High {badge_label}",
                    "badge_color": "#2563eb",
                    "badge_bg": "#eff6ff",
                    "badge_border": "#bfdbfe",
                    "rank": 1,
                    "id": high_rec["id"],
                    "title": high_rec["title"],
                    "authors": high_rec["authors"],
                    "year": high_rec["year"],
                    "conference": high_rec["conference"],
                    "paper_type": high_rec["paper_type"],
                    "tokens": high_rec["tokens"],
                    "total_tokens": high_rec["total_tokens"],
                    "pct_of_paper": high_rec["pct"],
                    "section_tokens": high_rec.get("section_tokens", {}),
                    "abstract": high_rec.get("abstract", ""),
                    "context": OUTLIER_CONTEXTS.get((sec_name, "high"), "Expansive development of this section."),
                    "excerpt": high_rec.get("excerpt", "")
                },
                {
                    "outlier_type": "Very Low",
                    "badge_label": f"Very Low {badge_label}",
                    "badge_color": "#d97706",
                    "badge_bg": "#fffbeb",
                    "badge_border": "#fde68a",
                    "rank": 2,
                    "id": low_rec["id"],
                    "title": low_rec["title"],
                    "authors": low_rec["authors"],
                    "year": low_rec["year"],
                    "conference": low_rec["conference"],
                    "paper_type": low_rec["paper_type"],
                    "tokens": low_rec["tokens"],
                    "total_tokens": low_rec["total_tokens"],
                    "pct_of_paper": low_rec["pct"],
                    "section_tokens": low_rec.get("section_tokens", {}),
                    "abstract": low_rec.get("abstract", ""),
                    "context": OUTLIER_CONTEXTS.get((sec_name, "low"), "Ultra-concise, compressed development focusing space on other sections."),
                    "excerpt": low_rec.get("excerpt", "")
                }
            ]

    # Section Metadata (for Full and Short)
    sections_meta = []
    for idx, sec_name in enumerate(CORE_SECTIONS):
        f_med = distributions_by_type["full"].get("All", {}).get(sec_name, {}).get("median", 0)
        s_med = distributions_by_type["short"].get("All", {}).get(sec_name, {}).get("median", 0)
        sections_meta.append({
            "order": idx + 1,
            "name": sec_name,
            "description": SECTION_DESCRIPTIONS[sec_name],
            "full_median": f_med,
            "short_median": s_med
        })

    payload = {
        "summary": {
            "title": "Beautiful Papers: Structural Silhouette & Section Token Distribution (2016–2026)",
            "total_papers_analyzed": counts["all"]["total"],
            "full_papers_count": counts["full"]["total"],
            "short_papers_count": counts["short"]["total"],
            "other_papers_count": counts["other"]["total"],
            "total_tokens_attributed": counts["all"]["tokens"],
            "attribution_rate": "100.0%",
            "years_covered": years,
            "cohort_buckets": [
                {"id": b[0], "label": b[2]} for b in COHORT_BUCKETS
            ],
            "papers_by_year": {g: dict(counts[g]["by_year"]) for g in groups},
            "papers_by_bucket": {g: dict(counts[g]["by_bucket"]) for g in groups}
        },
        "sections": sections_meta,
        "by_type": distributions_by_type,
        "distributions": distributions_by_type["all"],  # backwards-compat
        "outliers_by_type": outliers_data,
        "outliers": outliers_data["all"]
    }

    # Write derived cache
    derived_out = os.path.join(DERIVED_DIR, "beautiful_papers.json")
    with open(derived_out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote derived dataset: {derived_out}")

    # Write web client data
    web_out = os.path.join(WEB_DIR, "beautiful_papers.json")
    with open(web_out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote web client data: {web_out}")

    return payload

if __name__ == "__main__":
    generate_data()
