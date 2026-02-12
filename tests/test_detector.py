from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from concurrency_detector.main import run
from concurrency_detector.reporter import format_report


ROOT = Path(__file__).resolve().parent.parent


class ConcurrencyDetectorTests(unittest.TestCase):
    def test_combined_log_contains_all_expected_findings(self) -> None:
        result = run(str(ROOT / "input.log"))
        report = format_report(result)

        self.assertIn("DATA RACE DETECTED", report)
        self.assertIn("LOST UPDATE", report)
        self.assertIn("NON-SERIALIZABLE EXECUTION", report)
        self.assertIn("DEADLOCK DETECTED", report)

    def test_clean_log_reports_no_issues(self) -> None:
        result = run(str(ROOT / "input_clean.log"))
        report = format_report(result)

        self.assertIn("No data races detected", report)
        self.assertIn("No lost updates detected", report)
        self.assertIn("SERIALIZABLE EXECUTION", report)
        self.assertIn("No deadlocks detected", report)

    def test_cli_exit_code_and_report_header(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "concurrency_detector", str(ROOT / "input.log")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("======== ANALYSIS REPORT ========", proc.stdout)


if __name__ == "__main__":
    unittest.main()
