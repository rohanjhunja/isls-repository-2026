#!/usr/bin/env python3
import os
import tarfile
import zipfile
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(ROOT_DIR, "dist")
os.makedirs(DIST_DIR, exist_ok=True)

TAR_PATH = os.path.join(DIST_DIR, "isls-minimal-setup.tar.gz")
ZIP_PATH = os.path.join(DIST_DIR, "isls-minimal-setup.zip")

INCLUDE_ITEMS = [
    ".agents",
    "src",
    "web",
    "scripts",
    "profiles",
    "server.py",
    "pyproject.toml",
    "CLAUDE.md",
    "AGENTS.md",
    ".gitignore",
    os.path.join("data", "derived", "ground_truth_registry.json"),
    os.path.join("data", "reviews"),
    os.path.join("data", "observations")
]

EXCLUDE_PATTERNS = [
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    "proceedings.db",
    "blocks_manifest.jsonl",
    "legacy_backup",
    "reviews_cache"
]

def should_exclude(path):
    for pat in EXCLUDE_PATTERNS:
        if pat in path:
            return True
    return False

def tar_filter(tarinfo):
    if should_exclude(tarinfo.name):
        return None
    return tarinfo

print("Building minimal distribution package...")

# 1. Create tar.gz
with tarfile.open(TAR_PATH, "w:gz") as tar:
    for item in INCLUDE_ITEMS:
        full_path = os.path.join(ROOT_DIR, item)
        if os.path.exists(full_path):
            tar.add(full_path, arcname=item, filter=tar_filter)

tar_size_mb = os.path.getsize(TAR_PATH) / (1024 * 1024)

# 2. Create zip
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for item in INCLUDE_ITEMS:
        full_path = os.path.join(ROOT_DIR, item)
        if os.path.exists(full_path):
            if os.path.isdir(full_path):
                for root, dirs, files in os.walk(full_path):
                    # Filter out excluded directories in-place
                    dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                    for f in files:
                        file_full = os.path.join(root, f)
                        if not should_exclude(file_full):
                            rel_path = os.path.relpath(file_full, ROOT_DIR)
                            zf.write(file_full, arcname=rel_path)
            else:
                if not should_exclude(full_path):
                    zf.write(full_path, arcname=item)

zip_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)

print("\nPackaging Complete:")
print(f"  Tarball: {TAR_PATH} ({tar_size_mb:.2f} MB)")
print(f"  Zipfile: {ZIP_PATH} ({zip_size_mb:.2f} MB)")

if tar_size_mb < 12.0 and zip_size_mb < 15.0:
    print("SUCCESS: Package size is well within budget (~9.5 MB compressed)!")
else:
    print("WARNING: Package exceeded target size budget.")
