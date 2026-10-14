"""
Comprehensive Test Suite for Vacancy Filter Diagnostics, Role Inference,
Location Filtering, Experience Tiers, and MongoDB Atlas Fallback.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app import create_app
from app.services.role_inference_service import RoleInferenceEngine
from app.services.role_relevance_service import RoleRelevanceService
from app.services.role_taxonomy import RoleTaxonomy
from app.services.seniority_service import SeniorityService
from app.services.geo_eligibility_service import GeoEligibilityService
from app.services.job_service import JobService


class TestVacancyFilterDiagnostics(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_tech_candidate_domain_not_hijacked_by_architecture(self):
        """Verify resume with system architecture is classified as tech, never building architecture."""
        tech_resume = {
            "validation_status": "VALID_RESUME",
            "resume_score": 85,
            "technical_skills": ["Python", "React", "Machine Learning", "SQL", "Git"],
            "raw_text": "B.Tech Computer Science and Engineering. Final year project: finalized the system architecture and data pipeline using microservices."
        }
        profile = RoleInferenceEngine.infer_candidate_profile(tech_resume)
        self.assertEqual(profile.get("professional_domain"), "SOFTWARE_IT")
        self.assertIn(profile.get("professional_domain"), ["SOFTWARE_IT", "DATA_SCIENCE_AI"])
        self.assertNotEqual(profile.get("professional_domain"), "ARCHITECTURE")
        self.assertNotEqual(profile.get("professional_identity"), "Architectural Designer")

    def test_tech_candidate_domain_not_hijacked_by_semester(self):
        """Verify resume with '6th sem' or 'semester' is not hijacked into Marketing via 'sem'."""
        student_resume = {
            "validation_status": "VALID_RESUME",
            "resume_score": 80,
            "technical_skills": ["Java", "Python", "SQL", "Data Science", "C++"],
            "raw_text": "B.Tech CSE student currently in 6th sem. Completed coursework in data science and algorithms."
        }
        profile = RoleInferenceEngine.infer_candidate_profile(student_resume)
        self.assertEqual(profile.get("professional_domain"), "SOFTWARE_IT")
        self.assertNotEqual(profile.get("professional_domain"), "MARKETING")

    def test_genuine_building_architecture_detection(self):
        """Verify candidate with genuine B.Arch / building design is classified as ARCHITECTURE."""
        barch_resume = {
            "validation_status": "VALID_RESUME",
            "resume_score": 80,
            "technical_skills": ["AutoCAD", "Revit", "SketchUp", "Building Design"],
            "raw_text": "Bachelor of Architecture (B.Arch). Experienced in residential building design and spatial planning."
        }
        profile = RoleInferenceEngine.infer_candidate_profile(barch_resume)
        self.assertEqual(profile.get("professional_domain"), "ARCHITECTURE")
        self.assertEqual(profile.get("professional_identity"), "Architectural Designer")

    def test_role_relevance_automated_recommendation_flow(self):
        """Verify when role is not explicitly specified, candidate domain & inferred roles are accepted."""
        cand_profile = {
            "professional_domain": "SOFTWARE_IT",
            "primary_roles": ["Software Engineer", "Full Stack Developer"],
            "inferred_roles": ["Software Engineer", "Backend Developer", "Python Developer"],
            "core_skills": ["python", "react", "sql"]
        }
        # Inferred role matching
        job_match = {"title": "Python Developer", "clean_description": "We need Python and SQL skills."}
        res = RoleRelevanceService.evaluate_role_relevance(cand_profile, job_match, is_explicit_role=False)
        self.assertTrue(res.get("eligible"))
        self.assertIn(res.get("role_relevance_status"), ["DIRECT_ROLE_MATCH", "RELATED_ROLE"])

        # Domain matching for tech role
        tech_job = {"title": "Web Developer", "clean_description": "Frontend and backend web development with python and react."}
        res2 = RoleRelevanceService.evaluate_role_relevance(cand_profile, tech_job, is_explicit_role=False)
        self.assertTrue(res2.get("eligible"))

        # Cross-domain exclusion (Accountant should be rejected for tech profile)
        accountant_job = {"title": "Junior Accountant", "clean_description": "Tally and GST accounts payable."}
        res3 = RoleRelevanceService.evaluate_role_relevance(cand_profile, accountant_job, is_explicit_role=False)
        self.assertFalse(res3.get("eligible"))
        self.assertEqual(res3.get("role_relevance_status"), "UNRELATED")

    def test_role_relevance_explicit_filter(self):
        """Verify explicit user-selected role strictly filters jobs."""
        cand_profile = {
            "professional_domain": "SOFTWARE_IT",
            "primary_roles": ["Software Engineer"],
            "inferred_roles": ["Software Engineer"]
        }
        target_role = "Data Analyst"
        da_job = {"title": "Junior Data Analyst", "clean_description": "Data analysis and reporting"}
        swe_job = {"title": "Software Engineer", "clean_description": "Java backend engineering"}

        # Explicit filter for Data Analyst allows Data Analyst
        res_da = RoleRelevanceService.evaluate_role_relevance(cand_profile, da_job, target_role=target_role, is_explicit_role=True)
        self.assertTrue(res_da.get("eligible"))

        # Explicit filter for Data Analyst rejects Software Engineer
        res_swe = RoleRelevanceService.evaluate_role_relevance(cand_profile, swe_job, target_role=target_role, is_explicit_role=True)
        self.assertFalse(res_swe.get("eligible"))

    def test_seniority_evaluation_and_conflicts(self):
        """Verify seniority matching for entry-level candidates."""
        cand_entry = {"experience_level": "Fresher / Entry Level", "inferred_roles": ["Junior Software Engineer"]}
        entry_job = {"title": "Junior Developer", "experience_required": "0-1 years"}
        senior_job = {"title": "Lead Software Architect", "experience_required": "8+ years"}

        res_entry = SeniorityService.evaluate_seniority(cand_entry, entry_job)
        self.assertEqual(res_entry.get("seniority_status"), "MATCHED")
        self.assertFalse(res_entry.get("is_fresher_mismatch"))

        res_senior = SeniorityService.evaluate_seniority(cand_entry, senior_job)
        self.assertEqual(res_senior.get("seniority_status"), "SENIORITY_MISMATCH")
        self.assertTrue(res_senior.get("is_fresher_mismatch"))

    def test_geo_eligibility_worldwide_acceptance(self):
        """Verify worldwide vacancies are eligible across locations."""
        for loc in ["Bangalore, India", "Chennai, Tamil Nadu", "Berlin, Germany", "Remote - Worldwide", "San Francisco, CA"]:
            job = {"location": loc, "workplace_type": "HYBRID"}
            res = GeoEligibilityService.evaluate_geo_eligibility(job)
            self.assertTrue(res.get("eligible"))

    def test_find_verified_jobs_fallback_retrieval(self):
        """Verify find_verified_jobs retrieves real verified documents."""
        db_jobs = JobService.find_verified_jobs(target_role="Software Engineer", limit=10)
        self.assertIsInstance(db_jobs, list)
        self.assertGreater(len(db_jobs), 0)
        first_job = db_jobs[0]
        self.assertTrue(first_job.get("is_live"))
        self.assertIn("title", first_job)
        self.assertIn("company", first_job)
        self.assertIn("application_url", first_job)

    def test_find_verified_jobs_location_relaxation(self):
        """Verify when a specific location filter has 0 records, fallback relaxes gracefully."""
        db_jobs = JobService.find_verified_jobs(target_role="Software Engineer", location="NonExistentCityXYZ", limit=10)
        self.assertIsInstance(db_jobs, list)
        self.assertGreater(len(db_jobs), 0)


if __name__ == "__main__":
    unittest.main()
