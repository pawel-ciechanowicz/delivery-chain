#!/usr/bin/env python3
"""Create a deterministic fingerprint for a web release candidate.

Quality reports are excluded so documenting a candidate does not change it.
Dependency caches, build output, secrets files, and VCS metadata are excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys


EXCLUDED_DIR_NAMES = {
    ".git",
    ".vercel",
    "test-results",
    "playwright-report",
    ".next",
    ".nuxt",
    ".output",
    ".pytest_cache",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

EXCLUDED_FILE_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".log", ".pyc", ".pyo", ".tsbuildinfo"}


def is_excluded(relative_path: Path) -> bool:
    parts = relative_path.parts
    if len(parts) >= 2 and parts[0] == "docs" and parts[1] == "quality":
        return True
    if any(part in EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return True
    name = relative_path.name
    env_templates = {".env.example", ".env.sample", ".env.template"}
    if name in EXCLUDED_FILE_NAMES or (
        (name == ".env" or name.startswith(".env.")) and name not in env_templates
    ):
        return True
    return relative_path.suffix.lower() in EXCLUDED_SUFFIXES


def iter_candidate_files(root: Path):
    for current_root, directory_names, file_names in os.walk(root, followlinks=False):
        current = Path(current_root)
        directory_names[:] = sorted(
            name for name in directory_names
            if name not in EXCLUDED_DIR_NAMES
            and not is_excluded((current / name).relative_to(root))
        )
        for name in directory_names:
            path = current / name
            if path.is_symlink():
                raise ValueError(
                    f"Directory symlink is unsupported in candidate: {path.relative_to(root)}"
                )
        for file_name in sorted(file_names):
            path = current / file_name
            relative = path.relative_to(root)
            if not is_excluded(relative):
                yield path, relative


def fingerprint(root: Path) -> tuple[str, int]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")

    digest = hashlib.sha256()
    file_count = 0
    for path, relative in iter_candidate_files(root):
        relative_bytes = relative.as_posix().encode("utf-8")
        digest.update(len(relative_bytes).to_bytes(8, "big"))
        digest.update(relative_bytes)

        if path.is_symlink():
            payload = f"SYMLINK:{os.readlink(path)}".encode("utf-8")
            digest.update(len(payload).to_bytes(8, "big"))
            digest.update(payload)
        elif path.is_file():
            size = path.stat().st_size
            digest.update(size.to_bytes(8, "big"))
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        else:
            continue
        file_count += 1

    return f"snapshot:sha256:{digest.hexdigest()}", file_count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print a deterministic candidate fingerprint."
    )
    parser.add_argument("root", nargs="?", default=".", help="Project root")
    parser.add_argument(
        "--verbose", action="store_true", help="Also print the number of hashed files"
    )
    args = parser.parse_args()

    try:
        candidate, file_count = fingerprint(Path(args.root))
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(candidate)
    if args.verbose:
        print(f"files:{file_count}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
