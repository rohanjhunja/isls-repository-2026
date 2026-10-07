#!/usr/bin/env python3
"""
scripts/extract_external_citations.py

Deterministic pipeline to parse external citations to conferences, journals,
and sources across all 10 years of ISLS proceedings (2016–2026).

- Scans sections WHERE normalized_section = 'references'
- Extracts matched venue, disciplinary family, and verbatim citation snippet
- Populates SQLite table: external_citations in proceedings.db
- Generates precomputed static JSON caches in data/derived/, web/data/overview_static/, and docs/data/overview_static/
"""

import os
import re
import json
import sqlite3
import time
from collections import defaultdict, Counter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "proceedings.db")

VENUE_TAXONOMY = {
    "learning_sciences": {
        "name": "Learning Sciences Flagships",
        "description": "Core journals shaping learning sciences foundations",
        "venues": {
            "jls": {
                "name": "Journal of the Learning Sciences",
                "patterns": [r"\bjournal of the learning sciences\b", r"\bjls\b"]
            },
            "ijcscl": {
                "name": "ijCSCL",
                "patterns": [r"\binternational journal of computer[- ]supported collaborative learning\b", r"\bijcscl\b"]
            },
            "cognition_and_instruction": {
                "name": "Cognition and Instruction",
                "patterns": [r"\bcognition and instruction\b"]
            },
            "instructional_science": {
                "name": "Instructional Science",
                "patterns": [r"\binstructional science\b"]
            },
            "learning_and_instruction": {
                "name": "Learning and Instruction",
                "patterns": [r"\blearning and instruction\b"]
            }
        }
    },
    "edtech": {
        "name": "Educational Technology",
        "description": "Digital learning media, tools, and environments",
        "venues": {
            "computers_and_education": {
                "name": "Computers & Education",
                "patterns": [r"\bcomputers & education\b", r"\bcomputers and education\b"]
            },
            "computers_in_human_behavior": {
                "name": "Computers in Human Behavior",
                "patterns": [r"\bcomputers in human behavior\b"]
            },
            "bjet": {
                "name": "British Journal of Educational Tech (BJET)",
                "patterns": [r"\bbritish journal of educational technology\b", r"\bbjet\b"]
            },
            "etrd": {
                "name": "Educational Tech Research & Development (ETR&D)",
                "patterns": [r"\beducational technology research and development\b", r"\betr&d\b"]
            },
            "jcal": {
                "name": "Journal of Computer Assisted Learning",
                "patterns": [r"\bjournal of computer assisted learning\b", r"\bjcal\b"]
            },
            "internet_higher_educ": {
                "name": "Internet and Higher Education",
                "patterns": [r"\binternet and higher education\b"]
            },
            "interactive_learning_env": {
                "name": "Interactive Learning Environments",
                "patterns": [r"\binteractive learning environments\b"]
            }
        }
    },
    "hci_computing": {
        "name": "HCI & Computing Venues",
        "description": "Human-computer interaction and technical CS education",
        "venues": {
            "acm_chi": {
                "name": "ACM CHI (Human Factors in Computing)",
                "patterns": [
                    r"\bconference on human factors in computing systems\b",
                    r"\bchi\b.*\b(conference|proceedings|human factors)\b",
                    r"\bproceedings of the .*? acm .*? chi\b",
                    r"\bchi \'\d\d\b",
                    r"\bchi \d{4}\b"
                ]
            },
            "acm_cscw": {
                "name": "ACM CSCW (Computer-Supported Coop. Work)",
                "patterns": [r"\bcomputer[- ]supported cooperative work\b", r"\bcscw\b.*\b(conference|proceedings|\'\d\d|\d{4})\b"]
            },
            "acm_sigcse": {
                "name": "ACM SIGCSE (CS Education)",
                "patterns": [r"\bsigcse\b", r"\btechnical symposium on computer science education\b"]
            },
            "acm_idc": {
                "name": "ACM IDC (Interaction Design and Children)",
                "patterns": [r"\binteraction design and children\b", r"\bidc \'\d\d\b", r"\bidc \d{4}\b"]
            },
            "ieee_tlt": {
                "name": "IEEE Trans. on Learning Technologies",
                "patterns": [r"\bieee transactions on learning technologies\b", r"\bieee trans.*? learn.*? tech\b"]
            },
            "acm_dis": {
                "name": "ACM DIS (Designing Interactive Systems)",
                "patterns": [r"\bdesigning interactive systems\b", r"\bdis \'\d\d\b", r"\bdis \d{4}\b"]
            },
            "acm_tochi": {
                "name": "ACM TOCHI",
                "patterns": [r"\btransactions on computer[- ]human interaction\b", r"\btochi\b"]
            }
        }
    },
    "ai_analytics": {
        "name": "AI, Data Mining & Analytics",
        "description": "Artificial intelligence, learning analytics, and data mining",
        "venues": {
            "lak": {
                "name": "LAK (Learning Analytics & Knowledge)",
                "patterns": [r"\blearning analytics\b.*\bknowledge\b", r"\blak\b.*\b(conference|proceedings|\'\d\d|\d{4})\b"]
            },
            "aied": {
                "name": "AIED (AI in Education)",
                "patterns": [
                    r"\bartificial intelligence in education\b",
                    r"\baied\b.*\b(conference|proceedings|\'\d\d|\d{4})\b",
                    r"\bijaied\b",
                    r"\binternational journal of artificial intelligence in education\b"
                ]
            },
            "edm": {
                "name": "EDM (Educational Data Mining)",
                "patterns": [r"\beducational data mining\b", r"\bedm\b.*\b(conference|proceedings|\'\d\d|\d{4})\b"]
            },
            "jla": {
                "name": "Journal of Learning Analytics",
                "patterns": [r"\bjournal of learning analytics\b", r"\bjla\b"]
            },
            "neurips_ml": {
                "name": "AI & ML (NeurIPS, ICML, AAAI, ACL, EMNLP)",
                "patterns": [
                    r"\bneurips\b",
                    r"\bneural information processing systems\b",
                    r"\bicml\b",
                    r"\baaai\b",
                    r"\bacl\b.*\b(conference|proceedings|association for computational linguistics)\b",
                    r"\bemnlp\b"
                ]
            }
        }
    },
    "cogsci_psych": {
        "name": "Cognitive Science & Psychology",
        "description": "Cognitive psychology, child development, and learning theory",
        "venues": {
            "cognitive_science": {
                "name": "Cognitive Science",
                "patterns": [r"\bcognitive science\b"]
            },
            "j_educational_psychology": {
                "name": "Journal of Educational Psychology",
                "patterns": [r"\bjournal of educational psychology\b"]
            },
            "educational_psychologist": {
                "name": "Educational Psychologist",
                "patterns": [r"\beducational psychologist\b"]
            },
            "contemporary_educ_psych": {
                "name": "Contemporary Educational Psychology",
                "patterns": [r"\bcontemporary educational psychology\b"]
            },
            "child_development": {
                "name": "Child Development",
                "patterns": [r"\bchild development\b"]
            },
            "developmental_psychology": {
                "name": "Developmental Psychology",
                "patterns": [r"\bdevelopmental psychology\b"]
            },
            "mind_culture_activity": {
                "name": "Mind, Culture, and Activity",
                "patterns": [r"\bmind, culture, and activity\b", r"\bmind, culture and activity\b"]
            },
            "cognitive_development": {
                "name": "Cognitive Development",
                "patterns": [r"\bcognitive development\b"]
            }
        }
    },
    "educational_research": {
        "name": "Educational Research & Policy",
        "description": "General educational research, policy, and teacher education",
        "venues": {
            "aera_aerj": {
                "name": "AERA / AERJ / Educational Researcher",
                "patterns": [r"\bamerican educational research (journal|association)\b", r"\baerj\b", r"\beducational researcher\b", r"\baera\b"]
            },
            "review_of_educ_research": {
                "name": "Review of Educational Research",
                "patterns": [r"\breview of educational research\b"]
            },
            "teachers_college_record": {
                "name": "Teachers College Record",
                "patterns": [r"\bteachers college record\b"]
            },
            "harvard_educational_review": {
                "name": "Harvard Educational Review",
                "patterns": [r"\bharvard educational review\b"]
            },
            "curriculum_inquiry": {
                "name": "Curriculum Inquiry",
                "patterns": [r"\bcurriculum inquiry\b"]
            },
            "theory_into_practice": {
                "name": "Theory into Practice",
                "patterns": [r"\btheory into practice\b"]
            }
        }
    },
    "multidisciplinary": {
        "name": "Multidisciplinary Science",
        "description": "Broad natural sciences, psychology open-access, and interdisciplinary flagships",
        "venues": {
            "science_nature_pnas": {
                "name": "Science / Nature / PNAS",
                "patterns": [r"\bscience\b, \d+", r"\bnature\b, \d+", r"\bproceedings of the national academy of sciences\b", r"\bpnas\b"]
            },
            "frontiers_psych_educ": {
                "name": "Frontiers in Psychology / Education",
                "patterns": [r"\bfrontiers in (psychology|education)\b"]
            },
            "plos_one": {
                "name": "PLOS ONE",
                "patterns": [r"\bplos one\b"]
            }
        }
    }
}


