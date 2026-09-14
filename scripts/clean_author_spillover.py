#!/usr/bin/env python3
"""
Clean author fields across proceedings datasets:
1. Fixes title end strings / title subtitles that spilled into authors.
2. Strips institutional affiliations that were incorrectly captured as authors.
3. Updates ground_truth_registry.json, proceedings.db, and data/derived/*-proceedings/*.json.
"""

import os
import re
import json
import glob
import sqlite3
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DERIVED_DIR = os.path.join(DATA_DIR, "derived")
REGISTRY_PATH = os.path.join(DERIVED_DIR, "ground_truth_registry.json")
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")

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

def norm_str(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

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

    # Exact match with end of title
    if t_norm.endswith(a_norm):
        return True

    # Trailing n-gram match (last 2+ words match last 2+ words of title)
    a_words = a_norm.split()
    t_words = t_norm.split()
    if len(a_words) >= 2 and len(t_words) >= 2:
        for k in range(min(len(a_words), len(t_words)), 1, -1):
            if a_words[-k:] == t_words[-k:]:
                return True

    # Author starts with preposition/connector and appears inside title
    if re.match(r'^(and|in|the|of|for|with|through|to|from|by|on|at|during|across|within|towards|toward|into)\b', a, re.I):
        if a_norm in t_norm:
            return True

    # Multi-word phrase appearing verbatim in title
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
    # Strip leading "and "
    a = re.sub(r'^(?:and|&)\s+', '', a, flags=re.IGNORECASE).strip()
    # Strip trailing punctuation
    a = re.sub(r'[;,.]+$', '', a).strip()
    return a

def clean_authors_for_paper(title: str, raw_authors: List[Any], registry_authors: Optional[List[str]] = None) -> List[str]:
    # 1. If registry has clean authors (at least 1 and no title spillover), prefer registry
    if registry_authors:
        reg_clean = []
        for a in registry_authors:
            a_c = clean_author_name(str(a))
            if a_c and not is_title_spillover(a_c, title) and not is_affiliation_or_invalid(a_c):
                reg_clean.append(a_c)
        if reg_clean:
            return reg_clean

    # 2. Otherwise clean raw_authors
    extracted = []
    for item in raw_authors:
        if isinstance(item, dict):
            name = item.get("display_name") or item.get("name") or ""
        else:
            name = str(item)
        for part in re.split(r'[,;]', name):
            part = clean_author_name(part)
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

def run_cleanup():
    print("=== Step 1: Updating ground_truth_registry.json ===")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    reg_papers = registry.get("papers", [])
    fixed_reg_count = 0
    reg_by_id = {}
    reg_by_title = {}

    for p in reg_papers:
        pid = p.get("id")
        title = p.get("title", "")
        # Explicit fix for icls-volume-2026-paper-0217
        if pid == "icls-volume-2026-paper-0217":
            p["authors"] = ["Rukmini Manasa Avadhanam"]
            p["citation"] = "Rukmini Manasa Avadhanam (2026). Thinking with and Beyond the Tool: High School Students’ Use of GenAI During STEM Research Internships. Proceedings of ICLS 2026."
            fixed_reg_count += 1
            print(f"  Fixed {pid} in registry -> Rukmini Manasa Avadhanam")

        # General check in registry
        clean_a = clean_authors_for_paper(title, p.get("authors", []))
        if clean_a != p.get("authors", []):
            if clean_a: # Only update if we didn't wipe them out
                p["authors"] = clean_a
                fixed_reg_count += 1

        if pid:
            reg_by_id[pid] = p
        t_norm = norm_str(title)
        if t_norm:
            reg_by_title[t_norm] = p

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"Saved {REGISTRY_PATH}. Fixed {fixed_reg_count} papers in registry.")

    print("\n=== Step 2: Updating proceedings.db ===")
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # 2a. Fix icls-volume-2026-paper-0217
        cur.execute("SELECT id FROM authors WHERE display_name = 'Rukmini Manasa Avadhanam'")
        row = cur.fetchone()
        if row:
            real_aid = row[0]
        else:
            cur.execute("INSERT INTO authors (display_name) VALUES ('Rukmini Manasa Avadhanam')")
            real_aid = cur.lastrowid

        # Get old author id
        cur.execute("SELECT author_id FROM paper_authors WHERE paper_id = 'icls-volume-2026-paper-0217'")
        old_aid_rows = cur.fetchall()
        for (old_aid,) in old_aid_rows:
            cur.execute("DELETE FROM paper_authors WHERE paper_id = 'icls-volume-2026-paper-0217' AND author_id = ?", (old_aid,))
            # If old author has no other papers, remove
            cur.execute("SELECT COUNT(*) FROM paper_authors WHERE author_id = ?", (old_aid,))
            if cur.fetchone()[0] == 0:
                cur.execute("DELETE FROM authors WHERE id = ?", (old_aid,))

        cur.execute("INSERT OR REPLACE INTO paper_authors (paper_id, author_id, author_order) VALUES ('icls-volume-2026-paper-0217', ?, 1)", (real_aid,))
        print("  Fixed icls-volume-2026-paper-0217 author in proceedings.db")

        # 2b. Clean 'and Hiroshi Nemoto' -> 'Hiroshi Nemoto'
        cur.execute("SELECT id FROM authors WHERE display_name = 'and Hiroshi Nemoto'")
        row_and = cur.fetchone()
        if row_and:
            cur.execute("SELECT id FROM authors WHERE display_name = 'Hiroshi Nemoto'")
            row_clean = cur.fetchone()
            if row_clean:
                clean_nemoto_id = row_clean[0]
            else:
                cur.execute("INSERT INTO authors (display_name) VALUES ('Hiroshi Nemoto')")
                clean_nemoto_id = cur.lastrowid
            cur.execute("UPDATE paper_authors SET author_id = ? WHERE author_id = ?", (clean_nemoto_id, row_and[0]))
            cur.execute("DELETE FROM authors WHERE id = ?", (row_and[0],))
            print("  Fixed 'and Hiroshi Nemoto' in proceedings.db")

        conn.commit()
        conn.close()
        print("proceedings.db updated.")

    print("\n=== Step 3: Cleaning derived volume JSON files ===")
    volume_files = sorted(glob.glob(os.path.join(DERIVED_DIR, "*-proceedings", "*-proceedings.json")))
    total_spills_removed = 0
    total_papers_updated = 0

    for vpath in volume_files:
        vname = os.path.basename(vpath)
        with open(vpath, "r", encoding="utf-8") as f:
            v_data = json.load(f)

        papers = v_data.get("papers", [])
        vol_updated = 0
        vol_spills = 0

        for p in papers:
            pid = p.get("id")
            title = (p.get("title") or "").strip()
            raw_authors = p.get("authors", [])

            # Check if any author in raw_authors is a title spillover
            has_spill = False
            for a in raw_authors:
                aname = a.get("display_name") if isinstance(a, dict) else str(a)
                if is_title_spillover(aname, title):
                    has_spill = True
                    break

            # Find matching registry paper
            rp = reg_by_id.get(pid) or reg_by_title.get(norm_str(title))
            reg_auths = rp.get("authors") if rp else None

            cleaned_auth_names = clean_authors_for_paper(title, raw_authors, reg_auths)

            if cleaned_auth_names:
                # Compare with current authors
                curr_names = [a.get("display_name") if isinstance(a, dict) else str(a) for a in raw_authors]
                if cleaned_auth_names != curr_names:
                    # Update paper authors array
                    new_auth_objs = []
                    for name in cleaned_auth_names:
                        parts = name.split()
                        given = " ".join(parts[:-1]) if len(parts) > 1 else ""
                        family = parts[-1] if parts else name
                        new_auth_objs.append({
                            "display_name": name,
                            "given_name": given,
                            "family_name": family,
                            "affiliations": [],
                            "email": None
                        })
                    p["authors"] = new_auth_objs
                    vol_updated += 1
                    if has_spill:
                        vol_spills += 1

        with open(vpath, "w", encoding="utf-8") as f:
            json.dump(v_data, f, indent=2)

        print(f"  {vname}: Updated {vol_updated} papers (removed {vol_spills} title spillovers)")
        total_papers_updated += vol_updated
        total_spills_removed += vol_spills

    print(f"\nAll volumes processed: {total_papers_updated} papers updated, {total_spills_removed} title spillovers eliminated!")

if __name__ == "__main__":
    run_cleanup()
