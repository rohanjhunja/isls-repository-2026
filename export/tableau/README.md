# ISLS 10-Year Proceedings (2016–2026) Tableau Data Suite

This directory contains pre-processed, Tableau-optimized CSV exports for analyzing the 4,744 papers in the ISLS proceedings repository.

## Exported Files

### 1. `tableau_papers_master.csv` (1 row per paper - 4,744 rows)
- **Primary Key**: `paper_id`
- **Fields**: Title, Year, Conference, Paper Type, DOI, Citation, Page Count, Author Count, Primary Author, Semicolon-delimited Authors List, Setting, Subject, TPACK TK/PK/CK labels and 1-5 Centrality Scores, Conceptualisations List, Abstract.
- **Tableau Usage**: Drag directly into Tableau as a flat table for rapid trend charts, year-by-year histograms, and publication breakdowns.

### 2. `tableau_paper_labels_tall.csv` (Normalized Fact Table - 32,575 rows)
- **Grain**: Paper × Label
- **Fields**: `paper_id`, `year`, `conference`, `dimension`, `hierarchy_level_1`, `hierarchy_level_2`, `label_value`, `centrality_score`, `confidence`, `method`, `status`, `notes`.
- **Tableau Usage**: Connect to `tableau_papers_master.csv` via Tableau's Relationship canvas on `paper_id = paper_id`. Use `dimension` as a global slicer to filter or facet across TPACK, Setting, Subject, and Theories dynamically.

### 3. `tableau_author_network.csv` (Co-Authorship Edge Table - 54,951 rows)
- **Fields**: `author_1_name`, `author_2_name`, `year`, `collaboration_count`.
- **Tableau Usage**: Filter by Year or min collaboration count (e.g. >= 2) to visualize research lab clusters and co-authorship networks.

### 4. `tableau_citation_links.csv` (Cross-Citation Edge Table - 1,840 rows)
- **Fields**: `citing_paper_id`, `cited_paper_id`, `citing_year`, `cited_year`, `context_snippet`, `status`, `notes`.
- **Tableau Usage**: Use in Sankey diagrams or Gantt charts to track knowledge diffusion from earlier proceedings (2016–2018) to modern research (2024–2026).

### 5. `tableau_density_matrix.csv` (Callon's 2x2 Strategic Diagram - 59 labels)
- **Fields**: `dimension`, `label_value`, `paper_count_density`, `cross_label_centrality`, `callon_quadrant`.
- **Tableau Usage**: Create a scatter plot with `cross_label_centrality` on Columns (X) and `paper_count_density` on Rows (Y). Add reference lines at median values to partition the 4 quadrants automatically.

---
*Note: This extract was generated via Phase 1 (0-cost title/abstract lexical heuristics). Field statuses and notes document areas ready for Phase 2 batched LLM claim verification and Phase 3 reference list extraction.*
