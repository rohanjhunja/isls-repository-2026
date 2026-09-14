import os
import sqlite3
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "proceedings.db"


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create or connect to SQLite database with WAL mode enabled."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: str = DEFAULT_DB_PATH):
    """Initialize relational SQLite schema and FTS5 search virtual tables."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Papers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        handle TEXT,
        handle_url TEXT,
        doi TEXT,
        title TEXT NOT NULL,
        year INTEGER NOT NULL,
        conference TEXT NOT NULL,
        paper_type TEXT,
        citation TEXT,
        start_page INTEGER,
        end_page INTEGER,
        abstract TEXT,
        boundary_confidence REAL DEFAULT 1.0,
        filename TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Authors table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        display_name TEXT UNIQUE NOT NULL
    );
    """)

    # Paper Authors junction table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS paper_authors (
        paper_id TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        author_order INTEGER NOT NULL,
        PRIMARY KEY (paper_id, author_id),
        FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
        FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
    );
    """)

    # Sections table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sections (
        id TEXT PRIMARY KEY,
        paper_id TEXT NOT NULL,
        original_heading TEXT NOT NULL,
        normalized_section TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        order_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        pdf_start_page INTEGER,
        pdf_end_page INTEGER,
        FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
    );
    """)

    # FTS5 Virtual Table for Lexical BM25 Search
    cursor.execute("DROP TABLE IF EXISTS papers_fts;")
    cursor.execute("""
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

    conn.commit()
    conn.close()
    logger.info(f"Initialized clean SQLite schema and FTS5 table in {db_path}")


def insert_paper_record(conn: sqlite3.Connection, paper_data: Dict[str, Any], sections_data: List[Dict[str, Any]]) -> str:
    """Insert a single paper, authors, sections, and FTS5 index entries."""
    cursor = conn.cursor()

    # Insert paper
    cursor.execute("""
    INSERT OR REPLACE INTO papers (
        id, handle, handle_url, doi, title, year, conference, paper_type,
        citation, start_page, end_page, abstract, boundary_confidence, filename
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        paper_data["id"],
        paper_data.get("handle"),
        paper_data.get("handle_url"),
        paper_data.get("doi"),
        paper_data["title"],
        paper_data["year"],
        paper_data.get("conference", "ISLS"),
        paper_data.get("paper_type", "Paper"),
        paper_data.get("citation"),
        paper_data.get("start_page"),
        paper_data.get("end_page"),
        paper_data.get("abstract"),
        paper_data.get("boundary_confidence", 1.0),
        paper_data.get("filename"),
    ))

    # Insert authors
    author_names = paper_data.get("authors", [])
    author_text_list = []
    for order, author_name in enumerate(author_names):
        if not author_name or not author_name.strip():
            continue
        clean_name = author_name.strip()
        author_text_list.append(clean_name)

        cursor.execute("INSERT OR IGNORE INTO authors (display_name) VALUES (?)", (clean_name,))
        cursor.execute("SELECT id FROM authors WHERE display_name = ?", (clean_name,))
        row = cursor.fetchone()
        if row:
            author_id = row[0]
            cursor.execute(
                "INSERT OR REPLACE INTO paper_authors (paper_id, author_id, author_order) VALUES (?, ?, ?)",
                (paper_data["id"], author_id, order + 1),
            )

    authors_str = ", ".join(author_text_list)

    # Insert sections and FTS5 entries
    for sec_idx, sec in enumerate(sections_data):
        sec_id = sec.get("id") or f"{paper_data['id']}_sec_{sec_idx+1}"
        cursor.execute("""
        INSERT OR REPLACE INTO sections (
            id, paper_id, original_heading, normalized_section, level, order_index, text, pdf_start_page, pdf_end_page
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sec_id,
            paper_data["id"],
            sec["original_heading"],
            sec["normalized_section"],
            sec.get("level", 1),
            sec_idx + 1,
            sec["text"],
            sec.get("pdf_start_page"),
            sec.get("pdf_end_page"),
        ))

        # Index section in FTS5
        cursor.execute("""
        INSERT INTO papers_fts (paper_id, title, abstract, authors_text, section_title, body_text, normalized_section)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_data["id"],
            paper_data["title"],
            paper_data.get("abstract") or "",
            authors_str,
            sec["original_heading"],
            sec["text"],
            sec["normalized_section"],
        ))

    conn.commit()
    return paper_data["id"]
