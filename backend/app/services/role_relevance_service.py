import logging

logger = logging.getLogger(__name__)

class RoleRelevanceService:
    """
    Universal Domain & Role Relevance Service.
    Evaluates domain and role relevance between candidate profile (Healthcare, Accounting,
    Mechanical, Education, Marketing, Civil, HR, Sales, Software/IT, etc.)
    and job vacancy title/description.
    Classifies vacancies into:
      - DIRECT_ROLE_MATCH
      - RELATED_ROLE
      - WEAKLY_RELATED
      - UNRELATED
      - UNKNOWN
    """

    DOMAIN_KEYWORDS = {
        "HEALTHCARE": [
            "nurse", "nursing", "clinical", "hospital", "patient care", "medical",
            "doctor", "healthcare", "lab technician", "vital signs", "wound dressing"
        ],
        "ACCOUNTING_FINANCE": [
            "accountant", "accounting", "tally", "gst", "bookkeeping", "auditing",
            "accounts payable", "accounts receivable", "taxation", "finance executive",
            "financial analyst", "payroll"
        ],
        "MECHANICAL_ENGINEERING": [
            "mechanical engineer", "mechanical design", "autocad", "solidworks",
            "catia", "ansys", "machining", "manufacturing engineer", "cad engineer",
            "production engineer", "cnc"
        ],
        "CIVIL_ENGINEERING": [
            "civil engineer", "site engineer", "structural engineer", "construction engineer",
            "revit", "staad pro", "quantity surveyor", "building design"
        ],
        "ELECTRICAL_ENGINEERING": [
            "electrical engineer", "power engineer", "electrical design", "matlab",
            "simulink", "plc", "scada", "power electronics", "circuit design"
        ],
        "EDUCATION": [
            "teacher", "teaching", "b.ed", "curriculum", "school teacher", "lecturer",
            "tutor", "pedagogy", "academic counselor", "education coordinator"
        ],
        "MARKETING": [
            "marketing", "product marketing", "marketing lead", "digital marketing", "seo specialist", "marketing executive", "social media manager",
            "content marketer", "copywriter", "brand manager", "lead generation", "google ads"
        ],
        "HR": [
            "human resources", "hr executive", "recruiter", "talent acquisition",
            "hr generalist", "onboarding", "employee relations"
        ],
        "SALES": [
            "sales", "sales manager", "sales executive", "business development", "account executive", "inside sales",
            "field sales", "b2b sales", "sales representative", "client acquisition", "sales engineer"
        ],
        "SOFTWARE_IT": [
            "software developer", "software engineer", "backend developer", "backend engineer",
            "frontend developer", "frontend engineer", "full stack developer", "python developer",
            "java developer", "c++ developer", "data scientist", "data analyst", "devops engineer",
            "cloud engineer", "ai engineer", "web developer", "mobile developer"
        ],
        "DESIGN": [
            "graphic designer", "ui designer", "ux designer", "visual designer", "photoshop", "illustrator", "figma"
        ],
        "LEGAL": [
            "lawyer", "legal counsel", "legal associate", "advocate", "litigation", "corporate lawyer"
        ],
        "ARCHITECTURE": [
            "architect", "architectural designer", "building designer", "bim architect"
        ],
        "PHARMACY": [
            "pharmacist", "clinical pharmacist", "pharma executive", "drug safety associate"
        ],
        "LOGISTICS_SUPPLY_CHAIN": [
            "supply chain", "logistics executive", "procurement associate", "inventory controller"
        ],
        "HOSPITALITY": [
            "hospitality executive", "front desk officer", "guest relations", "hotel operations"
        ]
    }

    @classmethod
    def evaluate_role_relevance(cls, candidate_profile: dict, job: dict, target_role: str = None, is_explicit_role: bool = False) -> dict:
        """
        Evaluates role relevance between candidate profile / explicit target role & target job.
        Prioritizes user's explicitly intended target_role whenever supplied.
        Enforces RoleTaxonomy strict exclusion filters before ranking.
        """
        from app.services.role_taxonomy import RoleTaxonomy

        raw_title = str(job.get("title") or job.get("job_title") or "").strip()
        title = raw_title.lower()
        desc = str(job.get("raw_description") or job.get("clean_description") or "").strip().lower()
        searchable_job = f"{title} {desc[:500]}"

        if not raw_title:
            return {
                "eligible": False,
                "role_relevance_status": "UNKNOWN",
                "detected_job_role": "Unspecified Title",
                "reason": "Missing job title."
            }

        # 1. Primary Priority: Explicit User Target Role Filter (when user specifically selected/typed a role in UI)
        if is_explicit_role and target_role:
            eval_res = RoleTaxonomy.evaluate_role_match(target_role, raw_title)
            if eval_res["status"] == "STRICT_EXCLUSION" or eval_res.get("is_strictly_excluded"):
                return {
                    "eligible": False,
                    "role_relevance_status": "UNRELATED",
                    "detected_job_role": raw_title,
                    "reason": eval_res["reason"]
                }
            elif eval_res["match"]:
                return {
                    "eligible": True,
                    "role_relevance_status": "DIRECT_ROLE_MATCH" if eval_res["status"] == "DIRECT_MATCH" else "RELATED_ROLE",
                    "detected_job_role": target_role,
                    "reason": eval_res["reason"]
                }
            else:
                return {
                    "eligible": False,
                    "role_relevance_status": "UNRELATED",
                    "detected_job_role": raw_title,
                    "reason": f"Vacancy '{raw_title}' does not match explicitly selected target role '{target_role}'."
                }

        # 2. Automated Resume Recommendations Flow (or no explicit role filter)
        primary_role = (target_role or candidate_profile.get("target_role") or candidate_profile.get("preferred_job_role") or "").strip()
        inferred_roles = candidate_profile.get("inferred_roles", []) or candidate_profile.get("primary_roles", [])

        # 2a. Strict Exclusion Check against candidate's primary and inferred roles
        all_candidate_roles = ([primary_role] if primary_role else []) + list(inferred_roles)
        for cand_r in all_candidate_roles:
            eval_res = RoleTaxonomy.evaluate_role_match(cand_r, raw_title)
            if eval_res.get("status") == "STRICT_EXCLUSION" or eval_res.get("is_strictly_excluded"):
                return {
                    "eligible": False,
                    "role_relevance_status": "UNRELATED",
                    "detected_job_role": raw_title,
                    "reason": eval_res["reason"]
                }

        # 2b. Match against primary role
        if primary_role:
            eval_res = RoleTaxonomy.evaluate_role_match(primary_role, raw_title)
            if eval_res["match"]:
                return {
                    "eligible": True,
                    "role_relevance_status": "DIRECT_ROLE_MATCH" if eval_res["status"] == "DIRECT_MATCH" else "RELATED_ROLE",
                    "detected_job_role": primary_role,
                    "reason": eval_res["reason"]
                }

        # 2c. Match against other inferred roles
        for role in inferred_roles:
            if role and role != primary_role:
                eval_res = RoleTaxonomy.evaluate_role_match(role, raw_title)
                if eval_res["match"]:
                    return {
                        "eligible": True,
                        "role_relevance_status": "RELATED_ROLE",
                        "detected_job_role": role,
                        "reason": eval_res["reason"]
                    }

        # 3. Detect Job Domain
        detected_job_domain = None
        for dom_name, kw_list in cls.DOMAIN_KEYWORDS.items():
            for kw in kw_list:
                if kw in title:
                    detected_job_domain = dom_name
                    break
            if detected_job_domain:
                break

        cand_domain = str(candidate_profile.get("professional_domain") or "GENERAL_PROFESSIONAL").upper().strip()

        # Hard cross-domain check: prevent accountant showing up for software_it/data_analytics
        if cand_domain in ["SOFTWARE_IT", "DATA_ANALYTICS", "DATA_SCIENCE_AI"] and detected_job_domain in ["ACCOUNTING_FINANCE", "ARCHITECTURE", "HEALTHCARE"]:
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": raw_title,
                "reason": f"Vacancy in {detected_job_domain.title()} is strictly unrelated to candidate's technical profile."
            }

        # 4. Domain Match Check: Candidate Domain vs Job Domain
        if cand_domain in cls.DOMAIN_KEYWORDS and detected_job_domain:
            if cand_domain == detected_job_domain:
                return {
                    "eligible": True,
                    "role_relevance_status": "RELATED_ROLE",
                    "detected_job_role": raw_title,
                    "reason": f"Vacancy aligns with candidate's professional domain ({cand_domain.title()})."
                }
            else:
                return {
                    "eligible": False,
                    "role_relevance_status": "UNRELATED",
                    "detected_job_role": raw_title,
                    "reason": f"Vacancy in {detected_job_domain.title()} is unrelated to candidate's domain ({cand_domain.title()})."
                }

        # 5. Core skill overlap check only if within same general technical umbrella
        core_skills = [str(s).lower().strip() for s in candidate_profile.get("core_skills", []) if s]
        matched_skills = [s for s in core_skills if s in searchable_job]
        if len(matched_skills) >= 2:
            return {
                "eligible": True,
                "role_relevance_status": "RELATED_ROLE",
                "detected_job_role": raw_title,
                "reason": f"Matched candidate core domain skills ({', '.join(matched_skills[:3])})."
            }

        return {
            "eligible": False,
            "role_relevance_status": "UNRELATED",
            "detected_job_role": raw_title,
            "reason": f"Vacancy '{raw_title}' does not match candidate target roles or professional domain."
        }

