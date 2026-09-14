#!/usr/bin/env python3
"""Taxonomy Classifier: Populates label_definitions and paper_labels via 0-cost lexical heuristics."""

import re
import json
import sqlite3
from typing import Dict, List, Tuple, Any
from proceedings_ingest.concept_miner import CONCEPT_TAXONOMY

DB_PATH = "proceedings.db"

# 1. SETTING RULES
SETTING_TAXONOMY = {
    "K-12 Elementary": [
        r"\belementary school\b", r"\belementary student(s)?\b", r"\bprimary school\b",
        r"\bgrade(s)? [1-5]\b", r"\bk-5\b", r"\byoung children\b", r"\bearly childhood\b"
    ],
    "K-12 Secondary": [
        r"\bmiddle school\b", r"\bhigh school\b", r"\bsecondary school\b", r"\bsecondary student(s)?\b",
        r"\bgrade(s)? [6-9]\b", r"\bgrade(s)? 1[0-2]\b", r"\b6-12\b", r"\badolescent(s)?\b", r"\bteen(s|agers)?\b"
    ],
    "Higher Education": [
        r"\bhigher education\b", r"\bundergraduate(s)?\b", r"\buniversity\b", r"\bcollege student(s)?\b",
        r"\bpostsecondary\b", r"\bgraduate student(s)?\b", r"\bengineering course\b"
    ],
    "Informal / Out-of-School": [
        r"\binformal (learning|environment|setting)\b", r"\bmuseum(s)?\b", r"\bscience center(s)?\b",
        r"\bafter[- ]school\b", r"\bmakerspace(s)?\b", r"\blibrar(y|ies)\b", r"\bhome learning\b", r"\bfamily learning\b"
    ],
    "Workplace / Professional": [
        r"\bworkplace\b", r"\bprofessional development\b", r"\bteacher learning\b", r"\bin[- ]service teacher(s)?\b",
        r"\bpre[- ]service teacher(s)?\b", r"\bmedical education\b", r"\bclinical\b"
    ],
    "Online / Hybrid": [
        r"\bonline learning\b", r"\bmooc(s)?\b", r"\bhybrid learning\b", r"\bdistance learning\b",
        r"\bvirtual classroom\b", r"\bremote learning\b"
    ]
}

# 2. SUBJECT / DOMAIN RULES
SUBJECT_TAXONOMY = {
    "STEM - Computer Science & Coding": [
        r"\bcomputational thinking\b", r"\bcomputer science\b", r"\bprogram(ming|mers)?\b", r"\bcoding\b",
        r"\bscratch\b", r"\bpython\b", r"\bdata science\b", r"\balgorithm(s)?\b"
    ],
    "STEM - Natural Science": [
        r"\bscience education\b", r"\bphysics\b", r"\bbiology\b", r"\bchemist(ry|ical)\b",
        r"\becolog(y|ical)\b", r"\bclimate\b", r"\bastronomy\b", r"\bscientific (inquiry|reasoning)\b"
    ],
    "STEM - Mathematics": [
        r"\bmath(ematics)?\b", r"\balgebra\b", r"\bgeometr(y|ic)\b", r"\bfraction(s)?\b",
        r"\bmathematical reasoning\b", r"\bcalculus\b", r"\bproportional\b", r"\barithmetic\b"
    ],
    "STEM - Engineering & Robotics": [
        r"\bengineer(ing)?\b", r"\brobot(ic|ics)?\b", r"\bcircuit(s)?\b", r"\bmechanic(s|al)?\b"
    ],
    "Humanities, Language & Literacy": [
        r"\breading\b", r"\bliterac(y|ies)\b", r"\blanguage learning\b", r"\bwriting\b",
        r"\btranslingual\b", r"\bsecond language\b", r"\besl\b", r"\bliterature\b"
    ],
    "Social & Civic Studies": [
        r"\bhistory\b", r"\bsocial studies\b", r"\bcivic(s)?\b", r"\bdemocratic\b",
        r"\bclimate justice\b", r"\bpolitical\b", r"\bcommunity issue(s)?\b"
    ]
}

