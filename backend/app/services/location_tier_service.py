import logging
import re

logger = logging.getLogger(__name__)

class LocationTierService:
    """
    Centralized Location Normalization and Preference Classification Service.
    Categorizes vacancies into worldwide location regions and workplace types:
      - WORLDWIDE_REMOTE
      - NATIONAL_METRO
      - INTERNATIONAL
      - GENERAL_LOCATION
    """

    @classmethod
    def evaluate_location_tier(cls, job: dict) -> dict:
        """
        Evaluates and normalizes job location into readable location text and metadata.
        """
        raw_loc = str(job.get("location") or job.get("raw_location") or "").strip()
        cand_req_loc = str(job.get("candidate_required_location") or "").strip()
        workplace_type = str(job.get("workplace_type") or "ON_SITE").upper().strip()

        combined_loc_text = f"{raw_loc} {cand_req_loc}".lower()

        is_remote_job = workplace_type == "REMOTE" or "remote" in combined_loc_text

        if is_remote_job:
            tier = "WORLDWIDE_REMOTE"
            region = "GLOBAL_REMOTE"
            display = raw_loc or "Remote — Worldwide"
            weight = 3
        elif any(c in combined_loc_text for c in ["germany", "usa", "uk", "canada", "australia", "france", "singapore", "japan", "dubai", "uae", "berlin", "london"]):
            tier = "INTERNATIONAL"
            region = "INTERNATIONAL"
            display = raw_loc
            weight = 2
        elif any(c in combined_loc_text for c in ["india", "chennai", "bengaluru", "mumbai", "delhi", "hyderabad", "pune", "kolkata"]):
            tier = "NATIONAL_METRO"
            region = "INDIA"
            display = raw_loc
            weight = 2
        else:
            tier = "GENERAL_LOCATION"
            region = "WORLDWIDE"
            display = raw_loc or "Worldwide"
            weight = 1

        return {
            "location_tier": tier,
            "location_region": region,
            "display_location": display,
            "locations": [display],
            "location_tiers": [tier],
            "location_weight": weight
        }

