import logging
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.routes.auth import jwt_required
from app.services.job_service import JobService
from app.services.job_matching import JobMatchingEngine
from app.models.resume import ResumeModel
from app.models.resume_analysis import ResumeAnalysisModel
from app.models.user import UserModel
from app.models.job_match import JobMatchModel
from app.services.role_inference_service import RoleInferenceEngine
from app.services.job_providers.provider_factory import ProviderFactory
from app.services.deduplication import DeduplicationAndCacheEngine
from app.services.eligibility_service import EligibilityService
from app.services.geo_eligibility_service import GeoEligibilityService

from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)

# High-performance in-memory recommendations cache
_RECOMMENDATIONS_CACHE = {}
_RECOMMENDATIONS_CACHE_TTL = 1800  # 30 minutes

def clear_recommendations_cache(target_user_id=None):
    global _RECOMMENDATIONS_CACHE
    if target_user_id:
        _RECOMMENDATIONS_CACHE = {k: v for k, v in _RECOMMENDATIONS_CACHE.items() if k[0] != str(target_user_id)}
    else:
        _RECOMMENDATIONS_CACHE.clear()

job_bp = Blueprint('job', __name__)

@job_bp.route('/all', methods=['GET'])
def get_all_jobs():
    """Get all dataset jobs."""
    jobs = JobService.get_all_jobs()
    return jsonify({
        "success": True,
        "data": {
            "jobs": jobs,
            "total": len(jobs)
        }
    }), 200