# 3. TPACK: TECHNOLOGY (TK) RULES
TK_TAXONOMY = {
    "Generative AI & LLMs": [
        r"\blarge language model(s)?\b", r"\bllm(s)?\b", r"\bchatgpt\b", r"\bgenerative ai\b",
        r"\bgpt[- ][34]\b", r"\bconversational agent(s)?\b", r"\bprompt engineering\b"
    ],
    "Immersive VR / AR": [
        r"\bvirtual reality\b", r"\baugmented reality\b", r"\bvr\b", r"\bar\b", r"\bmr\b",
        r"\bimmersive\b", r"\bheadset\b", r"\bvirtual environment(s)?\b"
    ],
    "Simulations & Scientific Modeling": [
        r"\bsimulat(ion|ions|or)\b", r"\bcomputational model(ing)?\b", r"\bagent[- ]based model(ing)?\b",
        r"\bnetlogo\b", r"\bvisualization tool(s)?\b"
    ],
    "Robotics & Tangibles": [
        r"\brobot(ics)?\b", r"\btangible(s)?\b", r"\bphysical computing\b", r"\bmicro:bit\b", r"\barduino\b"
    ],
    "Collaborative Platforms & Forums": [
        r"\bdiscussion board(s)?\b", r"\bforum(s)?\b", r"\bcollaborative platform(s)?\b", r"\bwiki(s)?\b",
        r"\bshared canvas\b", r"\bshared workspace\b"
    ],
    "Analytics & Dashboards": [
        r"\bdashboard(s)?\b", r"\blearning analytics\b", r"\bfeedback system(s)?\b", r"\bvisual analytics\b"
    ],
    "Block-based Coding & Authoring": [
        r"\bblock[- ]based\b", r"\bscratch\b", r"\bauthoring tool(s)?\b", r"\bgame engine\b"
    ]
}

# 4. TPACK: PEDAGOGY (PK) RULES
PK_TAXONOMY = {
    "Inquiry-Based & Problem-Solving": [
        r"\binquiry[- ]based\b", r"\bproblem[- ]based\b", r"\bproblem solving\b", r"\bdiscovery learning\b"
    ],
    "Collaborative & CSCL": [
        r"\bcollaborative learning\b", r"\bcscl\b", r"\bpeer collaboration\b", r"\bgroup work\b", r"\bteam learning\b"
    ],
    "Productive Failure": [
        r"\bproductive failure\b", r"\bproblem[- ]solving before instruction\b", r"\bproductive struggle\b"
    ],
    "Scaffolded & Guided": [
        r"\bscaffold(ing|ed)?\b", r"\bguided exploration\b", r"\bstepwise support\b"
    ],
    "Game-Based & Playful": [
        r"\bgame[- ]based\b", r"\bgamif(ied|ication)\b", r"\beducational game(s)?\b", r"\bplayful learning\b"
    ],
    "Peer Argumentation & Discourse": [
        r"\bargumentation\b", r"\bdialogic\b", r"\bpeer feedback\b", r"\baccountable talk\b"
    ],
    "Co-Design & Participatory": [
        r"\bco-design\b", r"\bcodesign\b", r"\bparticipatory design\b", r"\bparticipatory\b"
    ]
}

def compile_rules(tax_dict):
    compiled = {}
    for cat, patterns in tax_dict.items():
        compiled[cat] = [re.compile(p, re.IGNORECASE) for p in patterns]
    return compiled

def calculate_centrality_score(title: str, abstract: str, matched_patterns: List[re.Pattern]) -> int:
    """Calculates 1-5 heuristic centrality score:
       5 = in title or multiple explicit claim occurrences
       3 = clear intervention presence in abstract
       1 = incidental mention
    """
    in_title = any(p.search(title) for p in matched_patterns)
    if in_title:
        return 5
    
    matches_in_abstract = sum(len(p.findall(abstract)) for p in matched_patterns)
    if matches_in_abstract >= 3:
        return 4
    elif matches_in_abstract >= 1:
        return 3
    return 1

