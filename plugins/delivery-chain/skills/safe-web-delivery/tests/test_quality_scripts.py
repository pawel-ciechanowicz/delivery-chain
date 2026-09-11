from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_release_gate import REPORTS, parse_frontmatter  # noqa: E402
from fingerprint_candidate import fingerprint  # noqa: E402


CHECK_SCRIPT = SCRIPTS_DIR / "check_release_gate.py"


class QualityScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "app.js").write_text("export const answer = 42;\n")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_reports(self, candidate: str, *, approved: bool = False) -> None:
        quality_dir = self.root / "docs" / "quality"
        quality_dir.mkdir(parents=True, exist_ok=True)
        for index, spec in enumerate(REPORTS):
            report_candidate = "planning" if index < 2 else candidate
            status = "PASS"
            extra = ""
            if index == 7:
                status = "APPROVED" if approved else "PENDING"
                if approved:
                    extra = "approved_by: owner\napproved_at: 2026-09-08T12:00:00+02:00\n"
                else:
                    extra = "approved_by:\napproved_at:\n"
            elif index == 5:
                extra = "reviewer_mode: fresh-task\n"
            headings = "\n\n".join(
                f"## {heading}\n\nEvidence for {heading}." for heading in spec.headings
            )
            content = (
                "---\n"
                f"artifact: {spec.artifact}\n"
                "schema_version: 1\n"
                f"status: {status}\n"
                f"candidate: {report_candidate}\n"
                "updated: 2026-09-08\n"
                f"{extra}"
                "---\n\n"
                f"# {spec.filename}\n\n"
                f"{headings}\n"
            )
            (quality_dir / spec.filename).write_text(content, encoding="utf-8")

    def run_gate(self, phase: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECK_SCRIPT), str(self.root), "--phase", phase],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_fingerprint_ignores_quality_reports_but_tracks_product_changes(self) -> None:
        before, _ = fingerprint(self.root)
        quality_dir = self.root / "docs" / "quality"
        quality_dir.mkdir(parents=True)
        (quality_dir / "note.md").write_text("report v1\n")
        after_report, _ = fingerprint(self.root)
        self.assertEqual(before, after_report)

        (self.root / "src" / "app.js").write_text("export const answer = 43;\n")
        after_product_change, _ = fingerprint(self.root)
        self.assertNotEqual(before, after_product_change)

    def test_fingerprint_rejects_directory_symlinks(self) -> None:
        (self.root / "public").symlink_to(self.root / "src", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Directory symlink.*public"):
            fingerprint(self.root)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "fingerprint_candidate.py"), str(self.root)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("Directory symlink", result.stderr)

    def test_fingerprint_ignores_excluded_directory_symlinks(self) -> None:
        before, _ = fingerprint(self.root)
        (self.root / "node_modules").symlink_to(self.root / "src", target_is_directory=True)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "quality").symlink_to(self.root / "src", target_is_directory=True)
        self.assertEqual(before, fingerprint(self.root)[0])

    def test_every_report_has_a_complete_template(self) -> None:
        templates_dir = SKILL_ROOT / "assets" / "templates"
        for spec in REPORTS:
            with self.subTest(template=spec.filename):
                template = templates_dir / spec.filename
                self.assertTrue(template.is_file())
                metadata, body = parse_frontmatter(template.read_text(encoding="utf-8"))
                self.assertEqual(metadata.get("artifact"), spec.artifact)
                self.assertEqual(metadata.get("schema_version"), "1")
                for heading in spec.headings:
                    self.assertIn(f"## {heading}", body)

    def test_machine_gate_passes_complete_consistent_reports(self) -> None:
        candidate, _ = fingerprint(self.root)
        self.write_reports(candidate)
        result = self.run_gate("machine")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS machine gate", result.stdout)

    def test_machine_gate_detects_changed_candidate(self) -> None:
        candidate, _ = fingerprint(self.root)
        self.write_reports(candidate)
        (self.root / "src" / "app.js").write_text("export const answer = 0;\n")
        result = self.run_gate("machine")
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not match reports", result.stderr)

    def test_machine_gate_rejects_author_self_review(self) -> None:
        candidate, _ = fingerprint(self.root)
        self.write_reports(candidate)
        report = self.root / "docs" / "quality" / "05-code-review.md"
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "reviewer_mode: fresh-task", "reviewer_mode: author-self-review"
            ),
            encoding="utf-8",
        )
        result = self.run_gate("machine")
        self.assertEqual(result.returncode, 1)
        self.assertIn("reviewer_mode must be", result.stderr)

    def test_final_gate_requires_explicit_human_approval(self) -> None:
        candidate, _ = fingerprint(self.root)
        self.write_reports(candidate, approved=False)
        pending_result = self.run_gate("final")
        self.assertEqual(pending_result.returncode, 1)
        self.assertIn("status must be `APPROVED`", pending_result.stderr)

        self.write_reports(candidate, approved=True)
        approved_result = self.run_gate("final")
        self.assertEqual(approved_result.returncode, 0, approved_result.stderr)
        self.assertIn("PASS final gate", approved_result.stdout)

    def test_gate_rejects_missing_required_section(self) -> None:
        candidate, _ = fingerprint(self.root)
        self.write_reports(candidate)
        report = self.root / "docs" / "quality" / "03-verification-report.md"
        report.write_text(
            report.read_text(encoding="utf-8").replace(
                "## Czego ten raport nie dowodzi", "## Inna sekcja"
            ),
            encoding="utf-8",
        )
        result = self.run_gate("machine")
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing section", result.stderr)


if __name__ == "__main__":
    unittest.main()
