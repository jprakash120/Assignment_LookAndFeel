from pathlib import Path
import math
import unittest

from downtime_analytics import answer_question, breakdown, filter_data, kpis, load_data


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "downtime_detail.csv"


class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data(DATA_PATH)

    def test_public_dataset_is_clean(self):
        self.assertEqual(len(self.data), 61)
        self.assertEqual(int(self.data.duplicated().sum()), 0)
        self.assertTrue(self.data["Downtime_Minutes"].gt(0).all())
        self.assertTrue(all(value.startswith("Operator ") for value in self.data["Operator"].unique()))

    def test_verified_portfolio_kpis(self):
        stats = kpis(self.data)
        self.assertEqual(stats["total_minutes"], 1388)
        self.assertEqual(stats["events"], 61)
        self.assertEqual(stats["affected_batches"], 35)
        self.assertEqual(stats["top_reason"], "Machine adjustment")
        self.assertEqual(stats["top_reason_minutes"], 332)
        self.assertTrue(math.isclose(stats["operator_error_share"], 776 / 1388))

    def test_shift_b_filter(self):
        shift_b = filter_data(self.data, shifts=["Shift B"])
        self.assertEqual(kpis(shift_b)["total_minutes"], 584)

    def test_breakdown_is_ranked(self):
        reasons = breakdown(self.data, "Description")
        self.assertEqual(reasons.iloc[0]["Description"], "Machine adjustment")
        self.assertTrue(reasons["Downtime_Minutes"].is_monotonic_decreasing)

    def test_question_answering_uses_filtered_rows(self):
        answer = answer_question(self.data, "What is the top downtime reason for CO-600?")
        self.assertIn("Machine failure", answer)
        self.assertIn("116 minutes", answer)

    def test_summary_includes_auditable_totals(self):
        answer = answer_question(self.data, "Summarize Shift B")
        self.assertIn("584 downtime minutes", answer)
        self.assertIn("Machine adjustment", answer)


if __name__ == "__main__":
    unittest.main()