def populate_all_labels(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("Registering Label Definitions...")
    # Register Dimensions & Labels in label_definitions
    definitions = [
        # Dimensions
        ("tpack_tk", "tpack_tk", "Technology Knowledge (TK)", 1, None, "Digital & physical learning technologies", "enum"),
        ("tpack_pk", "tpack_pk", "Pedagogical Knowledge (PK)", 1, None, "Instructional models & learning strategies", "enum"),
        ("tpack_ck", "tpack_ck", "Content Knowledge (CK)", 1, None, "Disciplinary domain & subject area", "enum"),
        ("setting", "setting", "Educational Setting", 1, None, "Educational environment / institution", "enum"),
        ("subject", "subject", "Subject Domain", 1, None, "Academic subject matter", "enum"),
        ("conceptualisation", "conceptualisation", "Named Conceptualisation", 1, None, "Theoretical and methodological frameworks", "enum")
    ]

    cur.executemany("""
        INSERT OR REPLACE INTO label_definitions (id, dimension, display_name, hierarchy_level, parent_id, description, allowed_values)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, definitions)
    conn.commit()

    compiled_setting = compile_rules(SETTING_TAXONOMY)
    compiled_subject = compile_rules(SUBJECT_TAXONOMY)
    compiled_tk = compile_rules(TK_TAXONOMY)
    compiled_pk = compile_rules(PK_TAXONOMY)
    
    compiled_concepts = {}
    for fam, labels in CONCEPT_TAXONOMY.items():
        compiled_concepts[fam] = compile_rules(labels)

    cur.execute("SELECT id, title, abstract, year FROM papers;")
    papers = cur.fetchall()
    print(f"Loaded {len(papers)} papers from database. Processing labels...")

    paper_label_rows = []
    
    for pid, title, abstract, year in papers:
        t = title or ""
        a = abstract or ""
        full_text = f"{t} {a}"

        # 1. Setting
        matched_setting = False
        for set_label, patterns in compiled_setting.items():
            if any(p.search(full_text) for p in patterns):
                matched_setting = True
                paper_label_rows.append((
                    pid, "setting", set_label, "Setting", set_label, None, 0.9,
                    "Matched title/abstract lexical pattern", "rule_lexical_0_cost", "heuristic_0_cost",
                    "Extracted via 0-cost title/abstract lexical heuristics; ready for Tier 2 batched LLM claim verification."
                ))
        if not matched_setting:
            paper_label_rows.append((
                pid, "setting", "Theoretical / Unspecified", "Setting", "Theoretical / Unspecified", None, 0.5,
                "No explicit institutional setting detected in abstract", "rule_lexical_0_cost", "heuristic_0_cost",
                "Unspecified in abstract; can be resolved via Tier 3 Methods section extraction."
            ))

        # 2. Subject / Content (CK)
        matched_subject = False
        for subj_label, patterns in compiled_subject.items():
            if any(p.search(full_text) for p in patterns):
                matched_subject = True
                c_score = calculate_centrality_score(t, a, patterns)
                # Add to subject
                paper_label_rows.append((
                    pid, "subject", subj_label, "Subject", subj_label, c_score, 0.9,
                    "Matched domain terminology in title/abstract", "rule_lexical_0_cost", "heuristic_0_cost",
                    "Extracted via 0-cost title/abstract lexical heuristics; ready for Tier 2 batched LLM claim verification."
                ))
                # Add to TPACK CK
                paper_label_rows.append((
                    pid, "tpack_ck", subj_label, "Content Knowledge (CK)", subj_label, c_score, 0.9,
                    f"CK Centrality Score: {c_score}/5", "rule_lexical_0_cost", "heuristic_0_cost",
                    "Centrality score estimated from title/abstract prominence; can be verified via Tier 2 claim analysis."
                ))
        if not matched_subject:
            paper_label_rows.append((
                pid, "subject", "Interdisciplinary & General", "Subject", "Interdisciplinary & General", 1, 0.5,
                "No single disciplinary subject term detected", "rule_lexical_0_cost", "heuristic_0_cost",
                "General learning sciences inquiry; can be refined in Phase 2."
            ))
            paper_label_rows.append((
                pid, "tpack_ck", "Interdisciplinary & General", "Content Knowledge (CK)", "Interdisciplinary & General", 1, 0.5,
                "CK Centrality Score: 1/5 (General context)", "rule_lexical_0_cost", "heuristic_0_cost",
                "General learning sciences context; can be refined in Phase 2."
            ))

        # 3. TPACK: Technology (TK)
        matched_tk = False
        for tk_label, patterns in compiled_tk.items():
            if any(p.search(full_text) for p in patterns):
                matched_tk = True
                c_score = calculate_centrality_score(t, a, patterns)
                paper_label_rows.append((
                    pid, "tpack_tk", tk_label, "Technology Knowledge (TK)", tk_label, c_score, 0.9,
                    f"TK Centrality Score: {c_score}/5", "rule_lexical_0_cost", "heuristic_0_cost",
                    "Centrality score estimated from title/abstract prominence; can be verified via Tier 2 claim analysis."
                ))
        if not matched_tk:
            paper_label_rows.append((
                pid, "tpack_tk", "Non-digital / Unspecified", "Technology Knowledge (TK)", "Non-digital / Unspecified", 1, 0.5,
                "No digital technology tool identified in abstract", "rule_lexical_0_cost", "heuristic_0_cost",
                "Non-digital or conceptual paper; can be verified via Tier 2."
            ))

        # 4. TPACK: Pedagogy (PK)
        matched_pk = False
        for pk_label, patterns in compiled_pk.items():
            if any(p.search(full_text) for p in patterns):
                matched_pk = True
                c_score = calculate_centrality_score(t, a, patterns)
                paper_label_rows.append((
                    pid, "tpack_pk", pk_label, "Pedagogical Knowledge (PK)", pk_label, c_score, 0.9,
                    f"PK Centrality Score: {c_score}/5", "rule_lexical_0_cost", "heuristic_0_cost",
                    "Centrality score estimated from title/abstract prominence; can be verified via Tier 2 claim analysis."
                ))
        if not matched_pk:
            paper_label_rows.append((
                pid, "tpack_pk", "General / Reflective", "Pedagogical Knowledge (PK)", "General / Reflective", 1, 0.5,
                "No specialized pedagogical model keyword matched", "rule_lexical_0_cost", "heuristic_0_cost",
                "General instructional setting; can be verified via Tier 2."
            ))

        # 5. Named Conceptualisations (Hierarchical)
        for fam, labels in compiled_concepts.items():
            for concept_label, patterns in labels.items():
                if any(p.search(full_text) for p in patterns):
                    c_score = calculate_centrality_score(t, a, patterns)
                    paper_label_rows.append((
                        pid, "conceptualisation", concept_label, fam, concept_label, c_score, 0.9,
                        f"Theoretical Family: {fam}", "rule_lexical_0_cost", "heuristic_0_cost",
                        "Hierarchical match in title/abstract; full theoretical framework extractable via Tier 3."
                    ))

    print(f"Total paper label instances generated: {len(paper_label_rows)}")
    print("Writing labels to database...")
    cur.execute("DELETE FROM paper_labels;")
    cur.executemany("""
        INSERT OR REPLACE INTO paper_labels (
            paper_id, label_id, label_value, hierarchy_level_1, hierarchy_level_2,
            centrality_score, confidence, evidence_snippet, method, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, paper_label_rows)

    conn.commit()
    conn.close()
    print("Successfully populated paper_labels table.")

if __name__ == "__main__":
    populate_all_labels()
