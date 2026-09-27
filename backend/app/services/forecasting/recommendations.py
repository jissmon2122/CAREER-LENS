DOMAIN_SKILLS = {
    "HEALTHCARE": ["nursing", "patient care", "clinical research", "pharmacology", "vital signs", "wound dressing", "iv administration", "ehr systems", "telehealth", "medical terminology"],
    "ACCOUNTING_FINANCE": ["tally prime", "gst", "financial analysis", "auditing", "accounts payable", "taxation", "excel", "financial modeling", "bookkeeping", "corporate finance"],
    "MECHANICAL_ENGINEERING": ["autocad", "solidworks", "catia", "ansys", "cnc machining", "hvac", "thermodynamics", "mechanical design", "gd&t", "manufacturing"],
    "CIVIL_ENGINEERING": ["autocad civil 3d", "revit", "staad pro", "structural design", "site engineering", "quantity surveying", "bim", "construction management"],
    "ELECTRICAL_ENGINEERING": ["power electronics", "plc", "scada", "circuit design", "matlab", "power systems", "high voltage", "switchgear", "automation"],
    "EDUCATION": ["curriculum development", "classroom management", "edtech", "lesson planning", "pedagogy", "student assessment", "online teaching", "academic counseling"],
    "MARKETING": ["digital marketing", "seo", "google ads", "social media marketing", "content strategy", "copywriting", "email marketing", "lead generation", "google analytics"],
    "SALES": ["b2b sales", "crm", "lead generation", "key account management", "cold calling", "sales strategy", "client acquisition", "negotiation"],
    "SOFTWARE_IT": ["python", "react", "node.js", "aws", "docker", "kubernetes", "sql", "data science", "machine learning", "typescript", "git"],
    "SCIENCE_RESEARCH": ["scientific research", "python", "matlab", "data analysis", "spectroscopy", "experimental design", "statistical modeling", "latex", "laboratory research", "quantum computing"],
    "DESIGN": ["figma", "photoshop", "illustrator", "ui/ux design", "typography", "indesign", "visual design", "wireframing"],
    "LEGAL": ["contract drafting", "corporate law", "legal research", "compliance", "litigation", "intellectual property", "due diligence"],
    "ARCHITECTURE": ["revit architecture", "building design", "autocad", "spatial design", "bim", "3ds max", "architectural drafting"],
    "LOGISTICS_SUPPLY_CHAIN": ["supply chain management", "inventory control", "logistics", "procurement", "warehouse management", "sap", "vendor management"],
    "HOSPITALITY": ["guest relations", "front desk operations", "hotel management", "event coordination", "customer experience", "hospitality management"]
}

class ForecastingRecommendationEngine:
    """
    Personalized Future Skill Recommendation Engine.
    Combines candidate resume skill gap + target job requirements + candidate professional domain + future market demand forecasts
    to prioritize candidate learning objectives.
    """

    @classmethod
    def generate_recommendations(cls, candidate_gap, forecasts_by_skill, candidate_profile=None, candidate_skills=None):
        """
        Generate personalized future skill recommendations tailored to candidate domain and possessed skills.
        """
        if candidate_skills is None:
            candidate_skills = []

        cand_skill_set = set(str(s).lower().strip() for s in candidate_skills if s)

        domain = (candidate_profile.get("professional_domain") if candidate_profile else "GENERAL_PROFESSIONAL") or "GENERAL_PROFESSIONAL"
        domain_skill_names = DOMAIN_SKILLS.get(domain, DOMAIN_SKILLS.get("SOFTWARE_IT"))

        prioritized_gaps = candidate_gap.get("prioritized_gaps", []) if candidate_gap else []
        recommendations = []
        seen_skills = set()

        # 1. Process prioritized gaps from skill gap engine
        for item in prioritized_gaps:
            sk = item["skill"]
            sk_clean = sk.lower().strip()
            seen_skills.add(sk_clean)
            fc = forecasts_by_skill.get(sk_clean, {})

            trend = fc.get("trend", "RISING")
            predicted_demand = fc.get("predicted_demand", 55.0)
            mae = fc.get("mae", 1.8)

            is_already_possessed = sk_clean in cand_skill_set

            if is_already_possessed:
                priority = "STRENGTHEN & ADVANCE"
                gap_type = "Possessed & Rising"
                reason = f"You already possess {sk.title()}. Market demand is {trend} ({predicted_demand}% adoption) — strengthen and advance your expertise."
            else:
                if trend in ("RISING", "EMERGING") or item.get("priority") in ("CRITICAL", "HIGH"):
                    priority = "HIGH PRIORITY"
                else:
                    priority = "RECOMMENDED"
                gap_type = item.get("category", "Required Skill")
                reason = f"Essential for {domain.title()} roles & Market Demand is {trend} ({predicted_demand}% projected adoption)."

            recommendations.append({
                "skill": sk.title(),
                "priority": priority,
                "gap_type": gap_type,
                "trend": trend,
                "predicted_market_demand": f"{predicted_demand}%",
                "model_mae": mae,
                "is_possessed": is_already_possessed,
                "recommendation_reason": reason
            })

        # 2. Add domain-specific rising skills if gap list is short
        for d_sk in domain_skill_names:
            d_sk_clean = d_sk.lower().strip()
            if d_sk_clean not in seen_skills:
                seen_skills.add(d_sk_clean)
                fc = forecasts_by_skill.get(d_sk_clean, {})
                trend = fc.get("trend", "RISING")
                predicted_demand = fc.get("predicted_demand", 50.0)
                mae = fc.get("mae", 2.0)
                is_already_possessed = d_sk_clean in cand_skill_set

                if is_already_possessed:
                    priority = "STRENGTHEN & ADVANCE"
                    gap_type = "Possessed & Rising"
                    reason = f"You possess {d_sk.title()}. Demand is projected at {predicted_demand}% for {domain.title()} roles — deepen your mastery."
                else:
                    priority = "HIGH PRIORITY" if trend in ("RISING", "EMERGING") else "RECOMMENDED"
                    gap_type = "Emerging Domain Skill"
                    reason = f"Key emerging skill in {domain.title()} with {trend} market demand ({predicted_demand}% projected adoption)."

                recommendations.append({
                    "skill": d_sk.title(),
                    "priority": priority,
                    "gap_type": gap_type,
                    "trend": trend,
                    "predicted_market_demand": f"{predicted_demand}%",
                    "model_mae": mae,
                    "is_possessed": is_already_possessed,
                    "recommendation_reason": reason
                })

        # Sort recommendations: HIGH PRIORITY and STRENGTHEN first, then by market demand descending
        def sort_key(r):
            p_val = 2 if r["priority"] == "HIGH PRIORITY" else (1 if r["priority"] == "STRENGTHEN & ADVANCE" else 0)
            d_val = float(r["predicted_market_demand"].replace("%", ""))
            return (p_val, d_val)

        recommendations.sort(key=sort_key, reverse=True)
        return recommendations[:10]
