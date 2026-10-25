import logging
import re
from app.services.role_taxonomy import RoleTaxonomy

logger = logging.getLogger(__name__)

class RoleInferenceEngine:
    """
    Universal Resume-Driven Candidate Profile & Target Role Inference Engine.
    Analyzes parsed resume skills, trade competencies, licenses, education, work experience,
    and domain text to accurately determine the candidate's authentic profession across ALL sectors:
      - AI & Machine Learning
      - Data Science & Analytics
      - Full Stack Development
      - Frontend Development
      - Backend Development
      - Cloud & DevOps Infrastructure
      - Cybersecurity
      - QA & Testing
      - General Software Development
      - Skilled Trades (Electrician, Plumber, Welder, Automotive Mechanic, HVAC, Maintenance)
      - Healthcare & Registered Nursing
      - Accounting & Finance
      - Education & Teaching
      - Human Resources
      - Office Administration
      - Hospitality & Culinary
      - Logistics & Warehouse
      - Construction & Carpentry
      - Sales & Retail
      - Marketing
      - Mechanical, Civil, and Electrical Engineering
      - Legal & Research
    Never defaults to IT or software when non-technical profiles are detected.
    Supports ambiguity detection and multi-profession target role refinement.
    """

    DOMAINS = {
        # =====================================================================
        # AI & MACHINE LEARNING
        # =====================================================================
        "AI_ML": {
            "persona": "AI & Machine Learning Specialist",
            "keywords": {
                "machine learning", "deep learning", "artificial intelligence", "ai engineer",
                "ml engineer", "nlp", "natural language processing", "computer vision",
                "tensorflow", "pytorch", "keras", "scikit-learn", "generative ai", "genai",
                "llm", "large language models", "transformers", "huggingface", "opencv",
                "mlops", "neural networks", "reinforcement learning", "bert", "gpt", "rag",
                "langchain", "prompt engineering", "ai research"
            },
            "base_roles": [
                "Machine Learning Engineer", "AI Engineer", "Applied AI Engineer",
                "Generative AI Engineer", "NLP Engineer", "Computer Vision Engineer", "MLOps Engineer", "Research Engineer"
            ],
            "primary_search_keyword": "machine learning engineer",
            "search_queries": ["Machine Learning Engineer", "AI Engineer", "NLP Engineer", "Computer Vision Engineer"]
        },

        # =====================================================================
        # DATA SCIENCE & ANALYTICS
        # =====================================================================
        "DATA_SCIENCE_ANALYTICS": {
            "persona": "Data Scientist & Analytics Specialist",
            "keywords": {
                "data science", "data scientist", "data analyst", "business intelligence",
                "bi analyst", "bi developer", "business analyst", "reporting analyst",
                "data engineer", "analytics engineer", "tableau", "power bi", "powerbi",
                "sql", "excel", "etl", "data warehouse", "bigquery", "snowflake",
                "data visualization", "looker", "data cleaning", "statistics", "data mining"
            },
            "base_roles": [
                "Data Analyst", "Data Scientist", "Business Intelligence Analyst",
                "BI Developer", "Business Analyst", "Data Engineer", "Reporting Analyst", "Junior Data Scientist"
            ],
            "primary_search_keyword": "data analyst",
            "search_queries": ["Data Analyst", "Data Scientist", "Business Intelligence Analyst", "Data Engineer"]
        },

        # =====================================================================
        # FULL STACK DEVELOPMENT
        # =====================================================================
        "FULL_STACK_DEVELOPMENT": {
            "persona": "Full Stack Software Developer",
            "keywords": {
                "full stack", "fullstack", "mern", "mean", "react and node", "react",
                "node.js", "nodejs", "express", "mongodb", "next.js", "full stack developer",
                "full stack engineer", "mern stack", "mean stack", "java full stack",
                "python full stack", "fullstack web"
            },
            "base_roles": [
                "Full Stack Developer", "MERN Stack Developer", "React and Node.js Developer",
                "Java Full Stack Developer", "Python Full Stack Developer", "MEAN Stack Developer"
            ],
            "primary_search_keyword": "full stack developer",
            "search_queries": ["Full Stack Developer", "MERN Stack Developer", "React and Node.js Developer"]
        },

        # =====================================================================
        # FRONTEND DEVELOPMENT
        # =====================================================================
        "FRONTEND_DEVELOPMENT": {
            "persona": "Frontend & UI Engineer",
            "keywords": {
                "frontend", "front-end", "front end", "react", "react.js", "angular",
                "vue", "vue.js", "html", "css", "javascript", "typescript", "tailwind",
                "redux", "ui developer", "ui engineer", "web designer", "client side"
            },
            "base_roles": [
                "Frontend Developer", "React Developer", "Angular Developer", "Vue.js Developer", "UI Engineer"
            ],
            "primary_search_keyword": "frontend developer",
            "search_queries": ["Frontend Developer", "React Developer", "UI Engineer"]
        },

        # =====================================================================
        # BACKEND DEVELOPMENT
        # =====================================================================
        "BACKEND_DEVELOPMENT": {
            "persona": "Backend Software Developer",
            "keywords": {
                "backend", "back-end", "back end", "python developer", "java developer",
                "node.js developer", "django", "flask", "fastapi", "spring boot", "express",
                ".net", "c#", "php", "laravel", "golang", "go", "rest api", "microservices",
                "server side", "api developer"
            },
            "base_roles": [
                "Backend Developer", "Python Developer", "Java Developer", "Node.js Developer", "API Developer", ".NET Developer", "PHP Developer"
            ],
            "primary_search_keyword": "backend developer",
            "search_queries": ["Backend Developer", "Python Developer", "Java Developer", "API Developer"]
        },

        # =====================================================================
        # CLOUD & INFRASTRUCTURE
        # =====================================================================
        "CLOUD_INFRASTRUCTURE": {
            "persona": "Cloud & DevOps Engineer",
            "keywords": {
                "devops", "cloud engineer", "aws", "azure", "gcp", "docker", "kubernetes",
                "terraform", "ci/cd", "jenkins", "ansible", "linux", "site reliability engineer",
                "sre", "platform engineer", "infrastructure engineer"
            },
            "base_roles": [
                "DevOps Engineer", "Cloud Engineer", "AWS Engineer", "Azure Engineer",
                "Site Reliability Engineer", "Platform Engineer", "Infrastructure Engineer"
            ],
            "primary_search_keyword": "devops engineer",
            "search_queries": ["DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer"]
        },

        # =====================================================================
        # CYBERSECURITY
        # =====================================================================
        "CYBERSECURITY": {
            "persona": "Cybersecurity & Information Security Specialist",
            "keywords": {
                "cybersecurity", "cyber security", "information security", "soc analyst",
                "penetration testing", "pen tester", "vulnerability assessment",
                "incident response", "security analyst", "siem", "wireshark", "ethical hacking",
                "cissp", "ceh", "network security", "firewall", "security engineer"
            },
            "base_roles": [
                "Security Analyst", "SOC Analyst", "Cybersecurity Analyst",
                "Penetration Tester", "Security Engineer", "Vulnerability Analyst", "Incident Response Analyst"
            ],
            "primary_search_keyword": "cybersecurity analyst",
            "search_queries": ["Cybersecurity Analyst", "Security Analyst", "SOC Analyst", "Penetration Tester"]
        },

        # =====================================================================
        # QA & TESTING
        # =====================================================================
        "QA_TESTING": {
            "persona": "Quality Assurance & Test Automation Engineer",
            "keywords": {
                "qa", "quality assurance", "software tester", "automation testing",
                "selenium", "cypress", "junit", "test automation", "qa engineer",
                "manual testing", "api testing", "postman", "sdet", "test cases"
            },
            "base_roles": [
                "QA Engineer", "Software Tester", "Automation Test Engineer", "SDET"
            ],
            "primary_search_keyword": "qa engineer",
            "search_queries": ["QA Engineer", "Software Tester", "Automation Test Engineer"]
        },

        # =====================================================================
        # GENERAL SOFTWARE DEVELOPMENT
        # =====================================================================
        "SOFTWARE_DEVELOPMENT": {
            "persona": "Software & Application Developer",
            "keywords": {
                "software engineer", "software developer", "application developer",
                "computer science", "algorithms", "data structures", "c++", "c#",
                "b.tech cse", "bca", "mca", "information technology", "programmer"
            },
            "base_roles": [
                "Software Developer", "Software Engineer", "Application Developer", "Junior Software Engineer", "Graduate Software Engineer"
            ],
            "primary_search_keyword": "software engineer",
            "search_queries": ["Software Engineer", "Software Developer", "Junior Software Engineer"]
        },

        # =====================================================================
        # ELECTRICAL & SKILLED TRADES
        # =====================================================================
        "SKILLED_TRADES_ELECTRICAL": {
            "persona": "Licensed Electrician & Electrical Systems Technician",
            "keywords": {
                "electrician", "electrical", "wiring", "conduit", "circuit breaker",
                "switchgear", "panel board", "multimeter", "high voltage", "low voltage",
                "troubleshooting", "cable pulling", "motor control", "nec", "national electrical code",
                "journeyman electrician", "master electrician", "electrical maintenance",
                "electrical helper", "industrial electrical", "residential electrical",
                "commercial electrical", "lockout", "tagout", "loto", "iti electrician",
                "substation", "switchboard", "breaker", "wireman", "lineman", "electrical technician"
            },
            "base_roles": [
                "Electrician", "Electrical Maintenance Technician", "Commercial Electrician",
                "Industrial Electrician", "Residential Electrician", "Electrical Helper", "Electrical Technician"
            ],
            "primary_search_keyword": "electrician",
            "search_queries": ["Electrician", "Electrical Maintenance Technician", "Industrial Electrician"]
        },
        "SKILLED_TRADES_PLUMBING": {
            "persona": "Plumber & Piping Systems Specialist",
            "keywords": {
                "plumber", "plumbing", "pipefitting", "pipefitter", "drainage", "pex",
                "copper piping", "pvc", "fixture installation", "backflow", "leak detection",
                "water heater", "plumbing apprentice", "journeyman plumber", "sewage",
                "pipe threading", "soldering", "rough-in"
            },
            "base_roles": [
                "Plumber", "Pipefitter", "Plumbing Technician", "Plumber Apprentice", "Maintenance Plumber"
            ],
            "primary_search_keyword": "plumber",
            "search_queries": ["Plumber", "Pipefitter", "Plumbing Technician"]
        },
        "SKILLED_TRADES_WELDING": {
            "persona": "Welder & Metal Fabrication Specialist",
            "keywords": {
                "welder", "welding", "mig", "tig", "stick welding", "smaw", "gmaw",
                "gtaw", "arc welding", "metal fabrication", "fabrication", "torch cutting",
                "structural welding", "pipe welder", "flux-cored", "grinding", "blueprint"
            },
            "base_roles": [
                "Welder", "Metal Fabricator", "MIG Welder", "TIG Welder", "Pipe Welder", "Structural Welder"
            ],
            "primary_search_keyword": "welder",
            "search_queries": ["Welder", "Metal Fabricator", "MIG Welder"]
        },
        "SKILLED_TRADES_MECHANIC": {
            "persona": "Automotive & Maintenance Mechanic",
            "keywords": {
                "mechanic", "automotive repair", "auto mechanic", "auto technician",
                "automotive technician", "engine diagnostics", "brake system", "suspension",
                "transmission repair", "obd", "diesel mechanic", "heavy equipment mechanic",
                "tire mounting", "wheel alignment", "preventative maintenance", "automotive mechanic"
            },
            "base_roles": [
                "Automotive Mechanic", "Auto Mechanic", "Maintenance Mechanic", "Diesel Mechanic", "Service Technician"
            ],
            "primary_search_keyword": "automotive mechanic",
            "search_queries": ["Automotive Mechanic", "Auto Mechanic", "Maintenance Mechanic"]
        },
        "SKILLED_TRADES_HVAC": {
            "persona": "HVAC & Refrigeration Systems Technician",
            "keywords": {
                "hvac", "refrigeration", "epa 608", "heat pump", "air conditioning",
                "ductwork", "heating system", "ventilation", "hvac technician",
                "hvac service", "freon", "air handler", "compressor", "thermostat"
            },
            "base_roles": [
                "HVAC Technician", "Refrigeration Technician", "HVAC Service Technician", "HVAC Installer"
            ],
            "primary_search_keyword": "hvac technician",
            "search_queries": ["HVAC Technician", "Refrigeration Technician", "HVAC Service"]
        },

        # =====================================================================
        # HEALTHCARE
        # =====================================================================
        "HEALTHCARE_NURSING": {
            "persona": "Healthcare & Registered Nursing Specialist",
            "keywords": {
                "nursing", "nurse", "registered nurse", "staff nurse", "clinical nurse",
                "patient care", "medication", "hospital", "vital signs", "wound dressing",
                "iv administration", "b.sc nursing", "m.sc nursing", "gnm", "anm",
                "patient triage", "clinical", "rn", "catheterization", "icu nurse"
            },
            "base_roles": [
                "Registered Nurse", "Staff Nurse", "Clinical Nurse", "Hospital Nurse", "Nursing Assistant"
            ],
            "primary_search_keyword": "nurse",
            "search_queries": ["Registered Nurse", "Staff Nurse", "Clinical Nurse"]
        },
        "HEALTHCARE_SUPPORT": {
            "persona": "Caregiver & Medical Support Specialist",
            "keywords": {
                "caregiver", "caregiving", "home health aide", "cna", "certified nursing assistant",
                "medical assistant", "elderly care", "patient hygiene", "phlebotomist",
                "phlebotomy", "medical lab technician", "mlt", "specimen collection",
                "radiology technician", "x-ray technician", "clinical assistant", "healthcare administrator"
            },
            "base_roles": [
                "Caregiver", "Medical Assistant", "Certified Nursing Assistant", "Home Health Aide",
                "Medical Laboratory Technician", "Radiology Technician", "Clinical Assistant", "Healthcare Administrator"
            ],
            "primary_search_keyword": "medical assistant",
            "search_queries": ["Caregiver", "Medical Assistant", "Certified Nursing Assistant"]
        },

        # =====================================================================
        # BUSINESS & FINANCE
        # =====================================================================
        "ACCOUNTING_FINANCE": {
            "persona": "Accounting & Finance Specialist",
            "keywords": {
                "accounting", "accountant", "tally", "gst", "bookkeeping", "bookkeeper",
                "taxation", "financial analysis", "auditing", "auditor", "accounts payable",
                "accounts receivable", "balance sheet", "tally prime", "cpa", "chartered accountant",
                "ca", "b.com", "m.com", "payroll", "invoice", "tally erp", "tds", "finance executive",
                "financial analyst", "tax associate", "payroll specialist", "accounts executive"
            },
            "base_roles": [
                "Accountant", "Accounts Executive", "Junior Accountant", "Bookkeeper",
                "Financial Analyst", "Auditor", "Tax Associate", "Payroll Specialist"
            ],
            "primary_search_keyword": "accountant",
            "search_queries": ["Accountant", "Accounts Executive", "Bookkeeper", "Financial Analyst"]
        },
        "HUMAN_RESOURCES": {
            "persona": "Human Resources Specialist",
            "keywords": {
                "human resources", "recruitment", "talent acquisition", "employee relations",
                "payroll management", "hr executive", "onboarding", "hris", "performance management",
                "hr generalist", "recruiter", "talent acquisition specialist", "hr coordinator"
            },
            "base_roles": [
                "HR Executive", "Recruiter", "Talent Acquisition Specialist", "HR Generalist", "Human Resources Coordinator"
            ],
            "primary_search_keyword": "human resources",
            "search_queries": ["HR Executive", "Recruiter", "Talent Acquisition Specialist"]
        },
        "ADMINISTRATION_OFFICE": {
            "persona": "Office Administration & Executive Support Specialist",
            "keywords": {
                "administrative assistant", "office administrator", "executive assistant",
                "receptionist", "office assistant", "office coordinator", "data entry",
                "calendar management", "filing", "scheduling", "secretarial", "office support",
                "clerk", "front desk"
            },
            "base_roles": [
                "Administrative Assistant", "Office Administrator", "Executive Assistant", "Receptionist", "Office Coordinator", "Data Entry Specialist"
            ],
            "primary_search_keyword": "administrative assistant",
            "search_queries": ["Administrative Assistant", "Office Administrator", "Receptionist"]
        },

        # =====================================================================
        # EDUCATION & TEACHING
        # =====================================================================
        "EDUCATION": {
            "persona": "Education & Teaching Specialist",
            "keywords": {
                "teaching", "teacher", "b.ed", "m.ed", "curriculum", "lesson planning",
                "classroom management", "pedagogy", "tutor", "lecturer", "professor",
                "education", "school teacher", "subject teacher", "academic instructor",
                "trainer", "teaching assistant", "tutoring", "student mentoring"
            },
            "base_roles": [
                "School Teacher", "Subject Teacher", "Tutor", "Academic Instructor", "Trainer", "Teaching Assistant", "Lecturer"
            ],
            "primary_search_keyword": "teacher",
            "search_queries": ["School Teacher", "Subject Teacher", "Tutor"]
        },

        # =====================================================================
        # OTHER PROFESSIONS
        # =====================================================================
        "HOSPITALITY_CULINARY": {
            "persona": "Culinary & Hospitality Specialist",
            "keywords": {
                "chef", "cook", "line cook", "sous chef", "culinary arts", "food preparation",
                "kitchen manager", "food safety", "haccp", "baking", "restaurant", "food service"
            },
            "base_roles": [
                "Chef", "Line Cook", "Kitchen Manager", "Food Service Worker", "Sous Chef"
            ],
            "primary_search_keyword": "chef",
            "search_queries": ["Chef", "Line Cook", "Food Service Worker"]
        },
        "LOGISTICS_WAREHOUSE": {
            "persona": "Logistics & Warehouse Operations Specialist",
            "keywords": {
                "warehouse", "forklift", "forklift operator", "order picker", "warehouse associate",
                "material handler", "shipping", "receiving", "logistics", "delivery driver", "truck driver"
            },
            "base_roles": [
                "Forklift Operator", "Warehouse Associate", "Order Picker", "Material Handler", "Delivery Driver"
            ],
            "primary_search_keyword": "warehouse associate",
            "search_queries": ["Forklift Operator", "Warehouse Associate", "Order Picker"]
        },
        "CONSTRUCTION_CARPENTRY": {
            "persona": "Construction & Carpentry Specialist",
            "keywords": {
                "carpenter", "carpentry", "framing", "drywall", "masonry", "construction worker", "mason"
            },
            "base_roles": [
                "Carpenter", "Construction Worker", "Drywall Installer", "Mason"
            ],
            "primary_search_keyword": "carpenter",
            "search_queries": ["Carpenter", "Construction Worker", "Drywall Installer"]
        },
        "SALES_RETAIL": {
            "persona": "Sales & Retail Customer Specialist",
            "keywords": {
                "sales", "sales executive", "sales representative", "retail sales", "cashier",
                "retail associate", "customer service representative", "account executive", "client acquisition"
            },
            "base_roles": [
                "Sales Executive", "Retail Associate", "Cashier", "Customer Service Representative", "Account Executive"
            ],
            "primary_search_keyword": "sales executive",
            "search_queries": ["Sales Executive", "Retail Associate", "Customer Service Representative"]
        },
        "MARKETING": {
            "persona": "Digital Marketing Specialist",
            "keywords": {
                "marketing", "digital marketing", "seo", "sem", "google ads", "social media marketing",
                "content marketing", "copywriting", "brand management", "lead generation"
            },
            "base_roles": [
                "Marketing Executive", "Digital Marketing Specialist", "SEO Specialist", "Content Marketer"
            ],
            "primary_search_keyword": "digital marketing",
            "search_queries": ["Marketing Executive", "Digital Marketing Specialist", "SEO Specialist"]
        },
        "MECHANICAL_ENGINEERING": {
            "persona": "Mechanical Design & Manufacturing Engineer",
            "keywords": {
                "mechanical engineering", "solidworks", "catia", "ansys", "machining",
                "manufacturing", "cnc", "cad", "cam", "thermodynamics", "mechanical engineer"
            },
            "base_roles": [
                "Mechanical Engineer", "Design Engineer", "CAD Engineer", "Production Engineer", "Manufacturing Engineer"
            ],
            "primary_search_keyword": "mechanical engineer",
            "search_queries": ["Mechanical Engineer", "Design Engineer", "CAD Engineer"]
        },
        "CIVIL_ENGINEERING": {
            "persona": "Civil & Structural Engineer",
            "keywords": {
                "civil engineering", "site engineer", "structural engineer", "revit",
                "staad pro", "quantity surveying", "surveying", "civil engineer"
            },
            "base_roles": [
                "Civil Engineer", "Site Engineer", "Structural Engineer", "Quantity Surveyor"
            ],
            "primary_search_keyword": "civil engineer",
            "search_queries": ["Civil Engineer", "Site Engineer", "Structural Engineer"]
        },
        "ELECTRICAL_ENGINEERING": {
            "persona": "Electrical & Control Systems Engineer",
            "keywords": {
                "electrical engineering", "power electronics", "circuit design", "matlab",
                "simulink", "plc", "scada", "power systems", "control systems", "electrical engineer"
            },
            "base_roles": [
                "Electrical Engineer", "Electrical Design Engineer", "Power Engineer", "Control Systems Engineer"
            ],
            "primary_search_keyword": "electrical engineer",
            "search_queries": ["Electrical Engineer", "Electrical Design Engineer", "Power Engineer"]
        }
    }

    # Backward-compatibility alias map
    DOMAIN_ALIASES = {
        "SOFTWARE_IT": "SOFTWARE_DEVELOPMENT",
        "DATA_ANALYTICS": "DATA_SCIENCE_ANALYTICS",
        "DATA_SCIENCE_AI": "AI_ML",
        "HR": "HUMAN_RESOURCES",
        "HEALTHCARE": "HEALTHCARE_NURSING"
    }

    @classmethod
    def infer_candidate_profile(cls, analysis_json: dict) -> dict:
        """
        Analyzes parsed resume analysis JSON using multi-signal evidence weighting
        (Work History > Licenses/Certifications > Skills > Education > Text) to determine
        the candidate's authentic profession. Never forces IT or Software roles.
        Supports multi-discipline profiles and uncertainty flags.
        """
        if not analysis_json:
            return cls._get_default_profile()

        tech_skills = analysis_json.get("technical_skills")
        if tech_skills is None:
            tech_skills = analysis_json.get("skills", [])
        if isinstance(tech_skills, dict):
            flat_skills = []
            for category, sk_list in tech_skills.items():
                if isinstance(sk_list, list):
                    flat_skills.extend(sk_list)
            tech_skills = flat_skills
        elif not isinstance(tech_skills, list):
            tech_skills = []

        soft_skills = analysis_json.get("soft_skills", [])
        if not isinstance(soft_skills, list):
            soft_skills = []

        raw_text = str(analysis_json.get("raw_text") or analysis_json.get("extracted_text") or analysis_json.get("text") or "").lower()

        education_entries = analysis_json.get("education", [])
        primary_degree = None
        primary_specialization = None
        if isinstance(education_entries, list) and len(education_entries) > 0:
            if isinstance(education_entries[0], dict):
                primary_degree = education_entries[0].get("degree")
                primary_specialization = education_entries[0].get("field")
            elif isinstance(education_entries[0], str):
                primary_degree = education_entries[0]

        certs = analysis_json.get("certifications", [])
        if not isinstance(certs, list):
            certs = []

        work_exp = analysis_json.get("work_experience")
        if work_exp is None:
            work_exp = analysis_json.get("experience", [])
        if not isinstance(work_exp, list):
            work_exp = []

        current_or_latest_role = None
        previous_roles = []
        if work_exp:
            if isinstance(work_exp[0], dict):
                current_or_latest_role = str(work_exp[0].get("role") or work_exp[0].get("title") or "").strip()
            elif isinstance(work_exp[0], str):
                current_or_latest_role = work_exp[0].strip()

            for w in work_exp[1:]:
                if isinstance(w, dict):
                    r_title = w.get("role") or w.get("title")
                    if r_title:
                        previous_roles.append(str(r_title).strip())
                elif isinstance(w, str) and w.strip():
                    previous_roles.append(w.strip())

        if not current_or_latest_role:
            current_or_latest_role = str(analysis_json.get("job_title") or analysis_json.get("preferred_job_role") or "").strip()

        yrs_exp = analysis_json.get("years_of_experience") or analysis_json.get("total_experience_years")
        exp_level = str(analysis_json.get("experience_level", "")).lower()
        edu_level = str(analysis_json.get("education_level", "Trade / Graduate"))

        # Build clean token sets for multi-signal evidence scoring
        cand_work_roles_text = f"{current_or_latest_role or ''} {' '.join(previous_roles)}".lower()
        cand_certs_text = " ".join(str(c) for c in certs).lower()
        cand_edu_text = f"{primary_degree or ''} {primary_specialization or ''}".lower()
        cand_skills_text = " ".join(str(s) for s in (tech_skills + soft_skills)).lower()

        # Tokenize raw text safely into words
        raw_words = set(re.findall(r'\b[a-z0-9\-\+\.#]+\b', raw_text))

        domain_evidence_scores = {}

        # Pre-check: Does current_or_latest_role directly match a known RoleTaxonomy entry?
        latest_role_taxonomy_match = None
        if current_or_latest_role:
            latest_role_taxonomy_match = RoleTaxonomy.find_taxonomy_entry(current_or_latest_role)

        for d_key, d_data in cls.DOMAINS.items():
            score = 0.0
            kw_set = d_data["keywords"]

            # Signal 1: Work Experience Role Matches (Weight: 4.0 - 8.0)
            if latest_role_taxonomy_match and latest_role_taxonomy_match.get("domain") == d_key:
                score += 10.0  # Massive signal: Candidate explicitly held this exact canonical profession!

            for kw in kw_set:
                if len(kw) > 3:
                    if re.search(r'\b' + re.escape(kw) + r'\b', cand_work_roles_text):
                        score += 4.0
                        if current_or_latest_role and re.search(r'\b' + re.escape(kw) + r'\b', current_or_latest_role.lower()):
                            score += 2.0  # Extra weight for current role

            # Signal 2: Licenses & Certifications (Weight: 3.5 per match)
            for kw in kw_set:
                if len(kw) > 3 and re.search(r'\b' + re.escape(kw) + r'\b', cand_certs_text):
                    score += 3.5

            # Signal 3: Specific Skills & Tools (Weight: 2.0 per match)
            for kw in kw_set:
                if len(kw) > 2 and re.search(r'\b' + re.escape(kw) + r'\b', cand_skills_text):
                    score += 2.0

            # Signal 4: Education & Vocational Qualifications (Weight: 1.5 per match)
            for kw in kw_set:
                if len(kw) > 3 and re.search(r'\b' + re.escape(kw) + r'\b', cand_edu_text):
                    score += 1.5

            # Signal 5: General Text Keywords Occurrence (Weight: 0.5 per distinct match)
            matched_raw_kws = kw_set.intersection(raw_words)
            score += len(matched_raw_kws) * 0.5

            domain_evidence_scores[d_key] = round(score, 2)

        # Sort candidate domains by evidence score descending
        sorted_domains = sorted(domain_evidence_scores.items(), key=lambda x: x[1], reverse=True)
        top_domain_key, top_score = sorted_domains[0] if sorted_domains else ("GENERAL_PROFESSIONAL", 0.0)
        second_domain_key, second_score = sorted_domains[1] if len(sorted_domains) > 1 else (None, 0.0)

        # Determine confidence and ambiguity
        is_ambiguous = False
        needs_confirmation = False
        alternative_professions = []

        if top_score == 0.0:
            prof_domain = "GENERAL_PROFESSIONAL"
            prof_identity = "Professional Candidate"
            primary_roles = ["Professional Associate", "Operations Specialist", "Executive Assistant"]
            related_roles = ["Service Coordinator", "General Associate"]
            alt_roles = ["Project Assistant"]
            search_queries = ["Associate", "Coordinator"]
            confidence = "LOW"
            is_ambiguous = True
            needs_confirmation = True
        else:
            domain_data = cls.DOMAINS[top_domain_key]
            prof_domain = top_domain_key
            prof_identity = domain_data["persona"]
            primary_roles = list(domain_data["base_roles"][:3])
            related_roles = list(domain_data["base_roles"][3:6])
            alt_roles = [f"{domain_data['primary_search_keyword'].title()} Associate", "Operations Specialist"]
            search_queries = list(domain_data.get("search_queries", [domain_data["primary_search_keyword"].title()]))

            # Check for close secondary domain (multi-discipline / ambiguity)
            if second_score > 0 and (top_score - second_score) <= 3.0:
                is_ambiguous = True
                needs_confirmation = True
                second_domain_data = cls.DOMAINS[second_domain_key]
                alternative_professions.append({
                    "domain": second_domain_key,
                    "persona": second_domain_data["persona"],
                    "primary_role": second_domain_data["base_roles"][0],
                    "evidence_score": second_score
                })
                confidence = "MEDIUM"
            else:
                confidence = "HIGH"

        # If latest role directly names a canonical role, ensure it leads primary_roles
        if latest_role_taxonomy_match:
            canonical_title = latest_role_taxonomy_match["canonical"]
            if canonical_title in primary_roles:
                primary_roles.remove(canonical_title)
            primary_roles = [canonical_title] + primary_roles[:2]
            if canonical_title not in search_queries:
                search_queries = [canonical_title] + search_queries[:2]
        elif current_or_latest_role and len(current_or_latest_role) > 3:
            role_clean = current_or_latest_role.title()
            if role_clean not in primary_roles and prof_domain != "GENERAL_PROFESSIONAL":
                d_kws = cls.DOMAINS.get(prof_domain, {}).get("keywords", set())
                if any(w in d_kws for w in current_or_latest_role.lower().split()):
                    primary_roles = [role_clean] + primary_roles[:2]
                    search_queries = [role_clean] + [q for q in search_queries if q != role_clean]

        clean_queries = []
        for q in search_queries:
            sq = str(q).strip()
            if sq and sq not in clean_queries:
                clean_queries.append(sq)
        if not clean_queries:
            clean_queries = [primary_roles[0]]

        industries_map = {
            "AI_ML": ["Artificial Intelligence", "Machine Learning", "Data Tech", "Cloud & SaaS"],
            "DATA_SCIENCE_ANALYTICS": ["Data Analytics", "Business Intelligence", "Fintech", "Technology"],
            "FULL_STACK_DEVELOPMENT": ["Web Development", "Software Engineering", "Cloud & SaaS"],
            "FRONTEND_DEVELOPMENT": ["UI/UX Engineering", "Web Applications", "Digital Media"],
            "BACKEND_DEVELOPMENT": ["Backend Systems", "Cloud Platforms", "API Services"],
            "CLOUD_INFRASTRUCTURE": ["Cloud Infrastructure", "DevOps", "Enterprise IT"],
            "CYBERSECURITY": ["Cybersecurity", "Network Security", "Security Operations"],
            "QA_TESTING": ["Quality Engineering", "Software Testing", "Agile Development"],
            "SOFTWARE_DEVELOPMENT": ["Software Engineering", "Information Technology", "Enterprise Applications"],
            "SKILLED_TRADES_ELECTRICAL": ["Electrical Contracting", "Building Maintenance", "Industrial Manufacturing"],
            "SKILLED_TRADES_PLUMBING": ["Plumbing & Piping", "Construction", "Facility Maintenance"],
            "SKILLED_TRADES_WELDING": ["Metal Fabrication", "Manufacturing", "Structural Construction"],
            "SKILLED_TRADES_MECHANIC": ["Automotive Services", "Fleet Maintenance", "Transportation Repair"],
            "SKILLED_TRADES_HVAC": ["HVAC Contracting", "Building Systems", "Mechanical Services"],
            "HEALTHCARE_NURSING": ["Healthcare & Hospitals", "Clinical Care", "Medical Facilities"],
            "HEALTHCARE_SUPPORT": ["Home Healthcare", "Assisted Living", "Diagnostic Labs"],
            "ACCOUNTING_FINANCE": ["Accounting & Audit", "Financial Services", "Corporate Finance"],
            "HUMAN_RESOURCES": ["Human Resources", "Talent Acquisition", "Staffing"],
            "ADMINISTRATION_OFFICE": ["Corporate Administration", "Office Management", "Professional Services"],
            "EDUCATION": ["K-12 Education", "Higher Education", "Vocational Training", "Tutoring"],
            "HOSPITALITY_CULINARY": ["Restaurants & Food Service", "Hotels & Lodging", "Catering"],
            "LOGISTICS_WAREHOUSE": ["Warehousing & Distribution", "Freight & Logistics", "Transportation"],
            "CONSTRUCTION_CARPENTRY": ["Residential & Commercial Construction", "Carpentry & Framing"],
            "SALES_RETAIL": ["Retail & Consumer Goods", "B2B Sales", "Customer Support"],
            "MARKETING": ["Digital Media & Advertising", "Brand Strategy", "E-Commerce"],
            "MECHANICAL_ENGINEERING": ["Automotive", "Manufacturing", "Heavy Machinery", "Aerospace"],
            "CIVIL_ENGINEERING": ["Civil Infrastructure", "Structural Engineering", "Construction Management"],
            "ELECTRICAL_ENGINEERING": ["Power Systems", "Control Systems", "Electrical Engineering"]
        }

        inferred_industries = industries_map.get(prof_domain, ["General Industry", "Services", "Operations"])

        # Extract tools & trade equipment
        known_tools = [
            "Multimeter", "Conduit Bender", "Wire Strippers", "Circuit Tester",
            "Pipe Wrench", "Soldering Torch", "PEX Crimper",
            "MIG Welder", "TIG Welder", "Plasma Cutter", "Angle Grinder",
            "OBD-II Scanner", "Torque Wrench", "Hydraulic Lift",
            "Manifold Gauges", "Vacuum Pump", "Leak Detector",
            "Forklift", "Pallet Jack", "RF Scanner",
            "AutoCAD", "SolidWorks", "Tally", "QuickBooks", "Excel", "Photoshop", "VS Code",
            "Docker", "Kubernetes", "Postman", "Tableau", "Power BI", "PyTorch", "TensorFlow"
        ]
        extracted_tools = [t for t in known_tools if any(t.lower() == str(sk).lower() for sk in tech_skills) or t.lower() in raw_text]

        return {
            "professional_domain": prof_domain,
            "professional_identity": prof_identity,
            "current_or_latest_role": current_or_latest_role,
            "previous_roles": previous_roles,
            "experience_level": exp_level or "Experienced Professional",
            "years_of_experience": yrs_exp,
            "primary_roles": primary_roles,
            "related_roles": related_roles,
            "alternative_roles": alt_roles,
            "search_queries": clean_queries[:4],
            "skills": list(set(tech_skills + soft_skills)),
            "technical_skills": list(tech_skills),
            "soft_skills": list(soft_skills),
            "tools": extracted_tools,
            "certifications": certs,
            "education": primary_degree or edu_level,
            "degree": primary_degree,
            "specialization": primary_specialization,
            "industries": inferred_industries,
            "languages": ["English"],

            # Backward-Compatible Helper Attributes:
            "persona": prof_identity,
            "core_skills": list(tech_skills[:12]),
            "inferred_roles": (primary_roles + related_roles)[:6],
            "primary_search_keyword": clean_queries[0],

            # Multi-Profession & Uncertainty Attributes:
            "confidence": confidence,
            "is_ambiguous": is_ambiguous,
            "needs_confirmation": needs_confirmation,
            "alternative_professions": alternative_professions
        }

    @classmethod
    def _get_default_profile(cls) -> dict:
        return {
            "professional_domain": "GENERAL_PROFESSIONAL",
            "professional_identity": "Professional Candidate",
            "current_or_latest_role": None,
            "previous_roles": [],
            "experience_level": "Fresher",
            "years_of_experience": None,
            "primary_roles": ["Professional Associate", "Operations Specialist"],
            "related_roles": ["Service Coordinator", "General Associate"],
            "alternative_roles": ["Project Assistant"],
            "search_queries": ["Associate", "Coordinator"],
            "skills": [],
            "technical_skills": [],
            "soft_skills": [],
            "tools": [],
            "certifications": [],
            "education": "Graduate",
            "degree": None,
            "specialization": None,
            "industries": ["General Services"],
            "languages": ["English"],
            "persona": "Professional Candidate",
            "core_skills": [],
            "inferred_roles": ["Professional Associate", "Operations Specialist"],
            "primary_search_keyword": "associate",
            "confidence": "LOW",
            "is_ambiguous": True,
            "needs_confirmation": True,
            "alternative_professions": []
        }
