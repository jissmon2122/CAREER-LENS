import logging
import re

logger = logging.getLogger(__name__)

class GeoEligibilityService:
    """
    Evaluates geographical candidate eligibility for job vacancies.
    Enforces WORLDWIDE geographic policy for universal resume-driven job discovery.
    Accepts legitimate vacancies globally (India, USA, UK, Germany, Canada, Australia,
    France, UAE, Singapore, Japan, Worldwide Remote, etc.).
    """

    GEO_POLICY = "WORLDWIDE"

    @classmethod
    def is_status_eligible(cls, geo_status: str) -> bool:
        """Central Invariant for Worldwide Geo Eligibility."""
        return True

    @classmethod
    def evaluate_geo_eligibility(cls, job: dict, target_country: str = None) -> dict:
        """
        Evaluates geographical candidate eligibility under WORLDWIDE policy.
        Returns dict with:
          - eligible: True (for all legitimate worldwide vacancies)
          - geo_policy: "WORLDWIDE"
          - geo_status: "WORLDWIDE_ELIGIBLE"
          - reason: str
          - display_location: str
        """
        raw_loc = str(job.get("location") or job.get("raw_location") or "").strip()
        cand_req_loc = str(job.get("candidate_required_location") or "").strip()
        workplace_type = str(job.get("workplace_type") or "").upper().strip()

        combined_loc = f"{raw_loc} {cand_req_loc}".strip()

        if not combined_loc:
            display_str = "Worldwide / Remote"
        elif workplace_type == "REMOTE" or "remote" in combined_loc.lower():
            if raw_loc and "remote" not in raw_loc.lower():
                display_str = f"Remote — {raw_loc}"
            else:
                display_str = raw_loc or "Remote — Worldwide"
        else:
            display_str = raw_loc

        return {
            "eligible": True,
            "geo_policy": cls.GEO_POLICY,
            "geo_status": "WORLDWIDE_ELIGIBLE",
            "reason": f"Worldwide job vacancy accepted ({display_str}).",
            "display_location": display_str
        }

