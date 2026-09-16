import os
import yaml
try:
    from rapidfuzz import fuzz
except ImportError:
    import difflib
    class _FuzzFallback:
        @staticmethod
        def partial_ratio(s1, s2):
            if not s1 or not s2:
                return 0
            s1_str, s2_str = str(s1).lower(), str(s2).lower()
            if s1_str in s2_str or s2_str in s1_str:
                return 100
            return int(difflib.SequenceMatcher(None, s1_str, s2_str).ratio() * 100)
    fuzz = _FuzzFallback()


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
    def __init__(self, properties_dir: str, core_properties_dir: Optional[str] = None):
        self.properties_dir = properties_dir
        self.core_properties_dir = core_properties_dir
        os.makedirs(properties_dir, exist_ok=True)
        if core_properties_dir:
            os.makedirs(core_properties_dir, exist_ok=True)

    def list_properties(self) -> List[PropertyDefinition]:
        props_by_id = {}
        # 1. Load core properties first
        dirs_to_check = []
        if self.core_properties_dir and os.path.exists(self.core_properties_dir):
            dirs_to_check.append(self.core_properties_dir)
        # 2. Load user properties (can override or extend core properties)
        if os.path.exists(self.properties_dir):
            dirs_to_check.append(self.properties_dir)

        for pdir in dirs_to_check:
            for root, _, files in os.walk(pdir):
                for f in files:
                    if f.endswith(".yaml") or f.endswith(".yml"):
                        path = os.path.join(root, f)
                        try:
                            with open(path, "r", encoding="utf-8") as stream:
                                data = yaml.safe_load(stream)
                                if isinstance(data, dict) and "id" in data:
                                    props_by_id[data["id"]] = PropertyDefinition(**data)
                        except Exception:
                            pass
        return list(props_by_id.values())

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
