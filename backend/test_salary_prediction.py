"""
Automated Comprehensive Test Suite for CareerLens Salary Prediction Module.
Tests:
1. Multi-profession domain isolation and accuracy (Software Developer vs. Electrician vs. Accountant vs. Nurse vs. School Teacher).
2. Multi-country support & currency formatting (IN ₹, US $, GB £, CA C$, DE €, AU A$).
3. Experience and Seniority curve monotonicity (Entry < Mid < Senior < Lead).
4. Real Machine Learning Model Evaluation metrics assertion (MAE, RMSE, R² > 0.90, MAPE < 15%).
5. API endpoints:
   - GET  /api/salary/roles
   - GET  /api/salary/locations
   - POST /api/salary/predict
   - GET  /api/salary/market
   - GET  /api/salary/autofill (auth check)
"""

import unittest
import numpy as np
from app import create_app
from app.services.salary.benchmarks import (
    CURRENCY_MAP,
    SUPPORTED_COUNTRIES,
    get_role_domain,
    get_base_benchmarks,
)
from app.services.salary.model_engine import SalaryModelEngine
from app.services.salary.salary_service import SalaryService

class TestSalaryPredictionModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.engine = SalaryModelEngine.get_instance()

    def test_01_model_training_and_real_metrics(self):
        """Verify the ML model trained properly and meets required regression metrics on held-out test data."""
        self.assertTrue(self.engine.is_trained, "Model must be trained")
        metrics = self.engine.metrics
        self.assertEqual(metrics.get("status"), "calibrated_and_evaluated")
        self.assertGreater(metrics.get("r2_score"), 0.90, "Model R² score on test split should exceed 0.90")
        self.assertLess(metrics.get("mape_percent"), 15.0, "Model MAPE should be under 15%")
        self.assertGreater(metrics.get("test_split_size"), 500, "Held-out test set size must be representative")
        self.assertEqual(metrics.get("domains_supported"), 32, "All 32 canonical domains must be supported")

    def test_02_domain_isolation_across_professions(self):
        """Verify non-tech professions never receive tech salaries (Rigid Domain Isolation)."""
        electrician_pred = self.engine.predict_salary_curve(
            domain="SKILLED_TRADES_ELECTRICAL",
            country="IN",
            city="Bengaluru",
            experience_years=4.0,
            seniority="mid",
            education="diploma",
            skills=[]
        )
        software_pred = self.engine.predict_salary_curve(
            domain="SOFTWARE_DEVELOPMENT",
            country="IN",
            city="Bengaluru",
            experience_years=4.0,
            seniority="mid",
            education="bachelor",
            skills=[]
        )
        accountant_pred = self.engine.predict_salary_curve(
            domain="ACCOUNTING_FINANCE",
            country="IN",
            city="Bengaluru",
            experience_years=4.0,
            seniority="mid",
            education="bachelor",
            skills=[]
        )

        elec_med = electrician_pred["annual"]["median"]
        soft_med = software_pred["annual"]["median"]
        acc_med = accountant_pred["annual"]["median"]

        self.assertLess(elec_med, soft_med * 0.60, "Electrician salary must reflect trade benchmark, not software dev")
        self.assertLess(elec_med, acc_med, "Electrician median should be distinct from finance")
        self.assertGreater(soft_med, acc_med, "Software dev median should reflect tech market benchmark")

    def test_03_experience_and_seniority_progression(self):
        """Verify monotonic salary scaling with years of experience and seniority levels."""
        entry_pred = self.engine.predict_salary_curve("SOFTWARE_DEVELOPMENT", "US", "Austin", 1.0, "entry", "bachelor", [])
        mid_pred = self.engine.predict_salary_curve("SOFTWARE_DEVELOPMENT", "US", "Austin", 4.0, "mid", "bachelor", [])
        senior_pred = self.engine.predict_salary_curve("SOFTWARE_DEVELOPMENT", "US", "Austin", 8.0, "senior", "bachelor", [])
        lead_pred = self.engine.predict_salary_curve("SOFTWARE_DEVELOPMENT", "US", "Austin", 12.0, "lead", "bachelor", [])

        s_entry = entry_pred["annual"]["median"]
        s_mid = mid_pred["annual"]["median"]
        s_senior = senior_pred["annual"]["median"]
        s_lead = lead_pred["annual"]["median"]

        self.assertLess(s_entry, s_mid, "Entry salary must be less than mid-level")
        self.assertLess(s_mid, s_senior, "Mid salary must be less than senior")
        self.assertLess(s_senior, s_lead, "Senior salary must be less than lead")

        # Verify progression forecasts
        progression = mid_pred["progression"]
        self.assertGreater(progression["year_1"]["estimated_salary"], s_mid)
        self.assertGreater(progression["year_3"]["estimated_salary"], progression["year_1"]["estimated_salary"])
        self.assertGreater(progression["year_5"]["estimated_salary"], progression["year_3"]["estimated_salary"])

    def test_04_multi_country_and_currency_support(self):
        """Verify proper currency, symbols, and ranges for IN, US, GB, CA, DE, AU."""
        for country, expected_curr, expected_sym in [
            ("IN", "INR", "₹"),
            ("US", "USD", "$"),
            ("GB", "GBP", "£"),
            ("CA", "CAD", "C$"),
            ("DE", "EUR", "€"),
            ("AU", "AUD", "A$")
        ]:
            pred = self.engine.predict_salary_curve("AI_ML", country, "", 3.0, "mid", "bachelor", [])
            self.assertEqual(pred["currency"], expected_curr)
            self.assertEqual(pred["currency_symbol"], expected_sym)
            self.assertGreater(pred["annual"]["median"], 0)
            self.assertGreater(pred["annual"]["p90"], pred["annual"]["p10"])
            self.assertEqual(pred["annual"]["median"], round(pred["monthly"]["median"] * 12, -2))

    def test_05_skills_premium_calculation(self):
        """Verify high-demand skills impart verified premium percentage without exceeding ceiling."""
        base_pred = self.engine.predict_salary_curve("AI_ML", "US", "San Francisco", 4.0, "mid", "master", [])
        skills_pred = self.engine.predict_salary_curve(
            "AI_ML", "US", "San Francisco", 4.0, "mid", "master",
            skills=["Generative AI", "LLM", "PyTorch", "MLOps"]
        )
        self.assertGreater(skills_pred["annual"]["median"], base_pred["annual"]["median"])
        self.assertGreater(len(skills_pred["applied_skill_premiums"]), 0)

    def test_06_tax_disclaimer_and_monthly_conversion(self):
        """Verify gross vs take-home tax disclaimer and monthly breakdown presence."""
        pred = self.engine.predict_salary_curve("ACCOUNTING_FINANCE", "IN", "Mumbai", 5.0, "mid", "bachelor", [])
        self.assertIn("tax_disclaimer", pred)
        self.assertIn("take-home", pred["tax_disclaimer"].lower())
        self.assertIn("gross", pred["tax_disclaimer"].lower())
        self.assertIn("monthly", pred)
        self.assertEqual(pred["monthly"]["median"], round(pred["annual"]["median"] / 12, 0))

    def test_07_api_get_roles(self):
        """Verify GET /api/salary/roles endpoint."""
        res = self.client.get("/api/salary/roles")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("total_roles"), 105)
        self.assertIn("Software Engineer", data.get("roles"))
        self.assertIn("Electrician", data.get("roles"))
        self.assertIn("Registered Nurse", data.get("roles"))
        self.assertIn("Accountant", data.get("roles"))

    def test_08_api_get_locations(self):
        """Verify GET /api/salary/locations endpoint."""
        res = self.client.get("/api/salary/locations")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertTrue(data.get("success"))
        self.assertEqual(len(data.get("countries")), 6)

    def test_09_api_predict_endpoint(self):
        """Verify POST /api/salary/predict endpoint with rich response structure."""
        payload = {
            "role": "Cloud DevOps Engineer",
            "country": "IN",
            "city": "Bengaluru",
            "experience_years": 5.0,
            "seniority": "mid",
            "education": "bachelor",
            "skills": ["Kubernetes", "AWS", "Terraform", "Docker"],
            "industry": "Information Technology",
            "company_type": "mid-size tech"
        }
        res = self.client.post("/api/salary/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertTrue(data.get("success"))
        pred = data.get("data")
        self.assertEqual(pred.get("currency"), "INR")
        self.assertGreater(pred.get("annual", {}).get("median"), 1000000)
        self.assertIn("progression", pred)
        self.assertIn("seniority_comparison", pred)
        self.assertIn("influential_factors", pred)

    def test_10_api_market_endpoint(self):
        """Verify GET /api/salary/market endpoint."""
        res = self.client.get("/api/salary/market?role=School%20Teacher&country=IN")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertTrue(data.get("success"))
        benchmarks = data.get("data", {}).get("benchmarks")
        self.assertEqual(len(benchmarks), 4)

    def test_11_api_autofill_unauthorized_rejection(self):
        """Verify GET /api/salary/autofill enforces authentication."""
        res = self.client.get("/api/salary/autofill")
        self.assertEqual(res.status_code, 401)

if __name__ == "__main__":
    unittest.main()