@job_bp.route('/recommended', methods=['GET'])
@jwt_required
def get_recommended_jobs():
    """
    GET /api/jobs/recommended
    Resume-Driven Automated Live Job Recommendation Endpoint.
    Analyzes candidate's uploaded resume, infers profile & target roles,
    queries live vacancy APIs, enforces India geo-eligibility,
    and returns 3 relevance buckets with 60/40 AI match scores.
    """
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
        
    user_id = str(user.get("_id", user.get("id")))
    try:

        # 1. HARD GATE: Fetch user's uploaded resumes & locate latest valid resume
        my_resumes = ResumeModel.find_by_user(user_id)
        if not my_resumes or len(my_resumes) == 0:
            return jsonify({
                "success": False,
                "status": "RESUME_REQUIRED",
                "message": "Please upload your resume to unlock personalized live job recommendations."
            }), 400

        analysis_doc = None
        latest_resume_doc = None

        for r_doc in my_resumes:
            r_id = str(r_doc.get("_id"))
            a_doc = ResumeAnalysisModel.find_by_resume_id(r_id)
            if not a_doc:
                from app.routes.resume import execute_resume_analysis_pipeline
                a_doc = execute_resume_analysis_pipeline(r_doc, user_id)

            if a_doc and isinstance(a_doc, dict) and a_doc.get("validation_status") == "VALID_RESUME" and a_doc.get("resume_score") is not None:
                analysis_doc = a_doc
                latest_resume_doc = r_doc
                break

        if not analysis_doc or not latest_resume_doc:
            return jsonify({
                "success": False,
                "status": "RESUME_REQUIRED",
                "message": "Job recommendations are unavailable because no valid analyzed resume was found. Please upload a valid text-based resume.",
                "error": "INVALID_DOCUMENT"
            }), 400

        latest_resume_id = str(latest_resume_doc.get("_id"))
        analysis_json = ResumeAnalysisModel.to_json(analysis_doc)

        user_json = UserModel.to_json(user)

        # 3. Candidate Profile & Location Resolution Priority
        candidate_profile = RoleInferenceEngine.infer_candidate_profile(analysis_json)
        candidate_skills = analysis_json.get("technical_skills", [])

        # Read optional user refining query params
        role_param = request.args.get('role', '').strip()
        location_param = request.args.get('location', '').strip()
        remote_param = request.args.get('remote', '').lower()
        is_remote = True if remote_param in ['true', '1', 'yes'] else (False if remote_param in ['false', '0', 'no'] else None)
        experience_param = request.args.get('experience', '').strip()
        min_match_param = request.args.get('min_match', '')
        force_refresh = request.args.get('refresh', '').lower() in ['true', '1', 'yes']

        # Target Role Resolution Priority:
        # 1. User-selected target role from UI query param
        # 2. User profile preferred_job_role
        # 3. Resume analysis primary_search_keyword / inferred_roles
        user_pref_role = (user_json.get('preferred_job_role') or '').strip()
        resume_primary_kw = (candidate_profile.get("primary_search_keyword") or '').strip()
        inferred_roles = candidate_profile.get("inferred_roles", [])
        first_inferred_role = inferred_roles[0].strip() if inferred_roles else ''

        target_role = role_param or user_pref_role or resume_primary_kw or first_inferred_role
        if target_role:
            user_json['preferred_job_role'] = target_role

        # Fast in-memory cache check: if user already has computed recommendations with these params, return immediately (0ms)
        cache_key = (user_id, latest_resume_id, target_role, location_param, is_remote, experience_param, min_match_param)
        now_ts = time.time()
        if not force_refresh and cache_key in _RECOMMENDATIONS_CACHE:
            cache_entry = _RECOMMENDATIONS_CACHE[cache_key]
            if now_ts - cache_entry['timestamp'] < _RECOMMENDATIONS_CACHE_TTL:
                logger.info(f"Serving live recommendations from memory cache for user {user_id} (role={target_role})")
                return jsonify(cache_entry['data']), 200

        # Location Resolution Priority: 1. UI Selected -> 2. User Profile -> 3. Resume -> 4. Default "India"
        user_pref_loc = (user_json.get('preferred_location') or user_json.get('location') or '').strip()
        resume_loc = (analysis_json.get('location') or candidate_profile.get('location') or '').strip()

        resolved_location = location_param or user_pref_loc or resume_loc or "India"

        target_country = "IN"
        if location_param and not any(k in location_param.lower() for k in ["india", "in", "chennai", "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", "delhi", "noida", "gurgaon"]):
            if not any(g in location_param.lower() for g in ["remote", "worldwide", "global"]):
                target_country = "GLOBAL"

        # Build controlled search queries dynamically:
        # If target_role is explicitly identified, focus directly on that role
        if target_role:
            search_keywords = [target_role]
        else:
            profile_queries = candidate_profile.get("search_queries", [])
            primary = candidate_profile.get("primary_search_keyword")
            inferred = candidate_profile.get("inferred_roles", [])

            search_keywords = []
            for q in profile_queries:
                if q and q not in search_keywords:
                    search_keywords.append(q)
            if primary and primary not in search_keywords:
                search_keywords.append(primary)
            for inf in inferred:
                if inf and inf not in search_keywords:
                    search_keywords.append(inf)

            if not search_keywords:
                search_keywords = [candidate_profile.get("professional_identity", "Professional")]
            # Prioritize top 2 most targeted queries to keep latency low
            search_keywords = search_keywords[:2]

        # Target search locations: under GEO_POLICY = WORLDWIDE, query broad/location-agnostic or candidate preferred location
        loc_targets = [location_param] if location_param else [""]

        # 4. Multi-Source Live Provider Execution (Adzuna + Jooble + IndianAPI) - Parallelized via ThreadPoolExecutor
        provider = ProviderFactory.get_provider()
        raw_live_jobs = []
        seen_job_keys = set()
        provider_status = {}
        providers_used = set()

        def _fetch_provider(kw, loc_target):
            search_params = {
                'keyword': kw,
                'location': loc_target,
                'country': target_country,
                'remote': is_remote,
                'experience': experience_param,
                'limit': 50
            }
            try:
                return provider.search_jobs(search_params)
            except Exception as e:
                logger.error(f"Error querying live provider for keyword '{kw}' at '{loc_target}': {e}")
                return {"success": False, "jobs": [], "error": str(e)}

        query_tasks = [(kw, loc) for kw in search_keywords for loc in loc_targets]
        max_workers = min(4, len(query_tasks)) if query_tasks else 1

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_fetch_provider, kw, loc): (kw, loc) for kw, loc in query_tasks}
            for future in as_completed(futures):
                provider_res = future.result()
                p_status = provider_res.get('provider_status', {})
                if p_status:
                    provider_status.update(p_status)
                p_used = provider_res.get('providers_used', [])
                if p_used:
                    providers_used.update(p_used)

                if provider_res.get('success'):
                    for item in provider_res.get('jobs', []):
                        j_id = str(item.get('provider_job_id', ''))
                        prov = str(item.get('provider', ''))
                        title = str(item.get('title', '')).lower()
                        company = str(item.get('company', '')).lower()
                        app_url = str(item.get('application_url', '')).strip()

                        dedup_key = (prov, j_id) if j_id else (app_url if app_url else (company, title))
                        if dedup_key not in seen_job_keys:
                            seen_job_keys.add(dedup_key)
                            raw_live_jobs.append(item)

        raw_jobs_count = len(raw_live_jobs)

        # 5. Deduplicate and cache live jobs
        normalized_jobs = DeduplicationAndCacheEngine.process_and_cache_jobs(raw_live_jobs)
        duplicates_removed_count = max(0, raw_jobs_count - len(normalized_jobs))

        # 6. Apply Geographic & Role Relevance Eligibility Filtering Stage (BEFORE Match Scoring/Ranking)
        from app.services.role_relevance_service import RoleRelevanceService
        from app.services.seniority_service import SeniorityService
        from app.services.location_tier_service import LocationTierService

        eligible_jobs = []
        geo_rejected_count = 0
        role_rejected_count = 0
        seniority_rejected_count = 0
        qualification_rejected_count = 0

        for job in normalized_jobs:
            if not job.get("is_live", True):
                continue

            # 6a. Geographic Eligibility Gate (Hard Filter - WORLDWIDE)
            geo_res = GeoEligibilityService.evaluate_geo_eligibility(job, target_country=target_country)
            if not geo_res.get("eligible"):
                geo_rejected_count += 1
                logger.info(f"Geographic Filter REJECTED job '{job.get('title')}' at '{job.get('company')}': {geo_res.get('reason')}")
                continue

            job["geo_eligibility"] = geo_res.get("geo_status")

            # 6b. Location Tier Normalization & Region Resolution
            loc_res = LocationTierService.evaluate_location_tier(job)
            job["location_tier"] = loc_res.get("location_tier")
            job["location_region"] = loc_res.get("location_region")
            job["display_location"] = loc_res.get("display_location")
            job["locations"] = loc_res.get("locations")
            job["location_tiers"] = loc_res.get("location_tiers")
            job["location_weight"] = loc_res.get("location_weight")

            # 6c. Role & Professional Domain Relevance Gate (Hard Filter)
            role_rel = RoleRelevanceService.evaluate_role_relevance(candidate_profile, job, target_role=target_role)
            job["role_relevance_status"] = role_rel.get("role_relevance_status")
            job["detected_job_role"] = role_rel.get("detected_job_role")
            job["role_relevance_reason"] = role_rel.get("reason")

            if not role_rel.get("eligible"):
                role_rejected_count += 1
                job["recommendation_status"] = "ROLE_MISMATCH"
                job["is_primary_recommendation"] = False
                logger.info(f"Role Relevance Filter REJECTED job '{job.get('title')}': {role_rel.get('reason')}")
                continue

            # 6d. Seniority Evaluation & Conflict Detection
            sen_res = SeniorityService.evaluate_seniority(candidate_profile, job)
            job["job_seniority"] = sen_res.get("job_seniority")
            job["candidate_seniority"] = sen_res.get("candidate_seniority")
            job["seniority_status"] = sen_res.get("seniority_status")
            job["is_fresher_mismatch"] = sen_res.get("is_fresher_mismatch")
            job["seniority_conflict_detected"] = sen_res.get("conflict_detected")
            job["seniority_reason"] = sen_res.get("reason")
            if sen_res.get("is_fresher_mismatch"):
                seniority_rejected_count += 1

            eligible_jobs.append(job)

        # 6e. Graceful MongoDB Fallback for Active Verified Vacancies
        # If live providers returned fewer than 10 eligible jobs (e.g. unconfigured provider keys, rate limits, or zero local matches),
        # query genuine verified active vacancies directly from MongoDB Atlas jobs collection.
        if len(eligible_jobs) < 10:
            logger.info(f"Augmenting recommendations with verified MongoDB jobs for role '{target_role}' (current eligible={len(eligible_jobs)})")
            try:
                fallback_db_jobs = JobService.find_verified_jobs(
                    target_role=target_role,
                    keyword=target_role or (search_keywords[0] if search_keywords else ""),
                    location=location_param,
                    is_remote=is_remote,
                    experience=experience_param,
                    limit=30
                )
                # If target_role query returned few, also try candidate's search_keywords
                if len(fallback_db_jobs) < 5 and search_keywords:
                    for alt_kw in search_keywords[:2]:
                        if alt_kw != target_role:
                            extra_jobs = JobService.find_verified_jobs(
                                target_role=alt_kw,
                                keyword=alt_kw,
                                location=location_param,
                                is_remote=is_remote,
                                limit=20
                            )
                            fallback_db_jobs.extend(extra_jobs)

                existing_signatures = {
                    (str(j.get("company", "")).lower().strip(), str(j.get("title", "")).lower().strip())
                    for j in eligible_jobs
                }

                for db_job in fallback_db_jobs:
                    sig = (str(db_job.get("company", "")).lower().strip(), str(db_job.get("title", "")).lower().strip())
                    if sig in existing_signatures:
                        continue
                    existing_signatures.add(sig)

                    # Evaluate geo eligibility
                    geo_res = GeoEligibilityService.evaluate_geo_eligibility(db_job, target_country=target_country)
                    if not geo_res.get("eligible"):
                        continue
                    db_job["geo_eligibility"] = geo_res.get("geo_status")

                    loc_res = LocationTierService.evaluate_location_tier(db_job)
                    db_job["location_tier"] = loc_res.get("location_tier")
                    db_job["location_region"] = loc_res.get("location_region")
                    db_job["display_location"] = loc_res.get("display_location")
                    db_job["locations"] = loc_res.get("locations")
                    db_job["location_tiers"] = loc_res.get("location_tiers")
                    db_job["location_weight"] = loc_res.get("location_weight")

                    role_rel = RoleRelevanceService.evaluate_role_relevance(candidate_profile, db_job, target_role=target_role)
                    db_job["role_relevance_status"] = role_rel.get("role_relevance_status")
                    db_job["detected_job_role"] = role_rel.get("detected_job_role")
                    db_job["role_relevance_reason"] = role_rel.get("reason")
                    if not role_rel.get("eligible"):
                        continue

                    sen_res = SeniorityService.evaluate_seniority(candidate_profile, db_job)
                    db_job["job_seniority"] = sen_res.get("job_seniority")
                    db_job["candidate_seniority"] = sen_res.get("candidate_seniority")
                    db_job["seniority_status"] = sen_res.get("seniority_status")
                    db_job["is_fresher_mismatch"] = sen_res.get("is_fresher_mismatch")
                    db_job["seniority_conflict_detected"] = sen_res.get("conflict_detected")
                    db_job["seniority_reason"] = sen_res.get("reason")

                    db_job["source_type"] = "VERIFIED_DATABASE"
                    eligible_jobs.append(db_job)
                    providers_used.add("Verified Database Store")
                    provider_status["verified_database"] = "LIVE_SUCCESS"
            except Exception as fb_err:
                logger.warning(f"Error augmenting with verified MongoDB jobs: {fb_err}")

        # 7. Calculate Hybrid AI Match Scores & Skill Gap Analysis for Geo & Role Eligible Jobs
        matched_job_cards = []
        for job in eligible_jobs:
            req_skills = job.get("required_skills", [])
            eligibility = EligibilityService.evaluate_eligibility(candidate_skills, req_skills, job.get("title"))
            job["eligibility_status"] = eligibility["status"]
            job["eligibility_reason"] = eligibility["reason"]
            if eligibility["status"] in ["INELIGIBLE", "MISSING_MANDATORY_REQUIREMENT"]:
                qualification_rejected_count += 1

            match_res = JobMatchingEngine.calculate_job_match(analysis_json, user_json, job)
            if match_res:
                raw_match = match_res.get("final_match_score", 0)

                # Apply Seniority Mismatch penalty for freshers applying to 5+ yr Senior/Lead roles
                if job.get("is_fresher_mismatch"):
                    final_score = max(0.0, round(raw_match - 25.0, 1))
                else:
                    final_score = raw_match

                job["match_score"] = final_score
                job["final_match_score"] = final_score
                job["deterministic_match_score"] = match_res.get("deterministic_match_score", 0)
                job["ai_semantic_score"] = match_res.get("ai_semantic_score", 0)
                job["matched_skills"] = match_res.get("matched_skills", [])
                job["missing_required_skills"] = match_res.get("missing_required_skills", [])
                job["explainable_reasons"] = match_res.get("explainable_reasons", [])

                # Determine Recommendation Quality & Status
                role_status = job.get("role_relevance_status")
                is_fresher_mis = job.get("is_fresher_mismatch")
                elig_status = job.get("eligibility_status")

                if is_fresher_mis:
                    rec_status = "SENIORITY_MISMATCH"
                    is_primary = False
                elif role_status == "WEAKLY_RELATED" or final_score < 50.0:
                    rec_status = "LOW_MATCH"
                    is_primary = False
                elif elig_status in ["INELIGIBLE", "MISSING_MANDATORY_REQUIREMENT"]:
                    rec_status = "QUALIFICATION_MISMATCH"
                    is_primary = False
                elif role_status in ["DIRECT_ROLE_MATCH", "RELATED_ROLE"] and final_score >= 50.0:
                    rec_status = "RECOMMENDED"
                    is_primary = True
                else:
                    rec_status = "RELATED"
                    is_primary = False

                job["recommendation_status"] = rec_status
                job["is_primary_recommendation"] = is_primary

                # Concise Explainability array
                why = []
                if role_status in ["DIRECT_ROLE_MATCH", "RELATED_ROLE"]:
                    why.append(f"✓ Role matches candidate domain ({candidate_profile.get('professional_domain', '').title()})")
                if len(job.get("matched_skills", [])) > 0:
                    why.append(f"✓ Matched {len(job.get('matched_skills', []))} core domain skills")
                if not job.get("is_fresher_mismatch"):
                    why.append(f"✓ Seniority aligns with experience ({job.get('job_seniority', 'Entry Level').title()})")
                if job.get("missing_required_skills"):
                    why.append(f"⚠ Missing skills: {', '.join(job.get('missing_required_skills', [])[:3])}")
                job["why_recommended"] = why

                # Comprehensive Match Explanation & Telemetry
                job["debug_trace"] = {
                    "provider": job.get("provider"),
                    "provider_job_id": job.get("provider_job_id"),
                    "title": job.get("title"),
                    "company": job.get("company"),
                    "location": job.get("location"),
                    "display_location": job.get("display_location"),
                    "location_tier": job.get("location_tier"),
                    "location_region": job.get("location_region"),
                    "geo_status": job.get("geo_eligibility"),
                    "workplace_type": job.get("workplace_type"),
                    "role_relevance_status": role_status,
                    "detected_candidate_roles": candidate_profile.get("inferred_roles", []),
                    "detected_job_role": job.get("detected_job_role"),
                    "seniority": job.get("job_seniority"),
                    "seniority_status": job.get("seniority_status"),
                    "recommendation_status": rec_status,
                    "is_primary_recommendation": is_primary,
                    "required_skills": req_skills,
                    "matched_skills": match_res.get("matched_skills", []),
                    "missing_skills": match_res.get("missing_required_skills", []),
                    "deterministic_score": match_res.get("deterministic_match_score", 0),
                    "ai_semantic_score": match_res.get("ai_semantic_score", 0),
                    "final_match_score": final_score,
                    "eligibility_decision": elig_status,
                    "final_recommendation_decision": "ACCEPTED" if is_primary else "OTHER_OPPORTUNITY"
                }

            matched_job_cards.append(job)

        # 8. Multi-Criteria Ranking:
        role_order = {"DIRECT_ROLE_MATCH": 3, "RELATED_ROLE": 2, "WEAKLY_RELATED": 1, "UNRELATED": 0}
        sen_order = {"MATCHED": 1, "SENIORITY_MISMATCH": 0}
        elig_order = {"ELIGIBLE": 2, "PARTIALLY_ELIGIBLE": 1, "INELIGIBLE": 0, "MISSING_MANDATORY_REQUIREMENT": 0}

        matched_job_cards.sort(
            key=lambda x: (
                1 if x.get("is_primary_recommendation") else 0,
                role_order.get(x.get("role_relevance_status"), 0),
                sen_order.get(x.get("seniority_status"), 0),
                elig_order.get(x.get("eligibility_status"), 0),
                x.get("match_score", 0),
                x.get("location_weight", 0)
            ),
            reverse=True
        )

        # Separate Primary Recommended Jobs vs Other Opportunities
        recommended_jobs = [j for j in matched_job_cards if j.get("is_primary_recommendation")]
        other_opportunities = [j for j in matched_job_cards if not j.get("is_primary_recommendation")]

        # If primary recommended is empty but other_opportunities exists, promote the top relevant opportunities
        if not recommended_jobs and other_opportunities:
            promoted = [j for j in other_opportunities if j.get("role_relevance_status") in ["DIRECT_ROLE_MATCH", "RELATED_ROLE"]]
            if not promoted:
                promoted = sorted(other_opportunities, key=lambda x: x.get("match_score", 0), reverse=True)[:5]
            for p_job in promoted:
                p_job["is_primary_recommendation"] = True
                if p_job.get("recommendation_status") in ["LOW_MATCH", "RELATED"]:
                    p_job["recommendation_status"] = "RECOMMENDED"
            recommended_jobs = promoted
            promoted_ids = {p.get("_id") for p in promoted}
            other_opportunities = [j for j in other_opportunities if j.get("_id") not in promoted_ids]

        # Filter by minimum match threshold if passed by user
        if min_match_param:
            try:
                min_m = float(min_match_param)
                recommended_jobs = [j for j in recommended_jobs if j.get("match_score", 0) >= min_m]
            except ValueError:
                pass

        # 9. Categorize into 3 Relevance Buckets with Strict Boundaries
        highly_relevant = [j for j in recommended_jobs if j.get("match_score", 0) >= 70]
        relevant = [j for j in recommended_jobs if 50 <= j.get("match_score", 0) < 70]
        potential = [j for j in other_opportunities if j.get("match_score", 0) < 50 or j.get("role_relevance_status") == "WEAKLY_RELATED"]

        grouped_recommendations = {}
        remote_jobs = [j for j in recommended_jobs if j.get("workplace_type") == "REMOTE"]
        if remote_jobs:
            grouped_recommendations["remote"] = remote_jobs

        onsite_jobs = [j for j in recommended_jobs if j.get("workplace_type") != "REMOTE"]
        if onsite_jobs:
            grouped_recommendations["onsite_hybrid"] = onsite_jobs

        formatted_time = datetime.now(timezone.utc).strftime("%d %B %Y, %I:%M %p")

        # Construct Debug Telemetry
        debug_telemetry = {
            "search_queries": search_keywords,
            "target_locations": loc_targets,
            "providers_used": list(providers_used),
            "provider_status": provider_status,
            "raw_jobs_received": raw_jobs_count,
            "normalized_jobs": len(normalized_jobs),
            "duplicates_removed": duplicates_removed_count,
            "geo_rejected_count": geo_rejected_count,
            "geo_eligible_count": max(0, len(normalized_jobs) - geo_rejected_count),
            "role_rejected_count": role_rejected_count,
            "eligible_jobs_count": len(eligible_jobs),
            "role_relevant_count": len(eligible_jobs),
            "seniority_rejected_count": seniority_rejected_count,
            "qualification_rejected_count": qualification_rejected_count,
            "qualification_compatible_count": max(0, len(eligible_jobs) - qualification_rejected_count),
            "recommended_count": len(recommended_jobs),
            "other_opportunities_count": len(other_opportunities)
        }

        logger.info(f"RESUME_ANALYSIS_SUCCESS: user_id={user_id}, resume_id={latest_resume_id}, domain={candidate_profile.get('professional_domain')}")
        logger.info(f"SEARCH_QUERY_GENERATED: queries={search_keywords}")
        logger.info(f"PROVIDER_TELEMETRY: raw_received={raw_jobs_count}, normalized={len(normalized_jobs)}, deduped={duplicates_removed_count}, worldwide_eligible={len(eligible_jobs)}, role_matches={len(matched_job_cards)}, final_recommended={len(recommended_jobs)}")

        if not matched_job_cards:
            status_code = "LIVE_SEARCH_SUCCESS_NO_MATCHES"
            msg = f"No active vacancies currently match '{target_role}'. Try broadening your search or adjusting location filters."

            return jsonify({
                "success": True,
                "status": status_code,
                "geo_policy": "WORLDWIDE",
                "message": msg,
                "target_role": target_role,
                "candidate_profile": candidate_profile,
                "last_updated_at": formatted_time,
                "last_verified_at": formatted_time,
                "total_vacancies": 0,
                "providers_used": list(providers_used),
                "provider_status": provider_status,
                "search_queries": search_keywords,
                "debug_telemetry": debug_telemetry,
                "data": {
                    "recommended_jobs": [],
                    "other_opportunities": [],
                    "highly_relevant": [],
                    "relevant": [],
                    "potential": [],
                    "grouped_recommendations": {},
                    "all_recommendations": []
                }
            }), 200

        resp_payload = {
            "success": True,
            "status": "LIVE_RECOMMENDATIONS_AVAILABLE",
            "geo_policy": "WORLDWIDE",
            "message": f"Personalized live job recommendations generated successfully for candidate profile ({candidate_profile.get('professional_domain', '').title()}).",
            "target_role": target_role,
            "candidate_profile": candidate_profile,
            "last_updated_at": formatted_time,
            "last_verified_at": formatted_time,
            "total_vacancies": len(recommended_jobs),
            "providers_used": list(providers_used),
            "provider_status": provider_status,
            "search_queries": search_keywords,
            "debug_telemetry": debug_telemetry,
            "data": {
                "recommended_jobs": recommended_jobs,
                "other_opportunities": other_opportunities,
                "highly_relevant": highly_relevant,
                "relevant": relevant,
                "potential": potential,
                "grouped_recommendations": grouped_recommendations,
                "all_recommendations": matched_job_cards
            }
        }

        # Cache successful recommendations in memory
        if len(_RECOMMENDATIONS_CACHE) > 100:
            _RECOMMENDATIONS_CACHE.clear()
        _RECOMMENDATIONS_CACHE[cache_key] = {
            "timestamp": time.time(),
            "data": resp_payload
        }

        return jsonify(resp_payload), 200
    except Exception as e:
        logger.exception(f"Unexpected error in get_recommended_jobs: {e}")
        try:
            emergency_jobs = JobService.find_verified_jobs(target_role=request.args.get('role', '') or "Software Engineer", limit=15)
            formatted_time = datetime.now(timezone.utc).strftime("%d %B %Y, %I:%M %p")
            return jsonify({
                "success": True,
                "status": "FALLBACK_RECOVERY",
                "message": "Displaying verified active vacancies from our database.",
                "last_updated_at": formatted_time,
                "total_vacancies": len(emergency_jobs),
                "data": {
                    "recommended_jobs": emergency_jobs,
                    "other_opportunities": [],
                    "highly_relevant": emergency_jobs[:3],
                    "relevant": emergency_jobs[3:],
                    "potential": [],
                    "grouped_recommendations": {},
                    "all_recommendations": emergency_jobs
                }
            }), 200
        except Exception:
            pass

        return jsonify({
            "success": True,
            "status": "FALLBACK_EMPTY",
            "message": "Live vacancies are momentarily updating. Please refresh in a few moments.",
            "total_vacancies": 0,
            "data": {
                "recommended_jobs": [],
                "other_opportunities": [],
                "highly_relevant": [],
                "relevant": [],
                "potential": [],
                "grouped_recommendations": {},
                "all_recommendations": []
            }
        }), 200


