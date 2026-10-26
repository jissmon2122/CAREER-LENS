"""
Salary Service for CareerLens.
Orchestrates:
- Canonical role resolution & domain validation
- Machine learning model prediction
- Live market checks via Adzuna / MongoDB where supported
- Profile autofill from user's latest parsed resume
- Metadata listings (supported roles, countries, currencies, cities)
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.role_taxonomy import RoleTaxonomy
from app.services.salary.benchmarks import (
    CURRENCY_MAP,
    SUPPORTED_COUNTRIES,
    CITY_MULTIPLIERS,
    get_role_domain,
)
from app.services.salary.model_engine import SalaryModelEngine

logger = logging.getLogger(__name__)

class SalaryService:
    @staticmethod
    def get_supported_roles() -> Dict[str, Any]:
        """Return all supported canonical roles grouped by domain for clean UI dropdowns and search."""
        domains: Dict[str, List[str]] = {}
        for role, data in RoleTaxonomy.ROLE_TAXONOMY.items():
            domain = data.get("domain", "OTHER")
            # Human-friendly domain label
            domain_label = domain.replace("_", " ").title()
            domains.setdefault(domain_label, []).append(role)

        for d in domains:
            domains[d].sort()

        all_roles = sorted(list(RoleTaxonomy.ROLE_TAXONOMY.keys()))
        return {
            "total_roles": len(all_roles),
            "domains": domains,
            "roles": all_roles
        }

    @staticmethod
    def get_supported_locations() -> Dict[str, Any]:
        """Return supported countries, currencies, and major city hubs with cost multipliers."""
        locations = []
        for country in SUPPORTED_COUNTRIES:
            code = country["code"]
            cities = []
            c_dict = CITY_MULTIPLIERS.get(code, {})
            for city_key, mult in c_dict.items():
                if city_key != "default":
                    cities.append({
                        "name": city_key.title(),
                        "multiplier": mult,
                        "tier": "Tier 1" if mult >= 1.15 else ("Tier 2" if mult >= 1.00 else "Tier 3")
                    })
            cities.sort(key=lambda x: x["name"])
            locations.append({
                **country,
                "cities": cities
            })
        return {
            "countries": locations,
            "currency_map": CURRENCY_MAP
        }

    @staticmethod
    def predict_salary(
        role_title: str,
        country: str = "IN",
        city: str = "",
        experience_years: float = 3.0,
        seniority: str = "mid",
        education: str = "bachelor",
        skills: Optional[List[str]] = None,
        industry: str = "Technology",
        company_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Produce a comprehensive salary prediction report for any profession.
        """
        skills = skills or []
        country = (country or "IN").upper()
        if country not in CURRENCY_MAP:
            country = "IN"

        # 1. Resolve Canonical Role and Domain
        entry = RoleTaxonomy.find_taxonomy_entry(role_title)
        canonical_role = entry.get("canonical") if entry else (role_title or "").strip()
        domain = get_role_domain(canonical_role)

        # 2. Invoke Model Engine
        engine = SalaryModelEngine.get_instance()
        prediction = engine.predict_salary_curve(
            domain=domain,
            country=country,
            city=city,
            experience_years=experience_years,
            seniority=seniority,
            education=education,
            skills=skills,
            company_type=company_type
        )

        # 3. Augment with Role Information
        prediction["role"] = {
            "input_title": role_title,
            "canonical_title": canonical_role,
            "domain": domain,
            "domain_label": domain.replace("_", " ").title()
        }
        prediction["industry"] = industry or "General"
        prediction["company_type"] = company_type.title()

        return prediction

    @staticmethod
    def get_market_overview(role_title: str, country: str = "IN") -> Dict[str, Any]:
        """Return broad labor market salary overview across multiple experience levels for a role."""
        country = (country or "IN").upper()
        if country not in CURRENCY_MAP:
            country = "IN"

        entry = RoleTaxonomy.find_taxonomy_entry(role_title)
        canonical_role = entry.get("canonical") if entry else role_title
        domain = get_role_domain(canonical_role)
        engine = SalaryModelEngine.get_instance()

        levels = [
            ("Entry (0-2 Yrs)", 1.0, "entry"),
            ("Mid (3-6 Yrs)", 4.0, "mid"),
            ("Senior (7-10 Yrs)", 8.0, "senior"),
            ("Lead / Staff (10+ Yrs)", 12.0, "lead"),
        ]

        overview_benchmarks = []
        for label, exp, sen in levels:
            res = engine.predict_salary_curve(
                domain=domain,
                country=country,
                city="",
                experience_years=exp,
                seniority=sen,
                education="bachelor",
                skills=[]
            )
            overview_benchmarks.append({
                "level": label,
                "median": res["annual"]["median"],
                "range_formatted": res["annual"]["range_formatted"],
                "monthly_median": res["monthly"]["median"],
                "monthly_formatted": res["monthly"]["median_formatted"]
            })

        curr_info = CURRENCY_MAP[country]
        return {
            "role": canonical_role,
            "domain": domain,
            "domain_label": domain.replace("_", " ").title(),
            "country": country,
            "currency": curr_info["currency"],
            "currency_symbol": curr_info["symbol"],
            "benchmarks": overview_benchmarks
        }

    @staticmethod
    def extract_autofill_from_user(user_id: str) -> Dict[str, Any]:
        """
        Extract profile parameters from the user's latest parsed resume in MongoDB.
        """
        try:
            from bson import ObjectId
            from app.db import Database
            db = Database.get_db()
            if db is None:
                return {"success": False, "message": "Database unavailable"}

            # Query the user's latest resume or analysis
            user_obj_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            resume_doc = db.resumes.find_one(
                {"user_id": user_obj_id},
                sort=[("created_at", -1), ("uploaded_at", -1)]
            )
            if not resume_doc:
                # Also check analyses collection
                analysis_doc = db.analyses.find_one(
                    {"user_id": user_obj_id},
                    sort=[("created_at", -1)]
                )
                if analysis_doc:
                    resume_doc = analysis_doc.get("resume_data", {})

            if not resume_doc:
                return {
                    "success": False,
                    "has_resume": False,
                    "message": "No parsed resume found for user. Manual entry available."
                }

            # Extract fields
            extracted_title = (
                resume_doc.get("target_role")
                or resume_doc.get("profession")
                or resume_doc.get("role")
                or resume_doc.get("job_title")
                or ""
            )
            extracted_exp = float(resume_doc.get("experience_years") or resume_doc.get("total_experience") or 3.0)
            skills = resume_doc.get("skills") or resume_doc.get("extracted_skills") or []
            location = resume_doc.get("location") or "Bengaluru"
            education = resume_doc.get("education_level") or "Bachelor"

            # Derive seniority from experience
            seniority = "mid"
            if extracted_exp < 2:
                seniority = "entry"
            elif extracted_exp >= 7:
                seniority = "senior"
            elif extracted_exp >= 11:
                seniority = "lead"

            # Parse city / country
            country = "IN"
            loc_l = location.lower()
            if any(c in loc_l for c in ["usa", "united states", "california", "new york", "san francisco", "texas", "seattle"]):
                country = "US"
            elif any(c in loc_l for c in ["uk", "united kingdom", "london", "england", "manchester"]):
                country = "GB"
            elif any(c in loc_l for c in ["canada", "toronto", "vancouver"]):
                country = "CA"
            elif any(c in loc_l for c in ["germany", "berlin", "munich"]):
                country = "DE"
            elif any(c in loc_l for c in ["australia", "sydney", "melbourne"]):
                country = "AU"

            entry = RoleTaxonomy.find_taxonomy_entry(extracted_title)
            canonical_role = entry.get("canonical") if entry else extracted_title

            return {
                "success": True,
                "has_resume": True,
                "profile": {
                    "role": canonical_role,
                    "raw_role": extracted_title,
                    "experience_years": extracted_exp,
                    "seniority": seniority,
                    "skills": skills[:15] if isinstance(skills, list) else [],
                    "city": location.split(",")[0].strip(),
                    "country": country,
                    "education": education
                }
            }
        except Exception as e:
            logger.error("Error extracting salary autofill for user %s: %s", user_id, e)
            return {"success": False, "message": str(e)}
