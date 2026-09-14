#!/usr/bin/env python3
"""Exports Tableau-ready CSV files and documentation from proceedings.db."""

import os
import sys
import csv
import sqlite3
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
from proceedings_ingest.overview_service import to_apa, to_apa_list

EXPORT_DIR = os.path.join(BASE_DIR, "export", "tableau")
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")

def export_all():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("1. Exporting Master Papers Flat CSV (tableau_papers_master.csv)...")
    # Fetch pre-aggregated labels per paper
    cur.execute("""
        SELECT 
            paper_id,
            label_id,
            label_value,
            centrality_score
        FROM paper_labels;
    """)
    labels_by_paper = defaultdict(lambda: defaultdict(list))
    scores_by_paper = defaultdict(dict)

    for pid, lid, lval, cscore in cur.fetchall():
        labels_by_paper[pid][lid].append(lval)
        if cscore is not None:
            # Keep max centrality score if multiple
            current = scores_by_paper[pid].get(lid, 0)
            if cscore > current:
                scores_by_paper[pid][lid] = cscore

    # Fetch master papers with authors
    cur.execute("""
        SELECT 
            p.id AS paper_id,
            p.title,
            p.year,
            p.conference,
            p.paper_type,
            p.doi,
            p.handle,
            p.handle_url,
            p.citation,
            p.start_page,
            p.end_page,
            CASE WHEN p.end_page >= p.start_page THEN p.end_page - p.start_page + 1 ELSE NULL END AS page_count,
            COUNT(pa.author_id) AS author_count,
            (SELECT a2.display_name FROM authors a2 JOIN paper_authors pa2 ON a2.id = pa2.author_id 
             WHERE pa2.paper_id = p.id AND pa2.author_order = 0 LIMIT 1) AS primary_author,
            GROUP_CONCAT(a.display_name, '; ' ORDER BY pa.author_order ASC) AS authors_list,
            p.abstract
        FROM papers p
        LEFT JOIN paper_authors pa ON p.id = pa.paper_id
        LEFT JOIN authors a ON pa.author_id = a.id
        GROUP BY p.id
        ORDER BY p.year DESC, p.id ASC;
    """)

    paper_rows = cur.fetchall()
    master_out = []
    header = [
        "paper_id", "title", "year", "conference", "paper_type", "doi", "handle", "handle_url",
        "citation", "start_page", "end_page", "page_count", "author_count", "primary_author", "authors_list",
        "setting", "subject", "tpack_tk_labels", "tpack_tk_centrality_score",
        "tpack_pk_labels", "tpack_pk_centrality_score", "tpack_ck_labels", "tpack_ck_centrality_score",
        "conceptualisations_list", "abstract"
    ]

    for row in paper_rows:
        pid = row[0]
        p_labels = labels_by_paper[pid]
        p_scores = scores_by_paper[pid]

        setting_str = "; ".join(p_labels.get("setting", ["Theoretical / Unspecified"]))
        subject_str = "; ".join(p_labels.get("subject", ["Interdisciplinary & General"]))
        tk_str = "; ".join(p_labels.get("tpack_tk", ["Non-digital / Unspecified"]))
        tk_score = p_scores.get("tpack_tk", 1)
        pk_str = "; ".join(p_labels.get("tpack_pk", ["General / Reflective"]))
        pk_score = p_scores.get("tpack_pk", 1)
        ck_str = "; ".join(p_labels.get("tpack_ck", ["Interdisciplinary & General"]))
        ck_score = p_scores.get("tpack_ck", 1)
        concepts_str = "; ".join(p_labels.get("conceptualisation", []))

        row_list = list(row[:15])
        row_list[13] = to_apa(row[13]) if row[13] else ""
        row_list[14] = to_apa_list((row[14] or "").split("; ")) if row[14] else ""

        master_out.append(row_list + [
            setting_str, subject_str, tk_str, tk_score,
            pk_str, pk_score, ck_str, ck_score,
            concepts_str, row[15]
        ])

    master_path = os.path.join(EXPORT_DIR, "tableau_papers_master.csv")
    with open(master_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(master_out)
    print(f"   -> Wrote {len(master_out)} rows to {master_path}")

    print("2. Exporting Tall Labels Fact CSV (tableau_paper_labels_tall.csv)...")
    cur.execute("""
        SELECT 
            pl.paper_id,
            p.year,
            p.conference,
            pl.label_id AS dimension,
            pl.hierarchy_level_1,
            pl.hierarchy_level_2,
            pl.label_value,
            pl.centrality_score,
            pl.confidence,
            pl.method,
            pl.status,
            pl.notes
        FROM paper_labels pl
        JOIN papers p ON pl.paper_id = p.id
        ORDER BY p.year DESC, pl.paper_id, pl.label_id;
    """)
    tall_rows = cur.fetchall()
    tall_path = os.path.join(EXPORT_DIR, "tableau_paper_labels_tall.csv")
    with open(tall_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "paper_id", "year", "conference", "dimension", "hierarchy_level_1", "hierarchy_level_2",
            "label_value", "centrality_score", "confidence", "method", "status", "notes"
        ])
        w.writerows(tall_rows)
    print(f"   -> Wrote {len(tall_rows)} rows to {tall_path}")

    print("3. Exporting Author Collaboration Network CSV (tableau_author_network.csv)...")
    cur.execute("""
        SELECT 
            author_1_name,
            author_2_name,
            year,
            COUNT(paper_id) AS collaboration_count
        FROM author_collaborations
        GROUP BY author_1_name, author_2_name, year
        ORDER BY year DESC, collaboration_count DESC;
    """)
    net_rows = cur.fetchall()
    net_rows_apa = [
        (to_apa(r[0]), to_apa(r[1]), r[2], r[3])
        for r in net_rows
    ]
    net_path = os.path.join(EXPORT_DIR, "tableau_author_network.csv")
    with open(net_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["author_1_name", "author_2_name", "year", "collaboration_count"])
        w.writerows(net_rows_apa)
    print(f"   -> Wrote {len(net_rows_apa)} rows to {net_path}")

    print("4. Exporting Citation Links CSV (tableau_citation_links.csv)...")
    cur.execute("""
        SELECT 
            citing_paper_id,
            cited_paper_id,
            citing_year,
            cited_year,
            context_snippet,
            status,
            notes
        FROM paper_citations
        ORDER BY citing_year DESC, cited_year DESC;
    """)
    cit_rows = cur.fetchall()
    cit_path = os.path.join(EXPORT_DIR, "tableau_citation_links.csv")
    with open(cit_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["citing_paper_id", "cited_paper_id", "citing_year", "cited_year", "context_snippet", "status", "notes"])
        w.writerows(cit_rows)
    print(f"   -> Wrote {len(cit_rows)} rows to {cit_path}")

    print("5. Exporting Callon 2x2 Research Density Matrix (tableau_density_matrix.csv)...")
    # Compute Centrality (cross-label co-occurrences) & Density (paper volume) per label
    cur.execute("""
        SELECT 
            pl1.label_id,
            pl1.label_value,
            COUNT(DISTINCT pl1.paper_id) AS paper_count,
            COUNT(DISTINCT pl2.label_value) AS cross_label_co_occurrences
        FROM paper_labels pl1
        LEFT JOIN paper_labels pl2 ON pl1.paper_id = pl2.paper_id AND (pl1.label_id != pl2.label_id OR pl1.label_value != pl2.label_value)
        GROUP BY pl1.label_id, pl1.label_value;
    """)
    density_raw = cur.fetchall()

    if density_raw:
        # Calculate medians for quadrant assignment
        all_counts = [r[2] for r in density_raw]
        all_cooc = [r[3] for r in density_raw]
        median_density = sorted(all_counts)[len(all_counts)//2]
        median_centrality = sorted(all_cooc)[len(all_cooc)//2]

        density_out = []
        for lid, lval, count, cooc in density_raw:
            is_high_d = count >= median_density
            is_high_c = cooc >= median_centrality
            if is_high_d and is_high_c:
                quad = "Quadrant I: Motor Themes (High Density, High Centrality)"
            elif is_high_d and not is_high_c:
                quad = "Quadrant II: Niche Themes (High Density, Low Centrality)"
            elif not is_high_d and is_high_c:
                quad = "Quadrant III: Basic & Transversal (Low Density, High Centrality)"
            else:
                quad = "Quadrant IV: Emerging / Declining (Low Density, Low Centrality)"

            density_out.append([lid, lval, count, cooc, median_density, median_centrality, quad])

        density_path = os.path.join(EXPORT_DIR, "tableau_density_matrix.csv")
        with open(density_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "dimension", "label_value", "paper_count_density", "cross_label_centrality",
                "median_density_threshold", "median_centrality_threshold", "callon_quadrant"
            ])
            w.writerows(density_out)
        print(f"   -> Wrote {len(density_out)} rows to {density_path}")

    # Write README
    readme_content = f"""# ISLS 10-Year Proceedings (2016–2026) Tableau Data Suite

This directory contains pre-processed, Tableau-optimized CSV exports for analyzing the 4,744 papers in the ISLS proceedings repository.

## Exported Files

### 1. `tableau_papers_master.csv` (1 row per paper - 4,744 rows)
- **Primary Key**: `paper_id`
- **Fields**: Title, Year, Conference, Paper Type, DOI, Citation, Page Count, Author Count, Primary Author, Semicolon-delimited Authors List, Setting, Subject, TPACK TK/PK/CK labels and 1-5 Centrality Scores, Conceptualisations List, Abstract.
- **Tableau Usage**: Drag directly into Tableau as a flat table for rapid trend charts, year-by-year histograms, and publication breakdowns.

### 2. `tableau_paper_labels_tall.csv` (Normalized Fact Table - {len(tall_rows):,} rows)
- **Grain**: Paper × Label
- **Fields**: `paper_id`, `year`, `conference`, `dimension`, `hierarchy_level_1`, `hierarchy_level_2`, `label_value`, `centrality_score`, `confidence`, `method`, `status`, `notes`.
- **Tableau Usage**: Connect to `tableau_papers_master.csv` via Tableau's Relationship canvas on `paper_id = paper_id`. Use `dimension` as a global slicer to filter or facet across TPACK, Setting, Subject, and Theories dynamically.

### 3. `tableau_author_network.csv` (Co-Authorship Edge Table - {len(net_rows):,} rows)
- **Fields**: `author_1_name`, `author_2_name`, `year`, `collaboration_count`.
- **Tableau Usage**: Filter by Year or min collaboration count (e.g. >= 2) to visualize research lab clusters and co-authorship networks.

### 4. `tableau_citation_links.csv` (Cross-Citation Edge Table - {len(cit_rows):,} rows)
- **Fields**: `citing_paper_id`, `cited_paper_id`, `citing_year`, `cited_year`, `context_snippet`, `status`, `notes`.
- **Tableau Usage**: Use in Sankey diagrams or Gantt charts to track knowledge diffusion from earlier proceedings (2016–2018) to modern research (2024–2026).

### 5. `tableau_density_matrix.csv` (Callon's 2x2 Strategic Diagram - {len(density_out)} labels)
- **Fields**: `dimension`, `label_value`, `paper_count_density`, `cross_label_centrality`, `callon_quadrant`.
- **Tableau Usage**: Create a scatter plot with `cross_label_centrality` on Columns (X) and `paper_count_density` on Rows (Y). Add reference lines at median values to partition the 4 quadrants automatically.

---
*Note: This extract was generated via Phase 1 (0-cost title/abstract lexical heuristics). Field statuses and notes document areas ready for Phase 2 batched LLM claim verification and Phase 3 reference list extraction.*
"""
    with open(os.path.join(EXPORT_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    conn.close()
    print("\nTableau Export Suite successfully generated in export/tableau/")

if __name__ == "__main__":
    export_all()
