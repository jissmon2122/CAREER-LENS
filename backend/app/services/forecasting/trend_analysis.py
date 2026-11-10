class TrendAnalysisEngine:
    """
    Skill Demand Trend Classification Engine.
    Categorizes skills into RISING, STABLE, DECLINING, and EMERGING trend categories
    based on historical and projected demand dynamics.
    """

    @classmethod
    def classify_trend(cls, history, current_demand, predicted_demand):
        """
        Classify trend given historical demand rates and predicted demand.

        Returns:
            dict: {
                "trend": "RISING"|"STABLE"|"DECLINING"|"EMERGING",
                "trend_label": str,
                "growth_rate": str,
                "relative_growth": str,
                "growth_diff": float,
                "reason": str
            }
        """
        current = float(current_demand) if current_demand else 0.0
        predicted = float(predicted_demand) if predicted_demand else current

        abs_diff = round(predicted - current, 2)
        rel_change = round((abs_diff / max(0.5, current)) * 100.0, 1) if current > 0 else 0.0

        # Emerging: Low current baseline (< 10%) but high relative growth (>= 20%)
        if current < 10.0 and rel_change >= 20.0 and abs_diff >= 0.5:
            trend = "EMERGING"
            label = "🚀 Emerging Skill"
            reason = f"High adoption momentum with +{rel_change}% relative growth trajectory."
        elif abs_diff >= 1.5 or rel_change >= 15.0:
            trend = "RISING"
            label = "🔥 Rising Demand"
            reason = f"Sustained positive demand trajectory (+{abs_diff}% absolute, +{rel_change}% relative)."
        elif abs_diff <= -1.5 or rel_change <= -15.0:
            trend = "DECLINING"
            label = "📉 Declining Trend"
            reason = f"Negative market trajectory ({abs_diff}% absolute change)."
        else:
            trend = "STABLE"
            label = "🟢 Stable Demand"
            reason = f"Consistent baseline market demand (~{current}% demand rate)."

        return {
            "trend": trend,
            "trend_label": label,
            "growth_rate": f"+{abs_diff}%" if abs_diff >= 0 else f"{abs_diff}%",
            "relative_growth": f"+{rel_change}%" if rel_change >= 0 else f"{rel_change}%",
            "growth_diff": abs_diff,
            "reason": reason
        }
