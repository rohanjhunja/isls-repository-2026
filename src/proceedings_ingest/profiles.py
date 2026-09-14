import os
import re
import yaml
from typing import Dict, Any, List, Optional


class ProfileManager:

    def __init__(self, profiles_dir: str):
        self.profiles_dir = profiles_dir
        self.common_profile = self._load_yaml(
            os.path.join(profiles_dir, "common.yaml")
        )

    def _load_yaml(self, filepath: str) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            return {}
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def get_profile_for_filename(self, filename: str) -> Dict[str, Any]:
        conf_dir = os.path.join(self.profiles_dir, "conferences")
        if os.path.exists(conf_dir):
            for fname in os.listdir(conf_dir):
                if fname.endswith(".yaml") or fname.endswith(".yml"):
                    path = os.path.join(conf_dir, fname)
                    data = self._load_yaml(path)
                    applies = data.get("profile", {}).get("applies_to", {})
                    regex = applies.get("filename_regex")
                    if regex and re.search(regex, filename, re.IGNORECASE):
                        # Merge with common profile
                        merged = self._merge_profiles(self.common_profile, data)
                        return merged
        return self.common_profile

    def _merge_profiles(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        merged = base.copy()
        for k, v in override.items():
            if isinstance(v, dict) and k in merged and isinstance(merged[k], dict):
                merged[k] = self._merge_profiles(merged[k], v)
            else:
                merged[k] = v
        return merged

    @staticmethod
    def map_heading_to_canonical_roles(
        heading: str, canonical_map: Dict[str, List[str]]
    ) -> List[str]:
        heading_clean = heading.strip().lower()
        # Remove leading numbers/punctuation like '1. ', '3.2 '
        heading_clean = re.sub(r"^[\d\.\s\-:]+", "", heading_clean).strip()

        matched_roles = []
        for role, aliases in canonical_map.items():
            for alias in aliases:
                if (
                    alias.lower() == heading_clean
                    or alias.lower() in heading_clean.split()
                ):
                    matched_roles.append(role)
                    break
        return matched_roles
