import os
import re
import json
import sqlite3
import gc
from rapidfuzz import fuzz
from proceedings_ingest.utils.memory import get_rss_memory_gb

KNOWN_SECTION_PATTERNS = [
    (r'(?i)^\s*(keynote|keynotes|keynote addresses)\s*$', "Keynotes"),
    (r'(?i)^\s*(special session|special sessions|invited session|invited sessions)\s*$', "Special Session"),
    (r'(?i)^\s*(interactive tools and demos|interactive tools|demos|demos and tools)\s*$', "Interactive Tools and Demos"),
    (r'(?i)^\s*(pre-conference workshops|pre-conference workshop|workshops|workshop)\s*$', "Pre-Conference Workshops"),
    (r'(?i)^\s*(community workshops|community workshop)\s*$', "Community Workshops"),
    (r'(?i)^\s*(early career workshops|early career workshop|early career)\s*$', "Early Career Workshops"),
    (r'(?i)^\s*(doctoral consortium|doctoral consortium papers)\s*$', "Doctoral Consortium"),
    (r'(?i)^\s*(long paper|long papers|full paper|full papers|long paper sessions)\s*$', "Long Papers"),
    (r'(?i)^\s*(short paper|short papers|short paper sessions)\s*$', "Short Papers"),
    (r'(?i)^\s*(practise-oriented paper|practise-oriented papers|practice-oriented paper|practice-oriented papers|practise oriented papers|practice oriented papers)\s*$', "Practise-Oriented Papers"),
    (r'(?i)^\s*(poster|posters|poster sessions|poster presentations|posters and late breaking results)\s*$', "Posters"),
    (r'(?i)^\s*(symposium|symposia|symposium sessions)\s*$', "Symposia"),
    (r'(?i)^\s*(panel|panels|roundtables|roundtable)\s*$', "Panels"),
]

def normalize_section_name(heading_text: str) -> str:
    cleaned = heading_text.strip()
    for pattern, canon in KNOWN_SECTION_PATTERNS:
        if re.search(pattern, cleaned):
            return canon
    # Capitalize title case if no exact match
    return cleaned.title()

def parse_toc_from_markdown(md_path: str):
    if not os.path.exists(md_path):
        return []

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    toc_start = -1
    for i, line in enumerate(lines[:1000]):
        if "table of contents" in line.lower():
            toc_start = i
            break

    if toc_start == -1:
        return []

    # Read TOC lines (stop when we see paper #1 or after ~500 lines)
    toc_lines = lines[toc_start:toc_start + 600]
    
    entries = []
    current_section = "General"

    toc_item_pattern = re.compile(r"^(.+?)\s*\.{3,}\s*(\d+)$")
    
    for line in toc_lines:
        line_str = line.strip()
        if not line_str or line_str.lower() == "table of contents" or "isls proceedings" in line_str.lower():
            continue

        # Check if line is a section header
        is_section_header = False
        for pattern, canon in KNOWN_SECTION_PATTERNS:
            if re.search(pattern, line_str):
                current_section = canon
                is_section_header = True
                break

        if is_section_header:
            continue

        # Check if line is a TOC paper entry with page number
        m = toc_item_pattern.match(line_str)
        if m:
            title_part = m.group(1).strip()
            page_part = m.group(2).strip()
            
            # Filter out known header keywords if wrongly matched
            if not any(k in title_part.lower() for k in ["table of contents", "isls proceedings"]):
                entries.append({
                    "title": title_part,
                    "printed_page": int(page_part),
                    "section": current_section
                })

    return entries

def process_volume(volume_dir: str, db_conn: sqlite3.Connection):
    volume_id = os.path.basename(volume_dir)
    json_path = os.path.join(volume_dir, f"{volume_id}.json")
    md_path = os.path.join(volume_dir, "proceedings.md")

    if not os.path.exists(json_path):
        return 0

    toc_entries = parse_toc_from_markdown(md_path)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data.get("papers", [])
    if not papers:
        return 0

    updated_count = 0

    # Map paper page ranges to TOC entries and section headers
    for i, paper in enumerate(papers):
        paper_title = paper.get("title", "")
        printed_start = paper.get("pages", {}).get("printed_start")
        try:
            p_start_num = int(printed_start) if printed_start and str(printed_start).isdigit() else None
        except ValueError:
            p_start_num = None

        matched_section = None

        # 1. Fuzzy title match against TOC entries
        best_score = 0
        for entry in toc_entries:
            score = fuzz.ratio(paper_title.lower(), entry["title"].lower())
            if score > 80 and score > best_score:
                best_score = score
                matched_section = entry["section"]

        # 2. Page number match if title match wasn't high confidence
        if not matched_section and p_start_num is not None and toc_entries:
            # Find TOC entries preceding or matching printed page
            closest_entry = None
            min_diff = float("inf")
            for entry in toc_entries:
                diff = abs(entry["printed_page"] - p_start_num)
                if diff <= 2 and diff < min_diff:
                    min_diff = diff
                    closest_entry = entry
            if closest_entry:
                matched_section = closest_entry["section"]

        # 3. Default fallback based on paper length or generic
        if not matched_section:
            pdf_start = paper.get("pages", {}).get("pdf_start", 0)
            pdf_end = paper.get("pages", {}).get("pdf_end", 0)
            page_count = max(1, pdf_end - pdf_start + 1)
            
            if page_count >= 7:
                matched_section = "Long Papers"
            elif page_count >= 4:
                matched_section = "Short Papers"
            elif page_count <= 2:
                matched_section = "Posters"
            else:
                matched_section = "General"

        paper["proceedings_section"] = matched_section
        updated_count += 1

    # Write updated collection JSON line by line or formatted
    data["papers"] = papers
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    # Update SQLite database
    cursor = db_conn.cursor()
    cursor.execute("UPDATE collections SET data_json = ? WHERE id = ?", (json.dumps(data), volume_id))
    for paper in papers:
        pid = paper["id"]
        cursor.execute("UPDATE papers SET data_json = ? WHERE id = ?", (json.dumps(paper), pid))
    
    db_conn.commit()
    del data
    del papers
    gc.collect()

    print(f"[{volume_id}] Updated {updated_count} papers with proceedings_section (RSS Memory: {get_rss_memory_gb():.3f} GB)")
    return updated_count

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    derived_dir = os.path.join(base_dir, "data", "derived")
    db_path = os.path.join(base_dir, "data", "index", "proceedings.db")

    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return

    db_conn = sqlite3.connect(db_path)

    volumes = [d for d in os.listdir(derived_dir) if os.path.isdir(os.path.join(derived_dir, d)) and d != "reviews_cache"]
    volumes.sort()

    total_papers = 0
    print(f"Starting proceedings_section extraction across {len(volumes)} volumes...")
    for vol in volumes:
        vol_path = os.path.join(derived_dir, vol)
        count = process_volume(vol_path, db_conn)
        total_papers += count

    db_conn.close()
    print(f"\nExtraction complete! Processed {total_papers} total papers across all volume JSONs.")

if __name__ == '__main__':
    main()
