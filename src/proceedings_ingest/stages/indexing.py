import json
import os
import sqlite3
from typing import List
from proceedings_ingest.models import Collection, Paper


class IndexingStage:

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.index_dir = os.path.join(data_dir, "index")
        os.makedirs(self.index_dir, exist_ok=True)
        self.db_path = os.path.join(self.index_dir, "proceedings.db")

    def build_index(self, collection: Collection):
        """Build SQLite database with FTS5 search table across paper sections."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create collections table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                kind TEXT,
                title TEXT,
                sha256 TEXT,
                paper_count INTEGER,
                data_json TEXT
            )
        """
        )

        # Create papers table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                collection_id TEXT,
                title TEXT,
                authors TEXT,
                abstract TEXT,
                pdf_start INTEGER,
                pdf_end INTEGER,
                data_json TEXT,
                FOREIGN KEY (collection_id) REFERENCES collections (id)
            )
        """
        )

        # Create FTS5 virtual table for section search
        cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
                paper_id,
                collection_id,
                title,
                authors,
                section_id,
                heading_original,
                canonical_roles,
                text,
                pdf_page_start,
                pdf_page_end
            )
        """
        )

        # Insert collection record
        cursor.execute(
            "INSERT OR REPLACE INTO collections VALUES (?, ?, ?, ?, ?, ?)",
            (
                collection.id,
                collection.kind,
                collection.title,
                collection.source.sha256,
                len(collection.papers),
                collection.model_dump_json(),
            ),
        )

        # Insert papers and section FTS records
        for paper in collection.papers:
            author_str = "; ".join(a.display_name for a in paper.authors)
            cursor.execute(
                "INSERT OR REPLACE INTO papers VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    paper.id,
                    collection.id,
                    paper.title,
                    author_str,
                    paper.abstract or "",
                    paper.pages.pdf_start,
                    paper.pages.pdf_end,
                    paper.model_dump_json(),
                ),
            )

            for sec in paper.sections:
                roles_str = ",".join(sec.canonical_roles)
                cursor.execute(
                    """
                    INSERT INTO sections_fts (
                        paper_id, collection_id, title, authors,
                        section_id, heading_original, canonical_roles,
                        text, pdf_page_start, pdf_page_end
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        paper.id,
                        collection.id,
                        paper.title,
                        author_str,
                        sec.id,
                        sec.heading_original,
                        roles_str,
                        sec.text,
                        sec.pages.pdf_start,
                        sec.pages.pdf_end,
                    ),
                )

        conn.commit()
        conn.close()
        return self.db_path
