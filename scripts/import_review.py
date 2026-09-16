#!/usr/bin/env python3
"""
ISLS Literature Review Importer
Imports an external literature review file, .isls-review.json bundle, or .zip archive
into the user's workspace/reviews/, workspace/properties/, and workspace/observations/.

Usage:
    python3 scripts/import_review.py <path_to_file> [--overwrite]
"""

import os
import sys
import json
import yaml
import zipfile
import sqlite3
import argparse
import subprocess
from datetime import datetime

def get_db_papers(db_path: str) -> set:
    if not os.path.exists(db_path):
        return set()
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM papers")
        ids = {r[0] for r in cur.fetchall()}
        conn.close()
        return ids
    except Exception:
        return set()

def import_review(filepath: str, overwrite: bool = False) -> str:
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    workspace_dir = os.path.join(base_dir, 'workspace')
    user_reviews_dir = os.path.join(workspace_dir, 'reviews')
    user_obs_dir = os.path.join(workspace_dir, 'observations')
    user_props_dir = os.path.join(workspace_dir, 'properties')

    for d in [user_reviews_dir, user_obs_dir, user_props_dir]:
        os.makedirs(d, exist_ok=True)

    db_path = os.path.join(base_dir, 'proceedings.db')
    if not os.path.exists(db_path):
        db_path = os.path.join(base_dir, 'data', 'index', 'proceedings.db')
    valid_paper_ids = get_db_papers(db_path)

    review_data = None
    md_content = ""
    properties_map = {}
    observations_list = []

    # Case 1: Zip Archive
    if zipfile.is_zipfile(filepath):
        with zipfile.ZipFile(filepath, 'r') as zf:
            for name in zf.namelist():
                if name.endswith('.json') and not name.startswith('observations/') and name != 'manifest.json':
                    review_data = json.loads(zf.read(name).decode('utf-8'))
                elif name.endswith('.md'):
                    md_content = zf.read(name).decode('utf-8')
                elif name.startswith('properties/') and (name.endswith('.yaml') or name.endswith('.yml')):
                    pkey = os.path.basename(name).replace('.yaml', '').replace('.yml', '')
                    properties_map[pkey] = yaml.safe_load(zf.read(name).decode('utf-8'))
                elif name.startswith('observations/') and name.endswith('.json'):
                    observations_list.append(json.loads(zf.read(name).decode('utf-8')))

    # Case 2: JSON file or .isls-review.json bundle
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        if isinstance(raw_data, dict) and raw_data.get('format') == 'isls-review-bundle':
            review_data = raw_data.get('review', {})
            md_content = raw_data.get('markdown', '')
            properties_map = raw_data.get('properties', {})
            observations_list = raw_data.get('observations', [])
        elif isinstance(raw_data, dict):
            # Standard single review json
            review_data = raw_data
        else:
            print("Error: Unrecognized JSON structure.")
            sys.exit(1)

    if not review_data or not isinstance(review_data, dict):
        print("Error: Could not extract valid review metadata from file.")
        sys.exit(1)

    review_id = review_data.get('id') or os.path.basename(filepath).split('.')[0]
    review_name = review_data.get('name') or review_id

    # Handle collision with existing user review
    dest_json = os.path.join(user_reviews_dir, f"{review_id}.json")
    if os.path.exists(dest_json) and not overwrite:
        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        review_id = f"{review_id}_imported_{suffix}"
        review_data['id'] = review_id
        review_data['name'] = f"{review_name} (Imported)"
        dest_json = os.path.join(user_reviews_dir, f"{review_id}.json")
        print(f"Note: Review with this ID already exists. Renaming imported review to '{review_id}'.")

    # Validate paper IDs against 10-year proceedings corpus
    pids = review_data.get('paper_ids', [])
    if not pids and 'papers' in review_data:
        pids = [p['id'] if isinstance(p, dict) else str(p) for p in review_data['papers']]

    matched_pids = [p for p in pids if p in valid_paper_ids]
    unmatched_pids = [p for p in pids if p not in valid_paper_ids]

    # Write review JSON
    with open(dest_json, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, indent=2)

    # Write review Markdown if available
    if md_content:
        dest_md = os.path.join(user_reviews_dir, f"{review_id}.md")
        with open(dest_md, 'w', encoding='utf-8') as f:
            f.write(md_content)

    # Unpack custom properties into workspace/properties/
    for pkey, pval in properties_map.items():
        prop_file = os.path.join(user_props_dir, f"{pkey.replace('.', '_')}.yaml")
        if not os.path.exists(prop_file) or overwrite:
            with open(prop_file, 'w', encoding='utf-8') as pf:
                yaml.dump(pval, pf, sort_keys=False)

    # Unpack observations into workspace/observations/
    for obs in observations_list:
        if isinstance(obs, dict) and 'paper_id' in obs and 'property_id' in obs:
            obs_fn = f"{obs['paper_id']}_{obs['property_id'].replace('.', '_')}.json"
            obs_file = os.path.join(user_obs_dir, obs_fn)
            if not os.path.exists(obs_file) or overwrite:
                with open(obs_file, 'w', encoding='utf-8') as of:
                    json.dump(obs, of, indent=2)

    # Rebuild review caches
    cache_script = os.path.join(base_dir, 'scripts', 'build_all_reviews_cache.py')
    if os.path.exists(cache_script):
        try:
            subprocess.run([sys.executable, cache_script], check=True, capture_output=True)
        except Exception as e:
            print(f"Warning: Cache rebuild encountered an issue: {e}")

    print("\n" + "="*60)
    print(f"✓ Review Successfully Imported into User Workspace!")
    print(f"  Review ID     : {review_id}")
    print(f"  Review Name   : {review_data.get('name')}")
    print(f"  Total Papers  : {len(pids)} ({len(matched_pids)} verified in 10-Yr corpus)")
    if unmatched_pids:
        print(f"  Unmatched PIDs: {len(unmatched_pids)} (not found in current DB)")
    print(f"  Properties    : {len(properties_map)} unpacked to workspace/properties/")
    print(f"  Observations  : {len(observations_list)} unpacked to workspace/observations/")
    print(f"  Review Path   : {dest_json}")
    print("="*60)
    print(f"\n🚀 Ready to View: http://localhost:8888/?review={review_id}\n")

    return review_id

def main():
    parser = argparse.ArgumentParser(description="Import an external review file or bundle into user workspace.")
    parser.add_argument("file", help="Path to review JSON file, .isls-review.json bundle, or .zip archive")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing review with same ID")
    args = parser.parse_args()
    import_review(args.file, args.overwrite)

if __name__ == "__main__":
    main()
