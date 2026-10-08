"""Verifica os indicadores e o comportamento real dos filtros do painel."""

import unittest
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from offshore_demo.analytics import summarize
from offshore_demo.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parents[1]


class AnalyticsTests(unittest.TestCase):
    def test_availability_uses_hours_instead_of_average_percentages(self):
        # Períodos de durações diferentes: disponibilidade global é 90%.
        data = pd.DataFrame({"budget_eur": [100, 100], "actual_eur": [80, 120], "period_hours": [100, 900], "planned_downtime_hours": [50, 20], "unplanned_downtime_hours": [0, 30]})
        result = summarize(data)
        self.assertEqual(result["availability_pct"], 90)
        self.assertEqual(result["variance_eur"], 0)

    def test_zero_budget_has_no_percentage(self):
        data = pd.DataFrame({"budget_eur": [0], "actual_eur": [10], "period_hours": [100], "planned_downtime_hours": [0], "unplanned_downtime_hours": [0]})
        self.assertIsNone(summarize(data)["variance_pct"])


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_pipeline(ROOT)

    def test_load_filter_and_empty_selection(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.metric), 4)
        full_budget = app.metric[0].value
        asset = app.sidebar.multiselect[0].options[0]
        app.sidebar.multiselect[0].set_value([asset]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertNotEqual(app.metric[0].value, full_budget)
        app.sidebar.multiselect[1].set_value([]).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.metric), 0)
        self.assertTrue(any("Seleciona" in item.value for item in app.warning))


if __name__ == "__main__":
    unittest.main()
