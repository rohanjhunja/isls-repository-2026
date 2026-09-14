#!/usr/bin/env python3
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from proceedings_ingest.overview_service import OverviewService

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "data", "overview_static"))
os.makedirs(OUT_DIR, exist_ok=True)

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "proceedings.db"))
svc = OverviewService(db_path)

print(f"Pre-baking 10-Yr Overview static data into {OUT_DIR}...")

# 1. Meta
meta = svc.get_meta()
with open(os.path.join(OUT_DIR, "meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f)
print("Saved meta.json")

# 2. Trends & Density for each dimension
dims = ["tpack_tk", "tpack_pk", "tpack_ck", "setting", "subject", "conceptualisation"]
for dim in dims:
    # Trends
    trends = svc.get_trends(dimension=dim, hierarchy_level=2, min_centrality=1, start_year=2016, end_year=2026)
    with open(os.path.join(OUT_DIR, f"trends_{dim}.json"), "w", encoding="utf-8") as f:
        json.dump(trends, f)
    if dim == "tpack_tk":
        with open(os.path.join(OUT_DIR, "trends.json"), "w", encoding="utf-8") as f:
            json.dump(trends, f)

    # Density
    density = svc.get_density_matrix(dimension=dim)
    with open(os.path.join(OUT_DIR, f"density_{dim}.json"), "w", encoding="utf-8") as f:
        json.dump(density, f)
    if dim == "tpack_tk":
        with open(os.path.join(OUT_DIR, "density.json"), "w", encoding="utf-8") as f:
            json.dump(density, f)
    print(f"Saved trends & density for {dim}")

# 3. Network
network = svc.get_author_network(min_weight=2, limit=110)
with open(os.path.join(OUT_DIR, "network.json"), "w", encoding="utf-8") as f:
    json.dump(network, f)
print("Saved network.json")

# 4. Citations
citations = svc.get_citation_flows(limit=60)
with open(os.path.join(OUT_DIR, "citations.json"), "w", encoding="utf-8") as f:
    json.dump(citations, f)
print("Saved citations.json")

# 5. Sample Papers
papers = svc.get_papers(limit=30)
with open(os.path.join(OUT_DIR, "papers.json"), "w", encoding="utf-8") as f:
    json.dump(papers, f)
print("Saved papers.json")

print("\nSuccessfully pre-baked all 10-Yr Overview static JSON files!")
