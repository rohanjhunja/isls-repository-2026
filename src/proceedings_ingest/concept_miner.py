#!/usr/bin/env python3
"""Inductive concept miner for theoretical conceptualisations across 4,744 ISLS papers."""

import re
import sqlite3
from collections import Counter
from typing import Dict, List, Tuple

# Predefined high-confidence Learning Sciences conceptualisation mapping
# Level 1 (Family) -> Level 2 (Specific Named Conceptualisation) -> Regex / Keyword triggers
CONCEPT_TAXONOMY = {
    "Sociocultural & Historical": {
        "Cultural-Historical Activity Theory (CHAT)": [
            r"\bactivity theory\b", r"\bchat\b", r"\bactivity system\b", r"\bexpansive learning\b", r"\bthird-generation activity\b"
        ],
        "Communities of Practice & Situated Learning": [
            r"\bcommunit(y|ies) of practice\b", r"\bsituated learning\b", r"\blegitimate peripheral participation\b"
        ],
        "Funds of Knowledge & Cultural Wealth": [
            r"\bfunds of knowledge\b", r"\bcultural wealth\b", r"\bcommunity cultural wealth\b"
        ],
        "Boundary Crossing & Brokerage": [
            r"\bboundary crossing\b", r"\bboundary object\b", r"\bbrokering\b"
        ]
    },
    "Cognitive & Constructivist": {
        "Productive Failure & Problem Solving": [
            r"\bproductive failure\b", r"\bproblem[- ]solving before instruction\b", r"\bproductive struggle\b"
        ],
        "Self-Regulated Learning (SRL) & Metacognition": [
            r"\bself-regulated learning\b", r"\bsrl\b", r"\bmetacogniti(on|ve)\b", r"\bco-regulation\b", r"\bsocially shared regulation\b"
        ],
        "Conceptual Change & Mental Models": [
            r"\bconceptual change\b", r"\bmental model(s)?\b", r"\bmisconception(s)?\b"
        ],
        "Cognitive Load Theory": [
            r"\bcognitive load\b", r"\bworking memory load\b"
        ],
        "Scaffolding & Guided Inquiry": [
            r"\bscaffold(ing|s|ed)?\b", r"\bguided inquiry\b", r"\bzone of proximal development\b", r"\bzpd\b"
        ]
    },
    "Embodied & Sensorimotor": {
        "Embodied Cognition & Gestures": [
            r"\bembodied cognition\b", r"\bembodiment\b", r"\bsensorimotor\b", r"\bgesture[- ]based\b", r"\bgrounded cognition\b"
        ],
        "Multimodal Learning Analytics (MMLA)": [
            r"\bmultimodal learning analytics\b", r"\bmmla\b", r"\bmultimodal data\b", r"\beye[- ]tracking\b", r"\bsensor data\b"
        ],
        "Spatial Reasoning & Manipulation": [
            r"\bspatial reasoning\b", r"\bspatial ability\b", r"\btangible manipulation\b"
        ]
    },
    "Collaborative & Dialogic": {
        "Computer-Supported Collaborative Learning (CSCL)": [
            r"\bcscl\b", r"\bcollaborative learning\b", r"\bcollaboration script(s)?\b", r"\bgroup cognition\b"
        ],
        "Accountable Talk & Dialogic Discourse": [
            r"\baccountable talk\b", r"\bdialogic (discourse|inquiry|teaching)\b", r"\bargumentation\b", r"\bdiscourse analysis\b"
        ],
        "Epistemic Network Analysis (ENA)": [
            r"\bepistemic network analysis\b", r"\bena\b", r"\bquantitative ethnography\b"
        ],
        "Classroom Orchestration": [
            r"\borchestrat(ion|ing)\b", r"\bteacher orchestration\b", r"\borchestration graph\b"
        ]
    },
    "Design & Participatory": {
        "Design-Based Research (DBR)": [
            r"\bdesign-based research\b", r"\bdbr\b", r"\bdesign experiment(s)?\b", r"\beducational design research\b"
        ],
        "Co-Design & Participatory Design": [
            r"\bco-design(ing)?\b", r"\bcodesign\b", r"\bparticipatory design\b", r"\bresearch-practice partnership(s)?\b", r"\brpp\b"
        ],
        "Constructionism & Maker-Centered Learning": [
            r"\bconstructionis(m|t)\b", r"\bmaker(space|[- ]centered)?\b", r"\btinkering\b", r"\bfabricat(ion|ing)\b"
        ]
    },
    "Critical, Equity & Culture": {
        "Culturally Sustaining & Decolonial Pedagogies": [
            r"\bculturally (sustaining|responsive|relevant)\b", r"\bdecolonial\b", r"\bdecoloniz(ing|ation)\b", r"\bindigenous\b"
        ],
        "Racial Equity, Power & Social Justice": [
            r"\bracial (equity|justice|identity)\b", r"\bsocial justice\b", r"\bpower dynamic(s)?\b", r"\bmarginaliz(ed|ation)\b"
        ],
        "Critical Digital Literacy & AI Ethics": [
            r"\bcritical (data|digital|ai) literac(y|ies)\b", r"\bai ethics\b", r"\balgorithmic bias\b"
        ]
    }
}

def mine_conceptualisations(db_path: str = "proceedings.db") -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, title, abstract, year FROM papers WHERE abstract IS NOT NULL;")
    rows = cur.fetchall()
    conn.close()

    matches_by_label = Counter()
    family_counts = Counter()
    paper_matches = []

    compiled_rules = {}
    for fam, labels in CONCEPT_TAXONOMY.items():
        compiled_rules[fam] = {}
        for lbl, patterns in labels.items():
            compiled_rules[fam][lbl] = [re.compile(p, re.IGNORECASE) for p in patterns]

    for pid, title, abstract, year in rows:
        text = f"{title} {abstract}"
        matched_for_paper = []

        for fam, labels in compiled_rules.items():
            for lbl, regexes in labels.items():
                found_match = False
                for rgx in regexes:
                    m = rgx.search(text)
                    if m:
                        matches_by_label[lbl] += 1
                        family_counts[fam] += 1
                        snippet = text[max(0, m.start()-40):min(len(text), m.end()+40)]
                        matched_for_paper.append({
                            "paper_id": pid,
                            "family": fam,
                            "label": lbl,
                            "snippet": f"...{snippet.strip()}...",
                            "year": year
                        })
                        found_match = True
                        break
        if matched_for_paper:
            paper_matches.extend(matched_for_paper)

    return {
        "total_papers_scanned": len(rows),
        "total_matches": len(paper_matches),
        "family_counts": dict(family_counts.most_common()),
        "label_counts": dict(matches_by_label.most_common()),
        "paper_matches": paper_matches
    }

if __name__ == "__main__":
    import json
    res = mine_conceptualisations()
    print(f"Scanned {res['total_papers_scanned']} papers.")
    print(f"Total concept matches: {res['total_matches']}\n")
    print("Family Counts:")
    for fam, cnt in res["family_counts"].items():
        print(f"  {fam:35}: {cnt:4d}")
    print("\nTop Conceptualisations:")
    for lbl, cnt in list(res["label_counts"].items())[:15]:
        print(f"  {lbl:45}: {cnt:4d}")
