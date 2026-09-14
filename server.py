import http.server
import socketserver
import json
import urllib.parse
import os
import sqlite3
import re
import sys
import mimetypes
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
from proceedings_ingest.dipstick_engine import DipstickEngine
from proceedings_ingest.review_service import ReviewService
from proceedings_ingest.overview_service import OverviewService
from proceedings_ingest.lexical_search import search_lexical_bm25
from proceedings_ingest.reranker import rerank_candidates
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors, sanitize_title_string, sanitize_author_list

PORT = 8888
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REVIEWS_DIR = os.path.join(DATA_DIR, 'reviews')
CACHE_DIR = os.path.join(DATA_DIR, 'derived', 'reviews_cache')
DB_PATH = os.path.join(BASE_DIR, 'proceedings.db')
WEB_DIR = os.path.join(BASE_DIR, 'web')

DIPSTICK_ENGINE = DipstickEngine(DATA_DIR)
REVIEW_SERVICE = ReviewService(DATA_DIR)
OVERVIEW_SERVICE = OverviewService(DB_PATH)

def get_db_connection():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    return None

def read_review_metadata(fpath):
    mtime = os.path.getmtime(fpath)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    paper_count = len(data.get('papers', [])) or len(data.get('paper_ids', []))
    return {
        'id': data.get('id', os.path.basename(fpath).replace('.json', '')),
        'name': data.get('name', 'Saved Review'),
        'description': data.get('description', ''),
        'created_at': data.get('created_at', datetime.fromtimestamp(mtime).isoformat()),
        'paper_count': paper_count,
        '_mtime': mtime
    }

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_HEAD(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        if path in ['/', '/cover', '/cover/', '/overview', '/overview/', '/viewer', '/viewer/']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            return
        super().do_HEAD()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_DELETE(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path

        if path.startswith('/api/reviews/'):
            review_id = path.replace('/api/reviews/', '').strip()
            review_json = os.path.join(REVIEWS_DIR, f"{review_id}.json")
            cache_json = os.path.join(CACHE_DIR, f"{review_id}.json")

            deleted = False
            if os.path.exists(review_json):
                os.remove(review_json)
                deleted = True
            if os.path.exists(cache_json):
                os.remove(cache_json)

            self.send_response(200 if deleted else 404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'deleted' if deleted else 'not_found', 'id': review_id}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        query_params = urllib.parse.parse_qs(url_parts.query)

        if path in ['/', '/cover', '/cover/']:
            cover_html_path = os.path.join(WEB_DIR, 'index.html')
            if not os.path.exists(cover_html_path):
                cover_html_path = os.path.join(WEB_DIR, 'cover.html')
            if os.path.exists(cover_html_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                with open(cover_html_path, 'rb') as f:
                    self.wfile.write(f.read())
                return

        elif path in ['/viewer', '/viewer/']:
            viewer_html_path = os.path.join(WEB_DIR, 'viewer.html')
            if not os.path.exists(viewer_html_path):
                viewer_html_path = os.path.join(WEB_DIR, 'index.html')
            if os.path.exists(viewer_html_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                with open(viewer_html_path, 'rb') as f:
                    self.wfile.write(f.read())
                return

        elif path in ['/overview', '/overview/']:
            overview_html_path = os.path.join(WEB_DIR, 'overview.html')
            if os.path.exists(overview_html_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                with open(overview_html_path, 'rb') as f:
                    self.wfile.write(f.read())
                return

        elif path == '/api/overview/meta':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = OVERVIEW_SERVICE.get_meta()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        elif path == '/api/overview/trends':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            dim = query_params.get('dimension', ['tpack_tk'])[0]
            labels_param = query_params.get('labels', [''])[0]
            labels = [l.strip() for l in labels_param.split(',') if l.strip()] if labels_param else None
            level = int(query_params.get('level', ['2'])[0])
            min_c = int(query_params.get('min_centrality', ['1'])[0])
            start_yr = int(query_params.get('start_year', ['2016'])[0])
            end_yr = int(query_params.get('end_year', ['2026'])[0])
            data = OVERVIEW_SERVICE.get_trends(dimension=dim, labels=labels, hierarchy_level=level,
                                               min_centrality=min_c, start_year=start_yr, end_year=end_yr)
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        elif path == '/api/overview/density':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            dim = query_params.get('dimension', [None])[0]
            data = OVERVIEW_SERVICE.get_density_matrix(dimension=dim)
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        elif path == '/api/overview/network':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            start_yr = int(query_params.get('start_year', ['2016'])[0])
            end_yr = int(query_params.get('end_year', ['2026'])[0])
            min_w = int(query_params.get('min_weight', ['2'])[0])
            limit = int(query_params.get('limit', ['70'])[0])
            data = OVERVIEW_SERVICE.get_author_network(start_year=start_yr, end_year=end_yr,
                                                       min_weight=min_w, limit=limit)
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        elif path == '/api/overview/citations':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            limit = int(query_params.get('limit', ['50'])[0])
            data = OVERVIEW_SERVICE.get_citation_flows(limit=limit)
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        elif path == '/api/overview/papers':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            dim = query_params.get('dimension', [None])[0]
            label = query_params.get('label', [None])[0]
            year = query_params.get('year', [None])[0]
            author = query_params.get('author', [None])[0]
            year_val = int(year) if year and year.isdigit() else None
            min_c = int(query_params.get('min_centrality', ['1'])[0])
            limit = int(query_params.get('limit', ['25'])[0])
            data = OVERVIEW_SERVICE.get_papers(dimension=dim, label=label, year=year_val,
                                               author=author, min_centrality=min_c, limit=limit)
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        elif path == '/api/overview/beautiful-papers':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            bp_path = os.path.join(DATA_DIR, 'derived', 'beautiful_papers.json')
            if not os.path.exists(bp_path):
                bp_path = os.path.join(WEB_DIR, 'beautiful_papers.json')
            if os.path.exists(bp_path):
                with open(bp_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(json.dumps({'error': 'Data not generated'}).encode('utf-8'))
            return

        elif path == '/api/titles':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            titles_index = DIPSTICK_ENGINE.get_titles_index()
            self.wfile.write(json.dumps(titles_index).encode('utf-8'))
            return

        elif path == '/api/dipstick/search':
            query = query_params.get('q', [''])[0] or query_params.get('query', [''])[0]
            sort_by = query_params.get('sort_by', ['relevance'])[0]
            sort_order = query_params.get('sort_order', ['desc'])[0]
            section = query_params.get('section', [None])[0]
            limit = int(query_params.get('limit', [50])[0])

            hits = search_lexical_bm25(
                query=query,
                normalized_section=section if section not in ['all', 'full_text', 'abstract'] else None,
                sort_by=sort_by,
                sort_order=sort_order,
                limit=limit,
                db_path=DB_PATH
            )

            if sort_by == 'relevance' and hits:
                hits = rerank_candidates(query, hits, top_k=limit)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'query': query, 'total_hits': len(hits), 'results': hits}).encode('utf-8'))
            return

        elif path == '/api/dipstick/expand':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            kw_param = query_params.get('keywords', [''])[0]
            section = query_params.get('section', ['abstract'])[0]
            kw_list = [k.strip() for k in kw_param.split(',') if k.strip()] or DIPSTICK_ENGINE.DEFAULT_KEYWORDS

            try:
                for event in DIPSTICK_ENGINE.expand_section_stream(kw_list, section_name=section):
                    msg = f"data: {json.dumps(event)}\n\n"
                    self.wfile.write(msg.encode('utf-8'))
                    self.wfile.flush()
            except Exception:
                pass
            return

        elif path == '/api/reviews/save':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            name = query_params.get('name', ['Custom Dipstick Review'])[0]
            kw_param = query_params.get('keywords', [''])[0]
            kw_list = [k.strip() for k in kw_param.split(',') if k.strip()]
            pids_param = query_params.get('paper_ids', [''])[0]
            paper_ids = [p.strip() for p in pids_param.split(',') if p.strip()] if pids_param else None

            manifest = DIPSTICK_ENGINE.save_dipstick_review(name, kw_list, paper_ids=paper_ids)
            self.wfile.write(json.dumps(manifest).encode('utf-8'))
            return

        elif path.rstrip('/') == '/api/reviews':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            reviews_list = []
            if os.path.exists(REVIEWS_DIR):
                for fname in os.listdir(REVIEWS_DIR):
                    if fname.endswith('.json'):
                        fpath = os.path.join(REVIEWS_DIR, fname)
                        try:
                            meta_info = read_review_metadata(fpath)
                            reviews_list.append(meta_info)
                        except Exception:
                            pass

            reviews_list.sort(key=lambda r: (r.get('created_at') or '', r.get('_mtime', 0)), reverse=True)
            self.wfile.write(json.dumps(reviews_list).encode('utf-8'))
            return

        elif path.startswith('/api/reviews/') and path.rstrip('/') != '/api/reviews':
            review_id = path.replace('/api/reviews/', '').strip()
            fpath = os.path.join(REVIEWS_DIR, f"{review_id}.json")

            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    review_obj = json.load(f)

                papers = []
                # 1. Check if inline paper objects exist in review file
                if 'papers' in review_obj and isinstance(review_obj['papers'], list) and len(review_obj['papers']) > 0:
                    papers = review_obj['papers']
                else:
                    # 2. Fetch paper objects from SQLite proceedings.db
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        for pid in review_obj.get('paper_ids', []):
                            cursor.execute("SELECT * FROM papers WHERE id = ? OR id LIKE ?", (pid, f"%{pid}%"))
                            p_row = cursor.fetchone()
                            if p_row:
                                p_dict = dict(p_row)
                                actual_id = p_dict['id']
                                cursor.execute("SELECT a.display_name FROM authors a JOIN paper_authors pa ON pa.author_id = a.id WHERE pa.paper_id = ? ORDER BY pa.author_order ASC", (actual_id,))
                                p_dict['authors'] = ", ".join([ar[0] for ar in cursor.fetchall()])
                                papers.append(p_dict)
                        conn.close()

                # Clean titles & authors across papers
                cleaned_papers = []
                for p in papers:
                    raw_t = p.get('title', '')
                    raw_a = p.get('authors', '')
                    if isinstance(raw_a, list):
                        raw_a = ", ".join([a.get('display_name', '') if isinstance(a, dict) else str(a) for a in raw_a])
                    c_t, c_a = repair_title_and_authors(raw_t, str(raw_a or ''), p.get('abstract') or '')
                    p_copy = dict(p)
                    p_copy['title'] = c_t
                    p_copy['authors'] = c_a
                    cleaned_papers.append(p_copy)

                meta_obj = dict(review_obj)
                meta_obj.pop('papers', None)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'meta': meta_obj, 'papers': cleaned_papers}).encode('utf-8'))
                return

            self.send_response(404)
            self.end_headers()
            return

        elif path.startswith('/api/paper/'):
            raw_pid = path.replace('/api/paper/', '').strip()
            paper_id = urllib.parse.unquote(raw_pid)
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM papers WHERE id = ?", (paper_id,))
                p_row = cursor.fetchone()
                if not p_row:
                    cursor.execute("SELECT * FROM papers WHERE id LIKE ? OR handle_url LIKE ?", (f"%{paper_id}%", f"%{paper_id}%"))
                    p_row = cursor.fetchone()
                if p_row:
                    p_dict = dict(p_row)
                    actual_id = p_dict['id']
                    cursor.execute("SELECT a.display_name FROM authors a JOIN paper_authors pa ON pa.author_id = a.id WHERE pa.paper_id = ? ORDER BY pa.author_order ASC", (actual_id,))
                    p_dict['authors'] = ", ".join([ar[0] for ar in cursor.fetchall()])
                    
                    cursor.execute("SELECT * FROM sections WHERE paper_id = ? ORDER BY order_index ASC", (actual_id,))
                    sec_rows = cursor.fetchall()
                    sections = [dict(s) for s in sec_rows]

                    # Fallback to local markdown on disk if DB sections are empty or placeholders
                    has_substantive_sec = any(len(s.get('text', '')) > 100 for s in sections)
                    if not has_substantive_sec:
                        candidate_md_paths = [
                            os.path.join(DATA_DIR, 'derived', 'papers', f'{actual_id}.md'),
                            os.path.join(DATA_DIR, 'derived', f'{p_dict.get("conference", "").lower()}-{p_dict.get("year", "")}-proceedings', 'papers', f'{actual_id}.md')
                        ]
                        for cmd_path in candidate_md_paths:
                            if os.path.exists(cmd_path):
                                try:
                                    with open(cmd_path, 'r', encoding='utf-8', errors='ignore') as mf:
                                        m_lines = mf.readlines()
                                    cur_h = 'Overview'
                                    cur_lines = []
                                    disk_secs = []
                                    for line in m_lines:
                                        if line.startswith('## '):
                                            if cur_lines:
                                                disk_secs.append({'original_heading': cur_h, 'normalized_section': cur_h.lower(), 'order_index': len(disk_secs)+1, 'text': "".join(cur_lines).strip()})
                                                cur_lines = []
                                            cur_h = line[3:].strip()
                                        else:
                                            cur_lines.append(line)
                                    if cur_lines:
                                        disk_secs.append({'original_heading': cur_h, 'normalized_section': cur_h.lower(), 'order_index': len(disk_secs)+1, 'text': "".join(cur_lines).strip()})
                                    if disk_secs:
                                        sections = disk_secs
                                        break
                                except Exception:
                                    pass

                    p_dict['sections'] = sections
                    
                    full_text_parts = []
                    for s in sections:
                        pg_str = f" (Pages {s['pdf_start_page']}-{s['pdf_end_page']})" if s.get('pdf_start_page') else ""
                        full_text_parts.append(f"### {s['original_heading']}{pg_str}\n{s['text']}")
                    
                    p_dict['full_text'] = "\n\n".join(full_text_parts)
                    total_words = sum(len(s.get('text', '').split()) for s in sections)
                    p_dict['total_words'] = total_words
                    p_dict['estimated_reading_minutes'] = max(1, round(total_words / 220)) if total_words > 0 else 0
                    p_dict['sections_count'] = len(sections)
                    p_dict['has_full_text'] = total_words > 120
                    
                    conn.close()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(p_dict).encode('utf-8'))
                    return
                conn.close()

            self.send_response(404)
            self.end_headers()
            return

        super().do_GET()

def run_server():
    os.makedirs(REVIEWS_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print(f"ISLS Literature Review Viewer Server running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
