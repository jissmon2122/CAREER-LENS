"""
Unit and Integration Tests for Strict Technical Skill Validation in Skill Demand Forecasting.
Verifies that random words, meaningless text, typos, and non-technical terms are strictly
rejected with HTTP 400 and structured suggestions, while valid skills and legitimate aliases succeed.
"""

import unittest
import json
from app import create_app
from app.services.forecasting.skill_registry import SkillRegistry

class TestSkillValidation(unittest.TestCase):
    """Test suite for SkillRegistry validation engine and forecasting API routes."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    # 1. UNIT TESTS: INVALID INPUTS
    def test_invalid_skills_unit(self):
        invalid_cases = [
            "asdfgh",
            "qwertyxyz",
            "hello123",
            "xyzabc",
            "randomword",
            "banana",
            "football123",
            "testtest",
            "12345",
            "",
            "   ",
            "notarealskill99"
        ]
        for term in invalid_cases:
            res = SkillRegistry.validate_skill(term)
            self.assertFalse(
                res["is_valid"],
                f"Expected '{term}' to be rejected as INVALID, but was accepted."
            )
            self.assertEqual(res["error"], "INVALID_SKILL")
            self.assertTrue(len(res["suggestions"]) > 0)
            self.assertIn("Python", res["suggestions"] + ["Java", "JavaScript", "SQL", "React", "AWS"])

    # 2. UNIT TESTS: VALID TECHNICAL SKILLS
    def test_valid_skills_unit(self):
        valid_cases = [
            ("Python", "Python", "Programming"),
            ("Java", "Java", "Programming"),
            ("SQL", "SQL", "Database / Data Analytics"),
            ("React", "React", "Frontend Development"),
            ("AWS", "AWS", "Cloud Computing"),
            ("Docker", "Docker", "DevOps / Cloud"),
            ("TensorFlow", "TensorFlow", "AI & ML"),
            ("Machine Learning", "Machine Learning", "AI & ML")
        ]
        for term, expected_canonical, expected_cat in valid_cases:
            res = SkillRegistry.validate_skill(term)
            self.assertTrue(
                res["is_valid"],
                f"Expected '{term}' to be accepted as VALID, but was rejected: {res}"
            )
            self.assertEqual(res["display_name"], expected_canonical)
            self.assertEqual(res["category"], expected_cat)

    # 3. UNIT TESTS: EDGE CASES & ALIASES
    def test_edge_cases_and_aliases_unit(self):
        edge_cases = [
            ("python", "Python"),
            ("PYTHON", "Python"),
            ("  Python  ", "Python"),
            ("Python with spaces", None),  # Not a real skill unless alias exists
            ("Node.js", "Node.js"),
            ("nodejs", "Node.js"),
            ("node.js", "Node.js"),
            ("C++", "C++"),
            ("c++", "C++"),
            ("cpp", "C++"),
            ("c plus plus", "C++"),
            ("C#", "C#"),
            ("c#", "C#"),
            ("csharp", "C#"),
            (".NET", ".NET"),
            (".net", ".NET"),
            ("dotnet", ".NET"),
            ("k8s", "Kubernetes"),
            ("golang", "Go"),
            ("postgres", "PostgreSQL"),
            ("powerbi", "Power BI")
        ]
        for term, expected_canonical in edge_cases:
            res = SkillRegistry.validate_skill(term)
            if expected_canonical is None:
                self.assertFalse(res["is_valid"], f"Expected '{term}' to be invalid")
            else:
                self.assertTrue(res["is_valid"], f"Expected '{term}' to be valid alias for {expected_canonical}")
                self.assertEqual(res["display_name"], expected_canonical)

    # 4. API INTEGRATION TESTS: INVALID INPUTS RETURN 400
    def test_api_invalid_skills_rejected_with_400(self):
        test_terms = ["asdfgh", "qwertyxyz", "hello123", "banana", "randomword", "xyzabc", "football123", "testtest"]
        for term in test_terms:
            resp = self.client.get(f"/api/forecasting/skill/{term}")
            self.assertEqual(
                resp.status_code, 400,
                f"Expected HTTP 400 for invalid skill '{term}', got {resp.status_code}"
            )
            data = resp.get_json()
            self.assertFalse(data.get("success"))
            self.assertEqual(data.get("error"), "INVALID_SKILL")
            self.assertIn("not a recognized technical skill", data.get("message", ""))
            self.assertTrue(isinstance(data.get("suggestions"), list))
            self.assertTrue(len(data.get("suggestions")) >= 1)

    # 5. API INTEGRATION TESTS: VALID INPUTS RETURN 200
    def test_api_valid_skills_accepted_with_200(self):
        valid_terms = ["Python", "Java", "SQL", "React", "AWS", "Docker", "TensorFlow"]
        for term in valid_terms:
            resp = self.client.get(f"/api/forecasting/skill/{term}")
            self.assertEqual(
                resp.status_code, 200,
                f"Expected HTTP 200 for valid skill '{term}', got {resp.status_code}"
            )
            data = resp.get_json()
            self.assertTrue(data.get("success"))
            forecast = data.get("data", {}).get("forecast", {})
            self.assertEqual(forecast.get("skill"), term)
            self.assertTrue(len(forecast.get("forecast_rates", [])) > 0)

    # 6. API INTEGRATION TESTS: EDGE CASES VIA HTTP
    def test_api_edge_cases_via_http(self):
        edge_tests = [
            ("python", 200, "Python"),
            ("PYTHON", 200, "Python"),
            ("%20%20Python%20%20", 200, "Python"),
            ("Node.js", 200, "Node.js"),
            ("C%2B%2B", 200, "C++"),
            ("C%23", 200, "C#"),
            (".NET", 200, ".NET"),
            ("k8s", 200, "Kubernetes"),
            ("golang", 200, "Go")
        ]
        for query, expected_status, expected_display in edge_tests:
            resp = self.client.get(f"/api/forecasting/skill/{query}")
            self.assertEqual(resp.status_code, expected_status, f"Query '{query}' failed with {resp.status_code}")
            data = resp.get_json()
            self.assertTrue(data.get("success"))
            self.assertEqual(data.get("data", {}).get("forecast", {}).get("skill"), expected_display)

    # 7. API INTEGRATION TESTS: COMPARISON ROUTE VALIDATION
    def test_api_compare_skills_validation(self):
        # All invalid skills -> 400
        resp_invalid = self.client.get("/api/forecasting/compare?skills=asdfgh,qwertyxyz,banana")
        self.assertEqual(resp_invalid.status_code, 400)
        data_invalid = resp_invalid.get_json()
        self.assertFalse(data_invalid.get("success"))
        self.assertEqual(data_invalid.get("error"), "INVALID_SKILL")

        # Valid skills -> 200
        resp_valid = self.client.get("/api/forecasting/compare?skills=Python,SQL,React,AWS")
        self.assertEqual(resp_valid.status_code, 200)
        data_valid = resp_valid.get_json()
        self.assertTrue(data_valid.get("success"))
        self.assertEqual(len(data_valid.get("data", {}).get("skills", [])), 4)

if __name__ == "__main__":
    unittest.main()
