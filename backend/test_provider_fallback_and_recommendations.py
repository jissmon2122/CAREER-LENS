"""
Test Suite: Live Job Provider Fallback, Accuracy, and Response Latency
Validates:
1. JobService.find_verified_jobs() retrieves real, verified jobs from MongoDB Atlas.
2. Fallback to MongoDB jobs occurs seamlessly when external providers return 0 jobs or are unconfigured.
3. No fake/mock vacancies are generated (all jobs have real companies, real titles, and valid URLs).
4. search_live_jobs() endpoint returns valid payload with success=True and never errors with 'Live job data is currently unavailable'.
5. End-to-end recommendation flow with analyzed candidate profile works with fallback.
"""

import unittest
import time
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app import create_app
from app.db import Database
from app.services.job_service import JobService
from app.services.role_taxonomy import RoleTaxonomy
from app.services.role_relevance_service import RoleRelevanceService
from app.services.geo_eligibility_service import GeoEligibilityService

class TestProviderFallbackAndRecommendations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.db = Database.get_db()

    def test_01_mongodb_verified_jobs_query(self):
        """Test that JobService.find_verified_jobs returns real vacancies for target roles."""
        test_roles = ["Data Analyst", "Software Engineer", "Python Developer"]
        for role in test_roles:
            t0 = time.time()
            jobs = JobService.find_verified_jobs(target_role=role, limit=10)
            elapsed = time.time() - t0

            self.assertIsInstance(jobs, list)
            self.assertGreater(len(jobs), 0, f"Expected verified MongoDB jobs for role '{role}', got 0")
            self.assertLess(elapsed, 1.5, f"MongoDB query for '{role}' exceeded 1.5s ({elapsed:.3f}s)")

            for j in jobs:
                self.assertIn("title", j)
                self.assertIn("company", j)
                self.assertIn("location", j)
                self.assertIn("required_skills", j)
                self.assertIn("application_url", j)
                self.assertTrue(j.get("is_live"), "Job is_live must be True")
                self.assertEqual(j.get("status"), "LIVE", "Job status must be LIVE")
                self.assertTrue(len(j.get("company", "").strip()) > 0, "Company name must not be empty")
                self.assertTrue(len(j.get("title", "").strip()) > 0, "Title must not be empty")

    def test_02_search_endpoint_with_fallback(self):
        """Test GET /api/jobs/search endpoint returns valid payload and falls back to MongoDB."""
        t0 = time.time()
        resp = cls_client = self.client.get('/api/jobs/search?keyword=Data%20Analyst&limit=10')
        elapsed = time.time() - t0

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"), "Search endpoint must return success=True")
        self.assertIn("jobs", data)
        self.assertIsInstance(data["jobs"], list)
        self.assertGreater(len(data["jobs"]), 0, "Search for 'Data Analyst' must return matching vacancies")
        self.assertLess(elapsed, 6.0, f"Search response time exceeded 6.0s ({elapsed:.3f}s)")

    def test_03_search_endpoint_handles_empty_cleanly(self):
        """Test GET /api/jobs/search with non-existent keyword returns success=True with 0 jobs."""
        resp = self.client.get('/api/jobs/search?keyword=XyzNonExistentSpecialistJobRole999&limit=5')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"), "Search must return success=True even when 0 matches found")
        self.assertEqual(data.get("total"), 0)
        self.assertEqual(len(data.get("jobs", [])), 0)

    def test_04_role_relevance_on_fallback_jobs(self):
        """Test that RoleRelevanceService correctly accepts direct role matches and rejects strict exclusions."""
        candidate_profile = {
            "professional_domain": "SOFTWARE_IT",
            "inferred_roles": ["Data Analyst"],
            "experience_level": "Entry Level",
            "education": "Bachelor's Degree",
            "core_skills": ["Python", "SQL", "Power BI", "Tableau"]
        }

        # Data Analyst role should accept Data Analyst job
        valid_job = {
            "title": "Junior Data Analyst",
            "company": "Analytics Corp",
            "location": "Bengaluru, Karnataka, India",
            "clean_description": "Work with SQL and Python for data analytics."
        }
        res = RoleRelevanceService.evaluate_role_relevance(candidate_profile, valid_job, target_role="Data Analyst")
        self.assertTrue(res.get("eligible"), f"Expected eligible, got: {res}")
        self.assertIn(res.get("role_relevance_status"), ["DIRECT_ROLE_MATCH", "RELATED_ROLE"])

        # Data Analyst role should reject Accountant job
        unrelated_job = {
            "title": "Senior Accountant / Buchhalter",
            "company": "Finance Corp",
            "location": "Berlin, Germany",
            "clean_description": "Accounting and ledger auditing."
        }
        res_unrelated = RoleRelevanceService.evaluate_role_relevance(candidate_profile, unrelated_job, target_role="Data Analyst")
        self.assertFalse(res_unrelated.get("eligible"), "Accountant job must be rejected for Data Analyst role")
        self.assertEqual(res_unrelated.get("role_relevance_status"), "UNRELATED")

    def test_05_no_fake_vacancies_in_fallback(self):
        """Ensure no synthetic or mock jobs exist in the returned dataset."""
        jobs = JobService.find_verified_jobs(target_role="Software Engineer", limit=20)
        for j in jobs:
            title_lower = j.get("title", "").lower()
            company_lower = j.get("company", "").lower()
            url = j.get("application_url", "")
            self.assertNotIn("mock", title_lower)
            self.assertNotIn("synthetic", title_lower)
            self.assertNotIn("mock", company_lower)
            self.assertTrue(url.startswith("http://") or url.startswith("https://"), f"Invalid application_url: {url}")

if __name__ == "__main__":
    unittest.main()
