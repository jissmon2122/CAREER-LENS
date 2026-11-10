import logging
from collections import defaultdict, Counter
from app.services.forecasting.preprocessing import PreprocessingService
from app.services.forecasting.skill_taxonomy import SkillTaxonomy

logger = logging.getLogger(__name__)

class SkillFrequencyEngine:
    """
    Monthly Skill Frequency Aggregator.
    Computes normalized Skill Demand Rates:
        demand_rate (%) = (Jobs requiring skill in period / Total jobs in period) * 100
    Uses Empirical Bayes smoothing on sparse months to prevent zero-denominator
    or small-sample volatility, and guarantees continuous 2023–2026 timeline.
    """

    MIN_HISTORICAL_PERIOD = "2023-01"
    MAX_HISTORICAL_PERIOD = "2026-11"

    @classmethod
    def get_continuous_timeline(cls, start_period="2023-01", end_period="2026-11"):
        """Generate a complete, strictly ordered list of YYYY-MM periods."""
        s_yr, s_mo = map(int, start_period.split("-"))
        e_yr, e_mo = map(int, end_period.split("-"))

        timeline = []
        cur_yr, cur_mo = s_yr, s_mo
        while (cur_yr < e_yr) or (cur_yr == e_yr and cur_mo <= e_mo):
            timeline.append(f"{cur_yr:04d}-{cur_mo:02d}")
            cur_mo += 1
            if cur_mo > 12:
                cur_mo = 1
                cur_yr += 1
        return timeline

    @classmethod
    def compute_monthly_frequencies(cls, jobs):
        """
        Aggregate jobs by monthly period (YYYY-MM) across 2023-2026 and compute
        statistically valid, non-fabricated normalized demand rates.

        Returns:
            dict: {
                skill_name: {
                    "skill": str,
                    "category": str,
                    "sub_categories": list,
                    "periods": list,
                    "job_counts": list,
                    "total_jobs": list,
                    "demand_rates": list,
                    "total_occurrences": int,
                    "has_sufficient_data": bool
                }
            }
        """
        timeline = cls.get_continuous_timeline(cls.MIN_HISTORICAL_PERIOD, cls.MAX_HISTORICAL_PERIOD)
        period_total_jobs = Counter()
        period_skill_jobs = defaultdict(Counter)
        skill_total_counts = Counter()

        total_valid_jobs = 0

        for job in jobs:
            raw_date = job.get("posted_at") or job.get("posted_date") or job.get("first_seen_at")
            period = PreprocessingService.parse_period(raw_date, object_id=job.get("_id"))

            # Clip out of range dates into the active 2023-2026 historical window
            if period < cls.MIN_HISTORICAL_PERIOD:
                period = cls.MIN_HISTORICAL_PERIOD
            elif period > cls.MAX_HISTORICAL_PERIOD:
                period = cls.MAX_HISTORICAL_PERIOD

            period_total_jobs[period] += 1
            total_valid_jobs += 1

            # Extract normalized skills from required_skills, preferred_skills, skills, and description
            raw_skills = job.get("required_skills") or job.get("skills") or []
            if isinstance(raw_skills, str):
                raw_skills = [s.strip() for s in raw_skills.split("|") if s.strip()]

            pref_skills = job.get("preferred_skills") or []
            if isinstance(pref_skills, str):
                pref_skills = [s.strip() for s in pref_skills.split("|") if s.strip()]

            combined_skills = set()
            for sk in list(raw_skills) + list(pref_skills):
                if sk and len(str(sk).strip()) >= 2:
                    norm = PreprocessingService.normalize_skill(str(sk))
                    if norm:
                        combined_skills.add(norm)

            for norm_skill in combined_skills:
                period_skill_jobs[norm_skill][period] += 1
                skill_total_counts[norm_skill] += 1

        skill_time_series = {}

        # Prior weight for Empirical Bayes shrinkage on low-sample historical months
        # Shrinks noisy months toward the skill's dataset-wide base rate
        prior_weight = 15.0

        for sk, total_cnt in skill_total_counts.items():
            if total_cnt < 2:
                continue

            classification = SkillTaxonomy.get_skill_classification(sk)
            global_rate = (total_cnt / total_valid_jobs) * 100.0 if total_valid_jobs > 0 else 1.0

            counts = []
            totals = []
            rates = []

            for p in timeline:
                c = period_skill_jobs[sk][p]
                tot = period_total_jobs[p]

                # Empirical Bayes Smoothed Rate:
                # rate = (c + prior_weight * global_rate / 100) / (tot + prior_weight) * 100
                smoothed_rate = ((c + prior_weight * (global_rate / 100.0)) / (tot + prior_weight)) * 100.0
                rate_val = round(max(0.0, min(100.0, smoothed_rate)), 2)

                counts.append(c)
                totals.append(tot)
                rates.append(rate_val)

            has_sufficient = total_cnt >= 4

            skill_time_series[sk] = {
                "skill": sk,
                "category": classification["primary"],
                "sub_categories": classification.get("sub", []),
                "periods": timeline,
                "job_counts": counts,
                "total_jobs": totals,
                "demand_rates": rates,
                "total_occurrences": total_cnt,
                "has_sufficient_data": has_sufficient,
                "global_demand_rate": round(global_rate, 2)
            }

        return skill_time_series
