"""
Skill Taxonomy and Domain Categorization Service.
Authoritative categorization mapping skills to industry domains.
Guarantees correct classification (e.g. Python -> Programming / AI & ML,
React -> Frontend Development, AWS -> Cloud Computing, Docker -> DevOps / Cloud,
Cybersecurity -> Security, etc.) and prevents unrelated cross-domain merging.
"""

class SkillTaxonomy:
    """Authoritative industry taxonomy for technical and domain skills."""

    TAXONOMY_MAP = {
        # Programming Languages
        "python": {"primary": "Programming", "sub": ["AI & ML", "Backend Development"]},
        "java": {"primary": "Programming", "sub": ["Backend Development", "Enterprise"]},
        "javascript": {"primary": "Programming", "sub": ["Frontend Development", "Web Development"]},
        "typescript": {"primary": "Programming", "sub": ["Frontend Development", "Web Development"]},
        "c": {"primary": "Programming", "sub": ["Embedded Systems", "Systems Programming"]},
        "c++": {"primary": "Programming", "sub": ["Game Development", "Systems Programming"]},
        "c#": {"primary": "Programming", "sub": [".NET", "Game Development"]},
        "go": {"primary": "Programming", "sub": ["Cloud Computing", "Backend Development"]},
        "rust": {"primary": "Programming", "sub": ["Systems Programming", "WebAssembly"]},
        "php": {"primary": "Programming", "sub": ["Web Development", "Backend Development"]},
        "kotlin": {"primary": "Programming", "sub": ["Mobile Development", "Android"]},
        "swift": {"primary": "Programming", "sub": ["Mobile Development", "iOS"]},
        "ruby": {"primary": "Programming", "sub": ["Web Development", "Ruby on Rails"]},
        "scala": {"primary": "Programming", "sub": ["Big Data", "Distributed Systems"]},
        "r": {"primary": "Programming", "sub": ["Data Science", "Statistics"]},
        "dart": {"primary": "Programming", "sub": ["Mobile Development", "Flutter"]},

        # AI & Machine Learning
        "machine learning": {"primary": "AI & ML", "sub": ["Data Science", "Predictive Modeling"]},
        "deep learning": {"primary": "AI & ML", "sub": ["Neural Networks", "Computer Vision"]},
        "nlp": {"primary": "AI & ML", "sub": ["Natural Language Processing", "LLMs"]},
        "computer vision": {"primary": "AI & ML", "sub": ["Image Processing", "OpenCV"]},
        "tensorflow": {"primary": "AI & ML", "sub": ["Deep Learning", "Frameworks"]},
        "pytorch": {"primary": "AI & ML", "sub": ["Deep Learning", "Neural Networks"]},
        "scikit-learn": {"primary": "AI & ML", "sub": ["Data Science", "Machine Learning"]},
        "keras": {"primary": "AI & ML", "sub": ["Deep Learning", "Neural Networks"]},
        "pandas": {"primary": "AI & ML", "sub": ["Data Science", "Data Analytics"]},
        "numpy": {"primary": "AI & ML", "sub": ["Data Science", "Scientific Computing"]},
        "data science": {"primary": "AI & ML", "sub": ["Analytics", "Modeling"]},
        "bert": {"primary": "AI & ML", "sub": ["NLP", "Transformers"]},
        "opencv": {"primary": "AI & ML", "sub": ["Computer Vision", "Image Processing"]},

        # Frontend Development
        "react": {"primary": "Frontend Development", "sub": ["Web Technologies", "UI Development"]},
        "react.js": {"primary": "Frontend Development", "sub": ["Web Technologies", "UI Development"]},
        "angular": {"primary": "Frontend Development", "sub": ["Web Technologies", "Enterprise"]},
        "vue": {"primary": "Frontend Development", "sub": ["Web Technologies", "UI Development"]},
        "vue.js": {"primary": "Frontend Development", "sub": ["Web Technologies", "UI Development"]},
        "next.js": {"primary": "Frontend Development", "sub": ["React Framework", "Full-Stack"]},
        "html": {"primary": "Frontend Development", "sub": ["Web Markup"]},
        "css": {"primary": "Frontend Development", "sub": ["Web Styling"]},
        "tailwind": {"primary": "Frontend Development", "sub": ["CSS Framework"]},
        "bootstrap": {"primary": "Frontend Development", "sub": ["CSS Framework"]},
        "redux": {"primary": "Frontend Development", "sub": ["State Management"]},
        "ui design": {"primary": "Frontend Development", "sub": ["UI/UX"]},
        "ux design": {"primary": "Frontend Development", "sub": ["UI/UX"]},
        "figma": {"primary": "Frontend Development", "sub": ["Design Tools", "Prototyping"]},

        # Backend Development
        "node.js": {"primary": "Backend Development", "sub": ["Web Technologies", "JavaScript Runtime"]},
        "express": {"primary": "Backend Development", "sub": ["Node Framework"]},
        "django": {"primary": "Backend Development", "sub": ["Python Framework"]},
        "flask": {"primary": "Backend Development", "sub": ["Python Microframework"]},
        "fastapi": {"primary": "Backend Development", "sub": ["Python APIs"]},
        "spring boot": {"primary": "Backend Development", "sub": ["Java Framework"]},
        "rest api": {"primary": "Backend Development", "sub": ["Web Services"]},
        "graphql": {"primary": "Backend Development", "sub": ["API Query Language"]},
        "microservices": {"primary": "Backend Development", "sub": ["Architecture"]},

        # Database & Data Analytics
        "sql": {"primary": "Database / Data Analytics", "sub": ["Relational Database", "Querying"]},
        "mysql": {"primary": "Database / Data Analytics", "sub": ["Relational Database"]},
        "postgresql": {"primary": "Database / Data Analytics", "sub": ["Relational Database"]},
        "mongodb": {"primary": "Database / Data Analytics", "sub": ["NoSQL", "Document Store"]},
        "redis": {"primary": "Database / Data Analytics", "sub": ["In-Memory Cache", "NoSQL"]},
        "oracle": {"primary": "Database / Data Analytics", "sub": ["Relational Database"]},
        "excel": {"primary": "Database / Data Analytics", "sub": ["Spreadsheets", "Reporting"]},
        "power bi": {"primary": "Database / Data Analytics", "sub": ["Business Intelligence", "Dashboards"]},
        "tableau": {"primary": "Database / Data Analytics", "sub": ["Business Intelligence", "Visualization"]},
        "data analysis": {"primary": "Database / Data Analytics", "sub": ["Business Analytics"]},
        "data analytics": {"primary": "Database / Data Analytics", "sub": ["Business Intelligence"]},
        "etl": {"primary": "Database / Data Analytics", "sub": ["Data Engineering"]},
        "data mining": {"primary": "Database / Data Analytics", "sub": ["Data Science"]},
        "data visualization": {"primary": "Database / Data Analytics", "sub": ["Reporting"]},
        "bigquery": {"primary": "Database / Data Analytics", "sub": ["Data Warehousing", "Cloud Data"]},
        "snowflake": {"primary": "Database / Data Analytics", "sub": ["Data Warehousing"]},

        # Cloud Computing
        "aws": {"primary": "Cloud Computing", "sub": ["Cloud Infrastructure", "DevOps"]},
        "azure": {"primary": "Cloud Computing", "sub": ["Cloud Infrastructure", "Microsoft"]},
        "google cloud": {"primary": "Cloud Computing", "sub": ["Cloud Infrastructure", "GCP"]},
        "gcp": {"primary": "Cloud Computing", "sub": ["Cloud Infrastructure", "Google Cloud"]},
        "cloud computing": {"primary": "Cloud Computing", "sub": ["Infrastructure", "Virtualization"]},

        # DevOps / Cloud
        "docker": {"primary": "DevOps / Cloud", "sub": ["Containerization", "Cloud"]},
        "kubernetes": {"primary": "DevOps / Cloud", "sub": ["Container Orchestration", "Cloud Native"]},
        "ci/cd": {"primary": "DevOps / Cloud", "sub": ["Automation", "Build Pipelines"]},
        "terraform": {"primary": "DevOps / Cloud", "sub": ["Infrastructure as Code"]},
        "ansible": {"primary": "DevOps / Cloud", "sub": ["Configuration Management"]},
        "jenkins": {"primary": "DevOps / Cloud", "sub": ["CI/CD Automation"]},
        "linux": {"primary": "DevOps / Cloud", "sub": ["Operating Systems", "SysAdmin"]},
        "bash": {"primary": "DevOps / Cloud", "sub": ["Shell Scripting"]},
        "shell scripting": {"primary": "DevOps / Cloud", "sub": ["Automation", "Linux"]},
        "git": {"primary": "DevOps / Cloud", "sub": ["Version Control"]},
        "github": {"primary": "DevOps / Cloud", "sub": ["Version Control", "Collaboration"]},

        # Cybersecurity & Information Security
        "cybersecurity": {"primary": "Security", "sub": ["Information Security", "Network Defense"]},
        "network security": {"primary": "Security", "sub": ["Firewalls", "Infrastructure"]},
        "ethical hacking": {"primary": "Security", "sub": ["Penetration Testing"]},
        "penetration testing": {"primary": "Security", "sub": ["Security Assessment"]},
        "cryptography": {"primary": "Security", "sub": ["Encryption", "Security Algorithms"]},
        "siem": {"primary": "Security", "sub": ["Security Monitoring", "Incident Response"]},
        "soc": {"primary": "Security", "sub": ["Incident Analysis"]},
        "information security": {"primary": "Security", "sub": ["Risk Management", "Compliance"]},
        "vulnerability assessment": {"primary": "Security", "sub": ["Penetration Testing"]},

        # Core Engineering & Manufacturing
        "compliance": {"primary": "Core Engineering / Operations", "sub": ["Regulatory", "Quality Assurance"]},
        "manufacturing": {"primary": "Core Engineering / Operations", "sub": ["Industrial", "Production"]},
        "engineering": {"primary": "Core Engineering / Operations", "sub": ["Technical"]},
        "autocad": {"primary": "Core Engineering / Operations", "sub": ["CAD Design", "Drafting"]},
        "cad": {"primary": "Core Engineering / Operations", "sub": ["Computer-Aided Design"]},
        "solidworks": {"primary": "Core Engineering / Operations", "sub": ["Mechanical CAD"]},
        "plc": {"primary": "Core Engineering / Operations", "sub": ["Industrial Automation"]},
        "scada": {"primary": "Core Engineering / Operations", "sub": ["Industrial Automation"]},
        "embedded systems": {"primary": "Core Engineering / Operations", "sub": ["Hardware", "Microcontrollers"]},

        # Business, Sales & Management
        "recruitment": {"primary": "Business & Talent", "sub": ["Human Resources", "Hiring"]},
        "talent acquisition": {"primary": "Business & Talent", "sub": ["Human Resources"]},
        "sourcing": {"primary": "Business & Talent", "sub": ["Recruitment"]},
        "onboarding": {"primary": "Business & Talent", "sub": ["HR Operations"]},
        "payroll": {"primary": "Business & Talent", "sub": ["Accounting", "Compensation"]},
        "gst": {"primary": "Finance & Accounting", "sub": ["Taxation", "Compliance"]},
        "tds": {"primary": "Finance & Accounting", "sub": ["Taxation", "Compliance"]},
        "tally": {"primary": "Finance & Accounting", "sub": ["Bookkeeping", "Accounting"]},
        "bookkeeping": {"primary": "Finance & Accounting", "sub": ["Financial Records"]},
        "taxation": {"primary": "Finance & Accounting", "sub": ["Finance", "Tax Compliance"]},
        "digital marketing": {"primary": "Marketing & Sales", "sub": ["Online Marketing", "Advertising"]},
        "seo": {"primary": "Marketing & Sales", "sub": ["Search Engine Optimization", "Web Traffic"]},
        "social media marketing": {"primary": "Marketing & Sales", "sub": ["Digital Media", "Branding"]},
        "crm": {"primary": "Marketing & Sales", "sub": ["Customer Relationship Management"]},
        "b2b sales": {"primary": "Marketing & Sales", "sub": ["Business Development"]},
        "lead generation": {"primary": "Marketing & Sales", "sub": ["Sales Pipeline"]},
        "product management": {"primary": "Management & Strategy", "sub": ["Product Lifecycle", "Strategy"]},
        "agile": {"primary": "Management & Strategy", "sub": ["Project Management", "Scrum"]},
        "scrum": {"primary": "Management & Strategy", "sub": ["Agile Methodology"]}
    }

    CATEGORIES = [
        "All Categories",
        "Programming",
        "AI & ML",
        "Frontend Development",
        "Backend Development",
        "Database / Data Analytics",
        "Cloud Computing",
        "DevOps / Cloud",
        "Security",
        "Core Engineering / Operations",
        "Finance & Accounting",
        "Marketing & Sales",
        "Business & Talent",
        "Management & Strategy"
    ]

    @classmethod
    def get_skill_classification(cls, skill_name: str) -> dict:
        """Classify a skill into its primary category and subcategories."""
        if not skill_name:
            return {"primary": "Other", "sub": []}
        
        # Check central SkillRegistry first
        try:
            from app.services.forecasting.skill_registry import SkillRegistry
            val = SkillRegistry.validate_skill(skill_name)
            if val["is_valid"]:
                return {"primary": val["category"], "sub": val["sub_categories"]}
        except ImportError:
            pass

        sk_clean = skill_name.lower().strip()
        
        if sk_clean in cls.TAXONOMY_MAP:
            return cls.TAXONOMY_MAP[sk_clean]

        # Fuzzy or partial domain inference
        if any(term in sk_clean for term in ["python", "java", "script", "lang", "c++", "golang"]):
            return {"primary": "Programming", "sub": []}
        if any(term in sk_clean for term in ["learning", "neural", "vision", "nlp", "ai", "model"]):
            return {"primary": "AI & ML", "sub": []}
        if any(term in sk_clean for term in ["react", "vue", "angular", "css", "html", "front"]):
            return {"primary": "Frontend Development", "sub": []}
        if any(term in sk_clean for term in ["node", "express", "django", "flask", "api", "backend"]):
            return {"primary": "Backend Development", "sub": []}
        if any(term in sk_clean for term in ["sql", "data", "mongo", "database", "analytics", "bi", "tableau"]):
            return {"primary": "Database / Data Analytics", "sub": []}
        if any(term in sk_clean for term in ["aws", "azure", "cloud", "gcp"]):
            return {"primary": "Cloud Computing", "sub": []}
        if any(term in sk_clean for term in ["docker", "k8s", "kubernetes", "devops", "ci/cd", "linux"]):
            return {"primary": "DevOps / Cloud", "sub": []}
        if any(term in sk_clean for term in ["security", "cyber", "hack", "penetration", "soc", "siem"]):
            return {"primary": "Security", "sub": []}
        if any(term in sk_clean for term in ["finance", "tax", "gst", "accounting", "ledger", "tally"]):
            return {"primary": "Finance & Accounting", "sub": []}
        if any(term in sk_clean for term in ["sale", "market", "seo", "branding", "crm"]):
            return {"primary": "Marketing & Sales", "sub": []}
        if any(term in sk_clean for term in ["recruit", "hire", "talent", "hr", "onboard"]):
            return {"primary": "Business & Talent", "sub": []}
        if any(term in sk_clean for term in ["cad", "mech", "manufactur", "engineer", "autocad"]):
            return {"primary": "Core Engineering / Operations", "sub": []}

        return {"primary": "General Technical", "sub": []}