@job_bp.route('/<job_id>/match', methods=['GET'])
@jwt_required
def get_job_match_analysis(job_id):
    """
    GET /api/jobs/<job_id>/match
    Returns detailed 6-component match analysis for a specific job.
    """
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
    user_id = str(user.get("_id", user.get("id")))

    # 1. Fetch target job
    job = JobService.get_job_by_id(job_id)
    if not job:
        return jsonify({
            "success": False,
            "message": "Job not found in database."
        }), 404

    # 2. Fetch user's latest resume & analysis
    my_resumes = ResumeModel.find_by_user(user_id)
    if not my_resumes or len(my_resumes) == 0:
        return jsonify({
            "success": False,
            "message": "Please upload and analyze your resume before matching with jobs."
        }), 400

    latest_resume_id = str(my_resumes[0].get("_id"))
    analysis_doc = ResumeAnalysisModel.find_by_resume_id(latest_resume_id)
    if not analysis_doc:
        return jsonify({
            "success": False,
            "message": "Please analyze your resume before matching with jobs."
        }), 400

    analysis_json = ResumeAnalysisModel.to_json(analysis_doc)

    # MANDATORY VALIDATION GUARD FOR JOB MATCHING
    if analysis_json.get("validation_status") != "VALID_RESUME" or analysis_json.get("resume_score") is None:
        return jsonify({
            "success": False,
            "status": "MATCHING_BLOCKED",
            "message": f"Job matching is blocked because the uploaded document is not a valid resume ({analysis_json.get('document_type', 'NON_RESUME')}).",
            "error": "INVALID_DOCUMENT"
        }), 400

    user_json = UserModel.to_json(user)

    # 3. Geo-Eligibility Check for Tamil Nadu Hard Gate
    geo_res = GeoEligibilityService.evaluate_geo_eligibility(job, target_country="IN")

    # 4. Calculate match
    match_result = JobMatchingEngine.calculate_job_match(analysis_json, user_json, job)
    match_result["geo_eligibility"] = geo_res
    match_result["is_tn_eligible"] = geo_res.get("eligible", False)
    match_result["recommendation_eligible"] = geo_res.get("eligible", False)
    if not geo_res.get("eligible"):
        match_result["is_primary_recommendation"] = False
        match_result["unsuitable_reason"] = f"Job is geographically ineligible for Tamil Nadu: {geo_res.get('reason')}"

    # 5. Save/update match document in MongoDB
    saved_doc = JobMatchModel.create_or_update_match(user_id, latest_resume_id, job_id, match_result)
    match_json = JobMatchModel.to_json(saved_doc)

    return jsonify({
        "success": True,
        "data": {
            "match": match_result,
            "persisted_match": match_json,
            "job": job
        }
    }), 200

