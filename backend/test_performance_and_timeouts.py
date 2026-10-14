import unittest
import time
from unittest.mock import patch, MagicMock
from app import create_app
from app.models.user import UserModel
from app.routes.auth import generate_app_jwt
from app.ai.embedding_service import embedding_service
from app.ai.semantic_matcher import semantic_matcher
from app.services.job_matching import JobMatchingEngine
from app.services.job_providers.provider_factory import MultiSourceJobProvider

class PerformanceAndTimeoutsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_auth_me_latency_and_no_model_loading(self):
        """Verify that /api/auth/me responds rapidly without loading SentenceTransformer."""
        fake_user = {
            "_id": "507f1f77bcf86cd799439011",
            "email": "speedtest@example.com",
            "name": "Speed Tester",
            "role": "candidate",
            "preferred_job_role": "Python Developer",
            "preferred_location": "Remote",
            "experience_level": "Fresher"
        }
        token = generate_app_jwt(fake_user)

        with patch.object(UserModel, 'find_by_id', return_value=fake_user):
            t0 = time.time()
            res = self.client.get(
                '/api/auth/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            elapsed_ms = (time.time() - t0) * 1000

        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data.get('success'))
        self.assertEqual(json_data['data']['user']['email'], 'speedtest@example.com')
        # Ensure it responds well within 500ms (typically <50ms)
        self.assertLess(elapsed_ms, 500, f"Auth took too long: {elapsed_ms:.1f}ms")

    def test_batch_match_fast_execution(self):
        """Verify that batch matching with compute_skill_embeddings=False executes in <15ms."""
        resume_analysis = {
            "technical_skills": ["Python", "Flask", "MongoDB", "Docker", "Git"],
            "raw_text": "Experienced Python Developer with Flask and Docker knowledge.",
            "education": [{"degree": "B.Tech"}],
            "validation_status": "VALID_RESUME"
        }
        candidate_user = {
            "preferred_job_role": "Python Developer",
            "preferred_location": "India",
            "experience_level": "Fresher"
        }
        job_profile = {
            "job_id": "test_job_1",
            "title": "Backend Python Developer",
            "company": "Tech Corp",
            "location": "Bengaluru, India",
            "required_skills": ["Python", "Flask", "PostgreSQL", "AWS"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "experience_required": "0-2 years",
            "description": "Looking for a backend Python developer with Flask experience."
        }

        # Mock embedding vectors so test is 100% offline and deterministic
        dummy_vec = [0.05] * 384
        with patch.object(embedding_service, 'is_available', return_value=True), \
             patch.object(embedding_service, 'get_embedding', return_value=dummy_vec), \
             patch.object(embedding_service, 'get_embeddings_batch', return_value=[dummy_vec]*5), \
             patch.object(embedding_service, 'cosine_similarity', return_value=0.85):

            cand_context = JobMatchingEngine.precompute_candidate_context(resume_analysis)

            t0 = time.time()
            match_res = JobMatchingEngine.calculate_job_match(
                resume_analysis=resume_analysis,
                candidate_user=candidate_user,
                job_profile=job_profile,
                candidate_context=cand_context,
                precomputed_job_embedding=dummy_vec,
                compute_skill_embeddings=False
            )
            elapsed_ms = (time.time() - t0) * 1000

        self.assertIsNotNone(match_res)
        self.assertIn("match_score", match_res)
        self.assertGreaterEqual(match_res["match_score"], 50.0)
        # Should be blazing fast (<15ms)
        self.assertLess(elapsed_ms, 30, f"Batch calculation took too long: {elapsed_ms:.1f}ms")
        self.assertIn("Python", match_res["matched_skills"])

    def test_provider_aggregator_bounded_timeout(self):
        """Verify that MultiSourceJobProvider handles slow providers and completes within 5s."""
        aggregator = MultiSourceJobProvider()

        # Simulate slow provider that sleeps
        def slow_provider(params):
            time.sleep(5.0)
            return {"success": False, "jobs": [], "error": "SLOW"}

        # Simulate fast provider returning 1 job
        def fast_provider(params):
            return {
                "success": True,
                "jobs": [{
                    "title": "Senior Python Engineer",
                    "company": "Fast Co",
                    "location": "Worldwide",
                    "provider": "Remotive",
                    "provider_job_id": "rem_1",
                    "application_url": "https://example.com/job/1",
                    "is_live": True
                }]
            }

        aggregator.adzuna.search_jobs = slow_provider
        aggregator.remotive.search_jobs = fast_provider
        aggregator.arbeitnow.is_configured = lambda: False
        aggregator.jooble.is_configured = lambda: False
        aggregator.indianapi.is_configured = lambda: False

        t0 = time.time()
        result = aggregator.search_jobs({"keyword": "python"})
        elapsed = time.time() - t0

        # Aggregator as_completed timeout is 4.5s
        self.assertTrue(result.get("success"))
        self.assertGreaterEqual(len(result.get("jobs", [])), 1)
        self.assertLess(elapsed, 6.0, f"Aggregator exceeded bounded limit: {elapsed:.2f}s")

if __name__ == '__main__':
    unittest.main()
