class EligibilityService:
    """
    Evaluates candidate eligibility status against mandatory job requirements.
    Prevents high AI semantic similarity scores from disguising missing mandatory requirements.
    """

    ELIGIBLE = "ELIGIBLE"
    PARTIALLY_ELIGIBLE = "PARTIALLY_ELIGIBLE"
    MISSING_MANDATORY_REQUIREMENT = "MISSING_MANDATORY_REQUIREMENT"
    UNKNOWN = "UNKNOWN"

    # Mandatory critical keywords that cannot be substituted semantically
    MANDATORY_LICENSES = {
        "nursing license", "rn license", "bar admission", "cpa", "medical license", "pilot license",
        "electrician license", "journeyman electrician", "master electrician",
        "plumbing license", "journeyman plumber", "master plumber",
        "cdl", "commercial driver license", "cdl-a",
        "teaching license", "cna", "certified nursing assistant", "epa 608"
    }

    @classmethod
    def evaluate_eligibility(cls, candidate_skills: list, job_required_skills: list, job_title: str = "") -> dict:
        if not job_required_skills:
            return {
                "status": cls.ELIGIBLE,
                "reason": "No mandatory skill requirements specified by provider."
            }

        cand_set = set(s.lower().strip() for s in (candidate_skills or []))
        req_set = set(s.lower().strip() for s in (job_required_skills or []))

        # Check for mandatory non-substitutable licenses/certifications
        missing_mandatory_licenses = []
        for req in req_set:
            if req in cls.MANDATORY_LICENSES and req not in cand_set:
                missing_mandatory_licenses.append(req)

        if missing_mandatory_licenses:
            return {
                "status": cls.MISSING_MANDATORY_REQUIREMENT,
                "reason": f"Missing mandatory license/credential: {', '.join(missing_mandatory_licenses)}"
            }

        # Calculate exact coverage ratio
        matched = [s for s in job_required_skills if s.lower().strip() in cand_set]
        coverage_ratio = len(matched) / len(job_required_skills) if job_required_skills else 1.0

        if coverage_ratio >= 0.75:
            return {
                "status": cls.ELIGIBLE,
                "reason": f"Candidate satisfies {len(matched)} of {len(job_required_skills)} required skills ({round(coverage_ratio*100)}%)."
            }
        elif coverage_ratio >= 0.40:
            return {
                "status": cls.PARTIALLY_ELIGIBLE,
                "reason": f"Candidate meets partial requirements ({round(coverage_ratio*100)}% coverage)."
            }
        else:
            return {
                "status": cls.MISSING_MANDATORY_REQUIREMENT,
                "reason": f"Candidate missing critical required skills ({round(coverage_ratio*100)}% coverage)."
            }
