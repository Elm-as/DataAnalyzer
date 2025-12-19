import unittest
import os
import sys

sys.path.append(os.path.dirname(__file__))
from app import app, active_analyzers


class ModelInspectionTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        active_analyzers.clear()

    def test_classification_summary_and_plots(self):
        payload = {
            "dataset_id": "cls1",
            "data": [
                {"x1": float(i), "x2": float(i % 3), "label": "A" if i % 2 == 0 else "B"}
                for i in range(30)
            ],
            "config": {
                "target": "label",
                "features": ["x1", "x2"],
                "methods": ["knn"],
                "test_size": 0.2,
                "cv_folds": 3
            }
        }

        analyze_resp = self.client.post("/analyze/classification", json=payload)
        self.assertEqual(analyze_resp.status_code, 200)

        summary_resp = self.client.post(
            "/models/summary",
            json={"dataset_id": "cls1", "model_type": "classification"}
        )
        self.assertEqual(summary_resp.status_code, 200)
        summary_body = summary_resp.get_json()
        self.assertEqual(summary_body.get("dataset_id"), "cls1")
        self.assertEqual(summary_body.get("model_type"), "classification")

        plots_resp = self.client.post("/models/plots/classification", json={"dataset_id": "cls1"})
        self.assertEqual(plots_resp.status_code, 200)
        plots_body = plots_resp.get_json()
        self.assertIn("plots", plots_body)
        self.assertIn("confusion_matrix", plots_body["plots"])


if __name__ == "__main__":
    unittest.main()
