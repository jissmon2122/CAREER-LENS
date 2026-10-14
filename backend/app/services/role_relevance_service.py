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
        "SKILLED_TRADES_ELECTRICAL": [
            "electrician", "electrical technician", "wiring", "conduit", "journeyman electrician",
            "master electrician", "electrical maintenance", "lineman", "wireman", "low voltage technician"
        ],
        "SKILLED_TRADES_PLUMBING": [
            "plumber", "plumbing", "pipefitter", "steamfitter", "drain cleaning",
            "journeyman plumber", "master plumber", "piping"
        ],
        "SKILLED_TRADES_WELDING": [
            "welder", "welding", "fabricator", "mig welder", "tig welder", "arc welder",
            "pipe welder", "structural welder"
        ],
        "SKILLED_TRADES_MECHANIC": [
            "automotive technician", "mechanic", "auto mechanic", "diesel mechanic",
            "fleet mechanic", "heavy equipment mechanic", "service technician", "brake technician"
        ],
        "SKILLED_TRADES_HVAC": [
            "hvac technician", "hvac", "refrigeration technician", "heating and cooling",
            "hvac installer", "air conditioning technician", "epa 608"
        ],
        "HEALTHCARE_SUPPORT": [
            "certified nursing assistant", "cna", "medical assistant", "caregiver", "home health aide",
            "phlebotomist", "dental assistant", "physical therapy aide", "patient care technician"
        ],
        "HEALTHCARE_NURSING": [
            "registered nurse", "staff nurse", "clinical nurse", "icu nurse", "charge nurse",
            "nurse practitioner", "triage nurse", "er nurse", "home health nurse"
        ],
        "HEALTHCARE": [
            "nurse", "nursing", "clinical", "hospital", "patient care", "medical",
            "doctor", "healthcare", "lab technician", "vital signs", "wound dressing"
        ],
        "ACCOUNTING_FINANCE": [
            "accountant", "accounting", "tally", "gst", "bookkeeping", "auditing",
            "accounts payable", "accounts receivable", "taxation", "finance executive",
            "financial analyst", "payroll"
        ],
        "EDUCATION_TEACHING": [
            "teacher", "teaching", "b.ed", "curriculum", "school teacher", "lecturer",
            "tutor", "pedagogy", "academic counselor", "education coordinator", "elementary teacher", "high school teacher"
        ],
        "EDUCATION": [
            "teacher", "teaching", "curriculum", "lecturer", "tutor", "pedagogy", "instructor"
        ],
        "ADMINISTRATION_OFFICE": [
            "administrative assistant", "office assistant", "executive assistant", "receptionist",
            "office administrator", "clerk", "data entry", "office manager"
        ],
        "HOSPITALITY_CULINARY": [
            "chef", "cook", "line cook", "prep cook", "sous chef", "kitchen assistant",
            "food preparation", "baker", "barista", "culinary"
        ],
        "HOSPITALITY": [
            "hospitality executive", "front desk officer", "guest relations", "hotel operations", "restaurant manager"
        ],
        "LOGISTICS_WAREHOUSE": [
            "forklift operator", "warehouse associate", "warehouse worker", "material handler",
            "order picker", "shipping and receiving", "truck driver", "delivery driver", "cdl driver", "logistics coordinator"
        ],
        "CONSTRUCTION_CARPENTRY": [
            "carpenter", "carpentry", "framing carpenter", "construction worker",
            "drywall installer", "mason", "masonry", "roofing", "general laborer"
        ],
        "SALES_RETAIL": [
            "retail associate", "cashier", "store associate", "sales associate", "customer service representative"
        ],
        "AGRICULTURE_FARMING": [
            "farm worker", "agricultural worker", "farmhand", "greenhouse worker", "irrigation technician", "ranch hand"
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
        "MARKETING": [
            "marketing", "product marketing", "marketing lead", "digital marketing", "seo specialist", "marketing executive", "social media manager",
            "content marketer", "copywriter", "brand manager", "lead generation", "google ads"
        ],
        "HR": [
            "human resources", "hr executive", "recruiter", "talent acquisition",
            "hr generalist", "onboarding", "employee relations"
        ],
        "HUMAN_RESOURCES": [
            "human resources", "hr executive", "recruiter", "talent acquisition", "hr generalist"
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
        "DATA_ANALYTICS": [
            "data analyst", "bi analyst", "business intelligence", "sql developer", "tableau", "power bi"
        ],
        "DESIGN": [
            "graphic designer", "ui designer", "ux designer", "visual designer", "photoshop", "illustrator", "figma"
        ],
        "DESIGN_CREATIVE": [
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
        ]
    }

    DOMAIN_GROUPS = {
        "SKILLED_TRADES_ELECTRICAL": {"SKILLED_TRADES_ELECTRICAL"},
        "SKILLED_TRADES_PLUMBING": {"SKILLED_TRADES_PLUMBING"},
        "SKILLED_TRADES_WELDING": {"SKILLED_TRADES_WELDING"},
        "SKILLED_TRADES_MECHANIC": {"SKILLED_TRADES_MECHANIC"},
        "SKILLED_TRADES_HVAC": {"SKILLED_TRADES_HVAC"},
        "HEALTHCARE": {"HEALTHCARE", "HEALTHCARE_SUPPORT", "HEALTHCARE_NURSING", "PHARMACY"},
        "HEALTHCARE_SUPPORT": {"HEALTHCARE", "HEALTHCARE_SUPPORT", "HEALTHCARE_NURSING"},
        "HEALTHCARE_NURSING": {"HEALTHCARE", "HEALTHCARE_SUPPORT", "HEALTHCARE_NURSING"},
        "ACCOUNTING_FINANCE": {"ACCOUNTING_FINANCE"},
        "EDUCATION": {"EDUCATION", "EDUCATION_TEACHING"},
        "EDUCATION_TEACHING": {"EDUCATION", "EDUCATION_TEACHING"},
        "ADMINISTRATION_OFFICE": {"ADMINISTRATION_OFFICE"},
        "HOSPITALITY": {"HOSPITALITY", "HOSPITALITY_CULINARY"},
        "HOSPITALITY_CULINARY": {"HOSPITALITY", "HOSPITALITY_CULINARY"},
        "LOGISTICS_WAREHOUSE": {"LOGISTICS_WAREHOUSE", "LOGISTICS_SUPPLY_CHAIN"},
        "LOGISTICS_SUPPLY_CHAIN": {"LOGISTICS_WAREHOUSE", "LOGISTICS_SUPPLY_CHAIN"},
        "CONSTRUCTION_CARPENTRY": {"CONSTRUCTION_CARPENTRY", "CIVIL_ENGINEERING"},
        "SALES_RETAIL": {"SALES_RETAIL", "SALES", "MARKETING"},
        "SALES": {"SALES_RETAIL", "SALES", "MARKETING"},
        "AGRICULTURE_FARMING": {"AGRICULTURE_FARMING"},
        "MECHANICAL_ENGINEERING": {"MECHANICAL_ENGINEERING"},
        "CIVIL_ENGINEERING": {"CIVIL_ENGINEERING", "CONSTRUCTION_CARPENTRY"},
        "ELECTRICAL_ENGINEERING": {"ELECTRICAL_ENGINEERING"},
        "SOFTWARE_IT": {"SOFTWARE_IT", "DATA_ANALYTICS"},
        "DATA_ANALYTICS": {"SOFTWARE_IT", "DATA_ANALYTICS"},
        "HUMAN_RESOURCES": {"HUMAN_RESOURCES", "HR"},
        "HR": {"HUMAN_RESOURCES", "HR"}
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

        # Hard cross-domain check: prevent software jobs from being recommended to non-software profiles and vice-versa
        non_software_domains = [
            "SKILLED_TRADES_ELECTRICAL", "SKILLED_TRADES_PLUMBING", "SKILLED_TRADES_WELDING",
            "SKILLED_TRADES_MECHANIC", "SKILLED_TRADES_HVAC", "HEALTHCARE", "HEALTHCARE_SUPPORT",
            "HEALTHCARE_NURSING", "EDUCATION", "EDUCATION_TEACHING", "ACCOUNTING_FINANCE",
            "ADMINISTRATION_OFFICE", "HOSPITALITY", "HOSPITALITY_CULINARY", "LOGISTICS_WAREHOUSE",
            "CONSTRUCTION_CARPENTRY", "AGRICULTURE_FARMING"
        ]
        if cand_domain in non_software_domains and detected_job_domain in ["SOFTWARE_IT", "DATA_ANALYTICS"]:
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": raw_title,
                "reason": f"Software/IT vacancy is strictly unrelated to candidate's {cand_domain.title()} profile."
            }

        if cand_domain in ["SOFTWARE_IT", "DATA_ANALYTICS"] and detected_job_domain in non_software_domains:
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": raw_title,
                "reason": f"Vacancy in {detected_job_domain.title()} is strictly unrelated to candidate's technical profile."
            }

        # 4. Domain Match Check: Candidate Domain vs Job Domain
        if cand_domain in cls.DOMAIN_KEYWORDS and detected_job_domain:
            allowed_group = cls.DOMAIN_GROUPS.get(cand_domain, {cand_domain})
            if detected_job_domain in allowed_group:
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

