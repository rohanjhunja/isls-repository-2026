#!/usr/bin/env python3
"""
ISLS Literature Review Exporter
Packages a literature review, its markdown report, associated custom properties,
and extracted observations into a portable .isls-review.json bundle for sharing.

Usage:
    python3 scripts/export_review.py <review_id> [--output <path>] [--format bundle|zip]
"""

import os
import sys
import json
import yaml
import zipfile
import argparse
from datetime import datetime

STANDARD_PROPERTIES = {
    "paper_id", "title", "authors", "year", "conference", "abstract",
    "summary", "keywords", "databases_searched", "filename", "pages"
}

def export_review(review_id: str, output_path: str = None, export_format: str = "bundle") -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    workspace_dir = os.path.join(base_dir, 'workspace')
    user_reviews_dir = os.path.join(workspace_dir, 'reviews')
    sample_reviews_dir = os.path.join(base_dir, 'data', 'sample_reviews')
    exports_dir = os.path.join(workspace_dir, 'exports')
    os.makedirs(exports_dir, exist_ok=True)

    # 1. Locate review definition
    review_json_path = os.path.join(user_reviews_dir, f"{review_id}.json")
    if not os.path.exists(review_json_path):
        review_json_path = os.path.join(sample_reviews_dir, f"{review_id}.json")
    if not os.path.exists(review_json_path):
        if not review_id.endswith('.json'):
            review_json_path = os.path.join(user_reviews_dir, f"{review_id}")
            if not os.path.exists(review_json_path):
                review_json_path = os.path.join(sample_reviews_dir, f"{review_id}")

    if not os.path.exists(review_json_path):
        print(f"Error: Review '{review_id}' not found in workspace/reviews/ or data/sample_reviews/.")
        sys.exit(1)

    with open(review_json_path, 'r', encoding='utf-8') as f:
        review_data = json.load(f)

    actual_id = review_data.get('id', review_id)
    review_name = review_data.get('name', actual_id)
    paper_ids = review_data.get('paper_ids', [])
    if not paper_ids and 'papers' in review_data:
        paper_ids = [p['id'] if isinstance(p, dict) else str(p) for p in review_data['papers']]

    # 2. Locate markdown report if exists
    md_content = ""
    for md_dir in [user_reviews_dir, sample_reviews_dir]:
        md_file = os.path.join(md_dir, f"{actual_id}.md")
        if os.path.exists(md_file):
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            break

    # 3. Collect custom property definitions
    selected_cols = review_data.get('selected_columns', []) + review_data.get('visible_columns', [])
    custom_col_keys = [c for c in set(selected_cols) if c not in STANDARD_PROPERTIES]
    
    properties_map = {}
    prop_dirs = [
        os.path.join(workspace_dir, 'properties'),
        os.path.join(base_dir, 'data', 'properties')
    ]
    for col in custom_col_keys:
        for pdir in prop_dirs:
            p_path = os.path.join(pdir, f"{col.replace('.', '_')}.yaml")
            if not os.path.exists(p_path):
                p_path = os.path.join(pdir, f"{col}.yaml")
            if os.path.exists(p_path):
                try:
                    with open(p_path, 'r', encoding='utf-8') as pf:
                        properties_map[col] = yaml.safe_load(pf)
                    break
                except Exception:
                    pass

    # 4. Collect observations for review's papers
    observations_list = []
    obs_dirs = [
        os.path.join(workspace_dir, 'observations'),
        os.path.join(base_dir, 'data', 'observations')
    ]
    for pid in paper_ids:
        for col in custom_col_keys:
            obs_filename = f"{pid}_{col.replace('.', '_')}.json"
            for odir in obs_dirs:
                obs_path = os.path.join(odir, obs_filename)
                if os.path.exists(obs_path):
                    try:
                        with open(obs_path, 'r', encoding='utf-8') as of:
                            observations_list.append(json.load(of))
                        break
                    except Exception:
                        pass

    # 5. Build export package
    bundle = {
        "format": "isls-review-bundle",
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "review": review_data,
        "markdown": md_content,
        "properties": properties_map,
        "observations": observations_list,
        "meta": {
            "paper_count": len(paper_ids),
            "custom_properties_count": len(properties_map),
            "observations_count": len(observations_list)
        }
    }

    if export_format == "zip":
        out_path = output_path or os.path.join(exports_dir, f"{actual_id}.isls-review.zip")
        with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{actual_id}.json", json.dumps(review_data, indent=2))
            if md_content:
                zf.writestr(f"{actual_id}.md", md_content)
            for pkey, pval in properties_map.items():
                zf.writestr(f"properties/{pkey.replace('.', '_')}.yaml", yaml.dump(pval, sort_keys=False))
            for obs in observations_list:
                obs_fn = f"{obs['paper_id']}_{obs['property_id'].replace('.', '_')}.json"
                zf.writestr(f"observations/{obs_fn}", json.dumps(obs, indent=2))
            zf.writestr("manifest.json", json.dumps(bundle["meta"], indent=2))
    else:
        out_path = output_path or os.path.join(exports_dir, f"{actual_id}.isls-review.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, indent=2)

    print("\n" + "="*60)
    print(f"✓ Review Successfully Exported!")
    print(f"  Review ID   : {actual_id}")
    print(f"  Review Name : {review_name}")
    print(f"  Papers      : {len(paper_ids)}")
    print(f"  Properties  : {len(properties_map)}")
    print(f"  Observations: {len(observations_list)}")
    print(f"  Output File : {out_path}")
    print("="*60)
    print("\nTo share with another researcher:")
    print(f"1. Send them this bundle file: {os.path.basename(out_path)}")
    print(f"2. They can import it by typing into Antigravity or Claude:")
    print(f"   import {os.path.basename(out_path)}")
    print("="*60 + "\n")

    return out_path

def main():
    parser = argparse.ArgumentParser(description="Export an ISLS literature review for sharing.")
    parser.add_argument("review_id", help="Review ID or filename to export")
    parser.add_argument("--output", "-o", help="Custom output filepath")
    parser.add_argument("--format", "-f", choices=["bundle", "zip"], default="bundle",
                        help="Export format: 'bundle' (.isls-review.json) or 'zip' (.isls-review.zip)")
    args = parser.parse_args()
    export_review(args.review_id, args.output, args.format)

if __name__ == "__main__":
    main()
