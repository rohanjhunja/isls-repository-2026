import os
import yaml
from typing import List, Dict, Any, Optional
from rapidfuzz import fuzz
from proceedings_ingest.review_models import PropertyDefinition


CANONICAL_BASIC_FIELDS = {
    "paper_id": "Paper ID / unique identifier",
    "title": "Title of the paper",
    "authors": "Authors and affiliations",
    "abstract": "Abstract summary",
    "keywords": "Author keywords",
    "conference": "Conference name/acronym/year",
    "journal": "Journal name",
    "year": "Publication year",
    "filename": "Source PDF filename",
    "pages": "Printed and PDF page ranges",
    "canonical_sections": "Original and canonical section headings",
}


class PropertyRegistry:
    def __init__(self, properties_dir: str):
        self.properties_dir = properties_dir
        os.makedirs(properties_dir, exist_ok=True)

    def list_properties(self) -> List[PropertyDefinition]:
        props = []
        for root, _, files in os.walk(self.properties_dir):
            for f in files:
                if f.endswith(".yaml") or f.endswith(".yml"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8") as stream:
                            data = yaml.safe_load(stream)
                            if isinstance(data, dict) and "id" in data:
                                props.append(PropertyDefinition(**data))
                    except Exception:
                        pass
        return props

    def get_property(self, property_id: str) -> Optional[PropertyDefinition]:
        for prop in self.list_properties():
            if prop.id == property_id:
                return prop
        return None

    def save_property(self, prop: PropertyDefinition) -> str:
        filename = f"{prop.id.replace('.', '_')}.yaml"
        file_path = os.path.join(self.properties_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(prop.dict(), f, sort_keys=False)
        return file_path

    def find_matching_properties(self, query_str: str) -> Dict[str, Any]:
        """Check canonical basic fields and registered property definitions."""
        matches = []
        query_lower = query_str.lower().strip()

        # Check canonical paper fields first
        for field, desc in CANONICAL_BASIC_FIELDS.items():
            score = max(fuzz.partial_ratio(query_lower, field), fuzz.partial_ratio(query_lower, desc.lower()))
            if score > 60:
                matches.append({
                    "kind": "canonical_field",
                    "id": field,
                    "label": field,
                    "description": desc,
                    "score": score,
                    "suggestion": f"Use basic canonical paper field '{field}' directly without extra extraction."
                })

        # Check existing property definitions
        for prop in self.list_properties():
            score_id = fuzz.partial_ratio(query_lower, prop.id.lower())
            score_label = fuzz.partial_ratio(query_lower, prop.label.lower())
            score_desc = fuzz.partial_ratio(query_lower, prop.description.lower()) if prop.description else 0
            score = max(score_id, score_label, score_desc)
            if score > 60:
                matches.append({
                    "kind": "registered_property",
                    "id": prop.id,
                    "label": prop.label,
                    "description": prop.description,
                    "version": prop.version,
                    "score": score,
                    "suggestion": f"Existing property '{prop.id}' matches. Consider reusing or extending it."
                })

        matches.sort(key=lambda x: x["score"], reverse=True)
        return {
            "query": query_str,
            "has_close_match": len(matches) > 0 and matches[0]["score"] >= 80,
            "matches": matches
        }
