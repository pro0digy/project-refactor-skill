#!/usr/bin/env python3
"""Read-only cross-platform project inventory. Emits JSON to stdout."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path


IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", ".next",
    ".nuxt", ".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "__pycache__", "dist", "build", "coverage", "target", ".tox",
    ".gradle", "bin", "obj",
}
PROTECTED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".sqlite", ".db"}
PROTECTED_NAMES = {".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}


def is_protected(name: str) -> bool:
    lowered = name.lower()
    return (
        lowered in PROTECTED_NAMES
        or lowered.startswith(".env.")
        or Path(lowered).suffix in PROTECTED_SUFFIXES
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summarize(root: Path, max_files: int, max_hash_bytes: int) -> dict:
    result: dict = {
        "root": str(root),
        "read_only": True,
        "scanned_files": 0,
        "total_bytes": 0,
        "skipped_protected_files": 0,
        "skipped_symlinks": 0,
        "skipped_generated_directories": [],
        "truncated": False,
        "extensions": {},
        "largest_files": [],
        "identical_file_groups": [],
        "warning": "Identical files are candidates for investigation, not proof of unused code.",
    }
    extensions: Counter[str] = Counter()
    biggest: list[tuple[int, str]] = []
    by_size: dict[int, list[Path]] = defaultdict(list)
    skipped_dirs: set[str] = set()

    for dirname, subdirs, filenames in os.walk(root, followlinks=False):
        current = Path(dirname)
        kept = []
        for subdir in subdirs:
            candidate = current / subdir
            if subdir in IGNORED_DIRS:
                skipped_dirs.add(str(candidate.relative_to(root)))
            elif candidate.is_symlink():
                result["skipped_symlinks"] += 1
            else:
                kept.append(subdir)
        subdirs[:] = kept
        for filename in filenames:
            candidate = current / filename
            if candidate.is_symlink():
                result["skipped_symlinks"] += 1
                continue
            if is_protected(filename):
                result["skipped_protected_files"] += 1
                continue
            try:
                length = candidate.stat().st_size
            except OSError:
                continue
            relative = str(candidate.relative_to(root))
            result["scanned_files"] += 1
            result["total_bytes"] += length
            extensions[candidate.suffix.lower() or "[no extension]"] += 1
            biggest.append((length, relative))
            if 0 < length <= max_hash_bytes:
                by_size[length].append(candidate)
            if result["scanned_files"] >= max_files:
                result["truncated"] = True
                subdirs[:] = []
                break
        if result["truncated"]:
            break

    by_hash: dict[tuple[int, str], list[str]] = defaultdict(list)
    for size, candidates in by_size.items():
        if len(candidates) < 2:
            continue
        for candidate in candidates:
            try:
                by_hash[(size, sha256_file(candidate))].append(str(candidate.relative_to(root)))
            except OSError:
                continue
    result["extensions"] = dict(extensions.most_common())
    result["largest_files"] = [
        {"bytes": size, "path": path} for size, path in sorted(biggest, reverse=True)[:20]
    ]
    result["identical_file_groups"] = [
        {"bytes_each": size, "files": sorted(paths)}
        for (size, _), paths in sorted(by_hash.items(), key=lambda item: -item[0][0])
        if len(paths) > 1
    ][:30]
    result["skipped_generated_directories"] = sorted(skipped_dirs)[:40]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Exact project directory to inspect")
    parser.add_argument("--max-files", type=int, default=25000)
    parser.add_argument("--max-hash-mb", type=int, default=2)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir() or root == Path(root.anchor) or root == Path.home():
        parser.error("--root must be an existing, specific project directory")
    if args.max_files < 1 or args.max_hash_mb < 0:
        parser.error("--max-files must be positive; --max-hash-mb must be nonnegative")
    print(json.dumps(summarize(root, args.max_files, args.max_hash_mb * 1024 * 1024),
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
