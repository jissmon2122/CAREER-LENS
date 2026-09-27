from app.services.job_matching import JobMatchingEngine

class MatchSimulator:
    """
    Hypothetical Match Score Simulator.
    Simulates match score improvement when a candidate hypothetically acquires missing skills.
    Reuses existing 6-component JobMatchingEngine WITHOUT mutating actual candidate database state.
    """

    @classmethod
    def simulate_skill_acquisition(cls, analysis_json, user_json, job, skills_to_add):
        """
        Simulate match score when skills_to_add are hypothetically added to candidate profile.
        
        Returns:
            dict containing original_match, simulated_match, score_difference, category_change, and status.
        """
        if not analysis_json or not job:
            return None

        # 1. Original Match
        orig_match = JobMatchingEngine.calculate_job_match(analysis_json, user_json, job)
        orig_score = orig_match.get("match_score", 0) if orig_match else 0
        orig_cat = orig_match.get("match_category", "Low") if orig_match else "Low"

        # 2. Build Hypothetical Analysis Payload
        sim_tech_skills = list(analysis_json.get("technical_skills", []))
        for sk in skills_to_add:
            if sk not in sim_tech_skills:
                sim_tech_skills.append(sk)

        hypothetical_analysis = dict(analysis_json)
        hypothetical_analysis["technical_skills"] = sim_tech_skills

        # 3. Calculate Simulated Match
        sim_match = JobMatchingEngine.calculate_job_match(hypothetical_analysis, user_json, job)
        sim_score = sim_match.get("match_score", 0) if sim_match else orig_score
        sim_cat = sim_match.get("match_category", orig_cat) if sim_match else orig_cat

        score_diff = sim_score - orig_score

        return {
            "status": "HYPOTHETICAL_SIMULATION",
            "job_id": job.get("id"),
            "job_title": job.get("title"),
            "skills_added": skills_to_add,
            "original_match_score": orig_score,
            "simulated_match_score": sim_score,
            "score_improvement": f"+{score_diff}%" if score_diff >= 0 else f"{score_diff}%",
            "original_category": orig_cat,
            "simulated_category": sim_cat,
            "category_improved": orig_cat != sim_cat,
            "simulated_matched_skills": sim_match.get("matched_skills", []),
            "simulated_missing_skills": sim_match.get("missing_required_skills", []),
            "disclaimer": "HYPOTHETICAL SIMULATION — Actual candidate resume and stored database records were NOT modified."
        }
