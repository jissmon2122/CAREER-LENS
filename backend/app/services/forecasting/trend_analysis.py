class TrendAnalysisEngine:
    """
    Skill Demand Trend Classification Engine.
    Categorizes skills into RISING, STABLE, DECLINING, and EMERGING trend categories with rationale.
    """

    @classmethod
    def classify_trend(cls, history, current_demand, predicted_demand):
        """
        Classify trend given historical demand rates and predicted demand.
        
        Returns:
            dict: { "trend": "RISING"|"STABLE"|"DECLINING"|"EMERGING", "trend_label": str, "growth_rate": str, "reason": str }
        """
        diff = round(predicted_demand - current_demand, 2)
        rel_change = round((diff / current_demand * 100), 1) if current_demand > 0 else 0.0

        # Emerging: Low baseline (< 35%) but high relative growth (> 20%)
        if current_demand < 35.0 and rel_change >= 20.0:
            trend = "EMERGING"
            label = "🚀 Emerging Skill"
            reason = f"High adoption velocity with +{rel_change}% relative demand growth."
        elif diff >= 3.0:
            trend = "RISING"
            label = "🔥 Rising Demand"
            reason = f"Sustained positive demand trajectory (+{diff}% absolute growth)."
        elif diff <= -3.0:
            trend = "DECLINING"
            label = "📉 Declining Trend"
            reason = f"Negative demand trend (-{abs(diff)}% absolute change)."
        else:
            trend = "STABLE"
            label = "🟢 Stable Demand"
            reason = f"Consistent baseline market demand (~{current_demand}%)."

        return {
            "trend": trend,
            "trend_label": label,
            "growth_rate": f"+{diff}%" if diff >= 0 else f"{diff}%",
            "relative_growth": f"+{rel_change}%" if rel_change >= 0 else f"{rel_change}%",
            "reason": reason
        }
