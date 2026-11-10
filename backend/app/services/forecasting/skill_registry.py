"""
Skill Registry and Validation Engine.
Centralized, authoritative technical skill registry that strictly validates
user-submitted skills before executing any forecasting algorithm or accessing
historical vacancy data.

Rejects random strings, non-technical words, gibberish, and numeric combinations.
Enforces canonical skill resolution and returns structured suggestions for unrecognized terms.
"""

import re
import difflib
from typing import Dict, Any, List, Optional, Tuple

class SkillRegistry:
    """Authoritative technical skill registry with strict validation and alias resolution."""

    # Top default suggestions for completely unrelated/gibberish terms
    DEFAULT_SUGGESTIONS = ["Python", "Java", "JavaScript", "React", "AWS", "SQL"]

    # Canonical Technical Skills Registry (Normalized lowercase key -> metadata)
    REGISTRY: Dict[str, Dict[str, Any]] = {
        # Programming Languages
        "python": {"display_name": "Python", "category": "Programming", "sub": ["AI & ML", "Backend Development"]},
        "java": {"display_name": "Java", "category": "Programming", "sub": ["Backend Development", "Enterprise"]},
        "c": {"display_name": "C", "category": "Programming", "sub": ["Systems Programming", "Embedded Systems"]},
        "c++": {"display_name": "C++", "category": "Programming", "sub": ["Systems Programming", "Game Development"]},
        "c#": {"display_name": "C#", "category": "Programming", "sub": [".NET", "Game Development"]},
        "javascript": {"display_name": "JavaScript", "category": "Programming", "sub": ["Frontend Development", "Web Development"]},
        "typescript": {"display_name": "TypeScript", "category": "Programming", "sub": ["Frontend Development", "Web Development"]},
        "go": {"display_name": "Go", "category": "Programming", "sub": ["Cloud Computing", "Backend Development"]},
        "rust": {"display_name": "Rust", "category": "Programming", "sub": ["Systems Programming", "WebAssembly"]},
        "php": {"display_name": "PHP", "category": "Programming", "sub": ["Web Development", "Backend Development"]},
        "ruby": {"display_name": "Ruby", "category": "Programming", "sub": ["Web Development", "Ruby on Rails"]},
        "kotlin": {"display_name": "Kotlin", "category": "Programming", "sub": ["Mobile Development", "Android"]},
        "swift": {"display_name": "Swift", "category": "Programming", "sub": ["Mobile Development", "iOS"]},
        "scala": {"display_name": "Scala", "category": "Programming", "sub": ["Big Data", "Distributed Systems"]},
        "r": {"display_name": "R", "category": "Programming", "sub": ["Data Science", "Statistics"]},
        "dart": {"display_name": "Dart", "category": "Programming", "sub": ["Mobile Development", "Flutter"]},
        "shell scripting": {"display_name": "Shell Scripting", "category": "DevOps / Cloud", "sub": ["Linux", "Automation"]},
        "bash": {"display_name": "Bash", "category": "DevOps / Cloud", "sub": ["Linux", "Shell Scripting"]},
        "perl": {"display_name": "Perl", "category": "Programming", "sub": ["Scripting", "SysAdmin"]},
        "matlab": {"display_name": "MATLAB", "category": "Programming", "sub": ["Scientific Computing", "Simulation"]},
        "lua": {"display_name": "Lua", "category": "Programming", "sub": ["Game Scripting", "Embedded"]},
        "julia": {"display_name": "Julia", "category": "Programming", "sub": ["Data Science", "Scientific Computing"]},
        "haskell": {"display_name": "Haskell", "category": "Programming", "sub": ["Functional Programming"]},
        ".net": {"display_name": ".NET", "category": "Programming", "sub": ["Backend Development", "Microsoft"]},

        # AI & Machine Learning
        "machine learning": {"display_name": "Machine Learning", "category": "AI & ML", "sub": ["Predictive Modeling", "Data Science"]},
        "deep learning": {"display_name": "Deep Learning", "category": "AI & ML", "sub": ["Neural Networks", "Computer Vision"]},
        "nlp": {"display_name": "NLP", "category": "AI & ML", "sub": ["Natural Language Processing", "LLMs"]},
        "natural language processing": {"display_name": "Natural Language Processing", "category": "AI & ML", "sub": ["NLP", "Transformers"]},
        "computer vision": {"display_name": "Computer Vision", "category": "AI & ML", "sub": ["Image Processing", "OpenCV"]},
        "tensorflow": {"display_name": "TensorFlow", "category": "AI & ML", "sub": ["Deep Learning", "Frameworks"]},
        "pytorch": {"display_name": "PyTorch", "category": "AI & ML", "sub": ["Deep Learning", "Neural Networks"]},
        "scikit-learn": {"display_name": "Scikit-Learn", "category": "AI & ML", "sub": ["Data Science", "Machine Learning"]},
        "keras": {"display_name": "Keras", "category": "AI & ML", "sub": ["Deep Learning", "Neural Networks"]},
        "pandas": {"display_name": "Pandas", "category": "AI & ML", "sub": ["Data Science", "Data Analytics"]},
        "numpy": {"display_name": "NumPy", "category": "AI & ML", "sub": ["Data Science", "Scientific Computing"]},
        "data science": {"display_name": "Data Science", "category": "AI & ML", "sub": ["Analytics", "Modeling"]},
        "bert": {"display_name": "BERT", "category": "AI & ML", "sub": ["NLP", "Transformers"]},
        "opencv": {"display_name": "OpenCV", "category": "AI & ML", "sub": ["Computer Vision", "Image Processing"]},
        "large language models": {"display_name": "Large Language Models", "category": "AI & ML", "sub": ["LLMs", "Generative AI"]},
        "generative ai": {"display_name": "Generative AI", "category": "AI & ML", "sub": ["LLMs", "Deep Learning"]},
        "transformers": {"display_name": "Transformers", "category": "AI & ML", "sub": ["Hugging Face", "NLP"]},
        "hugging face": {"display_name": "Hugging Face", "category": "AI & ML", "sub": ["Transformers", "NLP"]},
        "xgboost": {"display_name": "XGBoost", "category": "AI & ML", "sub": ["Machine Learning", "Gradient Boosting"]},
        "mlops": {"display_name": "MLOps", "category": "AI & ML", "sub": ["Model Deployment", "DevOps"]},
        "langchain": {"display_name": "LangChain", "category": "AI & ML", "sub": ["LLMs", "AI Agents"]},

        # Database & Data Analytics
        "sql": {"display_name": "SQL", "category": "Database / Data Analytics", "sub": ["Relational Database", "Querying"]},
        "mysql": {"display_name": "MySQL", "category": "Database / Data Analytics", "sub": ["Relational Database"]},
        "postgresql": {"display_name": "PostgreSQL", "category": "Database / Data Analytics", "sub": ["Relational Database"]},
        "mongodb": {"display_name": "MongoDB", "category": "Database / Data Analytics", "sub": ["NoSQL", "Document Store"]},
        "sqlite": {"display_name": "SQLite", "category": "Database / Data Analytics", "sub": ["Embedded Database"]},
        "redis": {"display_name": "Redis", "category": "Database / Data Analytics", "sub": ["In-Memory Cache", "NoSQL"]},
        "oracle": {"display_name": "Oracle", "category": "Database / Data Analytics", "sub": ["Enterprise Database"]},
        "excel": {"display_name": "Excel", "category": "Database / Data Analytics", "sub": ["Spreadsheets", "Reporting"]},
        "power bi": {"display_name": "Power BI", "category": "Database / Data Analytics", "sub": ["Business Intelligence", "Dashboards"]},
        "tableau": {"display_name": "Tableau", "category": "Database / Data Analytics", "sub": ["Business Intelligence", "Visualization"]},
        "data analysis": {"display_name": "Data Analysis", "category": "Database / Data Analytics", "sub": ["Business Analytics"]},
        "data analytics": {"display_name": "Data Analytics", "category": "Database / Data Analytics", "sub": ["Business Intelligence"]},
        "etl": {"display_name": "ETL", "category": "Database / Data Analytics", "sub": ["Data Engineering", "Pipelines"]},
        "snowflake": {"display_name": "Snowflake", "category": "Database / Data Analytics", "sub": ["Data Warehousing", "Cloud Data"]},
        "bigquery": {"display_name": "BigQuery", "category": "Database / Data Analytics", "sub": ["Data Warehousing", "GCP"]},
        "apache spark": {"display_name": "Apache Spark", "category": "Database / Data Analytics", "sub": ["Big Data", "Distributed Computing"]},
        "hadoop": {"display_name": "Hadoop", "category": "Database / Data Analytics", "sub": ["Big Data", "MapReduce"]},
        "kafka": {"display_name": "Kafka", "category": "Database / Data Analytics", "sub": ["Event Streaming", "Messaging"]},
        "airflow": {"display_name": "Airflow", "category": "Database / Data Analytics", "sub": ["Orchestration", "Pipelines"]},
        "dbt": {"display_name": "dbt", "category": "Database / Data Analytics", "sub": ["Data Transformation", "ELT"]},
        "databricks": {"display_name": "Databricks", "category": "Database / Data Analytics", "sub": ["Lakehouse", "Spark"]},
        "elasticsearch": {"display_name": "Elasticsearch", "category": "Database / Data Analytics", "sub": ["Search Engine", "NoSQL"]},
        "cassandra": {"display_name": "Cassandra", "category": "Database / Data Analytics", "sub": ["Distributed NoSQL"]},

        # Cloud Computing
        "aws": {"display_name": "AWS", "category": "Cloud Computing", "sub": ["Cloud Infrastructure", "DevOps"]},
        "azure": {"display_name": "Azure", "category": "Cloud Computing", "sub": ["Cloud Infrastructure", "Microsoft"]},
        "google cloud": {"display_name": "Google Cloud", "category": "Cloud Computing", "sub": ["GCP", "Cloud Infrastructure"]},
        "cloud computing": {"display_name": "Cloud Computing", "category": "Cloud Computing", "sub": ["Infrastructure", "Virtualization"]},
        "serverless": {"display_name": "Serverless", "category": "Cloud Computing", "sub": ["Cloud Functions", "Lambda"]},
        "openstack": {"display_name": "OpenStack", "category": "Cloud Computing", "sub": ["Private Cloud", "Virtualization"]},

        # DevOps / Infrastructure
        "docker": {"display_name": "Docker", "category": "DevOps / Cloud", "sub": ["Containerization", "Cloud"]},
        "kubernetes": {"display_name": "Kubernetes", "category": "DevOps / Cloud", "sub": ["Container Orchestration", "Cloud Native"]},
        "jenkins": {"display_name": "Jenkins", "category": "DevOps / Cloud", "sub": ["CI/CD Automation", "Build Pipelines"]},
        "terraform": {"display_name": "Terraform", "category": "DevOps / Cloud", "sub": ["Infrastructure as Code", "Cloud Automation"]},
        "ci/cd": {"display_name": "CI/CD", "category": "DevOps / Cloud", "sub": ["Continuous Integration", "Deployment"]},
        "ansible": {"display_name": "Ansible", "category": "DevOps / Cloud", "sub": ["Configuration Management", "Automation"]},
        "linux": {"display_name": "Linux", "category": "DevOps / Cloud", "sub": ["Operating Systems", "SysAdmin"]},
        "git": {"display_name": "Git", "category": "DevOps / Cloud", "sub": ["Version Control"]},
        "github": {"display_name": "GitHub", "category": "DevOps / Cloud", "sub": ["Version Control", "DevOps"]},
        "gitlab": {"display_name": "GitLab", "category": "DevOps / Cloud", "sub": ["CI/CD", "Version Control"]},
        "prometheus": {"display_name": "Prometheus", "category": "DevOps / Cloud", "sub": ["Monitoring", "Observability"]},
        "grafana": {"display_name": "Grafana", "category": "DevOps / Cloud", "sub": ["Dashboards", "Monitoring"]},
        "helm": {"display_name": "Helm", "category": "DevOps / Cloud", "sub": ["Kubernetes Package Manager"]},
        "nginx": {"display_name": "Nginx", "category": "DevOps / Cloud", "sub": ["Web Server", "Reverse Proxy"]},

        # Web & Frontend Development
        "react": {"display_name": "React", "category": "Frontend Development", "sub": ["Web Technologies", "UI Development"]},
        "angular": {"display_name": "Angular", "category": "Frontend Development", "sub": ["Web Technologies", "Enterprise"]},
        "vue": {"display_name": "Vue", "category": "Frontend Development", "sub": ["Web Technologies", "UI Development"]},
        "next.js": {"display_name": "Next.js", "category": "Frontend Development", "sub": ["React Framework", "Full-Stack"]},
        "html": {"display_name": "HTML", "category": "Frontend Development", "sub": ["Web Markup"]},
        "css": {"display_name": "CSS", "category": "Frontend Development", "sub": ["Web Styling"]},
        "tailwind css": {"display_name": "Tailwind CSS", "category": "Frontend Development", "sub": ["CSS Framework", "UI"]},
        "bootstrap": {"display_name": "Bootstrap", "category": "Frontend Development", "sub": ["CSS Framework", "Responsive UI"]},
        "redux": {"display_name": "Redux", "category": "Frontend Development", "sub": ["State Management", "React"]},
        "svelte": {"display_name": "Svelte", "category": "Frontend Development", "sub": ["Reactive UI", "Web Framework"]},
        "ui design": {"display_name": "UI Design", "category": "Frontend Development", "sub": ["UI/UX", "User Interfaces"]},
        "ux design": {"display_name": "UX Design", "category": "Frontend Development", "sub": ["User Experience", "Research"]},
        "figma": {"display_name": "Figma", "category": "Frontend Development", "sub": ["Prototyping", "Design Tools"]},

        # Web & Backend Development
        "node.js": {"display_name": "Node.js", "category": "Backend Development", "sub": ["JavaScript Runtime", "Web Services"]},
        "express": {"display_name": "Express", "category": "Backend Development", "sub": ["Node Framework", "REST APIs"]},
        "django": {"display_name": "Django", "category": "Backend Development", "sub": ["Python Framework", "Web Services"]},
        "flask": {"display_name": "Flask", "category": "Backend Development", "sub": ["Python Microframework", "APIs"]},
        "fastapi": {"display_name": "FastAPI", "category": "Backend Development", "sub": ["Python APIs", "Async"]},
        "spring boot": {"display_name": "Spring Boot", "category": "Backend Development", "sub": ["Java Framework", "Enterprise"]},
        "rest api": {"display_name": "REST API", "category": "Backend Development", "sub": ["Web Services", "HTTP"]},
        "graphql": {"display_name": "GraphQL", "category": "Backend Development", "sub": ["API Query Language"]},
        "microservices": {"display_name": "Microservices", "category": "Backend Development", "sub": ["Architecture", "Distributed Systems"]},
        "asp.net": {"display_name": "ASP.NET", "category": "Backend Development", "sub": [".NET", "Microsoft"]},

        # Security & Cybersecurity
        "cybersecurity": {"display_name": "Cybersecurity", "category": "Security", "sub": ["Information Security", "Network Defense"]},
        "network security": {"display_name": "Network Security", "category": "Security", "sub": ["Firewalls", "Infrastructure"]},
        "ethical hacking": {"display_name": "Ethical Hacking", "category": "Security", "sub": ["Penetration Testing", "Security Assessment"]},
        "penetration testing": {"display_name": "Penetration Testing", "category": "Security", "sub": ["Security Assessment", "Vulnerabilities"]},
        "cryptography": {"display_name": "Cryptography", "category": "Security", "sub": ["Encryption", "Security Algorithms"]},
        "siem": {"display_name": "SIEM", "category": "Security", "sub": ["Security Information", "Event Management"]},
        "soc": {"display_name": "SOC", "category": "Security", "sub": ["Security Operations", "Incident Response"]},
        "information security": {"display_name": "Information Security", "category": "Security", "sub": ["Risk Management", "Compliance"]},
        "vulnerability assessment": {"display_name": "Vulnerability Assessment", "category": "Security", "sub": ["Risk Analysis", "Auditing"]},
        "firewalls": {"display_name": "Firewalls", "category": "Security", "sub": ["Network Defense"]},
        "owasp": {"display_name": "OWASP", "category": "Security", "sub": ["Application Security"]},

        # Core Engineering & Manufacturing
        "autocad": {"display_name": "AutoCAD", "category": "Core Engineering / Operations", "sub": ["CAD Design", "Drafting"]},
        "solidworks": {"display_name": "SolidWorks", "category": "Core Engineering / Operations", "sub": ["Mechanical CAD", "3D Modeling"]},
        "cad": {"display_name": "CAD", "category": "Core Engineering / Operations", "sub": ["Computer-Aided Design"]},
        "plc": {"display_name": "PLC", "category": "Core Engineering / Operations", "sub": ["Industrial Automation", "Control Systems"]},
        "scada": {"display_name": "SCADA", "category": "Core Engineering / Operations", "sub": ["Industrial Automation", "Monitoring"]},
        "embedded systems": {"display_name": "Embedded Systems", "category": "Core Engineering / Operations", "sub": ["Microcontrollers", "Hardware"]},
        "manufacturing": {"display_name": "Manufacturing", "category": "Core Engineering / Operations", "sub": ["Production", "Industrial Operations"]},
        "compliance": {"display_name": "Compliance", "category": "Core Engineering / Operations", "sub": ["Quality Assurance", "Regulatory"]},
        "engineering": {"display_name": "Engineering", "category": "Core Engineering / Operations", "sub": ["Technical Operations"]},

        # Business, Management, Finance
        "agile": {"display_name": "Agile", "category": "Management & Strategy", "sub": ["Project Management", "Scrum"]},
        "scrum": {"display_name": "Scrum", "category": "Management & Strategy", "sub": ["Agile Methodology", "Sprints"]},
        "product management": {"display_name": "Product Management", "category": "Management & Strategy", "sub": ["Product Lifecycle", "Strategy"]},
        "seo": {"display_name": "SEO", "category": "Marketing & Sales", "sub": ["Search Engine Optimization", "Web Traffic"]},
        "digital marketing": {"display_name": "Digital Marketing", "category": "Marketing & Sales", "sub": ["Online Marketing", "Branding"]},
        "crm": {"display_name": "CRM", "category": "Marketing & Sales", "sub": ["Customer Relationship Management", "Salesforce"]},
        "recruitment": {"display_name": "Recruitment", "category": "Business & Talent", "sub": ["Human Resources", "Hiring"]},
        "talent acquisition": {"display_name": "Talent Acquisition", "category": "Business & Talent", "sub": ["Human Resources"]},
        "sourcing": {"display_name": "Sourcing", "category": "Business & Talent", "sub": ["Talent Search"]},
        "onboarding": {"display_name": "Onboarding", "category": "Business & Talent", "sub": ["HR Operations"]},
        "payroll": {"display_name": "Payroll", "category": "Business & Talent", "sub": ["Compensation", "Accounting"]},
        "gst": {"display_name": "GST", "category": "Finance & Accounting", "sub": ["Taxation", "Compliance"]},
        "tds": {"display_name": "TDS", "category": "Finance & Accounting", "sub": ["Taxation", "Compliance"]},
        "tally": {"display_name": "Tally", "category": "Finance & Accounting", "sub": ["Bookkeeping", "Accounting"]},
        "bookkeeping": {"display_name": "Bookkeeping", "category": "Finance & Accounting", "sub": ["Financial Records"]},
        "taxation": {"display_name": "Taxation", "category": "Finance & Accounting", "sub": ["Tax Compliance", "Finance"]}
    }

    # Legitimate Aliases, Abbreviations, and Common Misspellings
    # Map normalized lowercase variant -> canonical key in REGISTRY
    ALIASES: Dict[str, str] = {
        # Programming Aliases
        "py": "python",
        "python3": "python",
        "py3": "python",
        "golang": "go",
        "js": "javascript",
        "ts": "typescript",
        "cpp": "c++",
        "cplusplus": "c++",
        "c plus plus": "c++",
        "csharp": "c#",
        "c sharp": "c#",
        "cs": "c#",
        "dotnet": ".net",
        "dot net": ".net",
        ".net core": ".net",
        "asp.net": "asp.net",
        "aspnet": "asp.net",
        "rails": "ruby",
        "ruby on rails": "ruby",
        "flutter": "dart",
        "sh": "bash",
        "shell": "shell scripting",

        # AI & ML Aliases
        "ml": "machine learning",
        "dl": "deep learning",
        "nlp": "nlp",
        "tf": "tensorflow",
        "sklearn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "llm": "large language models",
        "llms": "large language models",
        "genai": "generative ai",
        "gen ai": "generative ai",
        "cv": "computer vision",
        "huggingface": "hugging face",
        "transformers": "transformers",

        # Database & Data Aliases
        "postgres": "postgresql",
        "psql": "postgresql",
        "mongo": "mongodb",
        "powerbi": "power bi",
        "power-bi": "power bi",
        "ms excel": "excel",
        "microsoft excel": "excel",
        "elastic search": "elasticsearch",
        "spark": "apache spark",
        "pyspark": "apache spark",
        "apache kafka": "kafka",
        "apache airflow": "airflow",
        "bi": "data analytics",

        # Cloud Aliases
        "amazon web services": "aws",
        "microsoft azure": "azure",
        "gcp": "google cloud",
        "google cloud platform": "google cloud",

        # DevOps Aliases
        "k8s": "kubernetes",
        "k8": "kubernetes",
        "cicd": "ci/cd",
        "ci-cd": "ci/cd",
        "ci cd": "ci/cd",

        # Web Development Aliases
        "reactjs": "react",
        "react.js": "react",
        "react js": "react",
        "angularjs": "angular",
        "angular.js": "angular",
        "vuejs": "vue",
        "vue.js": "vue",
        "vue js": "vue",
        "nodejs": "node.js",
        "node.js": "node.js",
        "node js": "node.js",
        "node": "node.js",
        "nextjs": "next.js",
        "next.js": "next.js",
        "next js": "next.js",
        "expressjs": "express",
        "express.js": "express",
        "tailwind": "tailwind css",
        "tailwindcss": "tailwind css",
        "spring": "spring boot",
        "html5": "html",
        "css3": "css",
        "restful api": "rest api",
        "rest": "rest api",

        # Security Aliases
        "cyber security": "cybersecurity",
        "infosec": "information security",
        "pentest": "penetration testing",
        "pen testing": "penetration testing",
        "security+": "information security"
    }

    @classmethod
    def normalize_input(cls, skill_input: str) -> str:
        """
        Normalize case and strip harmless whitespace.
        Preserves essential punctuation for technical terms like 'c++', 'c#', '.net', 'node.js'.
        """
        if not skill_input or not isinstance(skill_input, str):
            return ""
        norm = skill_input.strip().lower()
        # Collapse multiple spaces
        norm = re.sub(r'\s+', ' ', norm)
        return norm

    @classmethod
    def is_nonsense_pattern(cls, text: str) -> bool:
        """
        Detects obvious non-technical patterns:
        - Pure numbers (e.g. '123', '9999')
        - Arbitrary word+number combinations (e.g. 'hello123', 'banana123', 'football123')
        - Repetitive strings without meaning
        """
        # Pure digits
        if text.isdigit():
            return True
        # Ends with digits where prefix is not a recognized tech name (e.g. python3, html5 are valid, but banana123, hello123 are not)
        m = re.match(r'^([a-zA-Z]+)(\d+)$', text)
        if m:
            prefix, digits = m.groups()
            if text not in cls.REGISTRY and text not in cls.ALIASES:
                return True
        # Strings with 4+ consecutive identical characters (e.g. 'aaaaa', 'testttttt')
        if re.search(r'(.)\1{3,}', text):
            return True
        return False

    @classmethod
    def get_close_suggestions(cls, query: str, limit: int = 3) -> List[str]:
        """
        Compute close spelling suggestions from trusted canonical names.
        If no close matches are found, returns standard default suggestions.
        """
        if cls.is_nonsense_pattern(query) or len(query) < 3:
            return cls.DEFAULT_SUGGESTIONS[:limit]

        all_candidates = list(cls.REGISTRY.keys()) + list(cls.ALIASES.keys())
        # Filter candidates to roughly similar length (+/- 2 characters) to avoid false matches on short acronyms
        filtered = [c for c in all_candidates if abs(len(c) - len(query)) <= 3 and len(c) >= 3]
        matches = difflib.get_close_matches(query, filtered, n=limit, cutoff=0.72)

        results = []
        for m in matches:
            canonical_key = cls.ALIASES.get(m, m)
            if canonical_key in cls.REGISTRY:
                disp = cls.REGISTRY[canonical_key]["display_name"]
                if disp not in results:
                    results.append(disp)

        if not results:
            return cls.DEFAULT_SUGGESTIONS[:limit]

        return results[:limit]

    @classmethod
    def validate_skill(cls, raw_skill: str) -> Dict[str, Any]:
        """
        Strict validation against trusted technical skill registry.

        Returns:
            {
                "is_valid": bool,
                "canonical_key": str or None,
                "display_name": str or None,
                "category": str or None,
                "sub_categories": list,
                "error": str or None,
                "message": str or None,
                "suggestions": list
            }
        """
        if not raw_skill or not isinstance(raw_skill, str) or not raw_skill.strip():
            return {
                "is_valid": False,
                "canonical_key": None,
                "display_name": None,
                "category": None,
                "sub_categories": [],
                "error": "INVALID_SKILL",
                "message": "Skill name cannot be empty.",
                "suggestions": cls.DEFAULT_SUGGESTIONS[:3]
            }

        norm = cls.normalize_input(raw_skill)

        # Check for obvious nonsense patterns
        if cls.is_nonsense_pattern(norm) and norm not in cls.REGISTRY and norm not in cls.ALIASES:
            return {
                "is_valid": False,
                "canonical_key": None,
                "display_name": None,
                "category": None,
                "sub_categories": [],
                "error": "INVALID_SKILL",
                "message": f"The entered term '{raw_skill.strip()}' is not a recognized technical skill.",
                "suggestions": cls.get_close_suggestions(norm)
            }

        # 1. Exact match in REGISTRY
        if norm in cls.REGISTRY:
            info = cls.REGISTRY[norm]
            return {
                "is_valid": True,
                "canonical_key": norm,
                "display_name": info["display_name"],
                "category": info["category"],
                "sub_categories": info.get("sub", []),
                "error": None,
                "message": None,
                "suggestions": []
            }

        # 2. Exact match in ALIASES
        if norm in cls.ALIASES:
            canonical_key = cls.ALIASES[norm]
            if canonical_key in cls.REGISTRY:
                info = cls.REGISTRY[canonical_key]
                return {
                    "is_valid": True,
                    "canonical_key": canonical_key,
                    "display_name": info["display_name"],
                    "category": info["category"],
                    "sub_categories": info.get("sub", []),
                    "error": None,
                    "message": None,
                    "suggestions": []
                }

        # 3. Clean special punctuation for lookup (e.g. 'c plus plus' or 'dot net')
        condensed = re.sub(r'[\-_]', ' ', norm).strip()
        if condensed in cls.REGISTRY:
            info = cls.REGISTRY[condensed]
            return {
                "is_valid": True,
                "canonical_key": condensed,
                "display_name": info["display_name"],
                "category": info["category"],
                "sub_categories": info.get("sub", []),
                "error": None,
                "message": None,
                "suggestions": []
            }
        if condensed in cls.ALIASES:
            canonical_key = cls.ALIASES[condensed]
            if canonical_key in cls.REGISTRY:
                info = cls.REGISTRY[canonical_key]
                return {
                    "is_valid": True,
                    "canonical_key": canonical_key,
                    "display_name": info["display_name"],
                    "category": info["category"],
                    "sub_categories": info.get("sub", []),
                    "error": None,
                    "message": None,
                    "suggestions": []
                }

        # If not in REGISTRY and not in ALIASES, it is STRICTLY INVALID.
        suggestions = cls.get_close_suggestions(norm)
        return {
            "is_valid": False,
            "canonical_key": None,
            "display_name": None,
            "category": None,
            "sub_categories": [],
            "error": "INVALID_SKILL",
            "message": f"The entered term '{raw_skill.strip()}' is not a recognized technical skill.",
            "suggestions": suggestions
        }
