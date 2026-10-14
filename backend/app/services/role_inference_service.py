import logging

logger = logging.getLogger(__name__)

class RoleInferenceEngine:
    """
    Universal Resume-Driven Candidate Profile & Target Role Inference Engine.
    Analyzes parsed resume skills, education, experience, and domain text to determine
    the candidate's actual profession (Healthcare/Nursing, Accounting/Finance,
    Mechanical Engineering, Education/Teaching, Marketing, Civil, HR, Sales, Software/IT, etc.)
    and automatically infers suitable target job roles and search queries.
    """

    DOMAINS = {
        "HEALTHCARE": {
            "persona": "Healthcare & Nursing Specialist",
            "keywords": {
                "nursing", "nurse", "staff nurse", "registered nurse", "clinical nurse",
                "patient care", "medication", "hospital", "vital signs", "wound dressing",
                "iv administration", "pharmacist", "pharmacy", "medical", "anatomy",
                "physiology", "b.sc nursing", "m.sc nursing", "gnm", "anm", "healthcare",
                "doctor", "pharma", "lab technician", "clinical research"
            },
            "base_roles": ["Staff Nurse", "Registered Nurse", "Clinical Nurse", "Hospital Nurse", "Nursing Assistant", "Healthcare Associate"],
            "primary_search_keyword": "nurse"
        },
        "ACCOUNTING_FINANCE": {
            "persona": "Accounting & Finance Specialist",
            "keywords": {
                "accounting", "accountant", "tally", "gst", "bookkeeping", "taxation",
                "financial analysis", "auditing", "accounts payable", "accounts receivable",
                "balance sheet", "tally prime", "cpa", "chartered accountant", "ca",
                "b.com", "m.com", "payroll", "invoice", "tally erp", "finance executive"
            },
            "base_roles": ["Accountant", "Accounts Executive", "Junior Accountant", "Accounts Assistant", "Finance Executive", "Financial Analyst"],
            "primary_search_keyword": "accountant"
        },
        "MECHANICAL_ENGINEERING": {
            "persona": "Mechanical Design & Manufacturing Engineer",
            "keywords": {
                "mechanical engineering", "autocad", "solidworks", "catia", "ansys",
                "machining", "manufacturing", "cnc", "cad", "cam", "hvac", "thermodynamics",
                "hydraulics", "mechanical design", "production engineering", "b.e mechanical",
                "b.tech mechanical", "mechanical engineer"
            },
            "base_roles": ["Mechanical Engineer", "Design Engineer", "CAD Engineer", "Production Engineer", "Manufacturing Engineer", "Quality Engineer"],
            "primary_search_keyword": "mechanical engineer"
        },
        "EDUCATION": {
            "persona": "Education & Teaching Specialist",
            "keywords": {
                "teaching", "teacher", "b.ed", "m.ed", "curriculum", "lesson planning",
                "classroom management", "pedagogy", "tutor", "lecturer", "professor",
                "education", "school teacher", "subject teacher", "academic counselor"
            },
            "base_roles": ["School Teacher", "Subject Teacher", "Teaching Assistant", "Education Coordinator", "Academic Counselor", "Lecturer"],
            "primary_search_keyword": "teacher"
        },
        "MARKETING": {
            "persona": "Digital Marketing Specialist",
            "keywords": {
                "marketing", "digital marketing", "seo", "sem", "google ads", "social media marketing",
                "content marketing", "copywriting", "brand management", "email marketing",
                "lead generation", "market research", "social media manager"
            },
            "base_roles": ["Marketing Executive", "Digital Marketing Specialist", "SEO Specialist", "Marketing Coordinator", "Social Media Specialist", "Content Marketer"],
            "primary_search_keyword": "digital marketing"
        },
        "CIVIL_ENGINEERING": {
            "persona": "Civil & Structural Engineer",
            "keywords": {
                "civil engineering", "structural design", "construction", "revit", "staad pro",
                "surveying", "site engineer", "autocad civil", "building design", "b.e civil",
                "b.tech civil", "quantity surveying"
            },
            "base_roles": ["Civil Engineer", "Site Engineer", "Structural Engineer", "Construction Project Engineer", "Quantity Surveyor"],
            "primary_search_keyword": "civil engineer"
        },
        "HR": {
            "persona": "Human Resources Specialist",
            "keywords": {
                "human resources", "recruitment", "talent acquisition", "employee relations",
                "payroll management", "hr executive", "onboarding", "hris", "performance management",
                "hr generalist", "hr recruiter"
            },
            "base_roles": ["HR Executive", "Talent Acquisition Specialist", "HR Recruiter", "HR Generalist", "HR Assistant"],
            "primary_search_keyword": "human resources"
        },
        "SALES": {
            "persona": "Sales & Business Development Representative",
            "keywords": {
                "sales", "business development", "client acquisition", "cold calling",
                "b2b sales", "inside sales", "field sales", "key account management",
                "crm", "sales executive", "lead generation"
            },
            "base_roles": ["Sales Executive", "Business Development Associate", "Account Executive", "Sales Representative", "Business Development Manager"],
            "primary_search_keyword": "sales executive"
        },
        "SOFTWARE_IT": {
            "persona": "Software & Technology Specialist",
            "keywords": {
                "python", "java", "c++", "c#", "javascript", "typescript", "react", "node.js",
                "nodejs", "express", "mongodb", "sql", "flask", "django", "spring boot",
                "html", "css", "vue", "angular", "aws", "docker", "kubernetes", "git",
                "machine learning", "data science", "nlp", "ai", "pandas", "numpy",
                "scikit-learn", "tensorflow", "pytorch", "devops", "software engineer",
                "software developer", "full stack", "backend", "frontend", "computer science"
            },
            "base_roles": ["Software Engineer", "Python Developer", "Backend Developer", "Full Stack Developer", "Data Analyst", "Software Developer"],
            "primary_search_keyword": "software engineer"
        },
        "ELECTRICAL_ENGINEERING": {
            "persona": "Electrical & Control Systems Engineer",
            "keywords": {
                "electrical engineering", "electrical engineer", "power electronics", "circuit design",
                "plc", "scada", "high voltage", "power systems", "switchgear", "b.e electrical",
                "b.tech electrical", "transformer", "single line diagram", "substation"
            },
            "base_roles": ["Electrical Engineer", "Electrical Design Engineer", "Power Engineer", "Control Systems Engineer", "Electrical Maintenance Engineer"],
            "primary_search_keyword": "electrical engineer"
        },
        "SCIENCE_RESEARCH": {
            "persona": "Science & Research Specialist",
            "keywords": {
                "astrophysics", "astronomy", "astrophysicist", "astronomer", "physics", "physicist",
                "chemistry", "chemist", "biochemistry", "biology", "biologist", "microbiology",
                "genetics", "geology", "geologist", "environmental science", "scientific research",
                "research scientist", "postdoctoral", "ph.d", "phd", "spectroscopy", "telescope",
                "quantum", "laboratory research"
            },
            "base_roles": ["Research Scientist", "Staff Scientist", "Research Associate", "Postdoctoral Researcher", "Scientist"],
            "primary_search_keyword": "research scientist"
        }
    }

    @classmethod
    def infer_candidate_profile(cls, analysis_json: dict) -> dict:
        """
        Analyzes parsed resume analysis JSON to determine the candidate's actual
        professional domain, persona, inferred target roles, and candidate-specific search queries.
        """
        if not analysis_json:
            return cls._get_default_profile()

        tech_skills = analysis_json.get("technical_skills", [])
        if isinstance(tech_skills, dict):
            flat_skills = []
            for category, sk_list in tech_skills.items():
                if isinstance(sk_list, list):
                    flat_skills.extend(sk_list)
            tech_skills = flat_skills

        soft_skills = analysis_json.get("soft_skills", [])
        if not isinstance(soft_skills, list):
            soft_skills = []

        raw_text = str(analysis_json.get("raw_text") or analysis_json.get("extracted_text") or "").lower()

        education_entries = analysis_json.get("education", [])
        primary_degree = None
        primary_specialization = None
        if isinstance(education_entries, list) and len(education_entries) > 0:
            primary_degree = education_entries[0].get("degree")
            primary_specialization = education_entries[0].get("field")

        certs = analysis_json.get("certifications", [])
        if not isinstance(certs, list):
            certs = []

        work_exp = analysis_json.get("work_experience", [])
        if not isinstance(work_exp, list):
            work_exp = []

        current_or_latest_role = None
        previous_roles = []
        if work_exp:
            current_or_latest_role = work_exp[0].get("role")
            for w in work_exp[1:]:
                if w.get("role"):
                    previous_roles.append(str(w.get("role")))

        yrs_exp = analysis_json.get("years_of_experience") or analysis_json.get("total_experience_years")

        # Construct comprehensive candidate text representation across all sections
        all_candidate_text = f"{current_or_latest_role or ''} {' '.join(previous_roles)} {primary_degree or ''} {primary_specialization or ''} {' '.join(str(s) for s in tech_skills)} {' '.join(str(s) for s in soft_skills)} {raw_text}".lower()

        all_candidate_terms = set()
        for term in all_candidate_text.replace(",", " ").replace(".", " ").replace("/", " ").replace("-", " ").split():
            clean_term = term.strip().lower()
            if len(clean_term) > 2:
                all_candidate_terms.add(clean_term)
        for s in (tech_skills + soft_skills):
            if s:
                all_candidate_terms.add(str(s).lower().strip())

        exp_level = str(analysis_json.get("experience_level", "")).lower()
        edu_level = str(analysis_json.get("education_level", "Degree Graduate"))

        # Score domain clusters based on matching terms count
        domain_scores = {}
        for d_key, d_data in cls.DOMAINS.items():
            matches = all_candidate_terms.intersection(d_data["keywords"])
            domain_scores[d_key] = len(matches)

        top_domain_key = max(domain_scores, key=domain_scores.get) if domain_scores else None
        top_score = domain_scores.get(top_domain_key, 0) if top_domain_key else 0

        # Extract tools (software, hardware, instruments)
        known_tools = ["AutoCAD", "SolidWorks", "CATIA", "ANSYS", "Revit", "STAAD Pro", "Tally", "Photoshop", "Illustrator", "Figma", "Excel", "Power BI", "Tableau", "Git", "Docker", "VS Code", "Jira", "MATLAB", "Simulink", "QuickBooks", "SAP"]
        extracted_tools = [t for t in known_tools if any(t.lower() == str(sk).lower() for sk in tech_skills) or t.lower() in raw_text]

        # Explicit Profession Identity Recognition (Checks title, degree, skills, raw text)
        explicit_identity = None
        explicit_domain = None
        explicit_queries = []
        explicit_primary_roles = []
        explicit_related_roles = []
        explicit_alt_roles = []

        text_for_identity = all_candidate_text
        software_score = domain_scores.get("SOFTWARE_IT", 0)

        # Explicit Profession Identity Recognition (Checks title, degree, skills, raw text)
        # Priority 1: Software Engineering, Data Science, AI & Technology
        if any(k in text_for_identity for k in ["machine learning", "deep learning", "artificial intelligence", "data scientist", "nlp", "computer vision", "tensorflow", "pytorch", "llm", "genai", "generative ai"]):
            explicit_identity = "Data Science & AI Specialist"
            explicit_domain = "SOFTWARE_IT"
            explicit_primary_roles = ["Data Scientist", "Machine Learning Engineer", "AI Engineer"]
            explicit_related_roles = ["Data Analyst", "Applied Scientist", "Python Developer"]
            explicit_queries = ["Data Scientist", "Machine Learning Engineer", "Python Developer"]
        elif any(k in text_for_identity for k in ["data analyst", "data analytics", "business intelligence", "bi analyst", "power bi", "tableau", "sql analyst", "data reporter"]):
            explicit_identity = "Data Analytics & BI Specialist"
            explicit_domain = "SOFTWARE_IT"
            explicit_primary_roles = ["Data Analyst", "Business Intelligence Analyst", "Analytics Specialist"]
            explicit_related_roles = ["Data Engineer", "Reporting Analyst", "Python Developer"]
            explicit_queries = ["Data Analyst", "BI Analyst", "Data Analytics"]
        elif any(k in text_for_identity for k in ["devops", "cloud engineer", "aws engineer", "azure engineer", "site reliability engineer", "sre", "kubernetes", "docker", "ci/cd", "infrastructure engineer"]):
            explicit_identity = "Cloud & DevOps Engineer"
            explicit_domain = "SOFTWARE_IT"
            explicit_primary_roles = ["DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer"]
            explicit_related_roles = ["Platform Engineer", "Software Engineer", "Systems Engineer"]
            explicit_queries = ["DevOps Engineer", "Cloud Engineer"]
        elif any(k in text_for_identity for k in ["software architect", "solution architect", "solutions architect", "system architect", "cloud architect", "enterprise architect"]):
            explicit_identity = "Software & Systems Architect"
            explicit_domain = "SOFTWARE_IT"
            explicit_primary_roles = ["Software Architect", "Solutions Architect", "Senior Software Engineer"]
            explicit_related_roles = ["Backend Architect", "Cloud Architect", "Lead Developer"]
            explicit_queries = ["Software Architect", "Solutions Architect", "Software Engineer"]
        elif any(k in text_for_identity for k in [
            "software engineer", "software developer", "full stack", "fullstack", "backend developer",
            "frontend developer", "web developer", "python developer", "java developer", "react developer",
            "node developer", "computer science", "b.tech in computer", "b.tech cse", "b.e cse", "b.e. cse",
            "bca", "mca", "information technology"
        ]) or (software_score >= 3):
            explicit_identity = "Software & Technology Specialist"
            explicit_domain = "SOFTWARE_IT"
            explicit_primary_roles = ["Software Engineer", "Full Stack Developer", "Backend Developer"]
            explicit_related_roles = ["Frontend Developer", "Python Developer", "Software Developer"]
            explicit_queries = ["Software Engineer", "Full Stack Developer", "Backend Developer"]
        # Priority 2: Other Professional Domains (Education, Sciences, Engineering, Marketing, etc.)
        elif any(k in text_for_identity for k in ["b.ed", "m.ed", "school teacher", "high school teacher", "subject teacher", "classroom management", "pedagogy", "curriculum development", "lesson planning"]):
            explicit_identity = "Education & Teaching Specialist"
            explicit_domain = "EDUCATION"
            explicit_primary_roles = ["School Teacher", "Subject Teacher", "Teaching Assistant"]
            explicit_related_roles = ["Education Coordinator", "Academic Counselor", "Lecturer"]
            explicit_queries = ["Teacher", "School Teacher", "Subject Teacher"]
        elif any(k in text_for_identity for k in ["astrophysics", "astrophysicist", "astronomy", "astronomer", "stellar", "cosmology"]):
            explicit_identity = "Astrophysicist / Astronomical Researcher"
            explicit_domain = "SCIENCE_RESEARCH"
            explicit_primary_roles = ["Astrophysicist", "Astronomer", "Research Scientist"]
            explicit_related_roles = ["Data Scientist", "Observational Astronomer", "Postdoctoral Fellow"]
            explicit_queries = ["Astrophysicist", "Astronomer", "Research Scientist"]
        elif any(k in text_for_identity for k in ["physics", "physicist", "quantum", "condensed matter", "particle physics"]):
            explicit_identity = "Physicist / Physics Researcher"
            explicit_domain = "SCIENCE_RESEARCH"
            explicit_primary_roles = ["Physicist", "Research Scientist", "Applied Physicist"]
            explicit_related_roles = ["Laboratory Scientist", "Postdoctoral Researcher", "Data Analyst"]
            explicit_queries = ["Physicist", "Research Scientist"]
        elif any(k in text_for_identity for k in ["chemistry", "chemist", "analytical chemistry", "organic chemistry", "biochemistry"]):
            explicit_identity = "Chemist / Chemical Researcher"
            explicit_domain = "SCIENCE_RESEARCH"
            explicit_primary_roles = ["Chemist", "Analytical Chemist", "Research Scientist"]
            explicit_related_roles = ["Lab Manager", "Quality Control Chemist", "R&D Scientist"]
            explicit_queries = ["Chemist", "Analytical Chemist", "Research Scientist"]
        elif any(k in text_for_identity for k in ["biology", "biologist", "microbiology", "microbiologist", "molecular biology", "genetics"]):
            explicit_identity = "Biologist / Life Science Researcher"
            explicit_domain = "SCIENCE_RESEARCH"
            explicit_primary_roles = ["Biologist", "Microbiologist", "Research Scientist"]
            explicit_related_roles = ["Life Scientist", "Biotech Associate", "Lab Scientist"]
            explicit_queries = ["Biologist", "Microbiologist", "Research Scientist"]
        elif any(k in text_for_identity for k in ["scientific research", "research scientist", "postdoctoral researcher", "phd researcher"]):
            explicit_identity = "Research Scientist"
            explicit_domain = "SCIENCE_RESEARCH"
            explicit_primary_roles = ["Research Scientist", "Staff Scientist", "Research Associate"]
            explicit_related_roles = ["Postdoctoral Fellow", "R&D Specialist"]
            explicit_queries = ["Research Scientist", "Staff Scientist"]
        elif any(k in text_for_identity for k in ["civil engineering", "civil engineer", "site engineer", "structural design", "structural engineer", "autocad civil", "staad pro", "quantity surveying"]):
            explicit_identity = "Civil & Structural Engineer"
            explicit_domain = "CIVIL_ENGINEERING"
            explicit_primary_roles = ["Civil Engineer", "Site Engineer", "Structural Engineer"]
            explicit_related_roles = ["Construction Project Engineer", "Quantity Surveyor"]
            explicit_queries = ["Civil Engineer", "Site Engineer", "Structural Engineer"]
        elif any(k in text_for_identity for k in ["nursing", "registered nurse", "staff nurse", "clinical nurse", "b.sc nursing", "patient care"]):
            explicit_identity = "Healthcare & Nursing Specialist"
            explicit_domain = "HEALTHCARE"
            explicit_primary_roles = ["Staff Nurse", "Registered Nurse", "Clinical Nurse"]
            explicit_related_roles = ["Hospital Nurse", "Nursing Assistant", "Healthcare Associate"]
            explicit_queries = ["Nurse", "Staff Nurse", "Registered Nurse"]
        elif any(k in text_for_identity for k in ["accountant", "accounting", "tally prime", "tally erp", "tally", "gst", "bookkeeping", "accounts payable", "accounts receivable"]):
            explicit_identity = "Accounting & Finance Specialist"
            explicit_domain = "ACCOUNTING_FINANCE"
            explicit_primary_roles = ["Accountant", "Accounts Executive", "Junior Accountant"]
            explicit_related_roles = ["Accounts Assistant", "Finance Executive", "Financial Analyst"]
            explicit_queries = ["Accountant", "Accounts Executive", "Junior Accountant"]
        elif any(k in text_for_identity for k in ["mechanical engineering", "mechanical engineer", "solidworks", "catia", "ansys", "machining", "thermodynamics"]):
            explicit_identity = "Mechanical Design & Manufacturing Engineer"
            explicit_domain = "MECHANICAL_ENGINEERING"
            explicit_primary_roles = ["Mechanical Engineer", "Design Engineer", "CAD Engineer"]
            explicit_related_roles = ["Production Engineer", "Manufacturing Engineer", "Quality Engineer"]
            explicit_queries = ["Mechanical Engineer", "Design Engineer", "CAD Engineer"]
        elif any(k in text_for_identity for k in ["electrical engineering", "electrical engineer", "power electronics", "plc", "scada", "single line diagram"]):
            explicit_identity = "Electrical Engineer"
            explicit_domain = "ELECTRICAL_ENGINEERING"
            explicit_primary_roles = ["Electrical Engineer", "Electrical Design Engineer", "Power Engineer"]
            explicit_related_roles = ["Control Systems Engineer", "PLC Automation Engineer", "Electrical Maintenance Engineer"]
            explicit_queries = ["Electrical Engineer", "Electrical Design Engineer", "Power Engineer"]
        elif any(k in text_for_identity for k in ["digital marketing", "search engine marketing", "google ads", "social media marketing", "content marketing", "seo specialist", "marketing executive"]) and software_score < 3:
            explicit_identity = "Digital Marketing Specialist"
            explicit_domain = "MARKETING"
            explicit_primary_roles = ["Marketing Executive", "Digital Marketing Specialist", "SEO Specialist"]
            explicit_related_roles = ["Marketing Coordinator", "Social Media Specialist", "Content Marketer"]
            explicit_queries = ["Digital Marketing", "Marketing Executive", "SEO Specialist"]
        elif any(k in text_for_identity for k in ["human resources", "talent acquisition", "recruitment", "onboarding", "hris", "hr executive", "hr generalist"]):
            explicit_identity = "Human Resources Specialist"
            explicit_domain = "HR"
            explicit_primary_roles = ["HR Executive", "Talent Acquisition Specialist", "HR Recruiter"]
            explicit_related_roles = ["HR Generalist", "HR Assistant"]
            explicit_queries = ["Human Resources", "HR Executive", "Talent Acquisition Specialist"]
        elif any(k in text_for_identity for k in ["b2b sales", "inside sales", "field sales", "client acquisition", "sales executive", "business development"]):
            explicit_identity = "Sales & Business Development Representative"
            explicit_domain = "SALES"
            explicit_primary_roles = ["Sales Executive", "Business Development Associate", "Account Executive"]
            explicit_related_roles = ["Sales Representative", "Business Development Manager"]
            explicit_queries = ["Sales Executive", "Business Development Associate", "Account Executive"]
        elif any(k in text_for_identity for k in ["graphic design", "graphic designer", "photoshop", "illustrator", "indesign", "figma", "ui design", "ux design", "typography"]):
            explicit_identity = "Graphic / UI Designer"
            explicit_domain = "DESIGN"
            explicit_primary_roles = ["Graphic Designer", "UI/UX Designer", "Visual Designer"]
            explicit_related_roles = ["Brand Identity Designer", "Creative Associate", "Digital Artist"]
            explicit_queries = ["Graphic Designer", "UI Designer", "Visual Designer"]
        elif any(k in text_for_identity for k in ["lawyer", "advocate", "legal", "ll.b", "ll.m", "litigation", "contract drafting", "corporate law"]):
            explicit_identity = "Legal Professional / Lawyer"
            explicit_domain = "LEGAL"
            explicit_primary_roles = ["Legal Counsel", "Legal Associate", "Corporate Lawyer"]
            explicit_related_roles = ["Contracts Specialist", "Legal Advisor", "Compliance Officer"]
            explicit_queries = ["Legal Counsel", "Legal Associate", "Corporate Lawyer"]
        elif any(k in text_for_identity for k in ["b.arch", "m.arch", "building design", "revit architecture", "spatial design", "interior architecture", "landscape architect", "architectural drafting"]) and software_score < 2:
            explicit_identity = "Architectural Designer"
            explicit_domain = "ARCHITECTURE"
            explicit_primary_roles = ["Architect", "Architectural Designer", "Building Designer"]
            explicit_related_roles = ["BIM Architect", "Interior Architect", "Draftsman"]
            explicit_queries = ["Architect", "Architectural Designer", "Building Designer"]
        elif any(k in text_for_identity for k in ["pharmacist", "pharmacy", "b.pharm", "m.pharm", "pharmacology", "dispensing"]):
            explicit_identity = "Pharmacist"
            explicit_domain = "PHARMACY"
            explicit_primary_roles = ["Pharmacist", "Clinical Pharmacist", "Retail Pharmacist"]
            explicit_related_roles = ["Pharma Executive", "Medical Representative", "Drug Safety Associate"]
            explicit_queries = ["Pharmacist", "Clinical Pharmacist", "Pharma Executive"]
        elif any(k in text_for_identity for k in ["logistics", "supply chain", "inventory management", "procurement", "warehouse", "vendor management"]):
            explicit_identity = "Logistics & Supply Chain Specialist"
            explicit_domain = "LOGISTICS_SUPPLY_CHAIN"
            explicit_primary_roles = ["Supply Chain Coordinator", "Logistics Executive", "Procurement Associate"]
            explicit_related_roles = ["Inventory Controller", "Warehouse Supervisor", "Vendor Management Executive"]
            explicit_queries = ["Supply Chain Coordinator", "Logistics Executive", "Procurement Specialist"]
        elif any(k in text_for_identity for k in ["hospitality", "hotel management", "front desk", "guest relations", "catering"]):
            explicit_identity = "Hospitality Professional"
            explicit_domain = "HOSPITALITY"
            explicit_primary_roles = ["Hospitality Executive", "Front Desk Officer", "Guest Relations Executive"]
            explicit_related_roles = ["Hotel Operations Associate", "Event Coordinator", "Customer Service Executive"]
            explicit_queries = ["Hospitality Executive", "Guest Relations Executive", "Hotel Operations"]

        # If an explicit profession was identified, prioritize it
        if explicit_identity:
            prof_identity = explicit_identity
            prof_domain = explicit_domain
            primary_roles = explicit_primary_roles
            related_roles = explicit_related_roles
            alt_roles = ["Professional Associate", "Operations Specialist"]
            search_queries = explicit_queries
        elif top_score > 0 and top_domain_key in cls.DOMAINS:
            domain_data = cls.DOMAINS[top_domain_key]
            prof_domain = top_domain_key
            prof_identity = domain_data["persona"]
            primary_roles = list(domain_data["base_roles"][:3])
            related_roles = list(domain_data["base_roles"][3:])
            alt_roles = [f"{domain_data['primary_search_keyword'].title()} Associate", "Operations Associate"]
            search_queries = [domain_data["primary_search_keyword"].title()] + list(domain_data["base_roles"][:2])
        else:
            prof_domain = "GENERAL_PROFESSIONAL"
            first_skill = tech_skills[0].title() if tech_skills else "Professional"
            prof_identity = f"{first_skill} Specialist" if tech_skills else "Professional Candidate"
            primary_roles = [f"{first_skill} Specialist", f"{first_skill} Executive", f"{first_skill} Associate"]
            related_roles = [f"{first_skill} Coordinator", "Operations Associate"]
            alt_roles = ["General Professional", "Project Assistant"]
            search_queries = [first_skill, f"{first_skill} Executive"]

        is_entry = any(k in exp_level for k in ["student", "fresher", "0-2", "graduate", "junior", "entry"])
        if is_entry:
            primary_roles = [f"Junior {r}" for r in primary_roles[:2]] + [primary_roles[0]]

        # Ensure search_queries has unique, non-empty, title-cased strings
        clean_queries = []
        for q in search_queries:
            sq = str(q).strip()
            if sq and sq not in clean_queries:
                clean_queries.append(sq)
        if not clean_queries:
            clean_queries = [primary_roles[0]]

        industries_map = {
            "HEALTHCARE": ["Healthcare & Hospitals", "Pharmaceuticals", "Medical Devices"],
            "ACCOUNTING_FINANCE": ["Accounting & Audit", "Financial Services", "Banking", "Corporate Finance"],
            "MECHANICAL_ENGINEERING": ["Automotive", "Manufacturing", "Aerospace & Defense", "Heavy Machinery"],
            "CIVIL_ENGINEERING": ["Construction & Real Estate", "Infrastructure", "Structural Engineering"],
            "ELECTRICAL_ENGINEERING": ["Power & Energy", "Electrical Equipment", "Automation & Robotics"],
            "EDUCATION": ["K-12 Education", "Higher Education", "EdTech", "Academic Research"],
            "MARKETING": ["Digital Media & Advertising", "E-Commerce", "Brand Management"],
            "SALES": ["B2B Enterprise Sales", "Consumer Retail", "Business Development"],
            "SOFTWARE_IT": ["Software Development", "Information Technology", "Cloud & SaaS"],
            "DESIGN": ["Creative Media", "UI/UX Design", "Product Design"],
            "LEGAL": ["Legal Services", "Corporate Law", "Regulatory Compliance"],
            "ARCHITECTURE": ["Architecture & Planning", "Interior Design", "Building Design"],
            "PHARMACY": ["Pharmaceuticals", "Clinical Research", "Healthcare"],
            "LOGISTICS_SUPPLY_CHAIN": ["Logistics & Freight", "Supply Chain Management", "Warehousing"],
            "HOSPITALITY": ["Hotels & Hospitality", "Tourism", "Customer Experience"]
        }

        inferred_industries = industries_map.get(prof_domain, ["General Corporate", "Services", "Operations"])

        return {
            # Conceptual Required Profile Fields:
            "professional_domain": prof_domain,
            "professional_identity": prof_identity,
            "current_or_latest_role": current_or_latest_role,
            "previous_roles": previous_roles,
            "experience_level": exp_level or "Fresher / Entry Level",
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
            "inferred_roles": (primary_roles + related_roles)[:5],
            "primary_search_keyword": clean_queries[0]
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
            "primary_roles": ["Professional Associate", "Executive"],
            "related_roles": ["Operations Assistant"],
            "alternative_roles": ["General Associate"],
            "search_queries": ["Associate"],
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
            "inferred_roles": ["Professional Associate", "Executive"],
            "primary_search_keyword": "associate"
        }

