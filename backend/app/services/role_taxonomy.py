import logging
import re

logger = logging.getLogger(__name__)

class RoleTaxonomy:
    """
    Centralized Universal Role Taxonomy and Exclusion Dictionary.
    Maps canonical roles across all major professions:
    - Artificial Intelligence & Machine Learning (AI Engineer, ML Engineer, NLP, CV, MLOps, etc.)
    - Data Science & Analytics (Data Scientist, Data Analyst, BI Analyst, Data Engineer, etc.)
    - Software Development (Software Engineer, Developer, Application Developer)
    - Full Stack Development (Full Stack, MERN, MEAN, React/Node, etc.)
    - Frontend Development (Frontend, React, Angular, Vue, UI Engineer)
    - Backend Development (Backend, Python, Java, Node.js, API, .NET, PHP)
    - Cloud & Infrastructure (DevOps, Cloud Engineer, AWS, Azure, SRE, Platform)
    - Cybersecurity (Security Analyst, SOC Analyst, Penetration Tester, etc.)
    - Other Tech (QA, Tester, DBA, Network Engineer, IT Support, Mobile, Embedded)
    - Skilled Trades (Electrician, Plumber, Welder, Automotive Mechanic, HVAC, Maintenance)
    - Healthcare (Registered Nurse, Staff Nurse, Nursing Assistant, Caregiver, Med Lab Tech, Radiology)
    - Business & Finance (Accountant, Accounts Executive, Bookkeeper, Auditor, Financial Analyst, Tax, HR, Admin)
    - Education (School Teacher, Subject Teacher, Tutor, Instructor, Trainer)
    - Other Sectors (Chef, Warehouse/Forklift, Carpenter, Sales, Marketing, Civil/Mechanical Engineering)
    to equivalent title patterns and strict negative patterns.
    """

    ROLE_TAXONOMY = {
        # =====================================================================
        # A. ARTIFICIAL INTELLIGENCE & MACHINE LEARNING
        # =====================================================================
        "AI Engineer": {
            "canonical": "AI Engineer",
            "domain": "AI_ML",
            "allowed_patterns": [
                r"\bai\s+engineer\b",
                r"\bartificial\s+intelligence\s+engineer\b",
                r"\bai\s+specialist\b",
                r"\bai\s+developer\b",
                r"\bai\s+architect\b",
                r"\bapplied\s+ai\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bplumber\b", r"\bwelder\b", r"\bmechanic\b",
                r"\bnurse\b", r"\baccountant\b", r"\bbookkeeper\b", r"\bteacher\b",
                r"\bfrontend\s+developer\b", r"\bweb\s+developer\b"
            ]
        },
        "Machine Learning Engineer": {
            "canonical": "Machine Learning Engineer",
            "domain": "AI_ML",
            "allowed_patterns": [
                r"\bmachine\s+learning\s+engineer\b",
                r"\bml\s+engineer\b",
                r"\bml\s+developer\b",
                r"\bml\s+specialist\b",
                r"\bmachine\s+learning\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bplumber\b", r"\bwelder\b", r"\bmechanic\b",
                r"\bnurse\b", r"\baccountant\b", r"\bbookkeeper\b", r"\bteacher\b",
                r"\bfrontend\s+developer\b"
            ]
        },
        "Applied AI Engineer": {
            "canonical": "Applied AI Engineer",
            "domain": "AI_ML",
            "allowed_patterns": [
                r"\bapplied\s+ai\s+engineer\b",
                r"\bapplied\s+machine\s+learning\s+engineer\b",
                r"\bapplied\s+ai\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b", r"\bteacher\b"
            ]
        },
        "Generative AI Engineer": {
            "canonical": "Generative AI Engineer",
            "domain": "AI_ML",
            "allowed_patterns": [
                r"\bgenerative\s+ai\s+engineer\b",
                r"\bgen\s*ai\s+engineer\b",
                r"\bgenai\s+developer\b",
                r"\bllm\s+engineer\b",
                r"\bllm\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b", r"\bteacher\b"
            ]
        },
        "NLP Engineer": {
            "canonical": "NLP Engineer",
            "domain": "AI_ML",
            "allowed_patterns": [
                r"\bnlp\s+engineer\b",
                r"\bnatural\s+language\s+processing\s+engineer\b",
                r"\bnlp\s+scientist\b",
                r"\bnlp\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b", r"\bteacher\b"
            ]
        },
        "Computer Vision Engineer": {
            "canonical": "Computer Vision Engineer",
            "domain": "AI_ML",
            "allowed_patterns": [
                r"\bcomputer\s+vision\s+engineer\b",
                r"\bcv\s+engineer\b",
                r"\bvision\s+engineer\b",
                r"\bimage\s+processing\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b", r"\bteacher\b"
            ]
        },
        "MLOps Engineer": {
            "canonical": "MLOps Engineer",
            "domain": "AI_ML",
            "allowed_patterns": [
                r"\bmlops\s+engineer\b",
                r"\bmachine\s+learning\s+operations\b",
                r"\bml\s+infrastructure\s+engineer\b",
                r"\bml\s+platform\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b", r"\bteacher\b"
            ]
        },
        "Research Engineer": {
            "canonical": "Research Engineer",
            "domain": "AI_ML",
            "allowed_patterns": [
                r"\bresearch\s+engineer\b",
                r"\bai\s+research\s+engineer\b",
                r"\bml\s+research\s+engineer\b",
                r"\bresearch\s+scientist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # B. DATA SCIENCE & ANALYTICS
        # =====================================================================
        "Data Scientist": {
            "canonical": "Data Scientist",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\bdata\s+scientist\b",
                r"\bassociate\s+data\s+scientist\b",
                r"\bsenior\s+data\s+scientist\b",
                r"\blead\s+data\s+scientist\b",
                r"\bdata\s+science\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bplumber\b", r"\bwelder\b", r"\bmechanic\b",
                r"\bnurse\b", r"\baccountant\b", r"\bbookkeeper\b", r"\bteacher\b",
                r"\btax\s+associate\b"
            ]
        },
        "Junior Data Scientist": {
            "canonical": "Junior Data Scientist",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\bjunior\s+data\s+scientist\b",
                r"\bjr\.?\s+data\s+scientist\b",
                r"\bentry[- ]level\s+data\s+scientist\b",
                r"\btrainee\s+data\s+scientist\b",
                r"\bdata\s+scientist\s+intern\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Data Analyst": {
            "canonical": "Data Analyst",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\bdata\s+analyst\b",
                r"\bjunior\s+data\s+analyst\b",
                r"\bjr\.?\s+data\s+analyst\b",
                r"\bbusiness\s+data\s+analyst\b",
                r"\banalytics\s+specialist\b",
                r"\bdata\s+analytics\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bplumber\b", r"\bwelder\b", r"\bmechanic\b",
                r"\bnurse\b", r"\baccountant\b", r"\bbookkeeper\b", r"\bauditor\b",
                r"\btax\b", r"\bpayroll\b", r"\bteacher\b"
            ]
        },
        "Business Intelligence Analyst": {
            "canonical": "Business Intelligence Analyst",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\bbusiness\s+intelligence\s+analyst\b",
                r"\bbi\s+analyst\b",
                r"\bbi\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "BI Developer": {
            "canonical": "BI Developer",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\bbi\s+developer\b",
                r"\bbusiness\s+intelligence\s+developer\b",
                r"\btableau\s+developer\b",
                r"\bpower\s*bi\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Business Analyst": {
            "canonical": "Business Analyst",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\bbusiness\s+analyst\b",
                r"\bjr\.?\s+business\s+analyst\b",
                r"\bit\s+business\s+analyst\b",
                r"\btechnical\s+business\s+analyst\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bnurse\b", r"\baccountant\b"
            ]
        },
        "Reporting Analyst": {
            "canonical": "Reporting Analyst",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\breporting\s+analyst\b",
                r"\bmis\s+analyst\b",
                r"\bmis\s+executive\b",
                r"\bdata\s+reporting\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bnurse\b"
            ]
        },
        "Data Engineer": {
            "canonical": "Data Engineer",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\bdata\s+engineer\b",
                r"\bjunior\s+data\s+engineer\b",
                r"\bbig\s+data\s+engineer\b",
                r"\betl\s+developer\b",
                r"\bdata\s+pipeline\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Analytics Engineer": {
            "canonical": "Analytics Engineer",
            "domain": "DATA_SCIENCE_ANALYTICS",
            "allowed_patterns": [
                r"\banalytics\s+engineer\b",
                r"\bdbt\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # C. SOFTWARE DEVELOPMENT
        # =====================================================================
        "Software Engineer": {
            "canonical": "Software Engineer",
            "domain": "SOFTWARE_DEVELOPMENT",
            "allowed_patterns": [
                r"\bsoftware\s+engineer\b",
                r"\bassociate\s+software\s+engineer\b",
                r"\bsenior\s+software\s+engineer\b",
                r"\bsoftware\s+development\s+engineer\b",
                r"\bsde\b"
            ],
            "excluded_patterns": [
                r"\bfull[- ]?stack\b", r"\bfullstack\b", r"\bfrontend\b", r"\bfront[- ]?end\b",
                r"\belectrician\b", r"\bplumber\b", r"\bwelder\b", r"\bmechanic\b",
                r"\bnurse\b", r"\baccountant\b", r"\bbookkeeper\b", r"\bteacher\b",
                r"\bcivil\s+engineer\b"
            ]
        },
        "Software Developer": {
            "canonical": "Software Developer",
            "domain": "SOFTWARE_DEVELOPMENT",
            "allowed_patterns": [
                r"\bsoftware\s+developer\b",
                r"\bprogrammer\b",
                r"\bsoftware\s+programmer\b"
            ],
            "excluded_patterns": [
                r"\bfull[- ]?stack\b", r"\bfullstack\b", r"\bfrontend\b", r"\bfront[- ]?end\b",
                r"\belectrician\b", r"\bplumber\b", r"\bwelder\b", r"\bmechanic\b",
                r"\bnurse\b", r"\baccountant\b", r"\bteacher\b"
            ]
        },
        "Application Developer": {
            "canonical": "Application Developer",
            "domain": "SOFTWARE_DEVELOPMENT",
            "allowed_patterns": [
                r"\bapplication\s+developer\b",
                r"\bapplications\s+developer\b",
                r"\bapp\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Junior Software Engineer": {
            "canonical": "Junior Software Engineer",
            "domain": "SOFTWARE_DEVELOPMENT",
            "allowed_patterns": [
                r"\bjunior\s+software\s+engineer\b",
                r"\bjr\.?\s+software\s+engineer\b",
                r"\bjunior\s+developer\b",
                r"\bjr\.?\s+developer\b",
                r"\bentry[- ]level\s+software\s+engineer\b",
                r"\btrainee\s+software\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Graduate Software Engineer": {
            "canonical": "Graduate Software Engineer",
            "domain": "SOFTWARE_DEVELOPMENT",
            "allowed_patterns": [
                r"\bgraduate\s+software\s+engineer\b",
                r"\bgraduate\s+developer\b",
                r"\bsoftware\s+engineer\s+trainee\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # D. FULL STACK DEVELOPMENT
        # =====================================================================
        "Full Stack Developer": {
            "canonical": "Full Stack Developer",
            "domain": "FULL_STACK_DEVELOPMENT",
            "allowed_patterns": [
                r"\bfull[- ]?stack\s+developer\b",
                r"\bfull[- ]?stack\s+engineer\b",
                r"\bfullstack\s+web\s+developer\b",
                r"\bfull[- ]?stack\s+software\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bplumber\b", r"\bwelder\b", r"\bmechanic\b",
                r"\bnurse\b", r"\baccountant\b", r"\bteacher\b"
            ]
        },
        "MERN Stack Developer": {
            "canonical": "MERN Stack Developer",
            "domain": "FULL_STACK_DEVELOPMENT",
            "allowed_patterns": [
                r"\bmern\s+stack\s+developer\b",
                r"\bmern\s+developer\b",
                r"\bmern\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "MEAN Stack Developer": {
            "canonical": "MEAN Stack Developer",
            "domain": "FULL_STACK_DEVELOPMENT",
            "allowed_patterns": [
                r"\bmean\s+stack\s+developer\b",
                r"\bmean\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "React and Node.js Developer": {
            "canonical": "React and Node.js Developer",
            "domain": "FULL_STACK_DEVELOPMENT",
            "allowed_patterns": [
                r"\breact\s+(?:and|&)\s+node(?:\.js)?\s+developer\b",
                r"\bnode(?:\.js)?\s+(?:and|&)\s+react\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Java Full Stack Developer": {
            "canonical": "Java Full Stack Developer",
            "domain": "FULL_STACK_DEVELOPMENT",
            "allowed_patterns": [
                r"\bjava\s+full[- ]?stack\s+developer\b",
                r"\bjava\s+full[- ]?stack\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Python Full Stack Developer": {
            "canonical": "Python Full Stack Developer",
            "domain": "FULL_STACK_DEVELOPMENT",
            "allowed_patterns": [
                r"\bpython\s+full[- ]?stack\s+developer\b",
                r"\bpython\s+full[- ]?stack\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # E. FRONTEND DEVELOPMENT
        # =====================================================================
        "Frontend Developer": {
            "canonical": "Frontend Developer",
            "domain": "FRONTEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bfront[- ]?end\s+developer\b",
                r"\bfront[- ]?end\s+engineer\b",
                r"\bfrontend\s+web\s+developer\b",
                r"\bclient[- ]side\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "React Developer": {
            "canonical": "React Developer",
            "domain": "FRONTEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\breact\s+developer\b",
                r"\breact\.?js\s+developer\b",
                r"\breact\s+frontend\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Angular Developer": {
            "canonical": "Angular Developer",
            "domain": "FRONTEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bangular\s+developer\b",
                r"\bangular\s+frontend\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Vue.js Developer": {
            "canonical": "Vue.js Developer",
            "domain": "FRONTEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bvue(?:\.js)?\s+developer\b",
                r"\bvue\s+frontend\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "UI Engineer": {
            "canonical": "UI Engineer",
            "domain": "FRONTEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bui\s+engineer\b",
                r"\bui\s+developer\b",
                r"\buser\s+interface\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # F. BACKEND DEVELOPMENT
        # =====================================================================
        "Backend Developer": {
            "canonical": "Backend Developer",
            "domain": "BACKEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bback[- ]?end\s+developer\b",
                r"\bback[- ]?end\s+engineer\b",
                r"\bserver[- ]side\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Python Developer": {
            "canonical": "Python Developer",
            "domain": "BACKEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bpython\s+developer\b",
                r"\bpython\s+backend\s+developer\b",
                r"\bdjango\s+developer\b",
                r"\bflask\s+developer\b",
                r"\bfastapi\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Java Developer": {
            "canonical": "Java Developer",
            "domain": "BACKEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bjava\s+developer\b",
                r"\bjava\s+backend\s+developer\b",
                r"\bspring\s+boot\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Node.js Developer": {
            "canonical": "Node.js Developer",
            "domain": "BACKEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bnode(?:\.js)?\s+developer\b",
                r"\bnode\s+backend\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "API Developer": {
            "canonical": "API Developer",
            "domain": "BACKEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bapi\s+developer\b",
                r"\brest\s+api\s+developer\b",
                r"\bbackend\s+api\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        ".NET Developer": {
            "canonical": ".NET Developer",
            "domain": "BACKEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\b\.?net\s+developer\b",
                r"\bc#\s+developer\b",
                r"\basp\.net\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "PHP Developer": {
            "canonical": "PHP Developer",
            "domain": "BACKEND_DEVELOPMENT",
            "allowed_patterns": [
                r"\bphp\s+developer\b",
                r"\blaravel\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # G. CLOUD & INFRASTRUCTURE
        # =====================================================================
        "DevOps Engineer": {
            "canonical": "DevOps Engineer",
            "domain": "CLOUD_INFRASTRUCTURE",
            "allowed_patterns": [
                r"\bdevops\s+engineer\b",
                r"\bcloud\s+devops\s+engineer\b",
                r"\bdevops\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Cloud Engineer": {
            "canonical": "Cloud Engineer",
            "domain": "CLOUD_INFRASTRUCTURE",
            "allowed_patterns": [
                r"\bcloud\s+engineer\b",
                r"\bcloud\s+solutions\s+engineer\b",
                r"\bcloud\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "AWS Engineer": {
            "canonical": "AWS Engineer",
            "domain": "CLOUD_INFRASTRUCTURE",
            "allowed_patterns": [
                r"\baws\s+engineer\b",
                r"\baws\s+cloud\s+engineer\b",
                r"\baws\s+solutions\s+architect\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Azure Engineer": {
            "canonical": "Azure Engineer",
            "domain": "CLOUD_INFRASTRUCTURE",
            "allowed_patterns": [
                r"\bazure\s+engineer\b",
                r"\bazure\s+cloud\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Platform Engineer": {
            "canonical": "Platform Engineer",
            "domain": "CLOUD_INFRASTRUCTURE",
            "allowed_patterns": [
                r"\bplatform\s+engineer\b",
                r"\binfrastructure\s+platform\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Site Reliability Engineer": {
            "canonical": "Site Reliability Engineer",
            "domain": "CLOUD_INFRASTRUCTURE",
            "allowed_patterns": [
                r"\bsite\s+reliability\s+engineer\b",
                r"\bsre\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Infrastructure Engineer": {
            "canonical": "Infrastructure Engineer",
            "domain": "CLOUD_INFRASTRUCTURE",
            "allowed_patterns": [
                r"\binfrastructure\s+engineer\b",
                r"\bit\s+infrastructure\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # H. CYBERSECURITY
        # =====================================================================
        "Security Analyst": {
            "canonical": "Security Analyst",
            "domain": "CYBERSECURITY",
            "allowed_patterns": [
                r"\bsecurity\s+analyst\b",
                r"\binformation\s+security\s+analyst\b",
                r"\bcyber\s*security\s+analyst\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "SOC Analyst": {
            "canonical": "SOC Analyst",
            "domain": "CYBERSECURITY",
            "allowed_patterns": [
                r"\bsoc\s+analyst\b",
                r"\bsecurity\s+operations\s+center\s+analyst\b",
                r"\bsoc\s+tier\s+[123]\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Cybersecurity Analyst": {
            "canonical": "Cybersecurity Analyst",
            "domain": "CYBERSECURITY",
            "allowed_patterns": [
                r"\bcybersecurity\s+analyst\b",
                r"\bcyber\s+security\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Penetration Tester": {
            "canonical": "Penetration Tester",
            "domain": "CYBERSECURITY",
            "allowed_patterns": [
                r"\bpenetration\s+tester\b",
                r"\bpen\s+tester\b",
                r"\bethical\s+hacker\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Security Engineer": {
            "canonical": "Security Engineer",
            "domain": "CYBERSECURITY",
            "allowed_patterns": [
                r"\bsecurity\s+engineer\b",
                r"\bcyber\s*security\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Vulnerability Analyst": {
            "canonical": "Vulnerability Analyst",
            "domain": "CYBERSECURITY",
            "allowed_patterns": [
                r"\bvulnerability\s+analyst\b",
                r"\bvulnerability\s+assessment\s+analyst\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Incident Response Analyst": {
            "canonical": "Incident Response Analyst",
            "domain": "CYBERSECURITY",
            "allowed_patterns": [
                r"\bincident\s+response\s+analyst\b",
                r"\bincident\s+responder\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # I. OTHER TECHNOLOGY ROLES
        # =====================================================================
        "QA Engineer": {
            "canonical": "QA Engineer",
            "domain": "QA_TESTING",
            "allowed_patterns": [
                r"\bqa\s+engineer\b",
                r"\bquality\s+assurance\s+engineer\b",
                r"\bqa\s+analyst\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Software Tester": {
            "canonical": "Software Tester",
            "domain": "QA_TESTING",
            "allowed_patterns": [
                r"\bsoftware\s+tester\b",
                r"\bmanual\s+tester\b",
                r"\btest\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Automation Test Engineer": {
            "canonical": "Automation Test Engineer",
            "domain": "QA_TESTING",
            "allowed_patterns": [
                r"\bautomation\s+test(?:ing)?\s+engineer\b",
                r"\bsdet\b",
                r"\bqa\s+automation\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Database Administrator": {
            "canonical": "Database Administrator",
            "domain": "DATABASE_ADMIN",
            "allowed_patterns": [
                r"\bdatabase\s+administrator\b",
                r"\bdba\b",
                r"\bsql\s+database\s+administrator\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Network Engineer": {
            "canonical": "Network Engineer",
            "domain": "IT_SUPPORT_NETWORKING",
            "allowed_patterns": [
                r"\bnetwork\s+engineer\b",
                r"\bnetwork\s+administrator\b",
                r"\bcisco\s+network\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "IT Support Engineer": {
            "canonical": "IT Support Engineer",
            "domain": "IT_SUPPORT_NETWORKING",
            "allowed_patterns": [
                r"\bit\s+support\s+engineer\b",
                r"\bhelpdesk\s+technician\b",
                r"\bdesktop\s+support\s+engineer\b",
                r"\bit\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Mobile App Developer": {
            "canonical": "Mobile App Developer",
            "domain": "MOBILE_DEVELOPMENT",
            "allowed_patterns": [
                r"\bmobile\s+app\s+developer\b",
                r"\bandroid\s+developer\b",
                r"\bios\s+developer\b",
                r"\bflutter\s+developer\b",
                r"\breact\s+native\s+developer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Embedded Systems Engineer": {
            "canonical": "Embedded Systems Engineer",
            "domain": "EMBEDDED_SYSTEMS",
            "allowed_patterns": [
                r"\bembedded\s+systems\s+engineer\b",
                r"\bembedded\s+software\s+engineer\b",
                r"\bfirmware\s+engineer\b",
                r"\biot\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # J. ELECTRICAL & SKILLED TRADES
        # =====================================================================
        "Electrician": {
            "canonical": "Electrician",
            "domain": "SKILLED_TRADES_ELECTRICAL",
            "allowed_patterns": [
                r"\belectrician\b",
                r"\belectrical\s+maintenance\s+technician\b",
                r"\belectrical\s+technician\b",
                r"\bjourneyman\s+electrician\b",
                r"\bmaster\s+electrician\b",
                r"\bapprentice\s+electrician\b",
                r"\bcommercial\s+electrician\b",
                r"\bindustrial\s+electrician\b",
                r"\bresidential\s+electrician\b",
                r"\belectrical\s+helper\b",
                r"\bmaintenance\s+electrician\b",
                r"\bwireman\b",
                r"\blineman\b",
                r"\belectrical\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\bdata\s+analyst\b",
                r"\baccountant\b", r"\bnurse\b", r"\bprogrammer\b", r"\bweb\b",
                r"\bcloud\b", r"\bcyber\b"
            ]
        },
        "Electrical Technician": {
            "canonical": "Electrical Technician",
            "domain": "SKILLED_TRADES_ELECTRICAL",
            "allowed_patterns": [
                r"\belectrical\s+technician\b",
                r"\belectrical\s+service\s+technician\b",
                r"\belectrical\s+maintenance\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Electrical Maintenance Technician": {
            "canonical": "Electrical Maintenance Technician",
            "domain": "SKILLED_TRADES_ELECTRICAL",
            "allowed_patterns": [
                r"\belectrical\s+maintenance\s+technician\b",
                r"\bmaintenance\s+electrician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b"
            ]
        },
        "Industrial Electrician": {
            "canonical": "Industrial Electrician",
            "domain": "SKILLED_TRADES_ELECTRICAL",
            "allowed_patterns": [
                r"\bindustrial\s+electrician\b",
                r"\bplant\s+electrician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b"
            ]
        },
        "Plumber": {
            "canonical": "Plumber",
            "domain": "SKILLED_TRADES_PLUMBING",
            "allowed_patterns": [
                r"\bplumber\b",
                r"\bpipefitter\b",
                r"\bplumbing\s+technician\b",
                r"\bjourneyman\s+plumber\b",
                r"\bmaster\s+plumber\b",
                r"\bapprentice\s+plumber\b",
                r"\bmaintenance\s+plumber\b",
                r"\bsteamfitter\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Welder": {
            "canonical": "Welder",
            "domain": "SKILLED_TRADES_WELDING",
            "allowed_patterns": [
                r"\bwelder\b",
                r"\bmetal\s+fabricator\b",
                r"\bmig\s+welder\b",
                r"\btig\s+welder\b",
                r"\bpipe\s+welder\b",
                r"\bstructural\s+welder\b",
                r"\barc\s+welder\b",
                r"\bfabricator\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "HVAC Technician": {
            "canonical": "HVAC Technician",
            "domain": "SKILLED_TRADES_HVAC",
            "allowed_patterns": [
                r"\bhvac\s+technician\b",
                r"\brefrigeration\s+technician\b",
                r"\bhvac\s+service\s+technician\b",
                r"\bhvac\s+installer\b",
                r"\bhvac\s+mechanic\b",
                r"\bair\s+conditioning\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Mechanical Technician": {
            "canonical": "Mechanical Technician",
            "domain": "SKILLED_TRADES_MECHANIC",
            "allowed_patterns": [
                r"\bmechanical\s+technician\b",
                r"\bequipment\s+technician\b",
                r"\bmaintenance\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b"
            ]
        },
        "Automotive Mechanic": {
            "canonical": "Automotive Mechanic",
            "domain": "SKILLED_TRADES_MECHANIC",
            "allowed_patterns": [
                r"\bautomotive\s+mechanic\b",
                r"\bauto\s+mechanic\b",
                r"\bautomotive\s+technician\b",
                r"\bmechanic\b",
                r"\bdiesel\s+mechanic\b",
                r"\bvehicle\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Maintenance Technician": {
            "canonical": "Maintenance Technician",
            "domain": "SKILLED_TRADES_MECHANIC",
            "allowed_patterns": [
                r"\bmaintenance\s+technician\b",
                r"\bfacility\s+maintenance\s+technician\b",
                r"\bbuilding\s+maintenance\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },

        # =====================================================================
        # K. HEALTHCARE
        # =====================================================================
        "Registered Nurse": {
            "canonical": "Registered Nurse",
            "domain": "HEALTHCARE_NURSING",
            "allowed_patterns": [
                r"\bregistered\s+nurse\b",
                r"\brn\b",
                r"\bclinical\s+nurse\b",
                r"\bicu\s+nurse\b",
                r"\bcharge\s+nurse\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b", r"\belectrician\b"
            ]
        },
        "Staff Nurse": {
            "canonical": "Staff Nurse",
            "domain": "HEALTHCARE_NURSING",
            "allowed_patterns": [
                r"\bstaff\s+nurse\b",
                r"\bhospital\s+nurse\b",
                r"\bnurse\b",
                r"\bgeneral\s+nurse\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\baccountant\b", r"\belectrician\b"
            ]
        },
        "Nursing Assistant": {
            "canonical": "Nursing Assistant",
            "domain": "HEALTHCARE_SUPPORT",
            "allowed_patterns": [
                r"\bnursing\s+assistant\b",
                r"\bcertified\s+nursing\s+assistant\b",
                r"\bcna\b",
                r"\bpatient\s+care\s+assistant\b",
                r"\bpatient\s+care\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b"
            ]
        },
        "Caregiver": {
            "canonical": "Caregiver",
            "domain": "HEALTHCARE_SUPPORT",
            "allowed_patterns": [
                r"\bcaregiver\b",
                r"\bhome\s+health\s+aide\b",
                r"\bpersonal\s+care\s+aide\b",
                r"\belderly\s+caregiver\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b"
            ]
        },
        "Medical Laboratory Technician": {
            "canonical": "Medical Laboratory Technician",
            "domain": "HEALTHCARE_SUPPORT",
            "allowed_patterns": [
                r"\bmedical\s+lab(?:oratory)?\s+technician\b",
                r"\bmlt\b",
                r"\blab\s+technician\b",
                r"\bphlebotomist\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b"
            ]
        },
        "Radiology Technician": {
            "canonical": "Radiology Technician",
            "domain": "HEALTHCARE_SUPPORT",
            "allowed_patterns": [
                r"\bradiology\s+technician\b",
                r"\bradiologic\s+technologist\b",
                r"\bx[- ]ray\s+technician\b",
                r"\bmri\s+technician\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b"
            ]
        },
        "Clinical Assistant": {
            "canonical": "Clinical Assistant",
            "domain": "HEALTHCARE_SUPPORT",
            "allowed_patterns": [
                r"\bclinical\s+assistant\b",
                r"\bmedical\s+assistant\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b"
            ]
        },
        "Healthcare Administrator": {
            "canonical": "Healthcare Administrator",
            "domain": "HEALTHCARE_SUPPORT",
            "allowed_patterns": [
                r"\bhealthcare\s+administrator\b",
                r"\bhospital\s+administrator\b",
                r"\bclinical\s+coordinator\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\belectrician\b"
            ]
        },

        # =====================================================================
        # L. BUSINESS & FINANCE
        # =====================================================================
        "Accountant": {
            "canonical": "Accountant",
            "domain": "ACCOUNTING_FINANCE",
            "allowed_patterns": [
                r"\baccountant\b",
                r"\bjunior\s+accountant\b",
                r"\baccounts\s+assistant\b",
                r"\bstaff\s+accountant\b",
                r"\bgeneral\s+accountant\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b", r"\bnurse\b",
                r"\bdata\s+analyst\b", r"\bdata\s+scientist\b"
            ]
        },
        "Accounts Executive": {
            "canonical": "Accounts Executive",
            "domain": "ACCOUNTING_FINANCE",
            "allowed_patterns": [
                r"\baccounts\s+executive\b",
                r"\bfinance\s+executive\b",
                r"\baccounts\s+officer\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b", r"\bnurse\b"
            ]
        },
        "Bookkeeper": {
            "canonical": "Bookkeeper",
            "domain": "ACCOUNTING_FINANCE",
            "allowed_patterns": [
                r"\bbookkeeper\b",
                r"\bbookkeeping\s+specialist\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b", r"\bnurse\b"
            ]
        },
        "Financial Analyst": {
            "canonical": "Financial Analyst",
            "domain": "ACCOUNTING_FINANCE",
            "allowed_patterns": [
                r"\bfinancial\s+analyst\b",
                r"\bfinance\s+analyst\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b", r"\bnurse\b"
            ]
        },
        "Auditor": {
            "canonical": "Auditor",
            "domain": "ACCOUNTING_FINANCE",
            "allowed_patterns": [
                r"\bauditor\b",
                r"\binternal\s+auditor\b",
                r"\bstatutory\s+auditor\b",
                r"\bfinancial\s+auditor\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b", r"\bnurse\b"
            ]
        },
        "Tax Associate": {
            "canonical": "Tax Associate",
            "domain": "ACCOUNTING_FINANCE",
            "allowed_patterns": [
                r"\btax\s+associate\b",
                r"\btax\s+consultant\b",
                r"\bgst\s+practitioner\b",
                r"\btax\s+accountant\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b", r"\bnurse\b"
            ]
        },
        "Payroll Specialist": {
            "canonical": "Payroll Specialist",
            "domain": "ACCOUNTING_FINANCE",
            "allowed_patterns": [
                r"\bpayroll\s+specialist\b",
                r"\bpayroll\s+executive\b",
                r"\bpayroll\s+administrator\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b", r"\belectrician\b", r"\bnurse\b"
            ]
        },
        "HR Executive": {
            "canonical": "HR Executive",
            "domain": "HUMAN_RESOURCES",
            "allowed_patterns": [
                r"\bhr\s+executive\b",
                r"\bhuman\s+resources\s+executive\b",
                r"\bhr\s+generalist\b",
                r"\bhr\s+officer\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\belectrician\b"
            ]
        },
        "Recruiter": {
            "canonical": "Recruiter",
            "domain": "HUMAN_RESOURCES",
            "allowed_patterns": [
                r"\brecruiter\b",
                r"\btalent\s+acquisition\s+specialist\b",
                r"\btechnical\s+recruiter\b",
                r"\bhr\s+recruiter\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bnurse\b"
            ]
        },
        "Administrative Assistant": {
            "canonical": "Administrative Assistant",
            "domain": "ADMINISTRATION_OFFICE",
            "allowed_patterns": [
                r"\badministrative\s+assistant\b",
                r"\boffice\s+administrator\b",
                r"\bexecutive\s+assistant\b",
                r"\breceptionist\b",
                r"\boffice\s+assistant\b",
                r"\bdata\s+entry\s+specialist\b",
                r"\bclerk\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+engineer\b", r"\belectrician\b"
            ]
        },

        # =====================================================================
        # M. EDUCATION
        # =====================================================================
        "School Teacher": {
            "canonical": "School Teacher",
            "domain": "EDUCATION",
            "allowed_patterns": [
                r"\bschool\s+teacher\b",
                r"\bteacher\b",
                r"\bhigh\s+school\s+teacher\b",
                r"\bprimary\s+teacher\b",
                r"\belementary\s+teacher\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\belectrician\b", r"\baccountant\b"
            ]
        },
        "Subject Teacher": {
            "canonical": "Subject Teacher",
            "domain": "EDUCATION",
            "allowed_patterns": [
                r"\bsubject\s+teacher\b",
                r"\bmaths?\s+teacher\b",
                r"\bscience\s+teacher\b",
                r"\benglish\s+teacher\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\belectrician\b", r"\baccountant\b"
            ]
        },
        "Tutor": {
            "canonical": "Tutor",
            "domain": "EDUCATION",
            "allowed_patterns": [
                r"\btutor\b",
                r"\bprivate\s+tutor\b",
                r"\bonline\s+tutor\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\belectrician\b"
            ]
        },
        "Academic Instructor": {
            "canonical": "Academic Instructor",
            "domain": "EDUCATION",
            "allowed_patterns": [
                r"\bacademic\s+instructor\b",
                r"\binstructor\b",
                r"\blecturer\b",
                r"\bprofessor\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\belectrician\b"
            ]
        },
        "Trainer": {
            "canonical": "Trainer",
            "domain": "EDUCATION",
            "allowed_patterns": [
                r"\btrainer\b",
                r"\bcorporate\s+trainer\b",
                r"\bvocational\s+trainer\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b"
            ]
        },
        "Teaching Assistant": {
            "canonical": "Teaching Assistant",
            "domain": "EDUCATION",
            "allowed_patterns": [
                r"\bteaching\s+assistant\b",
                r"\bta\b",
                r"\bclassroom\s+assistant\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b"
            ]
        },

        # =====================================================================
        # N. OTHER SECTORS (Hospitality, Logistics, Construction, Engineering, Sales, Marketing)
        # =====================================================================
        "Chef": {
            "canonical": "Chef",
            "domain": "HOSPITALITY_CULINARY",
            "allowed_patterns": [
                r"\bchef\b", r"\bcook\b", r"\bline\s+cook\b", r"\bsous\s+chef\b",
                r"\bhead\s+chef\b", r"\bfood\s+service\s+worker\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\belectrician\b"
            ]
        },
        "Forklift Operator": {
            "canonical": "Forklift Operator",
            "domain": "LOGISTICS_WAREHOUSE",
            "allowed_patterns": [
                r"\bforklift\s+operator\b", r"\bforklift\s+driver\b",
                r"\bmaterial\s+handler\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\baccountant\b"
            ]
        },
        "Warehouse Associate": {
            "canonical": "Warehouse Associate",
            "domain": "LOGISTICS_WAREHOUSE",
            "allowed_patterns": [
                r"\bwarehouse\s+associate\b", r"\border\s+picker\b",
                r"\bwarehouse\s+worker\b", r"\bshipping\s+and\s+receiving\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\baccountant\b"
            ]
        },
        "Carpenter": {
            "canonical": "Carpenter",
            "domain": "CONSTRUCTION_CARPENTRY",
            "allowed_patterns": [
                r"\bcarpenter\b", r"\bframing\s+carpenter\b", r"\bfinish\s+carpenter\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\b", r"\bdeveloper\b"
            ]
        },
        "Sales Executive": {
            "canonical": "Sales Executive",
            "domain": "SALES_RETAIL",
            "allowed_patterns": [
                r"\bsales\s+executive\b", r"\bretail\s+associate\b",
                r"\bcustomer\s+service\s+representative\b", r"\bsales\s+representative\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\belectrician\b"
            ]
        },
        "Mechanical Engineer": {
            "canonical": "Mechanical Engineer",
            "domain": "MECHANICAL_ENGINEERING",
            "allowed_patterns": [
                r"\bmechanical\s+engineer\b", r"\bdesign\s+engineer\b",
                r"\bcad\s+engineer\b", r"\bproduction\s+engineer\b",
                r"\bmanufacturing\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Civil Engineer": {
            "canonical": "Civil Engineer",
            "domain": "CIVIL_ENGINEERING",
            "allowed_patterns": [
                r"\bcivil\s+engineer\b", r"\bsite\s+engineer\b",
                r"\bstructural\s+engineer\b", r"\bquantity\s+surveyor\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Electrical Engineer": {
            "canonical": "Electrical Engineer",
            "domain": "ELECTRICAL_ENGINEERING",
            "allowed_patterns": [
                r"\belectrical\s+engineer\b", r"\belectrical\s+design\s+engineer\b",
                r"\bpower\s+engineer\b", r"\bcontrol\s+systems\s+engineer\b"
            ],
            "excluded_patterns": [
                r"\bsoftware\s+developer\b", r"\baccountant\b", r"\bnurse\b"
            ]
        },
        "Digital Marketing Specialist": {
            "canonical": "Digital Marketing Specialist",
            "domain": "MARKETING",
            "allowed_patterns": [
                r"\bdigital\s+marketing\s+specialist\b",
                r"\bseo\s+specialist\b",
                r"\bcontent\s+marketer\b",
                r"\bmarketing\s+executive\b"
            ],
            "excluded_patterns": [
                r"\belectrician\b", r"\bnurse\b"
            ]
        }
    }

    # Cross-domain exclusion mapping to strictly prevent misaligned roles
    CROSS_DOMAIN_EXCLUSIONS = {
        "SKILLED_TRADES_ELECTRICAL": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "FRONTEND_DEVELOPMENT",
            "BACKEND_DEVELOPMENT", "AI_ML", "DATA_SCIENCE_ANALYTICS", "CLOUD_INFRASTRUCTURE",
            "CYBERSECURITY", "ACCOUNTING_FINANCE", "HEALTHCARE_NURSING", "HEALTHCARE_SUPPORT"
        ],
        "SKILLED_TRADES_PLUMBING": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "AI_ML", "DATA_SCIENCE_ANALYTICS",
            "ACCOUNTING_FINANCE", "HEALTHCARE_NURSING"
        ],
        "SKILLED_TRADES_WELDING": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "AI_ML", "DATA_SCIENCE_ANALYTICS",
            "ACCOUNTING_FINANCE", "HEALTHCARE_NURSING"
        ],
        "SKILLED_TRADES_MECHANIC": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "AI_ML", "DATA_SCIENCE_ANALYTICS",
            "ACCOUNTING_FINANCE", "HEALTHCARE_NURSING"
        ],
        "SKILLED_TRADES_HVAC": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "AI_ML", "DATA_SCIENCE_ANALYTICS",
            "ACCOUNTING_FINANCE", "HEALTHCARE_NURSING"
        ],
        "HEALTHCARE_NURSING": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "AI_ML", "DATA_SCIENCE_ANALYTICS",
            "SKILLED_TRADES_ELECTRICAL", "ACCOUNTING_FINANCE"
        ],
        "HEALTHCARE_SUPPORT": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "SKILLED_TRADES_ELECTRICAL",
            "ACCOUNTING_FINANCE"
        ],
        "EDUCATION": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "SKILLED_TRADES_ELECTRICAL",
            "ACCOUNTING_FINANCE"
        ],
        "ACCOUNTING_FINANCE": [
            "SOFTWARE_DEVELOPMENT", "FULL_STACK_DEVELOPMENT", "AI_ML", "DATA_SCIENCE_ANALYTICS",
            "SKILLED_TRADES_ELECTRICAL", "HEALTHCARE_NURSING"
        ],
        "SOFTWARE_DEVELOPMENT": [
            "SKILLED_TRADES_ELECTRICAL", "SKILLED_TRADES_PLUMBING", "ACCOUNTING_FINANCE",
            "HEALTHCARE_NURSING", "CIVIL_ENGINEERING"
        ],
        "FULL_STACK_DEVELOPMENT": [
            "SKILLED_TRADES_ELECTRICAL", "SKILLED_TRADES_PLUMBING", "ACCOUNTING_FINANCE",
            "HEALTHCARE_NURSING"
        ],
        "DATA_SCIENCE_ANALYTICS": [
            "SKILLED_TRADES_ELECTRICAL", "ACCOUNTING_FINANCE", "HEALTHCARE_NURSING",
            "CIVIL_ENGINEERING"
        ],
        "AI_ML": [
            "SKILLED_TRADES_ELECTRICAL", "ACCOUNTING_FINANCE", "HEALTHCARE_NURSING",
            "FRONTEND_DEVELOPMENT"
        ]
    }

    @classmethod
    def find_taxonomy_entry(cls, role_name: str):
        """Find matching taxonomy entry by canonical name or alias."""
        if not role_name:
            return None
        r_clean = role_name.strip().lower()

        # Exact match in dict keys
        for key, entry in cls.ROLE_TAXONOMY.items():
            if key.lower() == r_clean:
                return entry

        # Pattern match across allowed patterns (honoring excluded patterns)
        for key, entry in cls.ROLE_TAXONOMY.items():
            # Check excluded patterns first
            is_excluded = False
            for excl in entry.get("excluded_patterns", []):
                if re.search(excl, r_clean, re.IGNORECASE):
                    is_excluded = True
                    break
            if is_excluded:
                continue

            for pat in entry["allowed_patterns"]:
                if re.search(pat, r_clean, re.IGNORECASE):
                    return entry

        return None

    @classmethod
    def evaluate_role_match(cls, target_role: str, job_title: str) -> dict:
        """
        Evaluate if a job_title is a legitimate match for target_role across all professions.
        Returns:
          {
            "match": bool,
            "is_allowed": bool,
            "is_strictly_excluded": bool,
            "status": "DIRECT_MATCH" | "ALLOWED_EQUIVALENT" | "STRICT_EXCLUSION" | "UNMATCHED",
            "reason": str
          }
        """
        if not target_role or not job_title:
            return {
                "match": False,
                "is_allowed": False,
                "is_strictly_excluded": False,
                "status": "UNMATCHED",
                "reason": "Missing role or title"
            }

        title_lower = job_title.strip().lower()
        entry = cls.find_taxonomy_entry(target_role)

        if not entry:
            # Fallback for dynamic/unlisted roles: exact or clean word containment
            target_clean = target_role.lower().strip()
            if target_clean in title_lower:
                return {
                    "match": True,
                    "is_allowed": True,
                    "is_strictly_excluded": False,
                    "status": "DIRECT_MATCH",
                    "reason": f"Title contains '{target_role}'"
                }
            # Check if all major words match
            words = [w for w in target_clean.split() if len(w) > 2]
            if words and all(w in title_lower for w in words):
                return {
                    "match": True,
                    "is_allowed": True,
                    "is_strictly_excluded": False,
                    "status": "ALLOWED_EQUIVALENT",
                    "reason": f"Title matches words of '{target_role}'"
                }
            return {
                "match": False,
                "is_allowed": False,
                "is_strictly_excluded": False,
                "status": "UNMATCHED",
                "reason": f"Job does not match unlisted role '{target_role}'"
            }

        # 1. Hard Exclusion Check: If job title matches an excluded pattern, REJECT immediately!
        for exc in entry.get("excluded_patterns", []):
            if re.search(exc, title_lower, re.IGNORECASE):
                target_lower = target_role.lower()
                # Safety check: if target role itself contains the keyword, don't self-exclude
                if any(w in target_lower for w in re.findall(r'\b[a-z]{3,}\b', exc)):
                    continue
                return {
                    "match": False,
                    "is_allowed": False,
                    "is_strictly_excluded": True,
                    "status": "STRICT_EXCLUSION",
                    "reason": f"Title '{job_title}' strictly excluded for target role '{target_role}' by pattern '{exc}'"
                }

        # 2. Check Allowed Patterns
        for pat in entry.get("allowed_patterns", []):
            if re.search(pat, title_lower, re.IGNORECASE):
                is_direct = (entry["canonical"].lower() in title_lower)
                return {
                    "match": True,
                    "is_allowed": True,
                    "is_strictly_excluded": False,
                    "status": "DIRECT_MATCH" if is_direct else "ALLOWED_EQUIVALENT",
                    "reason": f"Title '{job_title}' aligns with '{target_role}' via pattern '{pat}'"
                }

        # 3. Soft title word overlap check (if target tokens are present in title)
        target_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", target_role.lower()))
        title_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", title_lower))
        if target_tokens and target_tokens.issubset(title_tokens):
            return {
                "match": True,
                "is_allowed": True,
                "is_strictly_excluded": False,
                "status": "ALLOWED_EQUIVALENT",
                "reason": f"Title '{job_title}' encompasses all keywords of target role '{target_role}'"
            }

        return {
            "match": False,
            "is_allowed": False,
            "is_strictly_excluded": False,
            "status": "UNMATCHED",
            "reason": f"Title '{job_title}' does not match requirements for '{target_role}'"
        }
