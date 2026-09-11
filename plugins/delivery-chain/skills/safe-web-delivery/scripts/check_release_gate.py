#!/usr/bin/env python3
"""Validate Safe Web Delivery reports and candidate consistency."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys

from fingerprint_candidate import fingerprint


@dataclass(frozen=True)
class ReportSpec:
    filename: str
    artifact: str
    headings: tuple[str, ...]


REPORTS = (
    ReportSpec(
        "00-project-brief.md",
        "quality/project-brief",
        (
            "W skrócie",
            "Cel i odbiorca",
            "Zakres",
            "Kryteria odbioru",
            "Ryzyka",
            "Decyzje człowieka",
        ),
    ),
    ReportSpec(
        "01-delivery-plan.md",
        "quality/delivery-plan",
        (
            "W skrócie",
            "Plan małych etapów",
            "Macierz testów",
            "Plan bezpieczeństwa",
            "Definition of Done",
        ),
    ),
    ReportSpec(
        "02-build-log.md",
        "quality/build-log",
        ("W skrócie", "Zmiany", "Testy podczas budowy", "Znane ograniczenia"),
    ),
    ReportSpec(
        "03-verification-report.md",
        "quality/verification",
        (
            "W skrócie",
            "Dowody techniczne",
            "Scenariusze akceptacyjne",
            "Evale",
            "Czego ten raport nie dowodzi",
        ),
    ),
    ReportSpec(
        "04-security-review.md",
        "quality/security-review",
        ("W skrócie", "Threat model", "Findings", "Dowody", "Ryzyko rezydualne"),
    ),
    ReportSpec(
        "05-code-review.md",
        "quality/code-review",
        ("W skrócie", "Findings", "Dowody", "Utrzymywalność", "Ograniczenia recenzji"),
    ),
    ReportSpec(
        "06-release-readiness.md",
        "quality/release-readiness",
        (
            "W skrócie",
            "Podsumowanie bramek",
            "Blockery",
            "Ryzyko rezydualne",
            "Scenariusz testu człowieka",
        ),
    ),
    ReportSpec(
        "07-human-approval.md",
        "quality/human-approval",
        ("W skrócie", "Kandydat", "Kontrole ręczne", "Decyzja"),
    ),
)

CANDIDATE_PATTERN = re.compile(
    r"^(?:git:[0-9a-fA-F]{7,40}|snapshot:sha256:[0-9a-fA-F]{64})$"
)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLACEHOLDER_PATTERN = re.compile(r"(?:\{\{|TODO|TBD|WYPEŁNIJ|\.\.\.)", re.IGNORECASE)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as error:
        raise ValueError("missing closing frontmatter delimiter") from error

    metadata: dict[str, str] = {}
    for raw_line in lines[1:end]:
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            raise ValueError(f"invalid frontmatter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"\'')
    return metadata, "\n".join(lines[end + 1 :])


def validate_report(path: Path, spec: ReportSpec, expected_status: str) -> tuple[list[str], dict[str, str]]:
    errors: list[str] = []
    if not path.is_file():
        return [f"{spec.filename}: missing file"], {}

    text = path.read_text(encoding="utf-8")
    try:
        metadata, body = parse_frontmatter(text)
    except ValueError as error:
        return [f"{spec.filename}: {error}"], {}

    required = ("artifact", "schema_version", "status", "candidate", "updated")
    for key in required:
        value = metadata.get(key, "")
        if not value:
            errors.append(f"{spec.filename}: missing frontmatter value `{key}`")
        elif PLACEHOLDER_PATTERN.search(value):
            errors.append(f"{spec.filename}: placeholder in `{key}`")

    if metadata.get("artifact") != spec.artifact:
        errors.append(
            f"{spec.filename}: artifact must be `{spec.artifact}`, got `{metadata.get('artifact', '')}`"
        )
    if metadata.get("schema_version") != "1":
        errors.append(f"{spec.filename}: schema_version must be `1`")
    if metadata.get("status") != expected_status:
        errors.append(
            f"{spec.filename}: status must be `{expected_status}`, got `{metadata.get('status', '')}`"
        )
    if metadata.get("updated") and not DATE_PATTERN.fullmatch(metadata["updated"]):
        errors.append(f"{spec.filename}: updated must use YYYY-MM-DD")

    if spec.filename == "05-code-review.md":
        reviewer_mode = metadata.get("reviewer_mode", "")
        if reviewer_mode not in {"independent-agent", "fresh-task"}:
            errors.append(
                f"{spec.filename}: reviewer_mode must be `independent-agent` or "
                f"`fresh-task`, got `{reviewer_mode}`"
            )

    for heading in spec.headings:
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", body, flags=re.MULTILINE):
            errors.append(f"{spec.filename}: missing section `## {heading}`")

    return errors, metadata


def validate_git_candidate(root: Path, candidate: str) -> list[str]:
    errors: list[str] = []
    requested_sha = candidate.removeprefix("git:").lower()
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip().lower()
        status_lines = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError) as error:
        return [f"cannot validate Git candidate: {error}"]

    if not head.startswith(requested_sha):
        errors.append(f"Git HEAD `{head}` does not match candidate `{requested_sha}`")

    changed_product_files = []
    for line in status_lines:
        changed_path = line[3:].split(" -> ")[-1]
        if not changed_path.startswith("docs/quality/"):
            changed_product_files.append(changed_path)
    if changed_product_files:
        preview = ", ".join(changed_product_files[:5])
        suffix = "" if len(changed_product_files) <= 5 else ", ..."
        errors.append(f"candidate has uncommitted product changes: {preview}{suffix}")
    return errors


def validate_current_candidate(root: Path, candidate: str) -> list[str]:
    if candidate.startswith("snapshot:sha256:"):
        actual, _ = fingerprint(root)
        if actual != candidate:
            return [f"current snapshot `{actual}` does not match reports `{candidate}`"]
        return []
    if candidate.startswith("git:"):
        return validate_git_candidate(root, candidate)
    return [f"invalid candidate format `{candidate}`"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Safe Web Delivery quality gates.")
    parser.add_argument("root", nargs="?", default=".", help="Project root")
    parser.add_argument("--phase", choices=("machine", "final"), default="machine")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    quality_dir = root / "docs" / "quality"
    required_reports = REPORTS[:6] if args.phase == "machine" else REPORTS
    errors: list[str] = []
    metadata_by_file: dict[str, dict[str, str]] = {}

    for index, spec in enumerate(required_reports):
        expected_status = "PASS"
        if args.phase == "final" and index == 7:
            expected_status = "APPROVED"
        report_errors, metadata = validate_report(
            quality_dir / spec.filename, spec, expected_status
        )
        errors.extend(report_errors)
        metadata_by_file[spec.filename] = metadata

    candidate_files = [spec.filename for spec in required_reports if spec.filename[:2] >= "02"]
    candidates = {
        metadata_by_file.get(filename, {}).get("candidate", "")
        for filename in candidate_files
    }
    candidates.discard("")
    if len(candidates) != 1:
        errors.append(
            "candidate-bound reports must contain exactly one shared candidate; "
            f"found {sorted(candidates)}"
        )
        candidate = ""
    else:
        candidate = next(iter(candidates))
        if not CANDIDATE_PATTERN.fullmatch(candidate):
            errors.append(f"invalid shared candidate format `{candidate}`")
        else:
            errors.extend(validate_current_candidate(root, candidate))

    if args.phase == "final":
        approval = metadata_by_file.get("07-human-approval.md", {})
        for key in ("approved_by", "approved_at"):
            value = approval.get(key, "")
            if not value or PLACEHOLDER_PATTERN.search(value):
                errors.append(f"07-human-approval.md: `{key}` is required for final gate")

    if errors:
        print(f"FAIL {args.phase} gate", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"PASS {args.phase} gate candidate={candidate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
