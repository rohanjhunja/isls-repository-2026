import sqlite3
import logging
from typing import List, Dict, Any, Optional
from proceedings_ingest.database import get_db_connection, DEFAULT_DB_PATH

logger = logging.getLogger(__name__)

# BM25 Column Weights: title:8, abstract:5, authors:6, section_title:3, body_text:1
BM25_WEIGHTS = "bm25(papers_fts, 8.0, 5.0, 6.0, 3.0, 1.0)"


def search_lexical_bm25(
    query: str,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    conference: Optional[str] = None,
    paper_type: Optional[str] = None,
    normalized_section: Optional[str] = None,
    sort_by: str = "relevance",  # 'relevance' or 'year'
    sort_order: str = "desc",    # 'desc' or 'asc'
    limit: int = 50,
    db_path: str = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    """Execute fielded lexical BM25 search using SQLite FTS5 index.
    Costs 0 LLM API tokens. Supports sorting by 'relevance' or 'year'."""
    if not query or not query.strip():
        return []

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Clean query for FTS5 syntax
    import re
    cleaned_terms = [f'"{t}"' for t in re.sub(r'[^\w\s]', ' ', query).split() if len(t) > 1]
    if not cleaned_terms:
        return []

    fts_query = " OR ".join(cleaned_terms)

    # Build SQL query joining papers_fts with papers table
    sql = f"""
    SELECT 
        fts.paper_id,
        p.title,
        p.year,
        p.conference,
        p.paper_type,
        p.doi,
        p.handle_url,
        p.abstract,
        fts.section_title,
        fts.normalized_section,
        snippet(papers_fts, 5, '<b>', '</b>', '...', 25) AS snippet,
        {BM25_WEIGHTS} AS rank_score
    FROM papers_fts fts
    JOIN papers p ON p.id = fts.paper_id
    WHERE papers_fts MATCH ?
    """

    params: List[Any] = [fts_query]

    if min_year is not None:
        sql += " AND p.year >= ?"
        params.append(min_year)

    if max_year is not None:
        sql += " AND p.year <= ?"
        params.append(max_year)

    if conference:
        sql += " AND p.conference LIKE ?"
        params.append(f"%{conference}%")

    if paper_type:
        sql += " AND p.paper_type LIKE ?"
        params.append(f"%{paper_type}%")

    if normalized_section:
        sql += " AND fts.normalized_section = ?"
        params.append(normalized_section)

    if sort_by == "year":
        order_dir = "DESC" if sort_order.lower() == "desc" else "ASC"
        sql += f" ORDER BY p.year {order_dir}, rank_score ASC LIMIT ?"
    else:
        sql += " ORDER BY rank_score ASC, p.year DESC LIMIT ?"
    params.append(limit)

    results: List[Dict[str, Any]] = []
    seen_papers = set()

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        for r in rows:
            paper_id = r["paper_id"]
            
            # Fetch authors list
            cursor.execute("""
            SELECT a.display_name FROM authors a
            JOIN paper_authors pa ON pa.author_id = a.id
            WHERE pa.paper_id = ?
            ORDER BY pa.author_order ASC
            """, (paper_id,))
            author_rows = cursor.fetchall()
            authors_list = [ar["display_name"] for ar in author_rows]

            # Rank score is negative in SQLite FTS5 bm25 (smaller/more negative is better)
            score = round(abs(float(r["rank_score"])), 3)

            item = {
                "paper_id": paper_id,
                "title": r["title"],
                "authors": authors_list,
                "year": r["year"],
                "conference": r["conference"],
                "paper_type": r["paper_type"],
                "doi": r["doi"],
                "handle_url": r["handle_url"],
                "abstract": r["abstract"],
                "matched_section_heading": r["section_title"],
                "matched_section_normalized": r["normalized_section"],
                "snippet": r["snippet"],
                "bm25_score": score,
            }

            # Deduplicate by paper_id keeping top section hit
            if paper_id not in seen_papers:
                seen_papers.add(paper_id)
                results.append(item)

    except Exception as e:
        logger.error(f"Error executing BM25 search for query '{query}': {e}")
    finally:
        conn.close()

    return results
