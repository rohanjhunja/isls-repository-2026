import hashlib
import json
import os
import re
import shutil
from datetime import datetime
import pypdf
from typing import Dict, Any


class RegisterStage:

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.incoming_dir = os.path.join(data_dir, "incoming")
        self.sources_dir = os.path.join(data_dir, "sources")
        self.registry_path = os.path.join(self.sources_dir, "registry.json")
        os.makedirs(self.sources_dir, exist_ok=True)
        os.makedirs(self.incoming_dir, exist_ok=True)

    def register_file(
        self, filepath: str, collection_id: str = "isls-2026", year: int = 2026
    ) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source file not found: {filepath}")

        # Compute SHA-256
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        sha256 = sha256_hash.hexdigest()

        # Count pages
        reader = pypdf.PdfReader(filepath)
        page_count = len(reader.pages)

        filename = os.path.basename(filepath)
        raw_id = os.path.splitext(filename)[0].lower().replace(" ", "-")
        doc_id = re.sub(r"-+", "-", raw_id).strip("-")

        # Copy to sources dir if not already there
        dest_path = os.path.join(self.sources_dir, filename)
        if os.path.abspath(filepath) != os.path.abspath(dest_path):
            shutil.copy2(filepath, dest_path)

        registry = self._load_registry()

        record = {
            "id": doc_id,
            "filename": filename,
            "source_path": dest_path,
            "sha256": sha256,
            "file_size": os.path.getsize(filepath),
            "pdf_page_count": page_count,
            "collection_id": collection_id,
            "year": year,
            "registered_at": datetime.utcnow().isoformat() + "Z",
            "status": "registered",
        }

        registry[doc_id] = record
        self._save_registry(registry)
        return record

    def _load_registry(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_registry(self, registry: Dict[str, Any]):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)
