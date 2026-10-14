import logging
import re

logger = logging.getLogger(__name__)

class RoleInferenceEngine:
    """
    Universal Resume-Driven Candidate Profile & Target Role Inference Engine.
    Analyzes parsed resume skills, trade competencies, licenses, education, experience,
    and domain text to determine the candidate's actual profession across ALL sectors
    (Skilled Trades: Electrician, Plumber, Welder, Mechanic, HVAC; Healthcare, Education,
    Accounting/Finance, Hospitality/Culinary, Logistics/Warehouse, Construction, Agriculture,
    Sales/Retail, Office Administration, Engineering, and IT) and automatically infers
    suitable target job roles and search queries.
    """

    DOMAINS = {
        "SKILLED_TRADES_ELECTRICAL": {
            "persona": "Licensed Electrician & Electrical Systems Technician",
            "keywords": {
                "electrician", "electrical", "wiring", "conduit", "circuit breaker",
                "switchgear", "panel board", "multimeter", "high voltage", "low voltage",
                "troubleshooting", "cable pulling", "motor control", "nec", "national electrical code",
                "journeyman electrician", "master electrician", "electrical maintenance",
                "electrical helper", "industrial electrical", "residential electrical",
                "commercial electrical", "lockout", "tagout", "loto", "iti electrician",
                "substation", "switchboard", "breaker", "wireman"
            },
            "base_roles": [
                "Electrician", "Electrical Maintenance Technician", "Commercial Electrician",
                "Industrial Electrician", "Residential Electrician", "Electrical Helper"
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
                "tire mounting", "wheel alignment", "preventative maintenance"
            },
            "base_roles": [
                "Automotive Technician", "Auto Mechanic", "Maintenance Mechanic", "Diesel Mechanic", "Service Technician"
            ],
            "primary_search_keyword": "automotive mechanic",
            "search_queries": ["Automotive Technician", "Auto Mechanic", "Maintenance Mechanic"]
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
        "HEALTHCARE": {
            "persona": "Healthcare & Registered Nursing Specialist",
            "keywords": {
                "nursing", "nurse", "registered nurse", "staff nurse", "clinical nurse",
                "patient care", "medication", "hospital", "vital signs", "wound dressing",
                "iv administration", "b.sc nursing", "m.sc nursing", "gnm", "anm",
                "patient triage", "clinical", "rn", "catheterization", "icu nurse"
            },
            "base_roles": [
                "Staff Nurse", "Registered Nurse", "Clinical Nurse", "Hospital Nurse", "Nursing Assistant"
            ],
            "primary_search_keyword": "nurse",
            "search_queries": ["Staff Nurse", "Registered Nurse", "Clinical Nurse"]
        },
        "HEALTHCARE_SUPPORT": {
            "persona": "Caregiver & Medical Support Specialist",
            "keywords": {
                "caregiver", "caregiving", "home health aide", "cna", "certified nursing assistant",
                "medical assistant", "elderly care", "patient hygiene", "phlebotomist",
                "phlebotomy", "medical lab technician", "mlt", "specimen collection",
                "activities of daily living", "assisted living"
            },
            "base_roles": [
                "Caregiver", "Medical Assistant", "Certified Nursing Assistant", "Home Health Aide", "Medical Laboratory Technician"
            ],
            "primary_search_keyword": "medical assistant",
            "search_queries": ["Caregiver", "Medical Assistant", "Certified Nursing Assistant"]
        },
        "EDUCATION": {
            "persona": "Education & Teaching Specialist",
            "keywords": {
                "teaching", "teacher", "b.ed", "m.ed", "curriculum", "lesson planning",
                "classroom management", "pedagogy", "tutor", "lecturer", "professor",
                "education", "school teacher", "subject teacher", "academic counselor",
                "special education", "tutoring", "student mentoring"
            },
            "base_roles": [
                "School Teacher", "Subject Teacher", "Tutor", "Education Coordinator", "Academic Counselor", "Lecturer"
            ],
            "primary_search_keyword": "teacher",
            "search_queries": ["School Teacher", "Subject Teacher", "Teacher"]
        },
        "ACCOUNTING_FINANCE": {
            "persona": "Accounting & Finance Specialist",
            "keywords": {
                "accounting", "accountant", "tally", "gst", "bookkeeping", "bookkeeper",
                "taxation", "financial analysis", "auditing", "auditor", "accounts payable",
                "accounts receivable", "balance sheet", "tally prime", "cpa", "chartered accountant",
                "ca", "b.com", "m.com", "payroll", "invoice", "tally erp", "tds", "finance executive"
            },
            "base_roles": [
                "Accountant", "Accounts Executive", "Junior Accountant", "Bookkeeper", "Financial Analyst", "Finance Executive"
            ],
            "primary_search_keyword": "accountant",
            "search_queries": ["Accountant", "Accounts Executive", "Junior Accountant"]
        },
        "ADMINISTRATION_OFFICE": {
            "persona": "Office Administration & Executive Support Specialist",
            "keywords": {
                "administrative assistant", "office administrator", "executive assistant",
                "receptionist", "office assistant", "office coordinator", "data entry",
                "calendar management", "filing", "scheduling", "secretarial", "office support",
                "front desk coordinator", "clerk"
            },
            "base_roles": [
                "Administrative Assistant", "Office Administrator", "Executive Assistant", "Receptionist", "Office Coordinator", "Data Entry Specialist"
            ],
            "primary_search_keyword": "administrative assistant",
            "search_queries": ["Administrative Assistant", "Office Administrator", "Receptionist"]
        },
        "HOSPITALITY_CULINARY": {
            "persona": "Culinary & Hospitality Specialist",
            "keywords": {
                "chef", "cook", "line cook", "sous chef", "culinary arts", "food preparation",
                "kitchen manager", "food safety", "haccp", "baking", "restaurant",
                "hotel", "guest service", "front desk", "food service", "catering", "bartender"
            },
            "base_roles": [
                "Chef", "Line Cook", "Kitchen Manager", "Food Service Worker", "Sous Chef", "Hotel Front Desk Associate"
            ],
            "primary_search_keyword": "chef",
            "search_queries": ["Chef", "Line Cook", "Food Service Worker"]
        },
        "LOGISTICS_WAREHOUSE": {
            "persona": "Logistics, Transportation & Warehouse Specialist",
            "keywords": {
                "warehouse", "forklift", "forklift operator", "order picker", "warehouse associate",
                "material handler", "shipping", "receiving", "logistics", "cdl",
                "commercial driver", "truck driver", "delivery driver", "inventory tracking",
                "pallet jack", "supply chain", "freight"
            },
            "base_roles": [
                "Forklift Operator", "Warehouse Associate", "Order Picker", "Material Handler", "Delivery Driver", "Logistics Coordinator"
            ],
            "primary_search_keyword": "warehouse associate",
            "search_queries": ["Forklift Operator", "Warehouse Associate", "Order Picker"]
        },
        "CONSTRUCTION_CARPENTRY": {
            "persona": "Construction & Carpentry Specialist",
            "keywords": {
                "carpenter", "carpentry", "framing", "drywall", "roofing", "masonry",
                "concrete", "construction worker", "construction laborer", "foreman",
                "scaffolding", "site safety", "osha", "mason"
            },
            "base_roles": [
                "Carpenter", "Construction Worker", "Drywall Installer", "Construction Foreman", "Mason", "Construction Laborer"
            ],
            "primary_search_keyword": "carpenter",
            "search_queries": ["Carpenter", "Construction Worker", "Drywall Installer"]
        },
        "SALES_RETAIL": {
            "persona": "Sales & Retail Customer Specialist",
            "keywords": {
                "sales", "sales executive", "sales representative", "retail sales",
                "cashier", "retail associate", "customer service representative",
                "pos", "store associate", "b2b sales", "inside sales", "business development",
                "client acquisition", "lead generation"
            },
            "base_roles": [
                "Sales Executive", "Retail Associate", "Cashier", "Customer Service Representative", "Store Associate", "Account Executive"
            ],
            "primary_search_keyword": "sales executive",
            "search_queries": ["Sales Executive", "Retail Associate", "Customer Service Representative"]
        },
        "AGRICULTURE": {
            "persona": "Agricultural & Farm Operations Specialist",
            "keywords": {
                "agriculture", "farming", "crop management", "tractor operator",
                "irrigation", "harvesting", "farm worker", "farm equipment", "livestock",
                "soil management", "agronomy"
            },
            "base_roles": [
                "Agricultural Specialist", "Farm Equipment Operator", "Crop Specialist", "Farm Worker"
            ],
            "primary_search_keyword": "agricultural worker",
            "search_queries": ["Agricultural Specialist", "Farm Equipment Operator", "Farm Worker"]
        },
        "MECHANICAL_ENGINEERING": {
            "persona": "Mechanical Design & Manufacturing Engineer",
            "keywords": {
                "mechanical engineering", "solidworks", "catia", "ansys", "machining",
                "manufacturing", "cnc", "cad", "cam", "thermodynamics", "hydraulics",
                "b.e mechanical", "b.tech mechanical", "mechanical design", "production engineering"
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
                "staad pro", "quantity surveying", "surveying", "construction management",
                "b.e civil", "b.tech civil", "autocad civil"
            },
            "base_roles": [
                "Civil Engineer", "Site Engineer", "Structural Engineer", "Construction Project Engineer", "Quantity Surveyor"
            ],
            "primary_search_keyword": "civil engineer",
            "search_queries": ["Civil Engineer", "Site Engineer", "Structural Engineer"]
        },
        "ELECTRICAL_ENGINEERING": {
            "persona": "Electrical & Control Systems Engineer",
            "keywords": {
                "electrical engineering", "power electronics", "circuit design", "matlab",
                "simulink", "plc", "scada", "b.e electrical", "b.tech electrical",
                "power systems", "control systems", "embedded systems"
            },
            "base_roles": [
                "Electrical Engineer", "Electrical Design Engineer", "Power Engineer", "Control Systems Engineer"
            ],
            "primary_search_keyword": "electrical engineer",
            "search_queries": ["Electrical Engineer", "Electrical Design Engineer", "Power Engineer"]
        },
        "SOFTWARE_IT": {
            "persona": "Software & Technology Specialist",
            "keywords": {
                "python", "java", "c++", "c#", "javascript", "typescript", "react", "node.js",
                "nodejs", "express", "mongodb", "sql", "flask", "django", "spring boot",
                "html", "css", "vue", "angular", "aws", "docker", "kubernetes", "git",
                "machine learning", "data science", "nlp", "ai", "pandas", "numpy",
                "scikit-learn", "tensorflow", "pytorch", "devops", "software engineer",
                "software developer", "full stack", "backend", "frontend", "computer science",
                "b.tech cse", "bca", "mca", "information technology"
            },
            "base_roles": [
                "Software Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer", "Python Developer", "Data Analyst"
            ],
            "primary_search_keyword": "software engineer",
            "search_queries": ["Software Engineer", "Full Stack Developer", "Backend Developer"]
        },
        "MARKETING": {
            "persona": "Digital Marketing Specialist",
            "keywords": {
                "marketing", "digital marketing", "seo", "sem", "google ads", "social media marketing",
                "content marketing", "copywriting", "brand management", "email marketing",
                "lead generation", "market research"
            },
            "base_roles": [
                "Marketing Executive", "Digital Marketing Specialist", "SEO Specialist", "Content Marketer", "Social Media Coordinator"
            ],
            "primary_search_keyword": "digital marketing",
            "search_queries": ["Marketing Executive", "Digital Marketing Specialist", "SEO Specialist"]
        },
        "HR": {
            "persona": "Human Resources Specialist",
            "keywords": {
                "human resources", "recruitment", "talent acquisition", "employee relations",
                "payroll management", "hr executive", "onboarding", "hris", "performance management",
                "hr generalist", "hr recruiter"
            },
            "base_roles": [
                "HR Executive", "Talent Acquisition Specialist", "HR Generalist", "HR Recruiter"
            ],
            "primary_search_keyword": "human resources",
            "search_queries": ["HR Executive", "Talent Acquisition Specialist", "HR Generalist"]
        },
        "LEGAL": {
            "persona": "Legal Professional",
            "keywords": {
                "lawyer", "advocate", "legal counsel", "ll.b", "ll.m", "litigation",
                "corporate law", "contract drafting", "paralegal", "compliance"
            },
            "base_roles": [
                "Legal Counsel", "Legal Associate", "Corporate Lawyer", "Paralegal"
            ],
            "primary_search_keyword": "legal counsel",
            "search_queries": ["Legal Counsel", "Legal Associate", "Corporate Lawyer"]
        },
        "SCIENCE_RESEARCH": {
            "persona": "Scientific Researcher",
            "keywords": {
                "research scientist", "physicist", "chemist", "biologist", "astrophysicist",
                "microbiology", "laboratory research", "postdoctoral", "ph.d", "phd", "spectroscopy"
            },
            "base_roles": [
                "Research Scientist", "Staff Scientist", "Lab Researcher", "Research Associate"
            ],
            "primary_search_keyword": "research scientist",
            "search_queries": ["Research Scientist", "Staff Scientist", "Research Associate"]
        },
        "ARCHITECTURE": {
            "persona": "Architectural Designer",
            "keywords": {
                "architecture", "architect", "b.arch", "m.arch", "building design", "revit",
                "sketchup", "spatial planning", "architectural drafting", "bim", "interior architecture",
                "residential design", "commercial architecture", "autocad"
            },
            "base_roles": [
                "Architectural Designer", "Architect", "BIM Architect", "Building Designer"
            ],
            "primary_search_keyword": "architect",
            "search_queries": ["Architectural Designer", "Architect", "BIM Architect"]
        }
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

        tech_skills = analysis_json.get("technical_skills", [])
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
            current_or_latest_role = str(work_exp[0].get("role", "")).strip()
            for w in work_exp[1:]:
                if w.get("role"):
                    previous_roles.append(str(w.get("role")).strip())

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

        for d_key, d_data in cls.DOMAINS.items():
            score = 0.0
            kw_set = d_data["keywords"]

            # Signal 1: Work Experience Role Matches (Weight: 4.0 per match)
            # Employment history is the strongest single indicator of actual profession
            for kw in kw_set:
                if len(kw) > 3:
                    if re.search(r'\b' + re.escape(kw) + r'\b', cand_work_roles_text):
                        score += 4.0
                        if current_or_latest_role and re.search(r'\b' + re.escape(kw) + r'\b', current_or_latest_role.lower()):
                            score += 2.0  # Extra weight for current role

            # Signal 2: Licenses & Certifications (Weight: 3.5 per match)
            # Professional trade licenses, state board credentials, CDL, RN, CPA, etc.
            for kw in kw_set:
                if len(kw) > 3 and re.search(r'\b' + re.escape(kw) + r'\b', cand_certs_text):
                    score += 3.5

            # Signal 3: Specific Skills & Tools (Weight: 2.0 per match)
            for kw in kw_set:
                if len(kw) > 2 and re.search(r'\b' + re.escape(kw) + r'\b', cand_skills_text):
                    score += 2.0

            # Signal 4: Education & Vocational Qualifications (Weight: 1.5 per match)
            # ITI, Trade Diploma, B.Sc Nursing, B.Ed, etc.
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
            # Genuine fallback when no specific profession keywords detected
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
            related_roles = list(domain_data["base_roles"][3:])
            alt_roles = [f"{domain_data['primary_search_keyword'].title()} Associate", "Operations Specialist"]
            search_queries = list(domain_data.get("search_queries", [domain_data["primary_search_keyword"].title()]))

            # Check for close secondary domain (multi-discipline / ambiguity)
            if second_score > 0 and (top_score - second_score) < 2.5:
                is_ambiguous = True
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

        # Check if work history specifically names an exact role that should lead primary roles
        if current_or_latest_role and len(current_or_latest_role) > 3:
            role_clean = current_or_latest_role.title()
            if role_clean not in primary_roles and prof_domain != "GENERAL_PROFESSIONAL":
                # Prepend the candidate's actual job title if it matches domain keywords
                d_kws = cls.DOMAINS.get(prof_domain, {}).get("keywords", set())
                if any(w in d_kws for w in current_or_latest_role.lower().split()):
                    primary_roles = [role_clean] + primary_roles[:2]
                    search_queries = [role_clean] + [q for q in search_queries if q != role_clean]

        is_entry = any(k in exp_level for k in ["student", "fresher", "0-2", "graduate", "junior", "entry"])
        if is_entry and prof_domain not in ["SKILLED_TRADES_ELECTRICAL", "SKILLED_TRADES_PLUMBING", "SKILLED_TRADES_WELDING"]:
            primary_roles = [f"Junior {r}" for r in primary_roles[:2]] + [primary_roles[0]]

        clean_queries = []
        for q in search_queries:
            sq = str(q).strip()
            if sq and sq not in clean_queries:
                clean_queries.append(sq)
        if not clean_queries:
            clean_queries = [primary_roles[0]]

        industries_map = {
            "SKILLED_TRADES_ELECTRICAL": ["Electrical Construction", "Building Maintenance", "Industrial Manufacturing", "Utilities"],
            "SKILLED_TRADES_PLUMBING": ["Plumbing & Piping", "Construction", "Facility Maintenance"],
            "SKILLED_TRADES_WELDING": ["Metal Fabrication", "Manufacturing", "Structural Construction"],
            "SKILLED_TRADES_MECHANIC": ["Automotive Services", "Fleet Maintenance", "Transportation Repair"],
            "SKILLED_TRADES_HVAC": ["HVAC/R Contracting", "Building Services", "Mechanical Contracting"],
            "HEALTHCARE": ["Healthcare & Hospitals", "Clinical Care", "Medical Facilities"],
            "HEALTHCARE_SUPPORT": ["Home Healthcare", "Assisted Living", "Outpatient Clinics", "Diagnostic Labs"],
            "EDUCATION": ["K-12 Education", "Higher Education", "Vocational Training", "Tutoring"],
            "ACCOUNTING_FINANCE": ["Accounting & Audit", "Financial Services", "Corporate Finance"],
            "ADMINISTRATION_OFFICE": ["Corporate Administration", "Office Management", "Professional Services"],
            "HOSPITALITY_CULINARY": ["Restaurants & Food Service", "Hotels & Lodging", "Catering & Events"],
            "LOGISTICS_WAREHOUSE": ["Warehousing & Distribution", "Freight & Logistics", "Transportation"],
            "CONSTRUCTION_CARPENTRY": ["Residential & Commercial Construction", "Carpentry & Framing"],
            "SALES_RETAIL": ["Retail & Consumer Goods", "B2B Sales", "Customer Support"],
            "AGRICULTURE": ["Farming & Agriculture", "Agribusiness", "Crop & Livestock Production"],
            "MECHANICAL_ENGINEERING": ["Automotive", "Manufacturing", "Heavy Machinery", "Aerospace"],
            "CIVIL_ENGINEERING": ["Civil Infrastructure", "Structural Engineering", "Construction Management"],
            "ELECTRICAL_ENGINEERING": ["Power Systems", "Control Systems", "Electrical Engineering"],
            "SOFTWARE_IT": ["Software Development", "Information Technology", "Cloud & SaaS"],
            "MARKETING": ["Digital Media & Advertising", "Brand Strategy", "E-Commerce"],
            "HR": ["Human Resources", "Talent Management", "Staffing"],
            "LEGAL": ["Legal Services", "Corporate Compliance", "Law Practice"],
            "SCIENCE_RESEARCH": ["Scientific Research", "R&D Laboratories", "Academic Research"],
            "ARCHITECTURE": ["Architecture & Planning", "Building Design", "Construction Consulting"]
        }

        inferred_industries = industries_map.get(prof_domain, ["General Industry", "Services", "Operations"])

        # Extract tools & trade equipment
        known_tools = [
            "Multimeter", "Conduit Bender", "Wire Strippers", "Megohmmeter", "Circuit Tester",
            "Pipe Wrench", "Soldering Torch", "Drain Snake", "PEX Crimper",
            "MIG Welder", "TIG Welder", "Plasma Cutter", "Angle Grinder",
            "OBD-II Scanner", "Torque Wrench", "Hydraulic Lift", "Brake Lathe",
            "Manifold Gauges", "Vacuum Pump", "Refrigerant Scale", "Leak Detector",
            "Forklift", "Pallet Jack", "RF Scanner", "Hand Truck",
            "AutoCAD", "SolidWorks", "Tally", "QuickBooks", "Excel", "Photoshop", "VS Code"
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

            # Multi-Profession & Uncertainty Attributes (Tasks 2 & 7):
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