def extract_snippet(text: str, match_start: int, match_end: int) -> str:
    """Extracts a neat, bounded context snippet around the matched citation pattern."""
    ctx_start = max(0, match_start - 120)
    ctx_end = min(len(text), match_end + 140)

    # Trim to nearest word or punctuation boundary
    if ctx_start > 0:
        prev_space = text.find(" ", ctx_start)
        if prev_space != -1 and prev_space < match_start:
            ctx_start = prev_space + 1

    if ctx_end < len(text):
        next_space = text.rfind(" ", match_end, ctx_end)
        if next_space != -1:
            ctx_end = next_space

    snippet = text[ctx_start:ctx_end].replace("\n", " ").strip()
    snippet = re.sub(r"\s+", " ", snippet)
    if ctx_start > 0:
        snippet = "..." + snippet
    if ctx_end < len(text):
        snippet = snippet + "..."
    return snippet


def main():
    t0 = time.time()
    print("=== Extracting External Citations from ISLS Proceedings (2016–2026) ===")

    # Compile all regular expressions
    compiled_taxonomy = {}
    for cat_id, cat_info in VENUE_TAXONOMY.items():
        compiled_venues = {}
        for venue_id, v_info in cat_info["venues"].items():
            compiled_venues[venue_id] = {
                "name": v_info["name"],
                "compiled": [re.compile(p, re.IGNORECASE) for p in v_info["patterns"]]
            }
        compiled_taxonomy[cat_id] = {
            "name": cat_info["name"],
            "description": cat_info["description"],
            "venues": compiled_venues
        }

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create external_citations table with indices
    cur.execute("DROP TABLE IF EXISTS external_citations;")
    cur.execute("""
        CREATE TABLE external_citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id TEXT NOT NULL,
            venue_id TEXT NOT NULL,
            venue_name TEXT NOT NULL,
            category_id TEXT NOT NULL,
            category_name TEXT NOT NULL,
            citing_year INTEGER NOT NULL,
            citation_snippet TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES papers(id)
        );
    """)
    cur.execute("CREATE INDEX idx_ext_cite_venue ON external_citations(venue_id);")
    cur.execute("CREATE INDEX idx_ext_cite_cat ON external_citations(category_id);")
    cur.execute("CREATE INDEX idx_ext_cite_paper ON external_citations(paper_id);")
    cur.execute("CREATE INDEX idx_ext_cite_year ON external_citations(citing_year);")

    # Fetch all reference sections
    cur.execute("""
        SELECT s.paper_id, p.year, s.text
        FROM sections s
        JOIN papers p ON s.paper_id = p.id
        WHERE s.normalized_section = 'references';
    """)
    section_rows = cur.fetchall()
    print(f"Loaded {len(section_rows)} reference sections from proceedings.db")

    # Group text by paper
    paper_sections = defaultdict(list)
    paper_years = {}
    for pid, yr, txt in section_rows:
        paper_sections[pid].append(txt)
        paper_years[pid] = yr

    print(f"Distinct papers with references: {len(paper_sections)}")

    # Extraction loop
    insert_records = []
    paper_venue_hits = defaultdict(lambda: Counter())  # venue_id -> year -> count of papers
    category_hits = defaultdict(lambda: Counter())     # cat_id -> year -> count of papers

    for pid, text_list in paper_sections.items():
        year = paper_years[pid]
        full_ref_text = "\n\n".join(text_list)

        for cat_id, cat_data in compiled_taxonomy.items():
            cat_matched = False
            for venue_id, v_data in cat_data["venues"].items():
                matched = False
                matched_snippet = None

                for rgx in v_data["compiled"]:
                    m = rgx.search(full_ref_text)
                    if m:
                        matched = True
                        matched_snippet = extract_snippet(full_ref_text, m.start(), m.end())
                        break

                if matched:
                    insert_records.append((
                        pid,
                        venue_id,
                        v_data["name"],
                        cat_id,
                        cat_data["name"],
                        year,
                        matched_snippet
                    ))
                    paper_venue_hits[venue_id][year] += 1
                    cat_matched = True

            if cat_matched:
                category_hits[cat_id][year] += 1

    # Bulk insert into SQLite
    cur.executemany("""
        INSERT INTO external_citations (
            paper_id, venue_id, venue_name, category_id, category_name, citing_year, citation_snippet
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """, insert_records)
    conn.commit()

    total_citations = len(insert_records)
    print(f"Successfully inserted {total_citations:,} external citation matches into external_citations table.")

    # Yearly paper totals
    cur.execute("SELECT year, COUNT(*) FROM papers GROUP BY year ORDER BY year;")
    yearly_totals = dict(cur.fetchall())
    years = sorted(yearly_totals.keys())

    # Build summary data structure for API and static caches
    categories_summary = []
    venues_summary = []

    for cat_id, cat_data in compiled_taxonomy.items():
        cat_counts = [category_hits[cat_id].get(y, 0) for y in years]
        cat_percentages = [
            round((category_hits[cat_id].get(y, 0) / yearly_totals.get(y, 1)) * 100, 2)
            for y in years
        ]
        total_citing_papers = sum(cat_counts)

        venues_in_cat = []
        for venue_id, v_data in cat_data["venues"].items():
            v_counts = [paper_venue_hits[venue_id].get(y, 0) for y in years]
            v_pcts = [
                round((paper_venue_hits[venue_id].get(y, 0) / yearly_totals.get(y, 1)) * 100, 2)
                for y in years
            ]
            v_total = sum(v_counts)

            v_entry = {
                "venue_id": venue_id,
                "venue_name": v_data["name"],
                "category_id": cat_id,
                "category_name": cat_data["name"],
                "counts": v_counts,
                "percentages": v_pcts,
                "total_papers": v_total,
                "penetration_pct": round((v_total / sum(yearly_totals.values())) * 100, 2)
            }
            venues_in_cat.append(v_entry)
            venues_summary.append(v_entry)

        # Sort venues in category by total papers descending
        venues_in_cat.sort(key=lambda v: v["total_papers"], reverse=True)

        categories_summary.append({
            "category_id": cat_id,
            "category_name": cat_data["name"],
            "description": cat_data["description"],
            "counts": cat_counts,
            "percentages": cat_percentages,
            "total_papers": total_citing_papers,
            "penetration_pct": round((total_citing_papers / sum(yearly_totals.values())) * 100, 2),
            "venues": venues_in_cat
        })

    # Sort categories by total citing papers descending
    categories_summary.sort(key=lambda c: c["total_papers"], reverse=True)
    venues_summary.sort(key=lambda v: v["total_papers"], reverse=True)

    static_payload = {
        "years": years,
        "yearly_paper_totals": [yearly_totals.get(y, 0) for y in years],
        "total_proceedings_papers": sum(yearly_totals.values()),
        "total_analyzed_papers": len(paper_sections),
        "total_external_citation_matches": total_citations,
        "categories": categories_summary,
        "venues": venues_summary,
        "taxonomy": VENUE_TAXONOMY
    }

    # Save to JSON caches
    paths_to_write = [
        os.path.join(PROJECT_ROOT, "data", "derived", "external_citations_trends.json"),
        os.path.join(PROJECT_ROOT, "web", "data", "overview_static", "external_citations.json"),
        os.path.join(PROJECT_ROOT, "docs", "data", "overview_static", "external_citations.json")
    ]

    for p in paths_to_write:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(static_payload, f, indent=2)
        print(f"Saved cache: {p}")

    conn.close()
    elapsed = time.time() - t0
    print(f"\nExtraction completed in {elapsed:.2f} seconds!")


if __name__ == "__main__":
    main()
