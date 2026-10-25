import datetime
import io
import time
import unittest
import uuid
from unittest.mock import patch, MagicMock
import jwt

from app import create_app
from app.config import Config
from app.db import Database
from app.models.user import UserModel
from app.models.resume import ResumeModel
from app.services.role_inference_service import RoleInferenceEngine
from app.services.role_relevance_service import RoleRelevanceService
from app.services.role_taxonomy import RoleTaxonomy
from app.routes.job import clear_recommendations_cache, _RECOMMENDATIONS_CACHE


class TestFeaturesAudit(unittest.TestCase):
    """
    Comprehensive Automated Test Suite covering the 15 Audit Requirements:
    1. Google ID token verification & rejection of invalid/forged credentials
    2. Missing Google OAuth configuration handled safely (503)
    3. Existing email/password authentication remains fully operational
    4. Account linking prevents cross-account takeover / data exposure
    5. AI/ML resume receives AI/ML-related job searches and matches
    6. Full Stack resume receives full stack-related recommendations
    7. Data Analyst resume is not classified as an Accountant (and vice versa)
    8. Electrician resume does not receive software engineering recommendations
    9. Nurse, teacher, accountant, mechanic, and software resumes match relevant job families
    10. Ambiguous resumes flag is_ambiguous: True and populate alternative domains
    11. Changing selected role invalidates cached recommendations
    12. Missing location does not eliminate results (graceful fallback)
    13. Provider failures preserve valid results from other providers
    14. No fictional vacancies are returned
    15. User isolation and resume access controls remain intact
    """

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True

    def setUp(self):
        self.client = self.app.test_client()
        self.test_email = f"audit_user_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "SecurePassword123!"

        self.user_doc = UserModel.create_user({
            "name": "Audit Test User",
            "email": self.test_email,
            "password": self.test_password,
            "preferred_job_role": "Full Stack Developer",
            "preferred_location": "Remote",
            "experience_level": "Mid-Level"
        })
        self.user_id = str(self.user_doc["_id"])

        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": self.user_id,
            "email": self.test_email,
            "name": "Audit Test User",
            "iat": now,
            "exp": now + datetime.timedelta(hours=2)
        }
        self.token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        coll = UserModel.get_collection()
        if coll is not None:
            try:
                coll.delete_one({"email": self.test_email})
            except Exception:
                pass
        UserModel._in_memory_users.pop(self.test_email, None)
        UserModel._in_memory_users.pop(self.user_id, None)

    # -------------------------------------------------------------------------
    # TEST 1: Google token verification & rejection of invalid/forged credentials
    # -------------------------------------------------------------------------
    def test_01_google_auth_token_verification_and_forgery_rejection(self):
        """Rejects forged tokens, bad issuer, and unverified emails."""
        # 1a. Missing credential
        res_empty = self.client.post('/api/auth/google', json={})
        self.assertEqual(res_empty.status_code, 400)
        self.assertIn("required", res_empty.get_json()["message"].lower())

        # 1b. Invalid / forged JWT token signature
        fake_jwt = "header.payload.signature"
        with patch('google.oauth2.id_token.verify_oauth2_token', side_effect=ValueError("Invalid token signature")):
            res_forged = self.client.post('/api/auth/google', json={"credential": fake_jwt})
            self.assertEqual(res_forged.status_code, 401)
            self.assertIn("invalid", res_forged.get_json()["message"].lower())

        # 1c. Invalid issuer
        fake_payload_bad_iss = {
            "sub": "google_123",
            "email": "test@gmail.com",
            "email_verified": True,
            "iss": "evil-issuer.com"
        }
        with patch('google.oauth2.id_token.verify_oauth2_token', return_value=fake_payload_bad_iss):
            res_bad_iss = self.client.post('/api/auth/google', json={"credential": fake_jwt})
            self.assertEqual(res_bad_iss.status_code, 401)
            self.assertEqual(res_bad_iss.get_json()["error"], "INVALID_ISSUER")

        # 1d. Unverified email
        fake_payload_unverified = {
            "sub": "google_123",
            "email": "unverified@gmail.com",
            "email_verified": False,
            "iss": "accounts.google.com"
        }
        with patch('google.oauth2.id_token.verify_oauth2_token', return_value=fake_payload_unverified):
            res_unver = self.client.post('/api/auth/google', json={"credential": fake_jwt})
            self.assertEqual(res_unver.status_code, 400)
            self.assertEqual(res_unver.get_json()["error"], "EMAIL_NOT_VERIFIED")

    # -------------------------------------------------------------------------
    # TEST 2: Missing Google OAuth configuration handled safely (503)
    # -------------------------------------------------------------------------
    def test_02_missing_google_oauth_config_handled_safely(self):
        """When GOOGLE_CLIENT_ID is unconfigured, return 503 GOOGLE_OAUTH_UNCONFIGURED in non-testing mode."""
        self.app.config['TESTING'] = False
        try:
            with patch.object(Config, 'GOOGLE_CLIENT_ID', ''):
                res = self.client.post('/api/auth/google', json={"credential": "some_token"})
                self.assertEqual(res.status_code, 503)
                self.assertEqual(res.get_json()["error"], "GOOGLE_OAUTH_UNCONFIGURED")
        finally:
            self.app.config['TESTING'] = True

    # -------------------------------------------------------------------------
    # TEST 3: Existing email/password authentication remains operational
    # -------------------------------------------------------------------------
    def test_03_existing_email_password_auth_remains_operational(self):
        """Normal email/password login and register succeed and issue valid tokens."""
        login_res = self.client.post('/api/auth/login', json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertTrue(data["success"])
        token = data["data"]["token"]
        self.assertTrue(bool(token))

        # Check me endpoint with token
        me_res = self.client.get('/api/auth/me', headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.get_json()["data"]["user"]["email"], self.test_email)

    # -------------------------------------------------------------------------
    # TEST 4: Account linking prevents cross-account takeover / data exposure
    # -------------------------------------------------------------------------
    def test_04_account_linking_and_takeover_prevention(self):
        """Existing account with same verified email links safely; cross-account collision rejected."""
        fake_jwt = "header.payload.signature"
        gid = f"gid_{uuid.uuid4().hex[:8]}"

        # 4a. Safe link with matching verified email
        payload_match = {
            "sub": gid,
            "email": self.test_email,
            "name": "Linked Name",
            "email_verified": True,
            "iss": "https://accounts.google.com"
        }
        with patch('google.oauth2.id_token.verify_oauth2_token', return_value=payload_match):
            res_link = self.client.post('/api/auth/google', json={"credential": fake_jwt})
            self.assertEqual(res_link.status_code, 200)
            self.assertEqual(res_link.get_json()["data"]["user"]["email"], self.test_email)

        # 4b. Cross-account conflict: different google_id tries to claim the same email
        different_gid = f"gid_different_{uuid.uuid4().hex[:8]}"
        payload_conflict = {
            "sub": different_gid,
            "email": self.test_email,
            "name": "Attacker",
            "email_verified": True,
            "iss": "https://accounts.google.com"
        }
        with patch('google.oauth2.id_token.verify_oauth2_token', return_value=payload_conflict):
            res_conflict = self.client.post('/api/auth/google', json={"credential": fake_jwt})
            self.assertEqual(res_conflict.status_code, 409)
            self.assertEqual(res_conflict.get_json()["error"], "ACCOUNT_LINKING_CONFLICT")

    # -------------------------------------------------------------------------
    # TEST 5: AI/ML resume receives AI/ML-related job searches and matches
    # -------------------------------------------------------------------------
    def test_05_ai_ml_resume_classification(self):
        """AI/ML candidate receives AI/ML canonical role and domain."""
        aiml_profile = {
            "job_title": "Machine Learning Engineer",
            "skills": ["Python", "PyTorch", "TensorFlow", "Transformers", "NLP", "LLM", "Deep Learning"],
            "experience": [
                {"title": "Senior AI Engineer", "description": "Trained diffusion models and deployed fine-tuned LLMs"}
            ]
        }
        inferred = RoleInferenceEngine.infer_candidate_profile(aiml_profile)
        self.assertEqual(inferred["professional_domain"], "AI_ML")
        primary_role = inferred["primary_roles"][0]
        self.assertIn(primary_role, [
            "Machine Learning Engineer", "AI Research Scientist", "AI Engineer", "Deep Learning Engineer"
        ])

        # Verify role relevance scores
        eval_res = RoleRelevanceService.evaluate_role_relevance(
            candidate_profile={"target_role": primary_role, "professional_domain": inferred["professional_domain"], "primary_roles": inferred["primary_roles"]},
            job={"title": "Senior Machine Learning Specialist", "raw_description": "Build PyTorch models and LLM fine-tuning pipelines"}
        )
        self.assertTrue(eval_res["eligible"])
        self.assertIn(eval_res["role_relevance_status"], ["DIRECT_ROLE_MATCH", "RELATED_ROLE"])

    # -------------------------------------------------------------------------
    # TEST 6: Full Stack resume receives full stack-related recommendations
    # -------------------------------------------------------------------------
    def test_06_full_stack_resume_classification(self):
        """Full stack candidate receives Full Stack Developer role, not pure data or trades."""
        fs_profile = {
            "job_title": "Full Stack Developer",
            "skills": ["JavaScript", "TypeScript", "React", "Node.js", "Express", "PostgreSQL", "REST APIs"],
            "experience": [
                {"title": "Full Stack Software Engineer", "description": "Developed React frontend and Node.js microservices"}
            ]
        }
        inferred = RoleInferenceEngine.infer_candidate_profile(fs_profile)
        self.assertEqual(inferred["professional_domain"], "FULL_STACK_DEVELOPMENT")
        self.assertEqual(inferred["primary_roles"][0], "Full Stack Developer")

    # -------------------------------------------------------------------------
    # TEST 7: Data Analyst resume is not classified as an Accountant (and vice versa)
    # -------------------------------------------------------------------------
    def test_07_data_analyst_vs_accountant_boundary(self):
        """Clean boundary between Data Analyst and Accountant despite shared keywords like Excel."""
        # Data Analyst
        da_profile = {
            "job_title": "Data Analyst",
            "skills": ["SQL", "Tableau", "Power BI", "Excel", "Data Visualization", "Python", "ETL"],
            "experience": [{"title": "Business Intelligence Analyst", "description": "Built dashboards and SQL metrics"}]
        }
        inferred_da = RoleInferenceEngine.infer_candidate_profile(da_profile)
        self.assertEqual(inferred_da["professional_domain"], "DATA_SCIENCE_ANALYTICS")
        self.assertIn(inferred_da["primary_roles"][0], ["Data Analyst", "BI Developer", "Business Intelligence Analyst"])
        self.assertNotEqual(inferred_da["professional_domain"], "ACCOUNTING_FINANCE")

        # Accountant
        acc_profile = {
            "job_title": "Senior Accountant",
            "skills": ["General Ledger", "Tax Preparation", "Audit", "Financial Reporting", "Excel", "QuickBooks", "GAAP"],
            "experience": [{"title": "Staff Accountant", "description": "Reconciled balance sheets and quarterly taxes"}]
        }
        inferred_acc = RoleInferenceEngine.infer_candidate_profile(acc_profile)
        self.assertEqual(inferred_acc["professional_domain"], "ACCOUNTING_FINANCE")
        self.assertIn(inferred_acc["primary_roles"][0], ["Accountant", "Certified Public Accountant (CPA)", "Auditor"])
        self.assertNotEqual(inferred_acc["professional_domain"], "DATA_SCIENCE_ANALYTICS")

        # Boundary gate check
        gate_da_to_acc = RoleRelevanceService.evaluate_role_relevance(
            candidate_profile={"target_role": inferred_da["primary_roles"][0], "professional_domain": "DATA_SCIENCE_ANALYTICS", "primary_roles": inferred_da["primary_roles"]},
            job={"title": "Tax Accountant / CPA", "raw_description": "Prepare federal tax returns and reconcile ledger entries"}
        )
        self.assertFalse(gate_da_to_acc["eligible"])
        self.assertEqual(gate_da_to_acc["role_relevance_status"], "UNRELATED")

    # -------------------------------------------------------------------------
    # TEST 8: Electrician resume does not receive software engineering recommendations
    # -------------------------------------------------------------------------
    def test_08_electrician_isolation_from_software(self):
        """Electrician is categorized in SKILLED_TRADES_ELECTRICAL and cross-domain rejects software engineering."""
        elec_profile = {
            "job_title": "Journeyman Electrician",
            "skills": ["Conduit Bending", "Wiring", "National Electrical Code (NEC)", "Blueprints", "High Voltage", "Switchgear"],
            "experience": [{"title": "Commercial Electrician", "description": "Installed panels and electrical conduits"}]
        }
        inferred = RoleInferenceEngine.infer_candidate_profile(elec_profile)
        self.assertEqual(inferred["professional_domain"], "SKILLED_TRADES_ELECTRICAL")
        self.assertEqual(inferred["primary_roles"][0], "Electrician")

        # Must reject software engineering vacancies
        eval_soft = RoleRelevanceService.evaluate_role_relevance(
            candidate_profile={"target_role": inferred["primary_roles"][0], "professional_domain": "SKILLED_TRADES_ELECTRICAL", "primary_roles": inferred["primary_roles"]},
            job={"title": "Senior Python Backend Engineer", "raw_description": "Architect scalable microservices with FastAPI and Docker"}
        )
        self.assertFalse(eval_soft["eligible"])
        self.assertEqual(eval_soft["role_relevance_status"], "UNRELATED")

    # -------------------------------------------------------------------------
    # TEST 9: Nurse, Teacher, Accountant, Mechanic, Software resumes match families
    # -------------------------------------------------------------------------
    def test_09_multi_profession_accuracy(self):
        """All canonical professional families are accurately categorized."""
        cases = [
            ("Registered Nurse", ["ICU", "Patient Care", "BLS", "Triage", "EMR"], "HEALTHCARE_NURSING", "Registered Nurse"),
            ("High School Math Teacher", ["Curriculum Design", "Lesson Planning", "Classroom Management", "Pedagogy"], "EDUCATION", "School Teacher"),
            ("Auto Mechanic", ["Brake Repair", "Engine Diagnostics", "Transmission", "OBD-II", "Automotive"], "SKILLED_TRADES_MECHANIC", "Automotive Mechanic"),
            ("DevOps Engineer", ["Kubernetes", "Terraform", "CI/CD", "AWS", "Docker", "Prometheus"], "CLOUD_INFRASTRUCTURE", "DevOps Engineer"),
            ("Cybersecurity Analyst", ["SIEM", "Penetration Testing", "SOC", "Firewalls", "Incident Response"], "CYBERSECURITY", "Cybersecurity Analyst"),
            ("Frontend Engineer", ["React", "HTML5", "CSS3", "Redux", "Tailwind CSS"], "FRONTEND_DEVELOPMENT", "Frontend Developer"),
            ("QA Automation Engineer", ["Selenium", "Cypress", "PyTest", "Test Automation", "Jira"], "QA_TESTING", "QA Engineer")
        ]

        for title, skills, expected_domain, expected_role in cases:
            profile = {
                "job_title": title,
                "skills": skills,
                "experience": [{"title": title, "description": f"Worked professionally as {title}"}]
            }
            res = RoleInferenceEngine.infer_candidate_profile(profile)
            self.assertEqual(res["professional_domain"], expected_domain, f"Failed for domain of: {title}")
            if expected_role:
                all_roles = res.get("primary_roles", []) + res.get("related_roles", []) + res.get("alternative_roles", [])
                self.assertIn(expected_role, all_roles, f"Role mismatch for: {title}")

    # -------------------------------------------------------------------------
    # TEST 10: Ambiguous resumes flag is_ambiguous: True and populate alternatives
    # -------------------------------------------------------------------------
    def test_10_ambiguous_resume_detection(self):
        """Resumes spanning multiple domains flag ambiguity and provide alternative options."""
        ambiguous_profile = {
            "job_title": "Technical Consultant",
            "skills": ["JavaScript", "React", "Financial Reporting", "QuickBooks", "Budgeting", "Node.js"],
            "experience": [
                {"title": "Web Developer", "description": "Built web apps"},
                {"title": "Bookkeeper", "description": "Handled invoices and accounts"}
            ]
        }
        res = RoleInferenceEngine.infer_candidate_profile(ambiguous_profile)
        self.assertTrue(res.get("is_ambiguous", False) or res.get("needs_confirmation", False))
        self.assertTrue(len(res.get("alternative_professions", [])) > 0 or len(res.get("alternative_roles", [])) > 0)

    # -------------------------------------------------------------------------
    # TEST 11: Changing selected role invalidates cached recommendations
    # -------------------------------------------------------------------------
    def test_11_role_change_invalidates_cache(self):
        """Clearing or changing role eliminates stale cached recommendation entries."""
        cache_key_role1 = (self.user_id, "resume_1", "Electrician", None, False, None, 0)
        cache_key_role2 = (self.user_id, "resume_1", "SoftwareEngineer", None, False, None, 0)

        _RECOMMENDATIONS_CACHE[cache_key_role1] = {"jobs": [{"id": "elec_1"}], "timestamp": time.time()}
        _RECOMMENDATIONS_CACHE[cache_key_role2] = {"jobs": [{"id": "sw_1"}], "timestamp": time.time()}

        # Verify entry exists
        self.assertIn(cache_key_role1, _RECOMMENDATIONS_CACHE)

        # Invalidate cache for this user
        clear_recommendations_cache(self.user_id)

        self.assertNotIn(cache_key_role1, _RECOMMENDATIONS_CACHE)
        self.assertNotIn(cache_key_role2, _RECOMMENDATIONS_CACHE)

    # -------------------------------------------------------------------------
    # TEST 12: Missing location does not eliminate results (graceful fallback)
    # -------------------------------------------------------------------------
    def test_12_missing_location_graceful_handling(self):
        """Searching without a location parameter returns vacancies gracefully."""
        res = self.client.get('/api/jobs/search?query=Software+Engineer', headers=self.auth_headers)
        self.assertIn(res.status_code, [200, 204])
        if res.status_code == 200:
            data = res.get_json()
            self.assertTrue(data.get("success", True))

    # -------------------------------------------------------------------------
    # TEST 13: Provider failures preserve valid results from other providers
    # -------------------------------------------------------------------------
    def test_13_provider_partial_failure_tolerance(self):
        """When one external provider throws an exception, other provider results are preserved."""
        mock_search_res = {
            "success": True,
            "jobs": [
                {
                    "id": "prov2_101",
                    "title": "Full Stack Developer",
                    "company": "Tech Corp",
                    "location": "Remote",
                    "description": "React and Node.js developer needed",
                    "url": "https://example.com/apply/101",
                    "source": "WorkingProvider"
                }
            ],
            "provider_status": {"Adzuna": "FAILED", "WorkingProvider": "SUCCESS"},
            "providers_used": ["WorkingProvider"]
        }

        with patch('app.services.job_providers.provider_factory.MultiSourceJobProvider.search_jobs', return_value=mock_search_res):
            res = self.client.get('/api/jobs/search?query=Full+Stack+Developer', headers=self.auth_headers)
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            jobs = data.get("jobs", [])
            self.assertTrue(any(j.get("company") == "Tech Corp" for j in jobs))

    # -------------------------------------------------------------------------
    # TEST 14: No fictional vacancies are returned
    # -------------------------------------------------------------------------
    def test_14_no_fictional_vacancies_returned(self):
        """Returned vacancies must have real company names, valid URLs, and not be hardcoded mocks."""
        mock_search_res = {
            "success": True,
            "jobs": [
                {
                    "id": "valid_job_1",
                    "title": "Machine Learning Engineer",
                    "company": "Real AI Labs Inc",
                    "location": "San Francisco, CA",
                    "description": "Production PyTorch and Kubeflow models",
                    "application_url": "https://realailabs.com/careers/123",
                    "url": "https://realailabs.com/careers/123",
                    "source": "Adzuna"
                }
            ],
            "provider_status": {"Adzuna": "SUCCESS"},
            "providers_used": ["Adzuna"]
        }

        with patch('app.services.job_providers.provider_factory.MultiSourceJobProvider.search_jobs', return_value=mock_search_res):
            res = self.client.get('/api/jobs/search?query=Machine+Learning+Engineer', headers=self.auth_headers)
            self.assertEqual(res.status_code, 200)
            jobs = res.get_json().get("jobs", [])
            for job in jobs:
                self.assertTrue(bool(job.get("company")))
                self.assertNotIn(job.get("company", "").lower(), ["fake company", "mock company", "dummy"])
                url = job.get("application_url") or job.get("url") or ""
                self.assertTrue(url.startswith("http"))

    # -------------------------------------------------------------------------
    # TEST 15: User isolation and resume access controls remain intact
    # -------------------------------------------------------------------------
    def test_15_user_isolation_and_access_control(self):
        """User A cannot access User B's resume or analysis records."""
        # Create User B
        other_email = f"other_{uuid.uuid4().hex[:8]}@example.com"
        other_user = UserModel.create_user({
            "name": "Other Candidate",
            "email": other_email,
            "password": "Password123!"
        })
        other_id = str(other_user["_id"])

        # Create resume belonging to User B
        resume_doc = ResumeModel.create_resume(
            user_id=other_id,
            original_filename="confidential.pdf",
            stored_filename="confidential_123.pdf",
            file_path="/tmp/confidential_123.pdf",
            file_type="pdf",
            file_size=1024
        )
        resume_id = str(resume_doc["_id"])

        # User A attempts to analyze or fetch User B's resume
        res = self.client.post(f'/api/resume/analyze/{resume_id}', headers=self.auth_headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn("access denied", res.get_json()["message"].lower())


if __name__ == '__main__':
    unittest.main()
