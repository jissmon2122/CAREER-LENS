import logging
import re

logger = logging.getLogger(__name__)

class SeniorityService:
    """
    Evaluates vacancy seniority requirements against candidate experience level.
    Detects conflicting seniority signals (e.g. title 'Senior Shopify Developer' vs raw exp '0-2 years')
    and flags SENIORITY_MISMATCH for fresher/student candidates.
    """

    SENIOR_TITLE_KEYWORDS = [
        "senior", "sr.", "sr ", "lead", "principal", "architect", "head",
        "director", "vp", "staff", "manager", "team lead"
    ]

    ENTRY_TITLE_KEYWORDS = [
        "junior", "jr.", "jr ", "entry", "intern", "fresher", "trainee",
        "graduate", "associate", "apprentice"
    ]

    @classmethod
    def evaluate_seniority(cls, candidate_profile: dict, job: dict) -> dict:
        """
        Evaluates seniority compatibility and detects conflicting signals.
        Returns dict:
          - job_seniority: "ENTRY_LEVEL" | "JUNIOR" | "MID" | "SENIOR" | "LEAD" | "UNKNOWN"
          - candidate_seniority: "ENTRY_LEVEL" | "MID" | "SENIOR"
          - seniority_status: "MATCHED" | "SENIORITY_MISMATCH" | "OVERQUALIFIED"
          - is_fresher_mismatch: bool
          - conflict_detected: bool
          - reason: str
        """
        cand_exp_raw = str(candidate_profile.get("experience_level", "")).lower()
        cand_roles = [str(r).lower() for r in candidate_profile.get("inferred_roles", [])]

        is_cand_entry = any(k in cand_exp_raw for k in ["student", "fresher", "0-2", "graduate", "junior", "entry"]) or \
                        any("junior" in r or "intern" in r for r in cand_roles)
        cand_seniority = "ENTRY_LEVEL" if is_cand_entry else ("SENIOR" if "5+" in cand_exp_raw or "senior" in cand_exp_raw else "MID")

        title = str(job.get("title") or job.get("job_title") or "").strip().lower()
        exp_req = str(job.get("experience_required") or job.get("experience") or "").strip().lower()
        desc = str(job.get("raw_description") or job.get("clean_description") or "").strip().lower()
        searchable_job = f"{title} {exp_req} {desc[:500]}"

        # Title-based Seniority (Highest Priority Signal)
        has_senior_title = any(k in title for k in cls.SENIOR_TITLE_KEYWORDS)
        has_entry_title = any(k in title for k in cls.ENTRY_TITLE_KEYWORDS)

        # Experience-field based Seniority
        years_match = re.search(r'(\d+)\s*\+\s*years', searchable_job)
        exp_years = int(years_match.group(1)) if years_match else None

        conflict_detected = False
        if has_senior_title and ("0-2" in exp_req or "fresher" in exp_req):
            conflict_detected = True

        # Resolve job seniority (Title supersedes raw field if title explicitly says Senior/Lead)
        if any(k in title for k in ["lead", "principal", "architect", "head", "director", "vp", "staff"]):
            job_seniority = "LEAD"
        elif has_senior_title or (exp_years and exp_years >= 5):
            job_seniority = "SENIOR"
        elif has_entry_title or "0-2" in exp_req or "fresher" in exp_req or "graduate" in exp_req:
            job_seniority = "ENTRY_LEVEL"
        elif (exp_years and exp_years >= 2) or "2-5" in exp_req:
            job_seniority = "MID"
        else:
            job_seniority = "UNKNOWN"

        # Seniority status determination
        seniority_status = "MATCHED"
        is_fresher_mismatch = False
        reason = f"Job seniority ({job_seniority}) aligns with candidate experience ({cand_seniority})."

        if cand_seniority == "ENTRY_LEVEL" and job_seniority in ["SENIOR", "LEAD"]:
            seniority_status = "SENIORITY_MISMATCH"
            is_fresher_mismatch = True
            reason = f"Vacancy '{title.title()}' requires senior/lead level experience ({job_seniority}), mismatched with fresher candidate."
            if conflict_detected:
                reason += " (Conflicting provider field detected: title explicitly requires Senior level)."

        return {
            "job_seniority": job_seniority,
            "candidate_seniority": cand_seniority,
            "seniority_status": seniority_status,
            "is_fresher_mismatch": is_fresher_mismatch,
            "conflict_detected": conflict_detected,
            "reason": reason
        }
