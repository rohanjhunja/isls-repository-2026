import os
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from proceedings_ingest.review_models import (
    LiteratureReview, PaperScope, SearchDefinition, PropertyDefinition, Observation
)
from proceedings_ingest.property_registry import PropertyRegistry
from proceedings_ingest.extraction_engine import ExtractionEngine
from proceedings_ingest.models import Paper
from proceedings_ingest.utils.memory import check_memory, force_garbage_collection


STANDARD_PROPERTIES = {
    "paper_id", "title", "authors", "year", "conference", "abstract", 
    "summary", "keywords", "databases_searched"
}


class ReviewService:
    def __init__(self, data_dir: str, max_memory_gb: float = 8.0, workspace_dir: Optional[str] = None):
        self.data_dir = data_dir
        self.max_memory_gb = max_memory_gb

        base_dir = os.path.dirname(os.path.abspath(data_dir))
        self.workspace_dir = workspace_dir or os.path.join(base_dir, "workspace")
        self.user_reviews_dir = os.path.join(self.workspace_dir, "reviews")
        self.sample_reviews_dir = os.path.join(data_dir, "sample_reviews")
        self.reviews_dir = self.user_reviews_dir  # default write directory

        self.cache_dir = os.path.join(data_dir, "derived", "reviews_cache")
        self.papers_dir = os.path.join(data_dir, "papers")
        self.obs_dir = os.path.join(self.workspace_dir, "observations")
        self.core_obs_dir = os.path.join(data_dir, "observations")
        self.properties_dir = os.path.join(self.workspace_dir, "properties")
        self.core_properties_dir = os.path.join(data_dir, "properties")
        self.exports_dir = os.path.join(self.workspace_dir, "exports")

        for d in [self.user_reviews_dir, self.sample_reviews_dir, self.cache_dir, 
                  self.papers_dir, self.obs_dir, self.properties_dir, self.exports_dir]:
            os.makedirs(d, exist_ok=True)

        self.property_registry = PropertyRegistry(self.properties_dir, self.core_properties_dir)

    def delete_review(self, review_id: str) -> bool:
        """Delete a user literature review and its cached views. Curated samples cannot be deleted."""
        sample_path = os.path.join(self.sample_reviews_dir, f"{review_id}.json")
        user_path = os.path.join(self.user_reviews_dir, f"{review_id}.json")

        if os.path.exists(sample_path) and not os.path.exists(user_path):
            raise ValueError(f"Review '{review_id}' is a curated sample template and cannot be deleted.")

        deleted = False
        for folder in [self.user_reviews_dir, self.cache_dir]:
            for ext in [".json", ".md"]:
                fpath = os.path.join(folder, f"{review_id}{ext}")
                if os.path.exists(fpath):
                    try:
                        os.remove(fpath)
                        deleted = True
                    except Exception:
                        pass
        return deleted

    def delete_paper_from_review(self, review_id: str, paper_id: str) -> bool:
        """Delete a paper (row) from a stored review."""
        review_paths = [
            os.path.join(self.reviews_dir, f"{review_id}.json"),
            os.path.join(self.cache_dir, f"{review_id}.json")
        ]
        modified = False

        for path in review_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    changed = False
                    if "paper_ids" in data and isinstance(data["paper_ids"], list):
                        if paper_id in data["paper_ids"]:
                            data["paper_ids"] = [p for p in data["paper_ids"] if p != paper_id]
                            changed = True

                    if "papers" in data and isinstance(data["papers"], list):
                        orig_len = len(data["papers"])
                        data["papers"] = [p for p in data["papers"] if (p.get("id") if isinstance(p, dict) else p) != paper_id]
                        if len(data["papers"]) < orig_len:
                            changed = True

                    if changed:
                        if "paper_count" in data:
                            data["paper_count"] = len(data.get("paper_ids", [])) or len(data.get("papers", []))
                        data["updated_at"] = datetime.datetime.now().isoformat()
                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                        modified = True
                except Exception:
                    pass

        if modified:
            try:
                self.export_review_markdown(review_id)
            except Exception:
                pass

        return modified

    def delete_column_from_review(self, review_id: str, column_key: str) -> bool:
        """Delete a property (column) from a review. Protects standard properties."""
        if column_key in STANDARD_PROPERTIES:
            raise ValueError(f"Standard property '{column_key}' cannot be deleted.")

        review_paths = [
            os.path.join(self.reviews_dir, f"{review_id}.json"),
            os.path.join(self.cache_dir, f"{review_id}.json")
        ]
        modified = False

        for path in review_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    changed = False
                    for list_key in ["selected_columns", "visible_columns"]:
                        if list_key in data and isinstance(data[list_key], list):
                            if column_key in data[list_key]:
                                data[list_key] = [c for c in data[list_key] if c != column_key]
                                changed = True

                    if "column_definitions" in data and isinstance(data["column_definitions"], dict):
                        if column_key in data["column_definitions"]:
                            del data["column_definitions"][column_key]
                            changed = True

                    if "property_versions" in data and isinstance(data["property_versions"], dict):
                        if column_key in data["property_versions"]:
                            del data["property_versions"][column_key]
                            changed = True

                    if changed:
                        data["updated_at"] = datetime.datetime.now().isoformat()
                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                        modified = True
                except Exception:
                    pass

        if modified:
            try:
                self.export_review_markdown(review_id)
            except Exception:
                pass

        return modified


    def create_review(
        self, name: str, description: Optional[str] = None, scope: Optional[PaperScope] = None
    ) -> LiteratureReview:
        review_id = f"rev_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()
        scope = scope or PaperScope()

        resolved_paper_ids = self._resolve_paper_scope(scope)

        review = LiteratureReview(
            id=review_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
            scope=scope,
            paper_ids=resolved_paper_ids,
            selected_columns=["paper_id", "title", "authors", "year", "abstract"],
            visible_columns=["paper_id", "title", "authors", "year", "abstract"]
        )
        self.save_review(review)
        return review

    def get_review(self, review_id: str) -> Optional[LiteratureReview]:
        # Check user workspace first
        path = os.path.join(self.user_reviews_dir, f"{review_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return LiteratureReview(**json.load(f))

        # Check core sample templates
        sample_path = os.path.join(self.sample_reviews_dir, f"{review_id}.json")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                return LiteratureReview(**json.load(f))

        return None

    def list_reviews(self) -> List[LiteratureReview]:
        reviews_map = {}
        # 1. Load curated samples first
        if os.path.exists(self.sample_reviews_dir):
            for f in os.listdir(self.sample_reviews_dir):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(self.sample_reviews_dir, f), "r", encoding="utf-8") as fs:
                            rev = LiteratureReview(**json.load(fs))
                            reviews_map[rev.id] = rev
                    except Exception:
                        pass

        # 2. Load user reviews (overrides sample if duplicate ID)
        if os.path.exists(self.user_reviews_dir):
            for f in os.listdir(self.user_reviews_dir):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(self.user_reviews_dir, f), "r", encoding="utf-8") as fs:
                            rev = LiteratureReview(**json.load(fs))
                            reviews_map[rev.id] = rev
                    except Exception:
                        pass

        return list(reviews_map.values())

    def save_review(self, review: LiteratureReview) -> str:
        review.updated_at = datetime.datetime.now().isoformat()
        path = os.path.join(self.user_reviews_dir, f"{review.id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(review.dict(), f, indent=2)
        
        # Auto-sync human readable markdown view file
        try:
            self.export_review_markdown(review.id)
        except Exception:
            pass
            
        return path

    def add_papers_to_review(self, review_id: str, paper_ids: List[str]) -> LiteratureReview:
        review = self.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")

        for pid in paper_ids:
            if pid not in review.paper_ids:
                review.paper_ids.append(pid)

        self.save_review(review)
        return review

    def is_dipstick_review(self, review_id: str) -> bool:
        """Check if a review is a Dipstick review before taking downstream actions."""
        review = self.get_review(review_id)
        if not review:
            return False
        return getattr(review, 'review_type', '') == 'dipstick' or review_id.startswith('dipstick_') or review_id.startswith('rev_dipstick_')

    def extract_property_for_review(
        self, review_id: str, property_id: str, paper_ids: Optional[List[str]] = None
    ) -> List[Observation]:
        check_memory(self.max_memory_gb)
        review = self.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")

        # Dipstick Pre-Check
        is_dipstick = self.is_dipstick_review(review_id)

        prop = self.property_registry.get_property(property_id)
        if not prop:
            raise ValueError(f"Property {property_id} not found in registry")

        if property_id not in review.selected_columns:
            review.selected_columns.append(property_id)
        if property_id not in review.visible_columns:
            review.visible_columns.append(property_id)
        review.property_versions[property_id] = prop.version

        target_papers = paper_ids or review.paper_ids
        engine = ExtractionEngine()
        observations = []

        for idx, pid in enumerate(target_papers):
            if idx % 10 == 0:
                check_memory(self.max_memory_gb)

            paper = self._load_paper(pid)
            if not paper:
                continue

            existing_obs = self._load_observation(pid, property_id)
            obs = engine.extract_property(paper, prop, existing_obs)
            self._save_observation(obs)
            observations.append(obs)

            # Eagerly release paper reference
            del paper
            del existing_obs

            if idx % 20 == 0:
                force_garbage_collection()

        force_garbage_collection()
        self.save_review(review)
        return observations

    def build_review_table(self, review_id: str) -> List[Dict[str, Any]]:
        check_memory(self.max_memory_gb)
        review = self.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")

        rows = []
        for idx, pid in enumerate(review.paper_ids):
            if idx % 20 == 0:
                check_memory(self.max_memory_gb)

            paper = self._load_paper(pid)
            if not paper:
                continue

            row = {}
            for col in review.selected_columns:
                # Basic paper fields
                if col == "paper_id":
                    row[col] = paper.id
                elif col == "title":
                    row[col] = paper.title
                elif col == "authors":
                    row[col] = ", ".join([a.display_name for a in paper.authors])
                elif col == "conference":
                    if paper.conference:
                        row[col] = f"{paper.conference.acronym} {paper.conference.year}"
                    else:
                        row[col] = None
                elif col == "year":
                    row[col] = paper.year
                elif col == "abstract":
                    row[col] = paper.abstract
                elif col == "keywords":
                    row[col] = ", ".join(paper.keywords)
                elif col == "filename":
                    row[col] = paper.filename
                else:
                    # Extracted observation
                    obs = self._load_observation(pid, col)
                    if obs:
                        row[col] = {
                            "value": obs.value,
                            "status": obs.status.value if hasattr(obs.status, "value") else str(obs.status),
                            "method": obs.method,
                            "evidence": [e.dict() for e in obs.evidence]
                        }
                    else:
                        row[col] = {"value": None, "status": "not_present", "method": "none", "evidence": []}

            rows.append(row)
            del paper

        force_garbage_collection()
        return rows

    def export_review_markdown(self, review_id: str) -> str:
        """Generate human-readable Markdown summary file for a review."""
        review = self.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")

        table_data = self.build_review_table(review_id)
        
        md = []
        md.append(f"# Literature Review: {review.name}\n")
        md.append(f"- **ID:** `{review.id}`")
        md.append(f"- **Created:** {review.created_at}")
        md.append(f"- **Updated:** {review.updated_at}")
        if review.description:
            md.append(f"- **Description:** {review.description}")
        md.append("")

        md.append("## Scope & Criteria")
        if review.scope.conferences:
            md.append(f"- **Conferences:** {', '.join(review.scope.conferences)}")
        if review.scope.journals:
            md.append(f"- **Journals:** {', '.join(review.scope.journals)}")
        if review.scope.years:
            md.append(f"- **Years:** {', '.join(map(str, review.scope.years))}")
        if review.scope.keywords:
            md.append(f"- **Keywords:** {', '.join(review.scope.keywords)}")
        md.append(f"- **Search Fields:** {', '.join(review.scope.search_fields)}")
        md.append(f"- **AI Search Enabled:** {review.scope.ai_search_enabled}")
        md.append("")

        md.append(f"## Papers ({len(review.paper_ids)})")
        if table_data:
            headers = review.selected_columns
            md.append("| " + " | ".join(headers) + " |")
            md.append("| " + " | ".join(["---"] * len(headers)) + " |")

            for row in table_data:
                line = []
                for col in headers:
                    val = row.get(col)
                    if isinstance(val, dict):
                        cell = str(val.get("value") or "")
                    else:
                        cell = str(val or "")
                    # Sanitize table pipe characters
                    line.append(cell.replace("|", "\\|").replace("\n", " "))
                md.append("| " + " | ".join(line) + " |")
        else:
            md.append("*No papers match current scope.*")

        md_content = "\n".join(md)
        
        # Save as review_id.md in reviews directory for direct viewing/editing
        md_file_path = os.path.join(self.reviews_dir, f"{review.id}.md")
        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return md_content

    def _resolve_paper_scope(self, scope: PaperScope) -> List[str]:
        pids = set(scope.explicit_paper_ids)
        search_fields = scope.search_fields or ["title", "abstract"]
        check_full_paper = "sections" in search_fields or "full_text" in search_fields

        if os.path.exists(self.papers_dir):
            for f in os.listdir(self.papers_dir):
                if f.endswith(".json"):
                    pid = f[:-5]
                    paper = self._load_paper(pid)
                    if not paper:
                        continue

                    # 1. Year filter
                    if scope.years and paper.year not in scope.years:
                        del paper
                        continue

                    # 2. Conference / Journal / Collection filter
                    if scope.conferences or scope.journals or scope.collections:
                        conf_name = paper.conference.acronym if paper.conference else ""
                        conf_full = paper.conference.name if paper.conference else ""
                        journal_name = paper.journal or ""
                        
                        conf_match = any(c.lower() in conf_name.lower() or c.lower() in conf_full.lower() for c in scope.conferences) if scope.conferences else False
                        journal_match = any(j.lower() in journal_name.lower() for j in scope.journals) if scope.journals else False
                        
                        if (scope.conferences or scope.journals) and not (conf_match or journal_match):
                            del paper
                            continue

                    # 3. Keyword search across scoped fields (unless AI search is specified)
                    if scope.keywords and not scope.ai_search_enabled:
                        target_text = ""
                        if "title" in search_fields:
                            target_text += (paper.title or "") + " "
                        if "abstract" in search_fields:
                            target_text += (paper.abstract or "") + " "
                        if check_full_paper:
                            for sec in paper.sections:
                                target_text += (sec.text or "") + " "

                        target_text_lower = target_text.lower()
                        kw_match = any(kw.lower() in target_text_lower for kw in scope.keywords)
                        if not kw_match:
                            del paper
                            continue

                    pids.add(pid)
                    del paper

        return list(pids)

    def _load_paper(self, paper_id: str) -> Optional[Paper]:
        path = os.path.join(self.papers_dir, f"{paper_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return Paper(**json.load(f))

        db_path = os.path.join(self.data_dir, "index", "proceedings.db")
        if os.path.exists(db_path):
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT data_json FROM papers WHERE id = ?", (paper_id,))
                row = cursor.fetchone()
                conn.close()
                if row and row[0]:
                    return Paper(**json.loads(row[0]))
            except Exception:
                pass

        return None

    def _load_observation(self, paper_id: str, property_id: str) -> Optional[Observation]:
        obs_key = f"{paper_id}_{property_id.replace('.', '_')}.json"
        # 1. Check user workspace observations
        user_path = os.path.join(self.obs_dir, obs_key)
        if os.path.exists(user_path):
            with open(user_path, "r", encoding="utf-8") as f:
                return Observation(**json.load(f))

        # 2. Check core observations
        core_path = os.path.join(self.core_obs_dir, obs_key)
        if os.path.exists(core_path):
            with open(core_path, "r", encoding="utf-8") as f:
                return Observation(**json.load(f))

        return None

    def _save_observation(self, obs: Observation):
        obs_key = f"{obs.paper_id}_{obs.property_id.replace('.', '_')}.json"
        path = os.path.join(self.obs_dir, obs_key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obs.dict(), f, indent=2)

