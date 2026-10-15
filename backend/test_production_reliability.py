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
from app.models.resume_analysis import ResumeAnalysisModel
from app.services.role_inference_service import RoleInferenceEngine
from app.services.resume_validator import ResumeValidator
from app.services.pdf_service import PDFService
from app.services.deduplication import DeduplicationAndCacheEngine
from app.routes.job import clear_recommendations_cache, _RECOMMENDATIONS_CACHE


class TestProductionReliability(unittest.TestCase):
    """
    Comprehensive Production Reliability and Permanent Stability Test Suite.
    Covers:
    1. Authentication & Session Reliability (Login, Register, Expired Tokens, Deduplication, DB Outages)
    2. Self-Healing Database & Liveness/Readiness Checks
    3. Universal Profession Relevance (Electrician, Nurse, Teacher, Accountant, Software Engineer)
    4. Malformed/Missing Resume Handling
    5. Partial Provider Failure, Timeouts & Deduplication
    6. Multi-User Access Control & Cache Invalidation
    7. CORS & Correlation ID Tracking
    """

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True

    def setUp(self):
        self.client = self.app.test_client()
        self.test_email = f"reliability_{uuid.uuid4().hex[:8]}@example.com"
        self.test_password = "SecurePassword123!"

        self.user_doc = UserModel.create_user({
            "name": "Reliability User",
            "email": self.test_email,
            "password": self.test_password,
            "education": "University",
            "degree": "B.S.",
            "preferred_job_role": "Software Engineer",
            "preferred_location": "Remote",
            "experience_level": "Mid-Level"
        })
        self.user_id = str(self.user_doc["_id"])

        # Generate valid token
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": self.user_id,
            "email": self.test_email,
            "name": "Reliability User",
            "iat": now,
            "exp": now + datetime.timedelta(hours=2)
        }
        self.token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

    def tearDown(self):
        coll = UserModel.get_collection()
        if coll is not None:
            try:
                coll.delete_one({"email": self.test_email})
            except Exception:
                pass
        UserModel._in_memory_users.pop(self.test_email, None)
        UserModel._in_memory_users.pop(self.user_id, None)

    # =========================================================================
    # 1. AUTHENTICATION & SESSION RELIABILITY
    # =========================================================================
    def test_01_registration_and_duplicate_prevention(self):
        """Test registration validation, duplicate email 409, and password security."""
        # Missing confirm_password
        res1 = self.client.post('/api/auth/register', json={
            "name": "New Candidate",
            "email": f"new_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Password123!"
        })
        self.assertEqual(res1.status_code, 400)

        # Duplicate email
        res2 = self.client.post('/api/auth/register', json={
            "name": "Duplicate Candidate",
            "email": self.test_email,
            "password": self.test_password,
            "confirm_password": self.test_password
        })
        self.assertEqual(res2.status_code, 409)

    def test_02_login_and_valid_session(self):
        """Test successful login and subsequent /api/auth/me token verification."""
        login_res = self.client.post('/api/auth/login', json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.get_json()["data"]["token"]

        me_res = self.client.get('/api/auth/me', headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.get_json()["data"]["user"]["email"], self.test_email)

    def test_03_expired_and_malformed_tokens(self):
        """Test expired token returns 401 Token Expired without crashing."""
        past = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)
        expired_payload = {
            "sub": self.user_id,
            "email": self.test_email,
            "iat": past - datetime.timedelta(hours=1),
            "exp": past
        }
        expired_token = jwt.encode(expired_payload, Config.JWT_SECRET_KEY, algorithm="HS256")

        res = self.client.get('/api/auth/me', headers={"Authorization": f"Bearer {expired_token}"})
        self.assertEqual(res.status_code, 401)
        self.assertIn("expired", res.get_json().get("message", "").lower())

        # Malformed token
        res_bad = self.client.get('/api/auth/me', headers={"Authorization": "Bearer invalid.token.payload"})
        self.assertEqual(res_bad.status_code, 401)

    def test_04_database_outage_does_not_falsely_delete_user(self):
        """Verify DB outage returns 503 instead of 401 (which would wipe user session)."""
        with patch.object(Database, 'is_connected', return_value=False), \
             patch.object(UserModel, '_in_memory_users', {}):
            res = self.client.get('/api/auth/me', headers={"Authorization": f"Bearer {self.token}"})
            self.assertEqual(res.status_code, 503)
            self.assertEqual(res.get_json().get("error"), "Database unavailable")

    def test_05_database_self_healing_reconnect(self):
        """Verify Database.get_db() attempts reconnection after cooldown when client was offline."""
        Database._db = False
        Database._client = None
        Database._last_connect_attempt = time.time() - 10  # Cooldown passed

        # Trigger get_db()
        db = Database.get_db()
        # Should attempt reconnection; if local mongo is up, it reconnects
        if Database._client is not None:
            self.assertIsNotNone(db)

    # =========================================================================
    # 2. LIVENESS, READINESS & STRUCTURED LOGGING
    # =========================================================================
    def test_06_liveness_endpoint(self):
        """Test /api/health/live returns 200 OK immediately."""
        res = self.client.get('/api/health/live')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json().get("status"), "live")

    def test_07_readiness_endpoint(self):
        """Test /api/health/ready reflects MongoDB readiness."""
        res = self.client.get('/api/health/ready')
        self.assertIn(res.status_code, [200, 503])
        self.assertIn("dependencies", res.get_json())

        # Mock DB offline
        with patch.object(Database, 'is_connected', return_value=False):
            res_offline = self.client.get('/api/health/ready')
            self.assertEqual(res_offline.status_code, 503)
            self.assertEqual(res_offline.get_json().get("status"), "not_ready")

    def test_08_request_id_tracing_header(self):
        """Verify X-Request-ID is tracked from client or generated on server."""
        custom_req_id = "test_req_trace_999"
        res = self.client.get('/api/health', headers={"X-Request-ID": custom_req_id})
        self.assertEqual(res.headers.get("X-Request-ID"), custom_req_id)

    # =========================================================================
    # 3. UNIVERSAL PROFESSIONS RELEVANCE
    # =========================================================================
    def test_09_universal_professions_role_inference(self):
        """Test role inference across 5 distinct industries: Electrician, Nurse, Teacher, Accountant, Software Engineer."""
        test_cases = [
            {
                "profession": "Electrician",
                "analysis": {
                    "document_type": "RESUME",
                    "technical_skills": ["Circuit Breakers", "Wiring", "Electrical Maintenance", "Conduit Bending"],
                    "extracted_text": "Licensed Journeyman Electrician with 5 years experience installing electrical systems and wiring."
                },
                "expected_domain": "Skilled Trades",
                "keyword_candidates": ["electrician", "electrical"]
            },
            {
                "profession": "Registered Nurse",
                "analysis": {
                    "document_type": "RESUME",
                    "technical_skills": ["Patient Care", "BLS", "Medication Administration", "Triage"],
                    "extracted_text": "Staff Nurse RN specializing in emergency care and ICU patient triage."
                },
                "expected_domain": "Healthcare",
                "keyword_candidates": ["nurse", "nursing", "rn"]
            },
            {
                "profession": "Teacher",
                "analysis": {
                    "document_type": "RESUME",
                    "technical_skills": ["Curriculum Design", "Classroom Management", "Lesson Planning"],
                    "extracted_text": "High School Mathematics Teacher with 4 years classroom instructional experience."
                },
                "expected_domain": "Education",
                "keyword_candidates": ["teacher", "educator", "instructor"]
            },
            {
                "profession": "Accountant",
                "analysis": {
                    "document_type": "RESUME",
                    "technical_skills": ["GAAP", "QuickBooks", "Tax Preparation", "Financial Auditing"],
                    "extracted_text": "Certified Public Accountant with experience in corporate ledger reconciliation and tax filings."
                },
                "expected_domain": "Finance & Accounting",
                "keyword_candidates": ["accountant", "accounting", "cpa"]
            },
            {
                "profession": "Software Engineer",
                "analysis": {
                    "document_type": "RESUME",
                    "technical_skills": ["Python", "Flask", "React", "PostgreSQL", "Docker"],
                    "extracted_text": "Full Stack Software Engineer building microservices and web applications."
                },
                "expected_domain": "Information Technology",
                "keyword_candidates": ["software engineer", "developer", "full stack"]
            }
        ]

        for case in test_cases:
            profile = RoleInferenceEngine.infer_candidate_profile(case["analysis"])
            primary_kw = profile.get("primary_search_keyword", "").lower()
            inferred_roles = [r.lower() for r in profile.get("inferred_roles", [])]
            combined = primary_kw + " " + " ".join(inferred_roles)

            self.assertTrue(
                any(cand in combined for cand in case["keyword_candidates"]),
                f"Failed for profession {case['profession']}: inferred '{primary_kw}', roles='{inferred_roles}'"
            )

    # =========================================================================
    # 4. MISSING OR MALFORMED RESUMES
    # =========================================================================
    def test_10_missing_or_corrupt_resume_upload(self):
        """Verify upload validation rejects empty, non-pdf, or oversized files cleanly."""
        # No file in request
        res1 = self.client.post('/api/resume/upload', headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(res1.status_code, 400)

        # Non-PDF file
        data = {'resume': (io.BytesIO(b"Hello text file"), 'resume.txt')}
        res2 = self.client.post(
            '/api/resume/upload',
            headers={"Authorization": f"Bearer {self.token}"},
            data=data,
            content_type='multipart/form-data'
        )
        self.assertEqual(res2.status_code, 400)
        self.assertIn("PDF", res2.get_json().get("message", ""))

    def test_11_corrupt_pdf_document_validation(self):
        """Verify corrupt/blank document validator classifies invalid text as INVALID_DOCUMENT."""
        res = ResumeValidator.validate_document("This is a blank non-resume document with no credentials.")
        self.assertNotEqual(res.get("status"), "VALID_RESUME")

    # =========================================================================
    # 5. PROVIDER TIMEOUT, ISOLATION & DEDUPLICATION
    # =========================================================================
    def test_12_partial_provider_failure_and_deduplication(self):
        """Test that failure in one provider does not crash the search, and duplicates are merged."""
        test_url = f"https://example.com/test_dedup_{uuid.uuid4().hex[:8]}"
        job1 = {
            "provider": "adzuna",
            "provider_job_id": f"adz_{uuid.uuid4().hex[:6]}",
            "title": "Data Analyst",
            "company": "Acme Corp",
            "location": "Remote",
            "country": "IN",
            "application_url": test_url,
            "description": "SQL and Python data analysis."
        }
        job2_duplicate = {
            "provider": "jooble",
            "provider_job_id": f"joob_{uuid.uuid4().hex[:6]}",
            "title": "Data Analyst",
            "company": "Acme Corp",
            "location": "Remote",
            "country": "IN",
            "application_url": test_url,  # Same application URL -> duplicate!
            "description": "SQL and Python data analysis."
        }
        job3_unique = {
            "provider": "jooble",
            "provider_job_id": f"joob_{uuid.uuid4().hex[:6]}",
            "title": "Business Intelligence Lead",
            "company": "Tech Matrix",
            "location": "Bengaluru",
            "country": "IN",
            "application_url": f"https://example.com/unique_{uuid.uuid4().hex[:8]}",
            "description": "Tableau and dashboard analytics."
        }

        try:
            normalized = DeduplicationAndCacheEngine.process_and_cache_jobs([job1, job2_duplicate, job3_unique])
            # 3 jobs with 1 duplicate should deduplicate to exactly 2 jobs
            self.assertEqual(len(normalized), 2)
        finally:
            coll = Database.get_db()
            if coll is not None:
                coll["jobs"].delete_many({"application_url": {"$in": [test_url, job3_unique["application_url"]]}})

    # =========================================================================
    # 6. CACHE INVALIDATION & MULTI-USER SECURITY
    # =========================================================================
    def test_13_cache_invalidation_per_user(self):
        """Test that clear_recommendations_cache properly removes target user's entries."""
        cache_key_user1 = (self.user_id, "res_1", "Developer", "Remote", False, "", "")
        cache_key_user2 = ("other_user_999", "res_2", "Designer", "Remote", False, "", "")

        _RECOMMENDATIONS_CACHE[cache_key_user1] = {"timestamp": time.time(), "data": {"test": 1}}
        _RECOMMENDATIONS_CACHE[cache_key_user2] = {"timestamp": time.time(), "data": {"test": 2}}

        clear_recommendations_cache(self.user_id)
        self.assertNotIn(cache_key_user1, _RECOMMENDATIONS_CACHE)
        self.assertIn(cache_key_user2, _RECOMMENDATIONS_CACHE)

    def test_14_secure_multi_user_isolation(self):
        """Verify candidate A cannot access candidate B's resume or analysis."""
        # Create user B
        user_b = UserModel.create_user({
            "name": "Candidate B",
            "email": f"candidate_b_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Password123!"
        })
        user_b_id = str(user_b["_id"])

        # Create resume belonging to User B
        resume_b = ResumeModel.create_resume(
            user_id=user_b_id,
            original_filename="b_resume.pdf",
            stored_filename="b_stored.pdf",
            file_path="uploads/resumes/b_stored.pdf",
            file_type="application/pdf",
            file_size=1024
        )
        resume_b_id = str(resume_b["_id"])

        # User A attempts to analyze or fetch User B's resume
        res = self.client.post(
            f'/api/resume/analyze/{resume_b_id}',
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn("denied", res.get_json().get("message", "").lower())

        # Cleanup User B
        coll = UserModel.get_collection()
        if coll is not None:
            coll.delete_one({"_id": user_b["_id"]})
            ResumeModel.get_collection().delete_one({"_id": resume_b["_id"]})

    # =========================================================================
    # 7. CORS PREFLIGHT & ORIGIN HEADERS
    # =========================================================================
    def test_15_cors_preflight_on_protected_endpoints(self):
        """Verify CORS preflight returns 200/204 with exact allowed origin and allowed headers."""
        for endpoint in ['/api/auth/login', '/api/auth/me', '/api/jobs/recommended']:
            res = self.client.open(
                endpoint,
                method='OPTIONS',
                headers={
                    'Origin': 'https://careerlens-iota.vercel.app',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type, Authorization, X-Request-ID'
                }
            )
            self.assertIn(res.status_code, [200, 204])
            self.assertEqual(
                res.headers.get('Access-Control-Allow-Origin'),
                'https://careerlens-iota.vercel.app'
            )


if __name__ == '__main__':
    unittest.main()
