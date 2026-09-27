import logging
from app.services.extraction_service import ExtractionService

logger = logging.getLogger(__name__)

class JobMatchingEngine:
    """
    Deterministic Weighted Job Matching Engine.
    Calculates 0-100% Match Scores, breakdown metrics, matched skills, missing skills, and explainable match reasons.
    """

    ALGORITHM_VERSION = "1.0"

    @classmethod
    def calculate_job_match(cls, resume_analysis, candidate_user, job_profile):
        """
        Compute deterministic match between candidate's analyzed resume & dataset job profile.
        
        Weights:
            - Required Skills: 40%
            - Preferred Skills: 10%
            - Experience: 15%
            - Education: 10%
            - Role Match: 15%
            - Location Match: 10%
            - TOTAL: 100%
        """
        if not resume_analysis or not job_profile:
            return None

        aliases = ExtractionService.get_skills_dictionary().get("aliases", {})

        # 1. Normalize Candidate Skills
        raw_cand_skills = resume_analysis.get("technical_skills", [])
        cand_skills = set(aliases.get(s.lower(), s) for s in raw_cand_skills)

        # 2. Normalize Job Required & Preferred Skills
        job_req_skills = job_profile.get("required_skills", [])
        job_pref_skills = job_profile.get("preferred_skills", [])

        # 3. Required Skill Match (40% Weight)
        matched_required = [s for s in job_req_skills if s in cand_skills]
        missing_required = [s for s in job_req_skills if s not in cand_skills]

        if job_req_skills:
            req_pct = (len(matched_required) / len(job_req_skills)) * 100.0
        else:
            req_pct = 100.0
        req_points = round(req_pct * 0.40, 2)

        # 4. Preferred Skill Match (10% Weight)
        matched_preferred = [s for s in job_pref_skills if s in cand_skills]
        missing_preferred = [s for s in job_pref_skills if s not in cand_skills]

        if job_pref_skills:
            pref_pct = (len(matched_preferred) / len(job_pref_skills)) * 100.0
            pref_points = round(pref_pct * 0.10, 2)
        else:
            pref_pct = 100.0
            pref_points = 10.0  # Do not penalize if no preferred skills specified

        # 5. Experience Match (15% Weight)
        cand_exp = (candidate_user.get("experience_level") or "Fresher").lower()
        job_exp = (job_profile.get("experience_required") or "Fresher").lower()

        if "fresher" in job_exp or "0-2" in job_exp or "student" in cand_exp or "fresher" in cand_exp:
            exp_pct = 100.0
        elif "2-5" in job_exp and ("2-5" in cand_exp or "5+" in cand_exp):
            exp_pct = 100.0
        elif "2-5" in job_exp and ("0-2" in cand_exp or "fresher" in cand_exp):
            exp_pct = 70.0
        elif "5+" in job_exp and ("fresher" in cand_exp or "student" in cand_exp):
            exp_pct = 40.0
        else:
            exp_pct = 80.0
        exp_points = round(exp_pct * 0.15, 2)

        # 6. Education Match (10% Weight)
        cand_edu = resume_analysis.get("education", [])
        if cand_edu and len(cand_edu) > 0 and cand_edu[0].get("degree"):
            edu_pct = 100.0
        elif candidate_user.get("education"):
            edu_pct = 100.0
        else:
            edu_pct = 75.0
        edu_points = round(edu_pct * 0.10, 2)

        # 7. Role Match (15% Weight)
        pref_role = (candidate_user.get("preferred_job_role") or "").lower().strip()
        job_title = (job_profile.get("job_title") or "").lower().strip()

        if not pref_role:
            role_pct = 75.0
        elif pref_role in job_title or job_title in pref_role:
            role_pct = 100.0
        elif any(w in job_title for w in pref_role.split()):
            role_pct = 85.0
        elif ("data" in pref_role and "data" in job_title) or ("dev" in pref_role and ("engineer" in job_title or "developer" in job_title)):
            role_pct = 75.0
        else:
            role_pct = 40.0
        role_points = round(role_pct * 0.15, 2)

        # 8. Location Match (10% Weight)
        pref_loc = (candidate_user.get("preferred_location") or "").lower().strip()
        job_loc = (job_profile.get("location") or "").lower().strip()

        if not pref_loc or "remote" in job_loc or "remote" in pref_loc:
            loc_pct = 100.0
        elif pref_loc in job_loc or job_loc in pref_loc:
            loc_pct = 100.0
        else:
            loc_pct = 25.0
        loc_points = round(loc_pct * 0.10, 2)

        # 9. Total Match Score Sum Calculation (0–100% Deterministic)
        deterministic_score = round(req_points + pref_points + exp_points + edu_points + role_points + loc_points)
        deterministic_score = max(0, min(100, deterministic_score))

        # 10. AI Semantic Match Calculation
        from app.ai.embedding_service import embedding_service
        from app.ai.semantic_matcher import semantic_matcher

        ai_available = embedding_service.is_available()
        ai_semantic_score = 0.0
        semantic_skill_categorization = []

        if ai_available:
            resume_text = (
                resume_analysis.get("raw_text") or
                resume_analysis.get("extracted_text") or
                " ".join([str(s) for s in raw_cand_skills])
            )
            job_desc = (
                job_profile.get("clean_description") or
                job_profile.get("raw_description") or
                job_profile.get("description") or
                job_profile.get("job_description") or
                f"{job_profile.get('title', '')} {' '.join(job_req_skills)}"
            )

            ai_res = semantic_matcher.compute_semantic_match(
                resume_text=resume_text,
                job_description=job_desc,
                candidate_skills=raw_cand_skills,
                job_skills=job_req_skills
            )
            ai_semantic_score = float(ai_res.get("ai_semantic_score", 0.0))
            semantic_skill_categorization = ai_res.get("skill_categorization", [])

            weighted_det = round(0.60 * deterministic_score, 2)
            weighted_ai = round(0.40 * ai_semantic_score, 2)
            # Combined Match Formula: 60% Existing Deterministic + 40% AI Semantic Match
            final_match_score = round(weighted_det + weighted_ai, 1)
        else:
            logger.warning("AI Embedding Service unavailable. Using deterministic score.")
            ai_semantic_score = float(deterministic_score)
            weighted_det = round(0.60 * deterministic_score, 2)
            weighted_ai = round(0.40 * ai_semantic_score, 2)
            final_match_score = float(deterministic_score)

        final_match_score = max(0.0, min(100.0, final_match_score))
        display_score = round(final_match_score, 1)

        # 11. Match Category based on final score
        if display_score >= 90:
            match_category = "Excellent Match"
        elif display_score >= 80:
            match_category = "Strong Match"
        elif display_score >= 70:
            match_category = "Good Match"
        elif display_score >= 60:
            match_category = "Moderate Match"
        else:
            match_category = "Low Match"

        # 12. Explainable Reasons List
        explainable_reasons = []
        if matched_required:
            explainable_reasons.append(f"Matched {len(matched_required)} required skills: {', '.join(matched_required[:4])}")
        if ai_available and ai_semantic_score >= 70.0:
            explainable_reasons.append(f"AI Semantic Match score is {ai_semantic_score}% (high conceptual fit)")
        if exp_pct >= 90:
            explainable_reasons.append("Experience requirements satisfied")
        if edu_pct >= 90:
            explainable_reasons.append("Education qualification requirements met")
        if role_pct >= 85:
            explainable_reasons.append(f"Target role '{job_profile.get('job_title')}' matches candidate career preference")
        if loc_pct >= 90:
            explainable_reasons.append(f"Location preference ({job_profile.get('location')}) matched")

        breakdown = {
            "required_skills": req_points,
            "preferred_skills": pref_points,
            "experience": exp_points,
            "education": edu_points,
            "role": role_points,
            "location": loc_points,
            "deterministic_total": deterministic_score,
            "weighted_deterministic": weighted_det,
            "ai_semantic_score": ai_semantic_score if ai_available else None,
            "weighted_ai": weighted_ai if ai_available else None,
            "total": display_score
        }

        return {
            "job_id": str(job_profile.get("job_id") or job_profile.get("id")),
            "job_title": job_profile.get("job_title"),
            "company": job_profile.get("company"),
            "location": job_profile.get("location"),
            "salary_min": job_profile.get("salary_min"),
            "salary_max": job_profile.get("salary_max"),
            "match_score": display_score,
            "final_match_score": display_score,
            "deterministic_match_score": deterministic_score,
            "ai_semantic_score": ai_semantic_score if ai_available else None,
            "ai_enabled": ai_available,
            "match_category": match_category,
            "matched_skills": sorted(list(set(matched_required + matched_preferred))),
            "missing_required_skills": sorted(missing_required),
            "missing_preferred_skills": sorted(missing_preferred),
            "semantic_skill_categorization": semantic_skill_categorization,
            "breakdown": breakdown,
            "explainable_reasons": explainable_reasons,
            "algorithm_version": cls.ALGORITHM_VERSION
        }