@job_bp.route('/search', methods=['GET'])
def search_live_jobs():
    """
    GET /api/jobs/search
    Legacy API search endpoint.
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        location = request.args.get('location', '').strip()
        country = request.args.get('country', '').strip()
        remote_param = request.args.get('remote', '').lower()
        is_remote = True if remote_param in ['true', '1', 'yes'] else (False if remote_param in ['false', '0', 'no'] else None)
        experience = request.args.get('experience', '').strip()
        employment_type = request.args.get('employment_type', '').strip()

        try:
            page = max(1, int(request.args.get('page', 1)))
        except ValueError:
            page = 1

        try:
            limit = min(50, max(1, int(request.args.get('limit', 20))))
        except ValueError:
            limit = 20

        search_params = {
            'keyword': keyword,
            'location': location,
            'country': country,
            'remote': is_remote,
            'experience': experience,
            'employment_type': employment_type,
            'page': page,
            'limit': limit
        }

        provider = ProviderFactory.get_provider()
        provider_res = provider.search_jobs(search_params)

        raw_jobs = provider_res.get('jobs', []) if provider_res.get('success') else []
        normalized_jobs = DeduplicationAndCacheEngine.process_and_cache_jobs(raw_jobs) if raw_jobs else []

        if keyword and normalized_jobs:
            from app.services.role_taxonomy import RoleTaxonomy
            filtered = []
            for j in normalized_jobs:
                t_match = RoleTaxonomy.evaluate_role_match(keyword, j.get('title', ''))
                if t_match.get("is_strictly_excluded"):
                    continue
                filtered.append(j)
            normalized_jobs = filtered

        source_name = provider_res.get('source', 'Live Job Provider')

        # Fallback to verified MongoDB Atlas jobs if live providers returned 0 matching jobs or failed
        if not normalized_jobs:
            logger.info(f"Live search returned 0 items for '{keyword}', falling back to verified MongoDB vacancies.")
            db_jobs = JobService.find_verified_jobs(
                keyword=keyword,
                target_role=keyword,
                location=location,
                is_remote=is_remote,
                experience=experience,
                limit=limit
            )
            if db_jobs:
                normalized_jobs = db_jobs
                source_name = "MongoDB Verified Vacancy Store"

        now_iso = datetime.now(timezone.utc).isoformat()

        return jsonify({
            "success": True,
            "source": source_name,
            "retrieved_at": now_iso,
            "page": page,
            "limit": limit,
            "total": len(normalized_jobs),
            "jobs": normalized_jobs
        }), 200

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Live job search exception: {e}")
        try:
            db_jobs = JobService.find_verified_jobs(
                keyword=request.args.get('keyword', ''),
                limit=20
            )
            if db_jobs:
                return jsonify({
                    "success": True,
                    "source": "MongoDB Verified Vacancy Store",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "page": 1,
                    "limit": len(db_jobs),
                    "total": len(db_jobs),
                    "jobs": db_jobs
                }), 200
        except Exception:
            pass

        return jsonify({
            "success": True,
            "source": "Live Job Search",
            "page": 1,
            "limit": 0,
            "total": 0,
            "jobs": [],
            "message": "No active vacancies matched your search query."
        }), 200

@job_bp.route('/action', methods=['POST'])
@jwt_required
def record_user_job_action():
    """
    POST /api/jobs/action
    Records candidate action on a job: SAVED, APPLIED, INTERVIEW, REJECTED, HIDDEN.
    """
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
    user_id = str(user.get("_id", user.get("id")))

    data = request.get_json() or {}
    job_id = data.get("job_id")
    action = data.get("action", "SAVED")
    notes = data.get("notes", "")

    if not job_id:
        return jsonify({"success": False, "message": "job_id is required."}), 400

    from app.models.user_job_action import UserJobActionModel
    result = UserJobActionModel.record_action(user_id, job_id, action, notes)

    return jsonify({
        "success": True,
        "message": f"Job action '{action}' recorded successfully.",
        "data": result
    }), 200

@job_bp.route('/saved', methods=['GET'])
@jwt_required
def get_saved_jobs():
    """
    GET /api/jobs/saved
    Fetch candidate's saved and tracked jobs.
    """
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
    user_id = str(user.get("_id", user.get("id")))

    from app.models.user_job_action import UserJobActionModel
    actions = UserJobActionModel.get_user_actions(user_id)

    return jsonify({
        "success": True,
        "data": {
            "actions": actions,
            "total": len(actions)
        }
    }), 200

@job_bp.route('/simulate-match', methods=['POST'])
@jwt_required
def simulate_match():
    """
    Hypothetical Match Score Simulator Endpoint.
    """
    user = getattr(request, 'current_user', None)
    if not user:
        return jsonify({"success": False, "message": "Unauthorized access."}), 401
    user_id = str(user.get("_id", user.get("id")))

    data = request.get_json(silent=True) or {}
    job_id = data.get("job_id")
    skills_to_add = data.get("skills_to_add", [])

    if not job_id:
        return jsonify({"success": False, "message": "job_id is required."}), 400

    job = JobService.get_job_by_id(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found."}), 404

    my_resumes = ResumeModel.find_by_user(user_id)
    if not my_resumes:
        return jsonify({"success": False, "message": "Please upload a resume first."}), 400

    latest_resume_id = str(my_resumes[0].get("_id"))
    analysis_doc = ResumeAnalysisModel.find_by_resume_id(latest_resume_id)
    if not analysis_doc:
        return jsonify({"success": False, "message": "Please analyze your resume first."}), 400

    analysis_json = ResumeAnalysisModel.to_json(analysis_doc)
    if analysis_json.get("validation_status") != "VALID_RESUME":
        return jsonify({"success": False, "message": "Simulation unavailable for invalid resume document."}), 400

    user_json = UserModel.to_json(user)

    from app.services.match_simulator import MatchSimulator
    sim_res = MatchSimulator.simulate_skill_acquisition(analysis_json, user_json, job, skills_to_add)

    return jsonify({
        "success": True,
        "data": {
            "simulation": sim_res
        }
    }), 200
