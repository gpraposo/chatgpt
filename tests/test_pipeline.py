"""Verificações das regras de qualidade e dos indicadores, sem dependências."""

import csv
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from decimal import Decimal
from pathlib import Path

from offshore_demo.pipeline import RAW_COLUMNS, run_pipeline, summarize, validate_rows


def sample_row(**changes):
    record = {
        "asset_id": "FPSO-A", "asset_name": "Unidade Aurora", "month": "2025-01",
        "budget_eur": "1000.00", "actual_eur": "1100.00", "period_hours": "744",
        "planned_downtime_hours": "10", "unplanned_downtime_hours": "20",
    }
    record.update(changes)
    return record


class ValidationTests(unittest.TestCase):
    def test_invalid_rows_are_reported_without_filling_missing_values(self):
        rows = [
            sample_row(actual_eur=""), sample_row(actual_eur="-1"),
            sample_row(month="2025-13"), sample_row(period_hours="720"),
            sample_row(planned_downtime_hours="740", unplanned_downtime_hours="10"),
            sample_row(actual_eur="NaN"), sample_row(actual_eur="100.001"),
        ]
        accepted, issues, duplicates = validate_rows(rows)
        self.assertEqual(accepted, [])
        self.assertEqual(duplicates, 0)
        self.assertEqual({issue["row_number"] for issue in issues}, set(range(2, 9)))
        self.assertTrue({"missing_value", "negative_value", "invalid_month",
                         "calendar_hours_mismatch", "downtime_exceeds_period",
                         "invalid_number", "currency_precision"}.issubset(
                             {issue["code"] for issue in issues}))

    def test_exact_duplicate_is_removed_but_conflicting_group_is_rejected(self):
        accepted, issues, duplicates = validate_rows([sample_row(), sample_row()])
        self.assertEqual(len(accepted), 1)
        self.assertEqual(duplicates, 1)
        self.assertEqual(issues[0]["status"], "removed")
        accepted, issues, duplicates = validate_rows([
            sample_row(), sample_row(actual_eur="1200.00"),
        ])
        self.assertEqual(accepted, [])
        self.assertEqual(duplicates, 0)
        self.assertEqual([issue["code"] for issue in issues], ["conflicting_duplicate"] * 2)

    def test_asset_name_must_match_its_identifier(self):
        accepted, issues, _ = validate_rows([
            sample_row(),
            sample_row(month="2025-02", period_hours="672", asset_name="Outro nome"),
        ])
        self.assertEqual(accepted, [])
        self.assertEqual([issue["code"] for issue in issues], ["inconsistent_asset"] * 2)

    def test_zero_budget_has_no_percentage_and_money_keeps_cents(self):
        accepted, _, _ = validate_rows([sample_row(budget_eur="0.00", actual_eur="0.10")])
        self.assertIsNone(accepted[0].variance_pct)
        self.assertEqual(accepted[0].variance_eur, Decimal("0.10"))
        self.assertEqual(accepted[0].csv_record()["variance_pct"], "")
        self.assertIsNone(summarize(accepted)["variance_pct"])

    def test_availability_uses_total_hours_and_both_types_of_downtime(self):
        accepted, _, _ = validate_rows([
            sample_row(planned_downtime_hours="74.4", unplanned_downtime_hours="0"),
            sample_row(month="2025-02", period_hours="672",
                       planned_downtime_hours="0", unplanned_downtime_hours="336"),
        ])
        result = summarize(accepted)
        expected = 100 * (744 + 672 - 74.4 - 336) / (744 + 672)
        self.assertAlmostEqual(result["availability_pct"], expected, places=4)
        self.assertNotAlmostEqual(result["availability_pct"], (90 + 50) / 2, places=2)


class PipelineTests(unittest.TestCase):
    def test_fixed_seed_generates_the_same_data_in_fresh_workspaces(self):
        with tempfile.TemporaryDirectory() as folder_a, tempfile.TemporaryDirectory() as folder_b:
            root_a, root_b = Path(folder_a), Path(folder_b)
            report_a = run_pipeline(root_a)
            report_b = run_pipeline(root_b)
            self.assertEqual(report_a, report_b)
            self.assertEqual((root_a / report_a["raw_file"]).read_bytes(),
                             (root_b / report_b["raw_file"]).read_bytes())

    def test_demo_is_repeatable_and_sql_matches_the_report(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = run_pipeline(root)
            raw = root / first["raw_file"]
            processed = root / first["processed_file"]
            raw_before = raw.read_bytes()
            processed_before = processed.read_bytes()
            second = run_pipeline(root)
            self.assertEqual(first, second)
            self.assertEqual(raw.read_bytes(), raw_before)
            self.assertEqual(processed.read_bytes(), processed_before)
            self.assertEqual(first["source"], "synthetic_demo")
            self.assertEqual(first["input_rows"], 21)
            self.assertEqual(first["accepted_rows"], 18)
            self.assertEqual(first["rejected_rows"], 2)
            self.assertEqual(first["duplicate_rows_removed"], 1)
            self.assertEqual(first["issue_counts"], {
                "duplicate_exact": 1, "missing_value": 1, "negative_value": 1,
            })
            with closing(sqlite3.connect(root / first["database_file"])) as connection:
                budget, actual, availability = connection.execute("""
                    SELECT SUM(f.budget_cents) / 100.0, SUM(f.actual_cents) / 100.0,
                        100.0 * SUM(f.period_hours - f.planned_downtime_hours - f.unplanned_downtime_hours)
                        / SUM(f.period_hours)
                    FROM fact_operations f
                    JOIN dim_asset a ON a.asset_id = f.asset_id
                    JOIN dim_month m ON m.month = f.month
                """).fetchone()
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM dim_asset").fetchone()[0], 3)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM dim_month").fetchone()[0], 6)
            self.assertEqual(budget, first["metrics"]["budget_eur"])
            self.assertEqual(actual, first["metrics"]["actual_eur"])
            self.assertAlmostEqual(availability, first["metrics"]["availability_pct"], places=4)

    def test_existing_user_csv_is_preserved_and_not_labelled_as_demo(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            raw = root / "data/raw/operations.csv"
            raw.parent.mkdir(parents=True)
            with raw.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=RAW_COLUMNS)
                writer.writeheader()
                writer.writerow(sample_row())
            original = raw.read_bytes()
            report = run_pipeline(root)
            self.assertEqual(raw.read_bytes(), original)
            self.assertEqual(report["source"], "local_csv")
            self.assertEqual(report["accepted_rows"], 1)
            self.assertFalse(raw.with_suffix(".source.json").exists())

    def test_missing_header_fails_without_replacing_previous_results(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run_pipeline(root)
            report_file = root / "data/processed/quality_report.json"
            before = report_file.read_bytes()
            (root / "data/raw/operations.csv").write_text("asset_id\nFPSO-A\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "colunas obrigatórias"):
                run_pipeline(root)
            self.assertEqual(report_file.read_bytes(), before)

    def test_empty_valid_dataset_has_null_metrics_and_a_readable_report(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            raw = root / "data/raw/operations.csv"
            raw.parent.mkdir(parents=True)
            raw.write_text(",".join(RAW_COLUMNS) + "\n", encoding="utf-8")
            report = run_pipeline(root)
            self.assertEqual(report["accepted_rows"], 0)
            self.assertIsNone(report["metrics"]["availability_pct"])
            self.assertIsNone(report["metrics"]["variance_pct"])
            stored = json.loads((root / "data/processed/quality_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report, stored)


if __name__ == "__main__":
    unittest.main()
