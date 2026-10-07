import sqlite3
import json
import re
import os
import sys
import datetime

# Ensure src is on path for text cleanup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors

DB_PATH = 'proceedings.db'
SOURCE_REVIEW_PATH = 'workspace/reviews/rev_agentic_teacher_codesign_tel.json'
TARGET_REVIEW_ID = 'rev_agentic_teacher_codesign_tel_2026'
TARGET_JSON_PATH = f'workspace/reviews/{TARGET_REVIEW_ID}.json'
TARGET_MD_PATH = f'workspace/reviews/{TARGET_REVIEW_ID}.md'
SYNTHESIS_MD_PATH = f'workspace/reviews/{TARGET_REVIEW_ID}_synthesis.md'
OBS_DIR = 'data/observations'
CACHE_DIR = 'data/derived/reviews_cache'

os.makedirs('workspace/reviews', exist_ok=True)
os.makedirs(OBS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Load source review and filter 2026 TEL: Yes papers
with open(SOURCE_REVIEW_PATH, 'r', encoding='utf-8') as f:
    source_data = json.load(f)

source_papers = source_data.get('papers', [])
p2026_tel = [
    p for p in source_papers 
    if str(p.get('year')) == '2026' and 'TEL**: Yes' in str(p.get('tel_intervention', ''))
]

print(f"Total source papers: {len(source_papers)}")
print(f"Filtered 2026 TEL: Yes papers: {len(p2026_tel)}")
assert len(p2026_tel) == 41, f"Expected 41 papers, found {len(p2026_tel)}"

