import logging

logger = logging.getLogger(__name__)

class RoleRelevanceService:
    """
    Universal Domain & Role Relevance Service.
    Evaluates domain and role relevance between candidate profile (AI/ML, Data Science,
    Full Stack, Frontend, Backend, Cloud/DevOps, Cybersecurity, QA, Skilled Trades,
    Healthcare, Accounting/Finance, Education, Marketing, Civil/Mechanical Engineering, HR, Sales, etc.)
    and job vacancy title/description.
    Classifies vacancies into:
      - DIRECT_ROLE_MATCH
      - RELATED_ROLE
      - WEAKLY_RELATED
      - UNRELATED
      - UNKNOWN
    """

    DOMAIN_KEYWORDS = {
        # AI & Machine Learning
        "AI_ML": [
            "ai engineer", "machine learning engineer", "ml engineer", "artificial intelligence",
            "applied ai engineer", "generative ai engineer", "genai", "llm engineer",
            "nlp engineer", "computer vision engineer", "mlops engineer", "deep learning engineer",
            "research engineer", "ai research", "prompt engineer"
        ],
        # Data Science & Analytics
        "DATA_SCIENCE_ANALYTICS": [
            "data scientist", "junior data scientist", "data analyst", "junior data analyst",
            "business intelligence analyst", "bi analyst", "bi developer", "business analyst",
            "reporting analyst", "data engineer", "analytics engineer", "tableau developer",
            "power bi developer", "data specialist"
        ],
        # Full Stack Development
        "FULL_STACK_DEVELOPMENT": [
            "full stack developer", "full stack engineer", "fullstack developer",
            "mern stack developer", "mean stack developer", "react and node",
            "java full stack developer", "python full stack developer", "full stack web developer"
        ],
        # Frontend Development
        "FRONTEND_DEVELOPMENT": [
            "frontend developer", "front end developer", "frontend engineer",
            "react developer", "angular developer", "vue.js developer", "vue developer",
            "ui engineer", "ui developer", "client side developer", "web developer"
        ],
        # Backend Development
        "BACKEND_DEVELOPMENT": [
            "backend developer", "back end developer", "backend engineer",
            "python developer", "java developer", "node.js developer", "node developer",
            "api developer", ".net developer", "c# developer", "php developer", "laravel developer",
            "spring boot developer", "django developer"
        ],
        # Cloud & Infrastructure
        "CLOUD_INFRASTRUCTURE": [
            "devops engineer", "cloud engineer", "aws engineer", "azure engineer",
            "gcp engineer", "platform engineer", "site reliability engineer", "sre",
            "infrastructure engineer", "cloud solutions architect"
        ],
        # Cybersecurity
        "CYBERSECURITY": [
            "security analyst", "soc analyst", "cybersecurity analyst", "cyber security specialist",
            "penetration tester", "pen tester", "ethical hacker", "security engineer",
            "vulnerability analyst", "incident response analyst", "information security analyst"
        ],
        # QA & Testing
        "QA_TESTING": [
            "qa engineer", "software tester", "automation test engineer", "sdet",
            "quality assurance engineer", "manual tester", "test automation engineer"
        ],
        # Software Development (General)
        "SOFTWARE_DEVELOPMENT": [
            "software engineer", "software developer", "application developer",
            "junior software engineer", "graduate software engineer", "programmer"
        ],
        # Skilled Trades
        "SKILLED_TRADES_ELECTRICAL": [
            "electrician", "electrical technician", "wiring", "conduit", "journeyman electrician",
            "master electrician", "electrical maintenance", "lineman", "wireman", "low voltage technician",
            "industrial electrician", "commercial electrician", "residential electrician"
        ],
        "SKILLED_TRADES_PLUMBING": [
            "plumber", "plumbing", "pipefitter", "steamfitter", "drain cleaning",
            "journeyman plumber", "master plumber", "piping technician"
        ],
        "SKILLED_TRADES_WELDING": [
            "welder", "welding", "fabricator", "mig welder", "tig welder", "arc welder",
            "pipe welder", "structural welder", "metal fabricator"
        ],
        "SKILLED_TRADES_MECHANIC": [
            "automotive technician", "mechanic", "auto mechanic", "diesel mechanic",
            "fleet mechanic", "heavy equipment mechanic", "service technician", "brake technician",
            "automotive mechanic", "maintenance technician"
        ],
        "SKILLED_TRADES_HVAC": [
            "hvac technician", "hvac", "refrigeration technician", "heating and cooling",
            "hvac installer", "air conditioning technician", "epa 608"
        ],
        # Healthcare
        "HEALTHCARE_NURSING": [
            "registered nurse", "staff nurse", "clinical nurse", "icu nurse", "charge nurse",
            "nurse practitioner", "triage nurse", "er nurse", "nurse", "nursing", "hospital nurse"
        ],
        "HEALTHCARE_SUPPORT": [
            "certified nursing assistant", "cna", "medical assistant", "caregiver", "home health aide",
            "phlebotomist", "dental assistant", "physical therapy aide", "patient care technician",
            "medical laboratory technician", "mlt", "radiology technician", "x-ray technician",
            "clinical assistant", "healthcare administrator"
        ],
        # Accounting & Finance
        "ACCOUNTING_FINANCE": [
            "accountant", "accounting", "tally", "gst", "bookkeeping", "bookkeeper", "auditing",
            "auditor", "accounts payable", "accounts receivable", "taxation", "finance executive",
            "financial analyst", "payroll specialist", "tax associate", "accounts executive"
        ],
        # Education & Teaching
        "EDUCATION": [
            "teacher", "teaching", "b.ed", "school teacher", "subject teacher", "lecturer",
            "tutor", "pedagogy", "academic instructor", "trainer", "teaching assistant", "professor"
        ],
        # Administration & Office
        "ADMINISTRATION_OFFICE": [
            "administrative assistant", "office assistant", "executive assistant", "receptionist",
            "office administrator", "clerk", "data entry specialist", "office coordinator"
        ],
        # Human Resources
        "HUMAN_RESOURCES": [
            "human resources", "hr executive", "recruiter", "talent acquisition",
            "hr generalist", "onboarding specialist", "hr coordinator"
        ],
        # Sales & Retail
        "SALES_RETAIL": [
            "sales executive", "retail associate", "cashier", "store associate",
            "sales representative", "customer service representative", "account executive", "inside sales"
        ],
        # Marketing
        "MARKETING": [
            "marketing executive", "digital marketing specialist", "seo specialist",
            "content marketer", "social media manager", "copywriter", "brand manager"
        ],
        # Engineering
        "MECHANICAL_ENGINEERING": [
            "mechanical engineer", "mechanical design", "solidworks", "catia", "ansys",
            "cad engineer", "production engineer", "manufacturing engineer"
        ],
        "CIVIL_ENGINEERING": [
            "civil engineer", "site engineer", "structural engineer", "construction engineer",
            "quantity surveyor", "revit civil"
        ],
        "ELECTRICAL_ENGINEERING": [
            "electrical engineer", "power engineer", "electrical design engineer",
            "control systems engineer", "power systems"
        ],
        # Logistics & Warehouse
        "LOGISTICS_WAREHOUSE": [
            "forklift operator", "warehouse associate", "warehouse worker", "material handler",
            "order picker", "shipping and receiving", "delivery driver", "truck driver", "logistics coordinator"
        ],
        # Hospitality
        "HOSPITALITY_CULINARY": [
            "chef", "cook", "line cook", "prep cook", "sous chef", "kitchen assistant",
            "baker", "culinary specialist", "food service worker"
        ],
        # Construction
        "CONSTRUCTION_CARPENTRY": [
            "carpenter", "carpentry", "framing carpenter", "drywall installer", "mason",
            "construction worker", "construction laborer"
        ]
    }

    DOMAIN_GROUPS = {
        "AI_ML": {"AI_ML", "DATA_SCIENCE_ANALYTICS"},
        "DATA_SCIENCE_ANALYTICS": {"DATA_SCIENCE_ANALYTICS", "AI_ML"},
        "FULL_STACK_DEVELOPMENT": {"FULL_STACK_DEVELOPMENT", "FRONTEND_DEVELOPMENT", "BACKEND_DEVELOPMENT", "SOFTWARE_DEVELOPMENT"},
        "FRONTEND_DEVELOPMENT": {"FRONTEND_DEVELOPMENT", "FULL_STACK_DEVELOPMENT"},
        "BACKEND_DEVELOPMENT": {"BACKEND_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "SOFTWARE_DEVELOPMENT"},
        "CLOUD_INFRASTRUCTURE": {"CLOUD_INFRASTRUCTURE", "BACKEND_DEVELOPMENT"},
        "CYBERSECURITY": {"CYBERSECURITY", "CLOUD_INFRASTRUCTURE"},
        "QA_TESTING": {"QA_TESTING", "SOFTWARE_DEVELOPMENT"},
        "SOFTWARE_DEVELOPMENT": {"SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "BACKEND_DEVELOPMENT", "FRONTEND_DEVELOPMENT"},
        "SKILLED_TRADES_ELECTRICAL": {"SKILLED_TRADES_ELECTRICAL"},
        "SKILLED_TRADES_PLUMBING": {"SKILLED_TRADES_PLUMBING"},
        "SKILLED_TRADES_WELDING": {"SKILLED_TRADES_WELDING"},
        "SKILLED_TRADES_MECHANIC": {"SKILLED_TRADES_MECHANIC"},
        "SKILLED_TRADES_HVAC": {"SKILLED_TRADES_HVAC"},
        "HEALTHCARE_NURSING": {"HEALTHCARE_NURSING", "HEALTHCARE_SUPPORT"},
        "HEALTHCARE_SUPPORT": {"HEALTHCARE_SUPPORT", "HEALTHCARE_NURSING"},
        "ACCOUNTING_FINANCE": {"ACCOUNTING_FINANCE"},
        "EDUCATION": {"EDUCATION"},
        "ADMINISTRATION_OFFICE": {"ADMINISTRATION_OFFICE", "HUMAN_RESOURCES"},
        "HUMAN_RESOURCES": {"HUMAN_RESOURCES", "ADMINISTRATION_OFFICE"},
        "HOSPITALITY_CULINARY": {"HOSPITALITY_CULINARY"},
        "LOGISTICS_WAREHOUSE": {"LOGISTICS_WAREHOUSE"},
        "CONSTRUCTION_CARPENTRY": {"CONSTRUCTION_CARPENTRY", "CIVIL_ENGINEERING"},
        "SALES_RETAIL": {"SALES_RETAIL", "MARKETING"},
        "MARKETING": {"MARKETING", "SALES_RETAIL"},
        "MECHANICAL_ENGINEERING": {"MECHANICAL_ENGINEERING"},
        "CIVIL_ENGINEERING": {"CIVIL_ENGINEERING", "CONSTRUCTION_CARPENTRY"},
        "ELECTRICAL_ENGINEERING": {"ELECTRICAL_ENGINEERING"}
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

        # 3. Detect Job Domain from Keywords
        detected_job_domain = None
        for dom_name, kw_list in cls.DOMAIN_KEYWORDS.items():
            for kw in kw_list:
                if kw in title:
                    detected_job_domain = dom_name
                    break
            if detected_job_domain:
                break

        cand_domain = str(candidate_profile.get("professional_domain") or "GENERAL_PROFESSIONAL").upper().strip()

        # Cross-Domain Isolation:
        non_tech_domains = [
            "SKILLED_TRADES_ELECTRICAL", "SKILLED_TRADES_PLUMBING", "SKILLED_TRADES_WELDING",
            "SKILLED_TRADES_MECHANIC", "SKILLED_TRADES_HVAC", "HEALTHCARE_NURSING", "HEALTHCARE_SUPPORT",
            "EDUCATION", "ACCOUNTING_FINANCE", "ADMINISTRATION_OFFICE", "HOSPITALITY_CULINARY",
            "LOGISTICS_WAREHOUSE", "CONSTRUCTION_CARPENTRY", "SALES_RETAIL"
        ]
        tech_domains = [
            "AI_ML", "DATA_SCIENCE_ANALYTICS", "FULL_STACK_DEVELOPMENT", "FRONTEND_DEVELOPMENT",
            "BACKEND_DEVELOPMENT", "CLOUD_INFRASTRUCTURE", "CYBERSECURITY", "QA_TESTING",
            "SOFTWARE_DEVELOPMENT"
        ]

        if cand_domain in non_tech_domains and detected_job_domain in tech_domains:
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": raw_title,
                "reason": f"Technical software vacancy is strictly unrelated to candidate's {cand_domain.title()} profile."
            }

        if cand_domain in tech_domains and detected_job_domain in non_tech_domains:
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": raw_title,
                "reason": f"Vacancy in {detected_job_domain.title()} is strictly unrelated to candidate's technical profile."
            }

        # Specific isolation between Data Analyst and Accountant
        if cand_domain == "ACCOUNTING_FINANCE" and detected_job_domain in ["DATA_SCIENCE_ANALYTICS", "AI_ML"]:
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": raw_title,
                "reason": "Data analytics role is not an accounting/finance position."
            }
        if cand_domain in ["DATA_SCIENCE_ANALYTICS", "AI_ML"] and detected_job_domain == "ACCOUNTING_FINANCE":
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": raw_title,
                "reason": "Accounting vacancy is not a data science or analytics position."
            }

        # Specific isolation between Electrician and Software
        if cand_domain == "SKILLED_TRADES_ELECTRICAL" and detected_job_domain in tech_domains:
            return {
                "eligible": False,
                "role_relevance_status": "UNRELATED",
                "detected_job_role": raw_title,
                "reason": "Software/IT vacancy is strictly unrelated to electrician profile."
            }

        # 4. Domain Match Check: Candidate Domain vs Job Domain
        if cand_domain in cls.DOMAIN_GROUPS and detected_job_domain:
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

        # 5. Core skill overlap check only if within same general domain umbrella
        core_skills = [str(s).lower().strip() for s in candidate_profile.get("core_skills", []) if s]
        matched_skills = [s for s in core_skills if len(s) > 2 and s in searchable_job]
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
