import re
from datetime import datetime, timezone

class PreprocessingService:
    """
    Data Preprocessing & Normalization Engine for Historical Job Market Datasets.
    Handles multi-format date extraction (epoch, ISO, YYYY-MM-DD), text cleaning,
    deduplication, and skill normalization.
    """

    @classmethod
    def parse_period(cls, date_val, object_id=None):
        """
        Parse posted date into standard YYYY-MM period format.
        Handles:
          - ISO strings: '2026-09-19T15:10:06.551832+00:00'
          - YYYY-MM-DD / YYYY-MM strings
          - Unix epoch timestamps (seconds & milliseconds) as numbers or numeric strings
          - BSON ObjectId generation time fallback
        """
        if date_val:
            # Handle float or int epoch timestamps
            if isinstance(date_val, (int, float)):
                try:
                    num = float(date_val)
                    if num > 1e11:  # milliseconds
                        num /= 1000.0
                    if 1e8 < num < 2.5e9:  # valid year range ~1973 to 2049
                        return datetime.fromtimestamp(num, tz=timezone.utc).strftime("%Y-%m")
                except Exception:
                    pass

            s = str(date_val).strip()

            # Handle numeric epoch string (e.g. '1789828224')
            if s.isdigit():
                try:
                    num = float(s)
                    if num > 1e11:
                        num /= 1000.0
                    if 1e8 < num < 2.5e9:
                        return datetime.fromtimestamp(num, tz=timezone.utc).strftime("%Y-%m")
                except Exception:
                    pass

            # Handle ISO string or YYYY-MM-DD
            if len(s) >= 7 and s[:4].isdigit() and s[4] == '-' and s[5:7].isdigit():
                year = int(s[:4])
                month = int(s[5:7])
                if 2015 <= year <= 2030 and 1 <= month <= 12:
                    return f"{year:04d}-{month:02d}"

        # Fallback to ObjectId generation timestamp if available
        if object_id and hasattr(object_id, 'generation_time'):
            try:
                return object_id.generation_time.strftime("%Y-%m")
            except Exception:
                pass

        return "2026-09"

    @classmethod
    def normalize_skill(cls, skill_name):
        """Normalize skill string to canonical lower-case representation."""
        if not skill_name:
            return ""
        s = skill_name.strip()
        aliases = {
            "react.js": "react",
            "reactjs": "react",
            "powerbi": "power bi",
            "node": "node.js",
            "nodejs": "node.js",
            "postgres": "postgresql",
            "aws cloud": "aws",
            "machine learning (ml)": "machine learning",
            "ml": "machine learning",
            "ai": "artificial intelligence",
            "k8s": "kubernetes",
            "golang": "go",
            "gcp": "google cloud",
            "tailwind css": "tailwind",
            "tailwindcss": "tailwind",
            "express.js": "express",
            "vue.js": "vue"
        }
        s_lower = s.lower()
        return aliases.get(s_lower, s_lower)

    @classmethod
    def generate_forecast_periods(cls, last_period: str, horizon: int = 36) -> list:
        """
        Generate sequential YYYY-MM forecast periods starting strictly after last_period.
        For example: if last_period is '2026-11' and horizon is 36,
        generates: ['2026-12', '2027-01', ..., '2029-11'].
        """
        try:
            year, month = map(int, last_period.split('-'))
        except Exception:
            year, month = 2026, 11

        future_periods = []
        cur_year = year
        cur_month = month

        for _ in range(horizon):
            cur_month += 1
            if cur_month > 12:
                cur_month = 1
                cur_year += 1
            future_periods.append(f"{cur_year:04d}-{cur_month:02d}")

        return future_periods
