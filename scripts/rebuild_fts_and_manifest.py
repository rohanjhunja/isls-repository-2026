#!/usr/bin/env python3
"""
Rebuild SQLite FTS5 Virtual Table (papers_fts) across 100% of Section Texts
Allows lexical BM25 queries across full body text of all papers (2016–2026).
"""

import os
import time
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")

def rebuild_fts():
    print("=== Rebuilding papers_fts FTS5 Search Index ===")
    t0 = time.time()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Drop old FTS table
    print("Dropping and recreating papers_fts virtual table...")
    c.execute("DROP TABLE IF EXISTS papers_fts;")
    c.execute("""
    CREATE VIRTUAL TABLE papers_fts USING fts5(
        paper_id UNINDEXED,
        title,
        abstract,
        authors_text,
        section_title,
        body_text,
        normalized_section UNINDEXED,
        tokenize = 'unicode61 remove_diacritics 1'
    );
    """)

    # Populate FTS table from papers and sections
    print("Indexing papers and section body texts...")
    c.execute("""
    INSERT INTO papers_fts (paper_id, title, abstract, authors_text, section_title, body_text, normalized_section)
    SELECT 
        p.id,
        p.title,
        COALESCE(p.abstract, ''),
        COALESCE((
            SELECT GROUP_CONCAT(a.display_name, ', ')
            FROM paper_authors pa
            JOIN authors a ON a.id = pa.author_id
            WHERE pa.paper_id = p.id
        ), '') as authors_text,
        s.original_heading as section_title,
        s.text as body_text,
        s.normalized_section
    FROM papers p
    JOIN sections s ON s.paper_id = p.id;
    """)
    sections_indexed = c.rowcount

    # Also index any papers that have no sections (e.g. abstract only) so they are searchable by title/abstract/authors
    c.execute("""
    INSERT INTO papers_fts (paper_id, title, abstract, authors_text, section_title, body_text, normalized_section)
    SELECT 
        p.id,
        p.title,
        COALESCE(p.abstract, ''),
        COALESCE((
            SELECT GROUP_CONCAT(a.display_name, ', ')
            FROM paper_authors pa
            JOIN authors a ON a.id = pa.author_id
            WHERE pa.paper_id = p.id
        ), '') as authors_text,
        'Abstract' as section_title,
        COALESCE(p.abstract, '') as body_text,
        'Abstract & Introduction' as normalized_section
    FROM papers p
    WHERE NOT EXISTS (SELECT 1 FROM sections s WHERE s.paper_id = p.id);
    """)
    abstracts_indexed = c.rowcount

    indexed_count = sections_indexed + abstracts_indexed
    conn.commit()
    conn.close()
    elapsed = time.time() - t0
    print(f"Indexed {indexed_count} documents ({sections_indexed} sections + {abstracts_indexed} abstract-only) into papers_fts in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    rebuild_fts()
