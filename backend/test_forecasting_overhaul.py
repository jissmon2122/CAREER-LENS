import unittest
from app import create_app
from app.db import Database
from app.services.forecasting.skill_taxonomy import SkillTaxonomy
from app.services.forecasting.forecasting_models import (
    BaselineNaiveModel,
    MovingAverageModel,
    LinearTrendModel,
    ExponentialSmoothingModel
)
from app.services.forecasting.evaluation import ModelEvaluator
from app.services.forecasting.trend_analysis import TrendAnalysisEngine
from app.services.forecasting.preprocessing import PreprocessingService

class TestForecastingOverhaul(unittest.TestCase):
    """
    Comprehensive test suite validating the Skill Demand Forecasting overhaul:
    - Mathematical correctness of all 4 forecasting algorithms
    - 36-month horizon and continuous 2023-2026 timeline
    - Accurate taxonomy & categorization without cross-domain pollution
    - Real-world database endpoints (top skills, single skill, comparison, categories)
    - Handling of sufficient vs insufficient historical data
    - Clamping: no negative values, no values > 100%
    """

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    # -------------------------------------------------------------
    # 1. Mathematical Algorithm Verification
    # -------------------------------------------------------------
    def test_naive_model_mathematics(self):
        """Verify Naive Baseline accurately projects last value and bounded intervals."""
        history = [12.0, 14.5, 15.0, 16.5, 18.0]
        model = BaselineNaiveModel().fit(history)
        preds, lower, upper = model.predict_with_intervals(horizon=36)

        self.assertEqual(len(preds), 36)
        self.assertEqual(len(lower), 36)
        self.assertEqual(len(upper), 36)
        for p in preds:
            self.assertEqual(p, 18.0)
            self.assertTrue(0.0 <= p <= 100.0)
        for i in range(36):
            self.assertTrue(lower[i] <= preds[i] <= upper[i])
            self.assertTrue(lower[i] >= 0.0)
            self.assertTrue(upper[i] <= 100.0)

    def test_moving_average_mathematics(self):
        """Verify Moving Average accurately averages recent window and projects bounded values."""
        history = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
        model = MovingAverageModel(window=3).fit(history)
        preds, lower, upper = model.predict_with_intervals(horizon=36)

        expected_ma = round((16.0 + 18.0 + 20.0) / 3.0, 2)  # 18.0
        self.assertEqual(preds[0], expected_ma)
        self.assertEqual(preds[-1], expected_ma)
        self.assertEqual(len(preds), 36)
        for i in range(36):
            self.assertTrue(0.0 <= preds[i] <= 100.0)
            self.assertTrue(lower[i] <= preds[i] <= upper[i])

    def test_linear_regression_dampening_and_bounding(self):
        """Verify Linear Trend dampens over 36 months to prevent runaway exponential explosion."""
        history = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        model = LinearTrendModel(dampening=0.96).fit(history)
        preds, lower, upper = model.predict_with_intervals(horizon=36)

        self.assertEqual(len(preds), 36)
        # Should be strictly increasing but dampened
        self.assertTrue(preds[0] > 10.0)
        self.assertTrue(preds[-1] > preds[0])
        # Verify it doesn't explode
        self.assertTrue(preds[-1] < 50.0)
        for p in preds:
            self.assertTrue(0.0 <= p <= 100.0)

    def test_damped_exponential_smoothing_mathematics(self):
        """Verify Damped Holt's Exponential Smoothing levels off smoothly without runaway."""
        history = [15.0, 16.0, 17.5, 19.0, 21.0, 23.5]
        model = ExponentialSmoothingModel(alpha=0.35, beta=0.15, phi=0.92).fit(history)
        preds, lower, upper = model.predict_with_intervals(horizon=36)

        self.assertEqual(len(preds), 36)
        self.assertTrue(preds[0] > history[0])
        self.assertTrue(preds[-1] > preds[0])
        # Verify values remain bounded in [0, 100]
        for p in preds:
            self.assertTrue(0.0 <= p <= 100.0)
        for i in range(36):
            self.assertTrue(lower[i] <= preds[i] <= upper[i])

    # -------------------------------------------------------------
    # 2. Chronological Model Evaluation & Selection
    # -------------------------------------------------------------
    def test_model_evaluation_selection(self):
        """Verify evaluator compares all 4 algorithms on validation split and picks lowest MAE."""
        series = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0]
        eval_res = ModelEvaluator.evaluate_and_select_best_model(series, horizon=36)

        self.assertIn("best_model_name", eval_res)
        self.assertIn("mae", eval_res)
        self.assertIn("rmse", eval_res)
        self.assertIn("mape", eval_res)
        self.assertIn("model_comparisons", eval_res)

        comparisons = eval_res["model_comparisons"]
        self.assertEqual(len(comparisons), 4)
        names = [c["name"] for c in comparisons]
        self.assertIn("Naive Baseline", names)
        self.assertIn("Moving Average", names)
        self.assertIn("Linear Regression", names)
        self.assertIn("Exponential Smoothing", names)

        # The lowest MAE must match the selected best_model_name
        min_mae = min(c["mae"] for c in comparisons)
        best_c = [c for c in comparisons if c["mae"] == min_mae][0]
        self.assertEqual(eval_res["best_model_name"], best_c["name"])

    # -------------------------------------------------------------
    # 3. Skill Taxonomy & Categorization Rules
    # -------------------------------------------------------------
    def test_skill_taxonomy_categorization(self):
        """Verify skills are mapped to correct primary categories without cross-contamination."""
        self.assertEqual(SkillTaxonomy.get_skill_classification("python")["primary"], "Programming")
        self.assertEqual(SkillTaxonomy.get_skill_classification("java")["primary"], "Programming")
        self.assertEqual(SkillTaxonomy.get_skill_classification("sql")["primary"], "Database / Data Analytics")
        self.assertEqual(SkillTaxonomy.get_skill_classification("react")["primary"], "Frontend Development")
        self.assertEqual(SkillTaxonomy.get_skill_classification("aws")["primary"], "Cloud Computing")
        self.assertEqual(SkillTaxonomy.get_skill_classification("docker")["primary"], "DevOps / Cloud")
        self.assertEqual(SkillTaxonomy.get_skill_classification("machine learning")["primary"], "AI & ML")
        self.assertEqual(SkillTaxonomy.get_skill_classification("cybersecurity")["primary"], "Security")

    # -------------------------------------------------------------
    # 4. Timeline & Date Generation
    # -------------------------------------------------------------
    def test_forecast_timeline_generation(self):
        """Verify sequential monthly generation for 36 months starting strictly after baseline."""
        periods = PreprocessingService.generate_forecast_periods("2026-11", horizon=36)
        self.assertEqual(len(periods), 36)
        self.assertEqual(periods[0], "2026-12")
        self.assertEqual(periods[1], "2027-01")
        self.assertEqual(periods[11], "2027-11")
        self.assertEqual(periods[12], "2027-12")
        self.assertEqual(periods[23], "2028-11")
        self.assertEqual(periods[35], "2029-11")

    # -------------------------------------------------------------
    # 5. Trend Classification
    # -------------------------------------------------------------
    def test_trend_classification_logic(self):
        """Verify mathematical classification into RISING, STABLE, DECLINING, and EMERGING."""
        # Rising
        t_rise = TrendAnalysisEngine.classify_trend([10, 11, 12], 12.0, 16.0)
        self.assertEqual(t_rise["trend"], "RISING")

        # Stable
        t_stable = TrendAnalysisEngine.classify_trend([20, 20.2, 20.1], 20.1, 20.5)
        self.assertEqual(t_stable["trend"], "STABLE")

        # Declining
        t_decl = TrendAnalysisEngine.classify_trend([30, 28, 25], 25.0, 21.0)
        self.assertEqual(t_decl["trend"], "DECLINING")

        # Emerging
        t_emerg = TrendAnalysisEngine.classify_trend([2.0, 2.5, 3.0], 3.0, 5.0)
        self.assertEqual(t_emerg["trend"], "EMERGING")

    # -------------------------------------------------------------
    # 6. Live API Endpoints Verification
    # -------------------------------------------------------------
    def test_api_categories_endpoint(self):
        """Test GET /api/forecasting/categories."""
        res = self.client.get('/api/forecasting/categories')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("categories", json_data["data"])
        self.assertIn("Programming", json_data["data"]["categories"])
        self.assertIn("AI & ML", json_data["data"]["categories"])

    def test_api_top_skills_endpoint(self):
        """Test GET /api/forecasting/top-skills with category filtering."""
        res = self.client.get('/api/forecasting/top-skills?category=Programming&limit=5')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("rising_skills", json_data["data"])
        self.assertIn("stable_skills", json_data["data"])

    def test_api_skill_forecast_endpoint(self):
        """Test GET /api/forecasting/skill/<name>?horizon=36."""
        res = self.client.get('/api/forecasting/skill/python?horizon=36')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        fc = json_data["data"]["forecast"]
        self.assertEqual(fc["skill"].lower(), "python")
        self.assertEqual(fc["category"], "Programming")
        self.assertEqual(len(fc["forecast_periods"]), 36)
        self.assertEqual(len(fc["forecast_rates"]), 36)
        self.assertEqual(len(fc["periods"]), 47)
        self.assertIn("model_comparisons", fc)
        self.assertEqual(len(fc["model_comparisons"]), 4)

    def test_api_skill_insufficient_data_endpoint(self):
        """Test GET /api/forecasting/skill/<name> with unobserved skill."""
        res = self.client.get('/api/forecasting/skill/nonexistent_quantum_skill_xyz?horizon=36')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        fc = json_data["data"]["forecast"]
        self.assertEqual(fc["reliability"], "INSUFFICIENT_HISTORICAL_DATA")
        self.assertFalse(fc["has_sufficient_data"])
        self.assertIn("insufficient", fc["notice"].lower())

    def test_api_compare_endpoint(self):
        """Test GET /api/forecasting/compare?skills=python,sql,react,aws&horizon=36."""
        res = self.client.get('/api/forecasting/compare?skills=python,sql,react,aws&horizon=36')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["data"]["horizon"], "36M")
        self.assertEqual(len(json_data["data"]["forecast_periods"]), 36)
        skills = json_data["data"]["skills"]
        self.assertGreaterEqual(len(skills), 3)

if __name__ == '__main__':
    unittest.main()
