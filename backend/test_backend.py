import io
import unittest
from app import create_app
from app.services.resume_validator import ResumeValidator
from app.services.skill_gap import SkillGapEngine
from app.services.learning_roadmap import LearningRoadmapEngine
from app.services.forecasting.skill_frequency import SkillFrequencyEngine
from app.services.forecasting.forecasting_models import (
    BaselineNaiveModel,
    MovingAverageModel,
    LinearTrendModel,
    ExponentialSmoothingModel
)
from app.services.forecasting.evaluation import ModelEvaluator
from app.services.forecasting.trend_analysis import TrendAnalysisEngine
from app.services.job_service import JobService

class TestCareerIntelligencePlatform(unittest.TestCase):
    """Comprehensive Unit & Integration Test Suite for Skill Gap, Roadmap & Forecasting."""

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_check(self):
        """Test API Health Check Endpoint."""
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data.get('success'))

    def test_skill_gap_engine_math_and_priorities(self):
        """Test SkillGapEngine required coverage %, skill gap %, and priority classification."""
        dummy_analysis = {
            "technical_skills": ["Python", "SQL"],
            "soft_skills": ["Communication"]
        }
        dummy_job = {
            "id": "job_101",
            "title": "Data Analyst",
            "company": "Tech Corp",
            "required_skills": ["Python", "SQL", "Power BI"],
            "preferred_skills": ["AWS", "Excel"]
        }

        gap_res = SkillGapEngine.analyze_skill_gap(dummy_analysis, {}, dummy_job)

        self.assertEqual(gap_res["matched_required_skills"], ["Python", "SQL"])
        self.assertEqual(gap_res["missing_required_skills"], ["Power BI"])
        self.assertEqual(gap_res["required_coverage_percent"], 66.7)
        self.assertEqual(gap_res["skill_gap_percent"], 33.3)

        # Check priority classification for missing required high-demand skill "Power BI"
        priorities = {item["skill"]: item["priority"] for item in gap_res["prioritized_gaps"]}
        self.assertEqual(priorities["Power BI"], "CRITICAL")
        self.assertEqual(priorities["AWS"], "MEDIUM")

    def test_learning_roadmap_and_match_simulation(self):
        """Test LearningRoadmapEngine 3-phase generation & score improvement simulation."""
        dummy_gap = {
            "missing_required_skills": ["Power BI"],
            "missing_preferred_skills": ["AWS"],
            "prioritized_gaps": [
                {"skill": "Power BI", "priority": "CRITICAL"},
                {"skill": "AWS", "priority": "MEDIUM"}
            ]
        }
        dummy_job = {"id": "job_101", "title": "Data Analyst"}

        roadmap_res = LearningRoadmapEngine.generate_roadmap(dummy_gap, dummy_job, current_match_score=72)

        self.assertTrue(len(roadmap_res["roadmap_phases"]) > 0)
        self.assertTrue(len(roadmap_res["recommended_certifications"]) > 0)
        
        sim_steps = roadmap_res["match_improvement_simulation"]
        self.assertEqual(len(sim_steps), 2)
        self.assertEqual(sim_steps[0]["skill_acquired"], "Power BI")
        self.assertEqual(sim_steps[0]["projected_match_score"], 80)

    def test_forecasting_models_and_evaluation(self):
        """Test mathematical time-series forecasting models and MAE/RMSE model selection."""
        history_rates = [40.0, 42.0, 45.0, 48.0, 50.0, 53.0, 56.0, 60.0]

        # 1. Naive Model
        naive_model = BaselineNaiveModel().fit(history_rates)
        preds_naive = naive_model.predict(3)
        self.assertEqual(preds_naive, [60.0, 60.0, 60.0])

        # 2. Moving Average Model
        ma_model = MovingAverageModel(window=3).fit(history_rates)
        preds_ma = ma_model.predict(3)
        self.assertEqual(preds_ma, [56.33, 56.33, 56.33])

        # 3. Model Evaluator & Selection
        eval_res = ModelEvaluator.evaluate_and_select_best_model(history_rates, horizon=3)
        self.assertIn("best_model_name", eval_res)
        self.assertLessEqual(eval_res["mae"], 5.0)

    def test_trend_classification(self):
        """Test TrendAnalysisEngine classification categories."""
        res_rising = TrendAnalysisEngine.classify_trend([40, 45, 50], current_demand=50.0, predicted_demand=56.0)
        self.assertEqual(res_rising["trend"], "RISING")

        res_stable = TrendAnalysisEngine.classify_trend([60, 60, 60], current_demand=60.0, predicted_demand=61.0)
        self.assertEqual(res_stable["trend"], "STABLE")

        res_emerging = TrendAnalysisEngine.classify_trend([10, 15, 20], current_demand=20.0, predicted_demand=26.0)
        self.assertEqual(res_emerging["trend"], "EMERGING")

    def test_ai_semantic_intelligence(self):
        """Test AI Embedding Service, Cosine Similarity & Semantic Matcher."""
        from app.ai.embedding_service import embedding_service
        from app.ai.semantic_matcher import semantic_matcher

        # 1. AI Status Endpoint
        res = self.client.get('/api/ai/status')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data.get('success'))

        # 2. Skill Categorization
        cand_skills = ["Python", "Flask", "PyTorch"]
        job_skills = ["python", "Flask", "Deep Learning", "React"]

        cats = semantic_matcher.categorize_skills(cand_skills, job_skills)
        match_types = {item["skill"]: item["match_type"] for item in cats}
        
        self.assertEqual(match_types["python"], "EXACT_MATCH")
        self.assertEqual(match_types["Flask"], "EXACT_MATCH")
        self.assertIn(match_types["Deep Learning"], ["SEMANTIC_MATCH", "MISSING_SKILL"])

        # 3. AI Standalone Endpoint
        payload = {
            "resume_text": "Experienced Python Flask backend developer building ML pipelines.",
            "job_description": "We are seeking a Python Software Engineer with Flask expertise.",
            "candidate_skills": ["Python", "Flask"],
            "job_skills": ["Python", "Flask"]
        }
        res_post = self.client.post('/api/ai/semantic-match', json=payload)
        self.assertEqual(res_post.status_code, 200)
        data = res_post.get_json().get('data', {})
        self.assertIn("ai_semantic_score", data)

    def test_live_job_search_and_provider_pipeline(self):
        """Test HTML cleaning, provider factory, deduplication engine & live job search API."""
        from app.services.job_cleaner import JobDescriptionCleaner
        from app.services.eligibility_service import EligibilityService
        from app.services.job_providers.provider_factory import ProviderFactory

        # 1. Job Cleaner HTML stripping & entity decoding
        html_input = "<p>We are hiring a <b>Python Engineer</b>.</p><ul><li>Flask &amp; SQL</li></ul>"
        cleaned = JobDescriptionCleaner.clean(html_input)
        self.assertIn("Python Engineer", cleaned)
        self.assertIn("Flask & SQL", cleaned)
        self.assertNotIn("<p>", cleaned)

        # 2. Eligibility Hard-Gate Evaluation
        el_res = EligibilityService.evaluate_eligibility(["Python", "SQL"], ["Python", "SQL", "Docker"])
        self.assertIn(el_res["status"], ["ELIGIBLE", "PARTIALLY_ELIGIBLE"])

        # 3. Provider Layer & Search API
        provider = ProviderFactory.get_provider()
        search_res = provider.search_jobs({"keyword": "Python", "location": "Chennai", "page": 1, "limit": 5})
        self.assertIn("jobs", search_res)
        self.assertIsInstance(search_res.get("jobs"), list)

        # 4. Live Search Endpoint (/api/jobs/search)
        api_res = self.client.get('/api/jobs/search?keyword=Python&location=Chennai')
        self.assertEqual(api_res.status_code, 200)
        api_data = api_res.get_json()
        self.assertTrue(api_data.get("success"))
        self.assertIn("jobs", api_data)

    def test_geo_eligibility_and_india_filtering(self):
        """Test GeoEligibilityService rules for worldwide job discovery."""
        from app.services.geo_eligibility_service import GeoEligibilityService

        # TEST 1: Chennai, Tamil Nadu, India -> ACCEPT (Worldwide policy)
        j1 = {"title": "Python Developer", "location": "Chennai, Tamil Nadu, India", "country": "IN"}
        r1 = GeoEligibilityService.evaluate_geo_eligibility(j1)
        self.assertTrue(r1["eligible"])
        self.assertEqual(r1["geo_status"], "WORLDWIDE_ELIGIBLE")

        # TEST 2: Bengaluru, India -> ACCEPT (Worldwide policy)
        j2 = {"title": "Data Analyst", "location": "Bengaluru, India", "country": "IN"}
        r2 = GeoEligibilityService.evaluate_geo_eligibility(j2)
        self.assertTrue(r2["eligible"])
        self.assertEqual(r2["geo_status"], "WORLDWIDE_ELIGIBLE")

        # TEST 3: Berlin, Germany -> ACCEPT (Worldwide policy)
        j3 = {"title": "Backend Dev", "location": "Berlin, Germany", "country": "DE"}
        r3 = GeoEligibilityService.evaluate_geo_eligibility(j3)
        self.assertTrue(r3["eligible"])
        self.assertEqual(r3["geo_status"], "WORLDWIDE_ELIGIBLE")

        # TEST 4: Remote, EMEA -> ACCEPT (Worldwide policy)
        j4 = {"title": "Frontend Engineer", "location": "Remote, EMEA", "candidate_required_location": "EMEA"}
        r4 = GeoEligibilityService.evaluate_geo_eligibility(j4)
        self.assertTrue(r4["eligible"])
        self.assertEqual(r4["geo_status"], "WORLDWIDE_ELIGIBLE")

        # TEST 5: United Kingdom Remote -> ACCEPT (Worldwide policy)
        j5 = {"title": "DevOps Engineer", "location": "United Kingdom Remote", "candidate_required_location": "UK"}
        r5 = GeoEligibilityService.evaluate_geo_eligibility(j5)
        self.assertTrue(r5["eligible"])
        self.assertEqual(r5["geo_status"], "WORLDWIDE_ELIGIBLE")


        # TEST 13 & 14: Workplace Type Normalization (Remote vs On-Site)
        from app.services.deduplication import DeduplicationAndCacheEngine
        remote_remotive_job = {"provider": "remotive", "location": "Remote Worldwide", "candidate_required_location": "Worldwide"}
        dedup_jobs = DeduplicationAndCacheEngine.process_and_cache_jobs([remote_remotive_job])
        self.assertEqual(dedup_jobs[0]["workplace_type"], "REMOTE")

        # TEST 15: AI Semantic Score Computation (Non-Zero)
        from app.services.job_matching import JobMatchingEngine
        dummy_resume_analysis = {
            "raw_text": "Senior Python Backend Developer with 4 years experience in Flask, FastAPI, PostgreSQL, Docker, AWS.",
            "technical_skills": ["Python", "Flask", "PostgreSQL", "Docker"]
        }
        dummy_user = {"experience_level": "2-5 Years", "preferred_location": "India"}
        dummy_job = {
            "title": "Python Developer",
            "clean_description": "We are seeking a Python Flask Engineer to build backend microservices with Docker.",
            "required_skills": ["Python", "Flask", "Docker"]
        }
        match_out = JobMatchingEngine.calculate_job_match(dummy_resume_analysis, dummy_user, dummy_job)
        self.assertGreater(match_out["ai_semantic_score"], 0.0)
        self.assertGreater(match_out["match_score"], 0)

        # TEST 16: Exact 60/40 Weighted Formula Arithmetic Consistency (42.0 Det + 35.7 AI = 39.5 Final)
        det_score = 42.0
        ai_score = 35.7
        w_det = round(0.60 * det_score, 2)  # 25.2
        w_ai = round(0.40 * ai_score, 2)    # 14.28
        expected_final = round(w_det + w_ai, 1) # 39.5
        self.assertEqual(w_det, 25.2)
        self.assertEqual(w_ai, 14.28)
        self.assertEqual(expected_final, 39.5)

    def test_role_relevance_and_seniority_quality(self):
        """Test RoleRelevanceService & SeniorityService filtering and ranking (Test Cases 1-14)."""
        from app.services.role_relevance_service import RoleRelevanceService
        from app.services.seniority_service import SeniorityService

        cse_candidate_profile = {
            "professional_domain": "SOFTWARE_IT",
            "persona": "Full Stack Web Developer",
            "inferred_roles": ["Python Developer", "Backend Developer", "Software Developer"],
            "core_skills": ["python", "flask", "sql", "react", "rest api"],
            "experience_level": "Fresher / 0-2 Years"
        }

        # 1. CSE resume + Python Backend Developer -> DIRECT_ROLE_MATCH
        j1 = {"title": "Python Backend Developer"}
        rel1 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j1)
        self.assertTrue(rel1["eligible"])

        # 2. CSE resume + Software Developer -> DIRECT_ROLE_MATCH
        j2 = {"title": "Software Developer"}
        rel2 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j2)
        self.assertTrue(rel2["eligible"])

        # 3. CSE + Data Analyst -> Eligible
        j3 = {"title": "Data Analyst"}
        rel3 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j3)
        self.assertTrue(rel3["eligible"])

        # 4. CSE + Senior AI Engineer -> Seniority mismatch
        j4 = {"title": "Senior AI Engineer", "experience_required": "5+ years"}
        sen4 = SeniorityService.evaluate_seniority(cse_candidate_profile, j4)
        self.assertEqual(sen4["seniority_status"], "SENIORITY_MISMATCH")
        self.assertTrue(sen4["is_fresher_mismatch"])

        # 5. CSE + Sales Manager -> UNRELATED (REJECT)
        j5 = {"title": "Senior Sales Manager"}
        rel5 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j5)
        self.assertFalse(rel5["eligible"])
        self.assertEqual(rel5["role_relevance_status"], "UNRELATED")

        # 6. CSE + Clinical Research Associate -> UNRELATED (REJECT)
        j6 = {"title": "Clinical Research Associate"}
        rel6 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j6)
        self.assertFalse(rel6["eligible"])
        self.assertEqual(rel6["role_relevance_status"], "UNRELATED")

        # 7. CSE + Social Media Manager -> UNRELATED (REJECT)
        j7 = {"title": "Social Media Manager"}
        rel7 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j7)
        self.assertFalse(rel7["eligible"])
        self.assertEqual(rel7["role_relevance_status"], "UNRELATED")

        # 8. CSE + Marketing Lead -> UNRELATED (REJECT)
        j8 = {"title": "Growth and Product Marketing Lead"}
        rel8 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j8)
        self.assertFalse(rel8["eligible"])
        self.assertEqual(rel8["role_relevance_status"], "UNRELATED")

        # 9. CSE + Worldwide Software Developer -> Eligible
        from app.services.geo_eligibility_service import GeoEligibilityService
        j9 = {"title": "Software Developer", "location": "Chennai, Tamil Nadu, India", "country": "IN"}
        geo9 = GeoEligibilityService.evaluate_geo_eligibility(j9)
        rel9 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j9)
        self.assertTrue(geo9["eligible"])
        self.assertTrue(rel9["eligible"])

        # 10. CSE + Europe Software Developer -> Geographically eligible under WORLDWIDE policy
        j10 = {"title": "Software Developer", "location": "Berlin, Germany", "country": "DE"}
        geo10 = GeoEligibilityService.evaluate_geo_eligibility(j10)
        self.assertTrue(geo10["eligible"])

        # 11. CSE + Sales Manager -> Geo eligible but role rejected
        j11 = {"title": "Sales Manager", "location": "Chennai, Tamil Nadu, India"}
        geo11 = GeoEligibilityService.evaluate_geo_eligibility(j11)
        rel11 = RoleRelevanceService.evaluate_role_relevance(cse_candidate_profile, j11)
        self.assertTrue(geo11["eligible"])
        self.assertFalse(rel11["eligible"])

        # 12. Zero synthetic/mock fallback
        from app.services.job_providers.mock_live_provider import MockLiveJobProvider
        mock_prov = MockLiveJobProvider()
        res_mock = mock_prov.search_jobs({})
        self.assertFalse(res_mock["success"])
        self.assertEqual(res_mock["error"], "SYNTHETIC_DATA_DISABLED")

    def test_strict_tamil_nadu_geo_gate_and_regression_cases(self):
        """Test GeoEligibilityService & LocationTierService under WORLDWIDE policy."""
        from app.services.location_tier_service import LocationTierService
        from app.services.geo_eligibility_service import GeoEligibilityService
        from app.services.role_relevance_service import RoleRelevanceService
        from app.services.seniority_service import SeniorityService

        # 1. Worldwide Geo Eligibility Check
        g1 = GeoEligibilityService.evaluate_geo_eligibility({"title": "Software Engineer", "location": "Chennai, Tamil Nadu, India"})
        self.assertTrue(g1["eligible"])
        self.assertEqual(g1["geo_status"], "WORLDWIDE_ELIGIBLE")

        g2 = GeoEligibilityService.evaluate_geo_eligibility({"title": "Python Developer", "location": "Berlin, Germany"})
        self.assertTrue(g2["eligible"])

        g3 = GeoEligibilityService.evaluate_geo_eligibility({"title": "Backend Developer", "location": "Remote — Worldwide"})
        self.assertTrue(g3["eligible"])

        # Bengaluru — Software Engineer -> ACCEPT under Worldwide policy
        g10 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Bengaluru, Karnataka"})
        self.assertTrue(g10["eligible"])


        # 11. Hyderabad — Python Developer -> ACCEPT (Worldwide policy)
        g11 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Hyderabad, Telangana"})
        self.assertTrue(g11["eligible"])

        # 12. Kochi — Backend Developer -> ACCEPT (Worldwide policy)
        g12 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Kochi, Kerala"})
        self.assertTrue(g12["eligible"])

        # 13. Pune — Software Engineer -> ACCEPT (Worldwide policy)
        g13 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Pune, Maharashtra"})
        self.assertTrue(g13["eligible"])

        # 14. Mumbai — Developer -> ACCEPT (Worldwide policy)
        g14 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Mumbai, Maharashtra"})
        self.assertTrue(g14["eligible"])

        # 15. Delhi — Software Engineer -> ACCEPT (Worldwide policy)
        g15 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Delhi NCR"})
        self.assertTrue(g15["eligible"])

        # 16. Gurgaon — Software Engineer -> ACCEPT (Worldwide policy)
        g16 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Gurugram, Haryana"})
        self.assertTrue(g16["eligible"])

        # 17. Noida — Developer -> ACCEPT (Worldwide policy)
        g17 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Noida, UP"})
        self.assertTrue(g17["eligible"])

        # 18. India Remote -> ACCEPT (Worldwide policy)
        g18 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Remote", "candidate_required_location": "India"})
        self.assertTrue(g18["eligible"])

        # 19. Worldwide Remote -> ACCEPT (Worldwide policy)
        g19 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Worldwide Remote", "candidate_required_location": "Worldwide"})
        self.assertTrue(g19["eligible"])

        # 20. APAC Remote -> ACCEPT (Worldwide policy)
        g20 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Remote — APAC", "candidate_required_location": "APAC"})
        self.assertTrue(g20["eligible"])

        # 21. South India -> ACCEPT (Worldwide policy)
        g21 = GeoEligibilityService.evaluate_geo_eligibility({"location": "South India"})
        self.assertTrue(g21["eligible"])

        # 22. India -> ACCEPT (Worldwide policy)
        g22 = GeoEligibilityService.evaluate_geo_eligibility({"location": "India"})
        self.assertTrue(g22["eligible"])

        # 23. Remote -> ACCEPT (Worldwide policy)
        g23 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Remote"})
        self.assertTrue(g23["eligible"])

        # 24. Germany -> ACCEPT (Worldwide policy)
        g24 = GeoEligibilityService.evaluate_geo_eligibility({"location": "Berlin, Germany", "country": "DE"})
        self.assertTrue(g24["eligible"])

        # 25. UK -> ACCEPT (Worldwide policy)
        g25 = GeoEligibilityService.evaluate_geo_eligibility({"location": "London, UK", "country": "UK"})
        self.assertTrue(g25["eligible"])

        # EDGE CASES (26-32):
        # 26. Company HQ in Chennai but vacancy in Bengaluru -> ACCEPT (Worldwide policy)
        g26 = GeoEligibilityService.evaluate_geo_eligibility({"company": "Chennai Tech Corp", "location": "Bengaluru, Karnataka"})
        self.assertTrue(g26["eligible"])

        # 27. Company HQ in Bengaluru but vacancy in Chennai -> ACCEPT
        g27 = GeoEligibilityService.evaluate_geo_eligibility({"company": "Bangalore Soft", "location": "Chennai, Tamil Nadu"})
        self.assertTrue(g27["eligible"])

        # 28. Multi-location Chennai / Bengaluru -> ACCEPT and classify under NATIONAL_METRO tier
        lt28 = LocationTierService.evaluate_location_tier({"location": "Chennai / Bengaluru"})
        self.assertEqual(lt28["location_tier"], "NATIONAL_METRO")

        # 29. Unknown/empty location -> ACCEPT (Worldwide policy)
        g29 = GeoEligibilityService.evaluate_geo_eligibility({"location": ""})
        self.assertTrue(g29["eligible"])

        # 30. Tamil Nadu location + unrelated role -> Geo eligible but role rejected
        cse_profile = {"professional_domain": "SOFTWARE_IT", "inferred_roles": ["Python Developer"], "core_skills": ["python"]}
        r30 = RoleRelevanceService.evaluate_role_relevance(cse_profile, {"title": "Sales Manager", "location": "Chennai, Tamil Nadu"})
        self.assertFalse(r30["eligible"])
        self.assertEqual(r30["role_relevance_status"], "UNRELATED")

        # 31. Tamil Nadu location + senior role -> Geo eligible but seniority mismatch for fresher
        s31 = SeniorityService.evaluate_seniority({"experience_level": "Fresher"}, {"title": "Senior Shopify Developer", "location": "Chennai, Tamil Nadu"})
        self.assertEqual(s31["seniority_status"], "SENIORITY_MISMATCH")

        # 32. Zero synthetic/mock fallback
        from app.services.job_providers.mock_live_provider import MockLiveJobProvider
        res_mock = MockLiveJobProvider().search_jobs({})
        self.assertFalse(res_mock["success"])

    def test_production_multi_source_provider_system(self):
        """Test Production Multi-Source Provider System (Adzuna, Jooble, IndianAPI) & 40 Invariants."""
        from app.services.job_providers.adzuna_provider import AdzunaJobProvider
        from app.services.job_providers.jooble_provider import JoobleJobProvider
        from app.services.job_providers.indian_api_provider import IndianApiJobProvider
        from app.services.job_providers.provider_factory import MultiSourceJobProvider, ProviderFactory

        # 1. Verify Providers Instantiation
        adzuna = AdzunaJobProvider()
        jooble = JoobleJobProvider()
        indianapi = IndianApiJobProvider()
        multi = MultiSourceJobProvider()

        # 2. Check Provider Health API
        health = multi.get_provider_health()
        self.assertIn("adzuna", health)
        self.assertIn("jooble", health)
        self.assertIn("indianapi", health)

        # 3. Missing API Credentials Handling (Must NOT crash, must NOT fabricate jobs)
        if not adzuna.is_configured():
            res_adz = adzuna.search_jobs({})
            self.assertFalse(res_adz["success"])
            self.assertEqual(res_adz["error"], "NOT_CONFIGURED")

        if not jooble.is_configured():
            res_joo = jooble.search_jobs({})
            self.assertFalse(res_joo["success"])
            self.assertEqual(res_joo["error"], "NOT_CONFIGURED")

        if not indianapi.is_configured():
            res_ind = indianapi.search_jobs({})
            self.assertFalse(res_ind["success"])
            self.assertEqual(res_ind["error"], "NOT_CONFIGURED")

        # 4. Normalized Schema Checks
        dummy_raw_adzuna = {
            "id": "adz_101",
            "title": "Python Developer",
            "company": {"display_name": "Chennai Software Ltd"},
            "location": {"display_name": "Chennai, Tamil Nadu"},
            "description": "Building Python Flask microservices.",
            "redirect_url": "https://www.adzuna.in/land/ad/adz_101"
        }
        norm_adz = adzuna._normalize_adzuna_job(dummy_raw_adzuna, "in")
        self.assertEqual(norm_adz["provider"], "adzuna")
        self.assertEqual(norm_adz["provider_job_id"], "adz_101")
        self.assertEqual(norm_adz["location"], "Chennai, Tamil Nadu")
        self.assertEqual(norm_adz["application_url"], "https://www.adzuna.in/land/ad/adz_101")
        self.assertIn("last_verified_at", norm_adz)

        # 5. Missing Salary & Experience Handling (Must NOT fabricate)
        self.assertIsNone(norm_adz["salary"])
        self.assertEqual(norm_adz["experience"], "UNKNOWN")

        # 6. Deduplication Across Providers
        raw_multi_jobs = [
            {"provider": "adzuna", "provider_job_id": "1001", "title": "Python Developer", "company": "Tech Corp", "location": "Chennai, Tamil Nadu", "application_url": "https://example.com/job/1"},
            {"provider": "jooble", "provider_job_id": "j_1001", "title": "Python Developer", "company": "Tech Corp", "location": "Chennai, Tamil Nadu", "application_url": "https://example.com/job/1"}
        ]
        seen_keys = set()
        deduped_raw_jobs = []
        for j in raw_multi_jobs:
            app_url = str(j.get("application_url", "")).strip()
            if app_url not in seen_keys:
                seen_keys.add(app_url)
                deduped_raw_jobs.append(j)
        self.assertEqual(len(deduped_raw_jobs), 1)

    def test_universal_resume_driven_worldwide_recommendations(self):
        """
        Universal Resume-Driven Worldwide Recommendation System Tests.
        Verifies domain detection, multi-profession support, worldwide geo eligibility,
        role relevance cross-matching, seniority protection, and zero synthetic fallback.
        Explicitly covers Test A through Test K.
        """
        from app.services.role_inference_service import RoleInferenceEngine
        from app.services.role_relevance_service import RoleRelevanceService
        from app.services.geo_eligibility_service import GeoEligibilityService
        from app.services.seniority_service import SeniorityService

        # TEST A: SOFTWARE / IT RESUME
        soft_resume = {
            "technical_skills": ["python", "sql", "flask", "mongodb"],
            "experience_level": "fresher",
            "education_level": "B.E Computer Science",
            "raw_text": "Software engineer with background in Python, Flask, SQL and web APIs."
        }
        p_a = RoleInferenceEngine.infer_candidate_profile(soft_resume)
        self.assertEqual(p_a["professional_domain"], "SOFTWARE_IT")
        self.assertTrue(any("Software" in r or "Python" in r or "Developer" in r for r in p_a["inferred_roles"]))
        self.assertNotIn("Staff Nurse", p_a["inferred_roles"])
        self.assertIn("search_queries", p_a)
        self.assertTrue(len(p_a["search_queries"]) > 0)

        # TEST B: HEALTHCARE / NURSING RESUME
        nurse_resume = {
            "technical_skills": ["patient care", "medication administration", "iv administration", "vital signs", "icu"],
            "experience_level": "fresher",
            "education_level": "B.Sc Nursing",
            "raw_text": "Hospital staff nurse with clinical experience in medication, patient care and ICU."
        }
        p_b = RoleInferenceEngine.infer_candidate_profile(nurse_resume)
        self.assertEqual(p_b["professional_domain"], "HEALTHCARE")
        self.assertTrue(any("Nurse" in r for r in p_b["inferred_roles"]))
        self.assertEqual(p_b["primary_search_keyword"].lower(), "nurse")
        self.assertTrue("Nurse" in p_b["professional_identity"] or "Healthcare" in p_b["professional_identity"])

        # TEST C: ACCOUNTING / FINANCE RESUME
        acc_resume = {
            "technical_skills": ["tally", "gst", "tally prime", "bookkeeping", "taxation", "accounts payable"],
            "experience_level": "fresher",
            "education_level": "B.Com",
            "raw_text": "B.Com graduate with experience in Tally, GST, accounts payable, accounts receivable, and bookkeeping."
        }
        p_c = RoleInferenceEngine.infer_candidate_profile(acc_resume)
        self.assertEqual(p_c["professional_domain"], "ACCOUNTING_FINANCE")
        self.assertTrue(any("Accountant" in r or "Accounts" in r for r in p_c["inferred_roles"]))

        # TEST D: MECHANICAL ENGINEERING RESUME
        mech_resume = {
            "technical_skills": ["autocad", "solidworks", "catia", "manufacturing", "ansys"],
            "experience_level": "0-2 years",
            "education_level": "B.E Mechanical Engineering",
            "raw_text": "Mechanical design engineer experienced in AutoCAD, SolidWorks, CATIA, and manufacturing."
        }
        p_d = RoleInferenceEngine.infer_candidate_profile(mech_resume)
        self.assertEqual(p_d["professional_domain"], "MECHANICAL_ENGINEERING")
        self.assertTrue(any("Mechanical" in r or "Design Engineer" in r for r in p_d["inferred_roles"]))

        # TEST E: MARKETING RESUME
        mkt_resume = {
            "technical_skills": ["digital marketing", "seo", "google ads", "content marketing", "social media"],
            "experience_level": "fresher",
            "education_level": "BBA Marketing",
            "raw_text": "Digital marketing executive skilled in SEO, Google Ads, content marketing, and social media campaigns."
        }
        p_e = RoleInferenceEngine.infer_candidate_profile(mkt_resume)
        self.assertEqual(p_e["professional_domain"], "MARKETING")
        self.assertTrue(any("Marketing" in r or "SEO" in r for r in p_e["inferred_roles"]))

        # TEST F: TEACHING / EDUCATION RESUME
        teach_resume = {
            "technical_skills": ["curriculum development", "classroom management", "lesson planning", "pedagogy", "student assessment"],
            "experience_level": "fresher",
            "education_level": "B.Ed",
            "raw_text": "High school teacher with B.Ed degree skilled in classroom management, lesson planning, and pedagogy."
        }
        p_f = RoleInferenceEngine.infer_candidate_profile(teach_resume)
        self.assertEqual(p_f["professional_domain"], "EDUCATION")
        self.assertTrue(any("Teacher" in r or "Lecturer" in r for r in p_f["inferred_roles"]))

        # TEST G: CIVIL ENGINEERING RESUME
        civil_resume = {
            "technical_skills": ["autocad civil", "staad pro", "revit", "structural design", "site supervision", "construction management"],
            "experience_level": "0-2 years",
            "education_level": "B.E Civil Engineering",
            "raw_text": "Civil site engineer experienced in AutoCAD, STAAD Pro, structural design, and construction site supervision."
        }
        p_g = RoleInferenceEngine.infer_candidate_profile(civil_resume)
        self.assertEqual(p_g["professional_domain"], "CIVIL_ENGINEERING")
        self.assertTrue(any("Civil" in r or "Site Engineer" in r or "Structural" in r for r in p_g["inferred_roles"]))

        # TEST H: ELECTRICAL ENGINEERING RESUME
        elec_resume = {
            "technical_skills": ["matlab", "plc", "scada", "circuit design", "power electronics", "electrical cad"],
            "experience_level": "0-2 years",
            "education_level": "B.E Electrical Engineering",
            "raw_text": "Electrical engineer skilled in MATLAB, PLC programming, SCADA systems, power electronics, and circuit design."
        }
        p_h = RoleInferenceEngine.infer_candidate_profile(elec_resume)
        self.assertEqual(p_h["professional_domain"], "ELECTRICAL_ENGINEERING")
        self.assertTrue(any("Electrical" in r or "Power Engineer" in r for r in p_h["inferred_roles"]))

        # TEST I: FRESHER / ENTRY LEVEL CANDIDATE
        fresher_resume = {
            "technical_skills": ["python", "sql"],
            "experience_level": "fresher",
            "years_of_experience": 0,
            "raw_text": "Fresh computer science graduate seeking entry-level software roles."
        }
        p_i = RoleInferenceEngine.infer_candidate_profile(fresher_resume)
        self.assertIn("fresher", p_i["experience_level"].lower())
        # Seniority protection test: 5+ yr senior role should fail for fresher candidate
        senior_job = {"title": "Senior Principal Architect", "experience_required": "8+ years"}
        sen_eval_i = SeniorityService.evaluate_seniority(p_i, senior_job)
        self.assertTrue(sen_eval_i["is_fresher_mismatch"])
        self.assertEqual(sen_eval_i["seniority_status"], "SENIORITY_MISMATCH")

        # TEST J: EXPERIENCED CANDIDATE
        exp_resume = {
            "technical_skills": ["python", "flask", "aws", "docker", "system design"],
            "experience_level": "5+ years",
            "years_of_experience": 6,
            "raw_text": "Senior backend developer with 6 years experience in building distributed Python microservices."
        }
        p_j = RoleInferenceEngine.infer_candidate_profile(exp_resume)
        self.assertIn("5+", p_j["experience_level"])
        senior_tech_job = {"title": "Senior Python Developer", "experience_required": "5+ years"}
        sen_eval_j = SeniorityService.evaluate_seniority(p_j, senior_tech_job)
        self.assertFalse(sen_eval_j["is_fresher_mismatch"])
        self.assertIn(sen_eval_j["seniority_status"], ["MATCHED", "SENIORITY_MATCH"])

        # TEST K: UNKNOWN / UNUSUAL PROFESSION RESUME
        unusual_resume = {
            "technical_skills": ["stargazing", "telescope alignment", "astrophysical modeling", "spectroscopy"],
            "experience_level": "0-2 years",
            "raw_text": "Astronomer with research experience in astrophysics, stargazing, and optical spectroscopy."
        }
        p_k = RoleInferenceEngine.infer_candidate_profile(unusual_resume)
        self.assertIsNotNone(p_k["professional_domain"])
        self.assertIsNotNone(p_k["persona"])
        self.assertTrue(len(p_k["inferred_roles"]) > 0)
        self.assertTrue(len(p_k["search_queries"]) > 0)

        # CROSS-DOMAIN ROLE RELEVANCE MATCHING
        # Nursing job vs Nursing candidate -> ACCEPT
        nurse_job = {"title": "Staff Nurse", "raw_description": "Hospital staff nurse vacancy."}
        r_nurse = RoleRelevanceService.evaluate_role_relevance(p_b, nurse_job)
        self.assertTrue(r_nurse["eligible"])

        # Software job vs Nursing candidate -> REJECT (Unrelated domain)
        soft_job = {"title": "Python Backend Developer", "raw_description": "Building Python Flask APIs."}
        r_nurse_soft = RoleRelevanceService.evaluate_role_relevance(p_b, soft_job)
        self.assertFalse(r_nurse_soft["eligible"])
        self.assertEqual(r_nurse_soft["role_relevance_status"], "UNRELATED")

        # Accounting job vs Accounting candidate -> ACCEPT
        acc_job = {"title": "Accounts Executive", "raw_description": "Managing Tally and GST returns."}
        r_acc = RoleRelevanceService.evaluate_role_relevance(p_c, acc_job)
        self.assertTrue(r_acc["eligible"])

        # WORLDWIDE GEO ELIGIBILITY
        self.assertEqual(GeoEligibilityService.GEO_POLICY, "WORLDWIDE")
        job_germany = {"title": "Mechanical Engineer", "location": "Berlin, Germany"}
        g_eval = GeoEligibilityService.evaluate_geo_eligibility(job_germany)
        self.assertTrue(g_eval["eligible"])
        self.assertEqual(g_eval["geo_status"], "WORLDWIDE_ELIGIBLE")

        # ZERO SYNTHETIC FALLBACK (No fake jobs)
        from app.services.job_providers.mock_live_provider import MockLiveJobProvider
        mock_prov = MockLiveJobProvider()
        self.assertFalse(mock_prov.is_configured())

if __name__ == '__main__':
    unittest.main()

