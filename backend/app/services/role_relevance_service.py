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
    def evaluate_role_relevance(cls, candidate_profile: dict, job: dict) -> dict:
        """
        Evaluates role relevance between candidate profile & target job.
        Returns dict:
          - eligible: bool
          - role_relevance_status: "DIRECT_ROLE_MATCH" | "RELATED_ROLE" | "WEAKLY_RELATED" | "UNRELATED" | "UNKNOWN"
          - detected_job_role: str
          - reason: str
        """
        title = str(job.get("title") or job.get("job_title") or "").strip().lower()
        desc = str(job.get("raw_description") or job.get("clean_description") or "").strip().lower()
        searchable_job = f"{title} {desc[:500]}"

        if not title:
            return {
                "eligible": False,
                "role_relevance_status": "UNKNOWN",
                "detected_job_role": "Unspecified Title",
                "reason": "Missing job title."
            }

        cand_domain = str(candidate_profile.get("professional_domain") or "GENERAL_PROFESSIONAL").upper().strip()
        inferred_roles = candidate_profile.get("inferred_roles", [])
        cand_roles_lower = [str(r).lower().strip() for r in inferred_roles if r]
        core_skills = [str(s).lower().strip() for s in candidate_profile.get("core_skills", []) if s]

        # Detect the job's domain
        detected_job_domain = None
        for dom_name, kw_list in cls.DOMAIN_KEYWORDS.items():
            for kw in kw_list:
                if kw in title:
                    detected_job_domain = dom_name
                    break
            if detected_job_domain:
                break

        # 1. Direct Target Role Match check (job title contains candidate's inferred target role)
        for role in cand_roles_lower:
            clean_role = role.replace("junior ", "").replace(" intern", "").replace("senior ", "").strip()
            if clean_role and clean_role in title:
                return {
                    "eligible": True,
                    "role_relevance_status": "DIRECT_ROLE_MATCH",
                    "detected_job_role": role.title(),
                    "reason": f"Job title explicitly matches candidate target role '{role.title()}'."
                }

        # 2. Domain Match Check: Candidate Domain vs Job Domain
        if cand_domain in cls.DOMAIN_KEYWORDS and detected_job_domain:
            if cand_domain == detected_job_domain:
                return {
                    "eligible": True,
                    "role_relevance_status": "RELATED_ROLE",
                    "detected_job_role": title.title(),
                    "reason": f"Vacancy aligns with candidate's professional domain ({cand_domain.title()})."
                }
            else:
                return {
                    "eligible": False,
                    "role_relevance_status": "UNRELATED",
                    "detected_job_role": title.title(),
                    "reason": f"Vacancy in {detected_job_domain.title()} is unrelated to candidate's domain ({cand_domain.title()})."
                }

        # 3. Core skill overlap check
        matched_skills = [s for s in core_skills if s in searchable_job]
        if matched_skills:
            return {
                "eligible": True,
                "role_relevance_status": "RELATED_ROLE" if len(matched_skills) >= 2 else "WEAKLY_RELATED",
                "detected_job_role": title.title(),
                "reason": f"Matched candidate core domain skills ({', '.join(matched_skills[:3])})."
            }

        # 4. Fallback for General / Unmapped Domains
        if cand_domain != "GENERAL_PROFESSIONAL" and detected_job_domain and cand_domain != detected_job_domain:
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": title.title(),
                "reason": f"Vacancy '{title.title()}' does not align with candidate profile ({cand_domain.title()})."
            }

        return {
            "eligible": True,
            "role_relevance_status": "WEAKLY_RELATED",
            "detected_job_role": title.title(),
            "reason": "General role alignment."
        }

