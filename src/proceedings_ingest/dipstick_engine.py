import os
import json
import sqlite3
import re
import uuid
import datetime
import urllib.parse
from typing import List, Dict, Any, Generator, Optional
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors


class DipstickEngine:
    """
    DipstickEngine provides ultra-fast, token-minimized search across 100% of papers
    in the repository. It enforces the priority order: ISLS -> CSCL -> ICLS.
    """

    DEFAULT_KEYWORDS = [
        "Systematic Review", "Scoping Review", "Meta-Analysis", "Umbrella Review",
        "Generative AI", "Large Language Models", "Learning Analytics",
        "Collaborative Learning", "Self-Regulated Learning", "Computational Thinking",
        "Teacher Noticing", "K-12 Education", "Higher Education"
    ]

    CANONICAL_COLUMNS = ["title", "year", "conference", "authors", "abstract"]

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(data_dir)), "proceedings.db")
        if not os.path.exists(self.db_path):
            self.db_path = os.path.join(data_dir, "proceedings.db")
        self.derived_dir = os.path.join(data_dir, "derived")
        self.reviews_dir = os.path.join(data_dir, "reviews")
        os.makedirs(self.reviews_dir, exist_ok=True)
        self._corpus_cache: Optional[List[Dict[str, Any]]] = None

    def _conference_sort_key(self, conf: Any) -> int:
        if isinstance(conf, dict):
            conf = conf.get("acronym", "ISLS")
        c = (str(conf) if conf else "").upper()
        if "ISLS" in c:
            return 1
        elif "CSCL" in c:
            return 2
        elif "ICLS" in c:
            return 3
        return 4

    def _repair_title_text(self, raw_title: str, sec_text: str = "", raw_authors: str = "") -> str:
        clean_t, _ = repair_title_and_authors(raw_title, raw_authors, sec_text)
        return clean_t or raw_title

    def load_title_abstract_corpus(self, force_reload: bool = False) -> List[Dict[str, Any]]:
        """
        Loads 100% of papers into memory, sorted strictly by ISLS -> CSCL -> ICLS.
        """
        if self._corpus_cache is not None and not force_reload:
            return self._corpus_cache

        papers = []

        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
                if cursor.fetchone():
                    query = """
                    SELECT p.id, p.title, p.abstract, p.year, p.conference, p.paper_type, p.doi, p.handle_url
                    FROM papers p
                    """
                    rows = cursor.execute(query).fetchall()
                    for pid, title, abstract, year, conf, paper_type, doi, handle_url in rows:
                        try:
                            # Fetch authors
                            cursor.execute("""
                            SELECT a.display_name FROM authors a
                            JOIN paper_authors pa ON pa.author_id = a.id
                            WHERE pa.paper_id = ?
                            ORDER BY pa.author_order ASC
                            """, (pid,))
                            author_rows = cursor.fetchall()
                            raw_authors_str = ", ".join([ar[0] for ar in author_rows])

                            repaired_title, repaired_authors = repair_title_and_authors(title or "", raw_authors_str, abstract or "")

                            papers.append({
                                "id": pid,
                                "title": repaired_title,
                                "abstract": abstract or "",
                                "year": year or "",
                                "conference": conf or "ISLS",
                                "paper_type": paper_type or "Paper",
                                "doi": doi,
                                "handle_url": handle_url,
                                "authors": repaired_authors,
                                "search_text": f"{repaired_title} {repaired_authors} {abstract or ''}".lower()
                            })
                        except Exception:
                            continue
                conn.close()
            except Exception:
                pass

        if not papers and os.path.exists(self.derived_dir):
            for vol_dir in os.listdir(self.derived_dir):
                vol_path = os.path.join(self.derived_dir, vol_dir, f"{vol_dir}.json")
                if os.path.exists(vol_path):
                    try:
                        with open(vol_path, "r", encoding="utf-8") as f:
                            vol_data = json.load(f)
                            for p in vol_data.get("papers", []):
                                pid = p.get("id") or p.get("paper_id", "")
                                title = p.get("title", "")
                                abstract = p.get("abstract", "")
                                year = p.get("year", "")
                                authors = ", ".join([a.get("display_name", "") if isinstance(a, dict) else str(a) for a in p.get("authors", [])])
                                conf = p.get("conference", "ISLS")
                                papers.append({
                                    "id": pid,
                                    "title": title,
                                    "abstract": abstract,
                                    "year": year,
                                    "conference": conf,
                                    "authors": authors,
                                    "search_text": f"{title} {abstract}".lower()
                                })
                    except Exception:
                        pass

        # Sort strictly by conference priority: ISLS -> CSCL -> ICLS
        papers.sort(key=lambda x: (self._conference_sort_key(x["conference"]), x["year"], x["id"]))
        self._corpus_cache = papers
        return papers

    def get_titles_index(self) -> List[Dict[str, Any]]:
        """
        Returns lightweight title index [id, title, year, conference, authors]
        for instant client-side filtering (< 350 KB total).
        """
        papers = self.load_title_abstract_corpus()
        return [
            {
                "id": p["id"],
                "title": p["title"],
                "year": p["year"],
                "conference": p["conference"],
                "authors": p["authors"],
                "abstract": p.get("abstract", "")
            }
            for p in papers
        ]

    def stream_keyword_matches(
        self, keywords: List[str], scope_fields: Optional[List[str]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generates SSE events keyword-by-keyword in strict order: ISLS -> CSCL -> ICLS.
        """
        papers = self.load_title_abstract_corpus()
        total_papers = len(papers)

        yield {
            "event": "start",
            "total_papers": total_papers,
            "total_keywords": len(keywords),
            "scope": scope_fields or ["title", "abstract"]
        }

        for kw in keywords:
            clean_kw = kw.strip()
            if not clean_kw:
                continue

            pattern = re.compile(r'\b' + re.escape(clean_kw) + r'\b', re.IGNORECASE)
            matched_papers = []
            for paper in papers:
                if pattern.search(paper["search_text"]):
                    matched_papers.append({
                        "id": paper["id"],
                        "title": paper["title"],
                        "year": paper["year"],
                        "conference": paper["conference"],
                        "authors": paper["authors"]
                    })

            yield {
                "event": "keyword_match",
                "keyword": clean_kw,
                "match_count": len(matched_papers),
                "paper_ids": [p["id"] for p in matched_papers],
                "sample_matches": matched_papers[:5],
                "coverage_pct": round((len(matched_papers) / total_papers * 100), 2) if total_papers > 0 else 0.0
            }

        yield {
            "event": "complete",
            "total_papers_scanned": total_papers,
            "timestamp": datetime.datetime.now().isoformat()
        }

    def expand_section_stream(
        self, keywords: List[str], section_name: str = "abstract"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Streams section search results ordered by ISLS -> CSCL -> ICLS and Keyword 1 -> N.
        """
        papers = self.load_title_abstract_corpus()
        total_papers = len(papers)

        yield {
            "event": "expand_start",
            "section": section_name,
            "total_keywords": len(keywords),
            "total_papers": total_papers
        }

        for kw in keywords:
            clean_kw = kw.strip()
            if not clean_kw:
                continue

            pattern = re.compile(r'\b' + re.escape(clean_kw) + r'\b', re.IGNORECASE)
            matched_papers = []

            # Check section text against abstract or database sections
            if section_name.lower() in ["abstract", "abstracts"]:
                for paper in papers:
                    target_blob = paper["abstract"].lower()
                    if pattern.search(target_blob):
                        matched_papers.append({
                            "id": paper["id"],
                            "title": paper["title"],
                            "year": paper["year"],
                            "conference": paper["conference"],
                            "authors": paper["authors"]
                        })
            else:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                sec_filter = ""
                if "method" in section_name.lower():
                    sec_filter = " AND (s.normalized_section LIKE '%method%' OR s.original_heading LIKE '%method%')"
                elif "result" in section_name.lower() or "finding" in section_name.lower():
                    sec_filter = " AND (s.normalized_section LIKE '%result%' OR s.normalized_section LIKE '%finding%' OR s.original_heading LIKE '%result%')"
                elif "discussion" in section_name.lower() or "conclusion" in section_name.lower():
                    sec_filter = " AND (s.normalized_section LIKE '%discussion%' OR s.normalized_section LIKE '%conclusion%')"
                
                c.execute(f"SELECT DISTINCT paper_id FROM sections s WHERE s.text LIKE ? {sec_filter}", (f"%{clean_kw}%",))
                matched_pids = set(r[0] for r in c.fetchall())
                conn.close()

                for paper in papers:
                    if paper["id"] in matched_pids:
                        matched_papers.append({
                            "id": paper["id"],
                            "title": paper["title"],
                            "year": paper["year"],
                            "conference": paper["conference"],
                            "authors": paper["authors"]
                        })

            yield {
                "event": "section_match",
                "section": section_name,
                "keyword": clean_kw,
                "match_count": len(matched_papers),
                "matched_papers": matched_papers
            }

        yield {
            "event": "expand_complete",
            "section": section_name,
            "timestamp": datetime.datetime.now().isoformat()
        }

    def save_dipstick_review(
        self, name: str, keywords: List[str], paper_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Creates and persists a LiteratureReview JSON manifest in data/reviews/rev_<id>.json.
        Always sets selected_columns = ["title", "year", "conference", "authors", "abstract"].
        """
        review_id = f"rev_dipstick_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()

        if paper_ids is None:
            eval_data = self.evaluate_keyword_matches(keywords)
            matched_pids = set()
            for kw_res in eval_data["keywords"].values():
                matched_pids.update(kw_res["matched_paper_ids"])
            paper_ids = sorted(list(matched_pids))

        total_scanned = len(self.load_title_abstract_corpus())

        manifest = {
            "id": review_id,
            "name": name,
            "description": f"Dipstick Review scanning 100% of papers on Title & Abstract scope.",
            "created_at": now,
            "updated_at": now,
            "review_type": "dipstick",
            "scope_fields": ["title", "abstract"],
            "selected_columns": self.CANONICAL_COLUMNS,
            "visible_columns": self.CANONICAL_COLUMNS,
            "keywords": keywords,
            "paper_ids": paper_ids,
            "total_papers_scanned": total_scanned,
            "matched_paper_count": len(paper_ids),
            "tokens_used": 0
        }

        file_path = os.path.join(self.reviews_dir, f"{review_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        md_path = os.path.join(self.reviews_dir, f"{review_id}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Literature Review: {name}\n\n")
            f.write(f"- **Review ID**: `{review_id}`\n")
            f.write(f"- **Created At**: `{now}`\n")
            f.write(f"- **Matching Papers**: {len(paper_ids)}\n")
            f.write(f"- **Selected Columns**: {', '.join(self.CANONICAL_COLUMNS)}\n")
            f.write(f"- **Keywords**: {', '.join(keywords)}\n\n")
            f.write("## Web Viewer Launch Link\n\n")
            kw_param = urllib.parse.quote(", ".join(keywords))
            f.write(f"[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8080/?keywords={kw_param}&review={review_id})\n")

        return manifest

    def evaluate_keyword_matches(
        self, keywords: List[str], scope_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        papers = self.load_title_abstract_corpus()
        results: Dict[str, Dict[str, Any]] = {}

        compiled_patterns = {}
        for kw in keywords:
            clean_kw = kw.strip()
            if clean_kw:
                compiled_patterns[clean_kw] = re.compile(r'\b' + re.escape(clean_kw) + r'\b', re.IGNORECASE)

        for kw, pattern in compiled_patterns.items():
            matched_papers = []
            for paper in papers:
                if pattern.search(paper["search_text"]):
                    matched_papers.append(paper["id"])

            results[kw] = {
                "keyword": kw,
                "match_count": len(matched_papers),
                "matched_paper_ids": matched_papers,
                "coverage_pct": round((len(matched_papers) / len(papers) * 100), 2) if papers else 0.0
            }

        return {
            "total_papers_scanned": len(papers),
            "scope": scope_fields or ["title", "abstract"],
            "keywords": results
        }
