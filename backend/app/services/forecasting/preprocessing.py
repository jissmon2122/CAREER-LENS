import re
from datetime import datetime

class PreprocessingService:
    """
    Data Preprocessing & Normalization Engine for Historical Job Market Datasets.
    Handles date formatting, text cleaning, deduplication, and skill normalization.
    """

    @classmethod
    def parse_period(cls, date_str):
        """Parse posted date into standard YYYY-MM period format."""
        if not date_str:
            return "2026-01"
        try:
            dt = datetime.strptime(str(date_str).strip()[:10], "%Y-%m-%d")
            return dt.strftime("%Y-%m")
        except Exception:
            return "2026-01"

    @classmethod
    def normalize_skill(cls, skill_name):
        """Normalize skill string to canonical lower-case representation."""
        if not skill_name:
            return ""
        s = skill_name.strip()
        # Aliases mapping
        aliases = {
            "react.js": "react",
            "reactjs": "react",
            "powerbi": "power bi",
            "node": "node.js",
            "nodejs": "node.js",
            "postgres": "postgresql",
            "aws cloud": "aws"
        }
        s_lower = s.lower()
        return aliases.get(s_lower, s_lower)
