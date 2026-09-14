#!/usr/bin/env python3
"""Initialize taxonomy, label, author collaboration, and citation linking tables in proceedings.db."""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'proceedings.db')

def init_tables(db_path=DB_PATH):
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS label_definitions (
        id TEXT PRIMARY KEY,
        dimension TEXT NOT NULL,
        display_name TEXT NOT NULL,
        hierarchy_level INTEGER DEFAULT 1,
        parent_id TEXT,
        description TEXT,
        allowed_values TEXT,
        version TEXT DEFAULT '1.0.0',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS paper_labels (
        paper_id TEXT NOT NULL,
        label_id TEXT NOT NULL,
        label_value TEXT NOT NULL,
        hierarchy_level_1 TEXT,
        hierarchy_level_2 TEXT,
        centrality_score INTEGER,
        confidence REAL DEFAULT 1.0,
        evidence_snippet TEXT,
        method TEXT NOT NULL,
        status TEXT DEFAULT 'extracted',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (paper_id, label_id, label_value),
        FOREIGN KEY (paper_id) REFERENCES papers(id)
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_paper_labels_label ON paper_labels(label_id, label_value);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_paper_labels_dim ON paper_labels(label_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_paper_labels_paper ON paper_labels(paper_id);")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS author_collaborations (
        author_1_id INTEGER NOT NULL,
        author_2_id INTEGER NOT NULL,
        author_1_name TEXT NOT NULL,
        author_2_name TEXT NOT NULL,
        year INTEGER NOT NULL,
        paper_id TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        PRIMARY KEY (author_1_id, author_2_id, paper_id)
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_collab_year ON author_collaborations(year);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_collab_authors ON author_collaborations(author_1_name, author_2_name);")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS paper_citations (
        citing_paper_id TEXT NOT NULL,
        cited_paper_id TEXT NOT NULL,
        citing_year INTEGER NOT NULL,
        cited_year INTEGER NOT NULL,
        context_snippet TEXT,
        status TEXT DEFAULT 'detected',
        notes TEXT,
        PRIMARY KEY (citing_paper_id, cited_paper_id)
    );
    """)

    conn.commit()
    conn.close()
    print("Taxonomy tables initialized successfully.")

if __name__ == '__main__':
    init_tables()
