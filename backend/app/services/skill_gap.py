import re

class SkillGapEngine:
    """
    Skill Gap Analysis Engine.
    Evaluates candidate skills against a target job's required and preferred skill sets.
    Categorizes missing skills into priority tiers (CRITICAL, HIGH, MEDIUM, LOW) and
    calculates exact Required Coverage % and Skill Gap %.
    """

    @classmethod
    def analyze_skill_gap(cls, analysis_json, user_json, job):
        """
        Analyze skill gap between candidate profile and target job.
        
        Returns:
            dict containing matched skills, missing skills, coverage %, gap %, and prioritized gaps.
        """
        candidate_tech_skills = analysis_json.get("technical_skills", []) if analysis_json else []
        candidate_soft_skills = analysis_json.get("soft_skills", []) if analysis_json else []
        candidate_all = set([s.lower().strip() for s in candidate_tech_skills + candidate_soft_skills])

        # Target job skills
        job_req_skills = job.get("required_skills", [])
        job_pref_skills = job.get("preferred_skills", [])

        # Categorize matches & gaps
        matched_required = []
        missing_required = []
        for req in job_req_skills:
            req_clean = req.lower().strip()
            if req_clean in candidate_all or any(req_clean in c for c in candidate_all):
                matched_required.append(req)
            else:
                missing_required.append(req)

        matched_preferred = []
        missing_preferred = []
        for pref in job_pref_skills:
            pref_clean = pref.lower().strip()
            if pref_clean in candidate_all or any(pref_clean in c for c in candidate_all):
                matched_preferred.append(pref)
            else:
                missing_preferred.append(pref)

        # Coverage & Gap Math
        total_req_count = len(job_req_skills)
        if total_req_count > 0:
            required_coverage_percent = round((len(matched_required) / total_req_count) * 100, 1)
        else:
            required_coverage_percent = 100.0

        skill_gap_percent = round(100.0 - required_coverage_percent, 1)

        # AI Semantic Skill Categorization
        from app.ai.embedding_service import embedding_service
        from app.ai.semantic_matcher import semantic_matcher

        semantic_breakdown = []
        semantic_matches = []
        if embedding_service.is_available():
            semantic_breakdown = semantic_matcher.categorize_skills(candidate_tech_skills, job_req_skills)
            for item in semantic_breakdown:
                if item["match_type"] == "SEMANTIC_MATCH":
                    semantic_matches.append({
                        "required_skill": item["skill"],
                        "matched_candidate_skill": item["matched_with"],
                        "similarity_score": round(item["similarity"] * 100, 1)
                    })

        # Prioritize Missing Skills
        # High market demand skills (e.g. Python, React, Power BI, SQL, AWS, Node.js) get CRITICAL priority if required
        high_demand_keywords = {"python", "sql", "react", "power bi", "aws", "node.js", "docker", "excel", "machine learning", "tableau"}
        
        prioritized_gaps = []

        # 1. Missing Required Skills
        for sk in missing_required:
            sk_clean = sk.lower().strip()
            # Check if there was a semantic match for this missing required skill
            sem_item = next((item for item in semantic_breakdown if item["skill"].lower() == sk_clean and item["match_type"] == "SEMANTIC_MATCH"), None)
            
            if sem_item:
                priority = "SEMANTIC_GAP"
                reason = f"Candidate has related skill '{sem_item['matched_with']}' ({round(sem_item['similarity']*100, 1)}% similarity). Minor gap."
            elif sk_clean in high_demand_keywords:
                priority = "CRITICAL"
                reason = f"Essential required skill for {job.get('title', 'Target Role')} & High Market Demand."
            else:
                priority = "HIGH"
                reason = f"Mandatory required skill for {job.get('title', 'Target Role')}."

            prioritized_gaps.append({
                "skill": sk,
                "category": "Required",
                "priority": priority,
                "reason": reason
            })

        # 2. Missing Preferred Skills
        for sk in missing_preferred:
            prioritized_gaps.append({
                "skill": sk,
                "category": "Preferred",
                "priority": "MEDIUM",
                "reason": f"Bonus preferred skill for {job.get('title', 'Target Role')}."
            })

        return {
            "job_id": job.get("id"),
            "job_title": job.get("title"),
            "company": job.get("company"),
            "required_coverage_percent": required_coverage_percent,
            "skill_gap_percent": skill_gap_percent,
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
            "missing_preferred_skills": missing_preferred,
            "semantic_matches": semantic_matches,
            "semantic_breakdown": semantic_breakdown,
            "total_missing_skills_count": len(missing_required) + len(missing_preferred),
            "prioritized_gaps": prioritized_gaps
        }

