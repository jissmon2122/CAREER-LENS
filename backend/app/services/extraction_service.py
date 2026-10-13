import os
import re
import json

class ExtractionService:
    """Service for parsing raw resume text into structured resume fields and skill sets."""

    _skills_data = None

    @classmethod
    def get_skills_dictionary(cls):
        """Load skills dictionary from JSON configuration file."""
        if cls._skills_data is None:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'skills.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    cls._skills_data = json.load(f)
            else:
                cls._skills_data = {
                    "technical_skills": {
                        "programming_languages": ["Python", "Java", "JavaScript", "C", "C++", "SQL"],
                        "web_technologies": ["HTML", "CSS", "React", "Node.js"],
                        "databases": ["MySQL", "MongoDB", "PostgreSQL"],
                        "data_science_ml": ["Pandas", "NumPy", "Machine Learning"],
                        "data_analytics": ["Excel", "Power BI", "Tableau"],
                        "cloud_devops": ["AWS", "Docker", "Git"],
                        "tools": ["Git", "GitHub", "VS Code"]
                    },
                    "soft_skills": ["Communication", "Leadership", "Teamwork", "Problem Solving"],
                    "aliases": {"react.js": "React", "node.js": "Node.js"}
                }
        return cls._skills_data

    @staticmethod
    def extract_contact_info(text):
        """Extract email, phone number, LinkedIn URL, and GitHub URL from raw text."""
        contact_info = {
            "email": None,
            "email_present": False,
            "phone": None,
            "phone_present": False,
            "linkedin": None,
            "linkedin_present": False,
            "github": None,
            "github_present": False
        }

        if not text:
            return contact_info

        # 1. Email Regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info["email"] = email_match.group(0).lower()
            contact_info["email_present"] = True

        # 2. Phone Regex (Indian and International)
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}'
        phone_matches = re.findall(phone_pattern, text)
        for pm in phone_matches:
            digits = re.sub(r'\D', '', pm)
            if 10 <= len(digits) <= 13:
                contact_info["phone"] = pm.strip()
                contact_info["phone_present"] = True
                break

        # 3. LinkedIn Regex
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)/?'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
            contact_info["linkedin_present"] = True

        # 4. GitHub Regex
        github_pattern = r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/?'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact_info["github"] = f"https://github.com/{github_match.group(1)}"
            contact_info["github_present"] = True

        return contact_info

    @staticmethod
    def detect_sections(text):
        """Detect section headers present in resume text."""
        sections_detected = []
        if not text:
            return sections_detected

        section_patterns = {
            "contact": r'\b(contact|personal details|contact information|address)\b',
            "summary": r'\b(summary|objective|career objective|about me|profile summary)\b',
            "education": r'\b(education|academic background|qualification|academic credentials)\b',
            "skills": r'\b(skills|technical skills|key competencies|core competencies|technologies)\b',
            "projects": r'\b(projects|academic projects|key projects|personal projects)\b',
            "experience": r'\b(experience|work experience|professional experience|employment history)\b',
            "internships": r'\b(internship|internships|industrial training)\b',
            "certifications": r'\b(certifications|certificates|professional certifications|courses)\b',
            "achievements": r'\b(achievements|awards|accomplishments|honors)\b',
            "languages": r'\b(languages|languages known)\b'
        }

        for sec_name, pattern in section_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                sections_detected.append(sec_name)

        return sections_detected

    _compiled_skill_patterns = None
    _compiled_soft_patterns = None

    @classmethod
    def _ensure_compiled_patterns(cls):
        """Precompile regex patterns once to maximize regex matching speed across job datasets."""
        if cls._compiled_skill_patterns is not None:
            return
        skills_dict = cls.get_skills_dictionary()
        tech_categories = skills_dict.get("technical_skills", {})
        soft_skills_list = skills_dict.get("soft_skills", [])

        cls._compiled_skill_patterns = {}
        for category, skill_list in tech_categories.items():
            cls._compiled_skill_patterns[category] = [
                (skill, re.compile(r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])', re.IGNORECASE))
                for skill in skill_list
            ]

        cls._compiled_soft_patterns = [
            (soft, re.compile(r'\b' + re.escape(soft) + r'\b', re.IGNORECASE))
            for soft in soft_skills_list
        ]

    @classmethod
    def extract_skills(cls, text):
        """Extract technical skills (categorized) and soft skills using word boundaries & alias mappings."""
        cls._ensure_compiled_patterns()
        skills_dict = cls.get_skills_dictionary()
        aliases = skills_dict.get("aliases", {})

        extracted_tech_by_category = {}
        all_extracted_tech = set()
        extracted_soft = set()

        if not text:
            return {
                "categorized_technical_skills": {},
                "technical_skills": [],
                "soft_skills": []
            }

        # 1. Technical Skills Extraction using precompiled fast regexes
        for category, compiled_pairs in cls._compiled_skill_patterns.items():
            found_in_category = set()
            for skill, regex in compiled_pairs:
                if regex.search(text):
                    normalized_name = aliases.get(skill.lower(), skill)
                    found_in_category.add(normalized_name)
                    all_extracted_tech.add(normalized_name)

            if found_in_category:
                extracted_tech_by_category[category] = sorted(list(found_in_category))

        # 2. Soft Skills Extraction using precompiled fast regexes
        for soft_skill, regex in cls._compiled_soft_patterns:
            if regex.search(text):
                extracted_soft.add(soft_skill)

        return {
            "categorized_technical_skills": extracted_tech_by_category,
            "technical_skills": sorted(list(all_extracted_tech)),
            "soft_skills": sorted(list(extracted_soft))
        }

    @staticmethod
    def extract_education(text):
        """Extract degree, field of study, institution, and graduation year."""
        education_list = []
        if not text:
            return education_list

        degree_patterns = [
            r'\b(B\.?Tech|B\.?E\.?|Bachelor of Technology|Bachelor of Engineering)\b',
            r'\b(M\.?Tech|M\.?E\.?|Master of Technology|Master of Engineering)\b',
            r'\b(B\.?Sc|Bachelor of Science|BCA|Bachelor of Computer Applications|B\.?Pharm|B\.?Com|BBA|BA|LL\.?B)\b',
            r'\b(M\.?Sc|Master of Science|MCA|Master of Computer Applications|M\.?Pharm|M\.?Com|MBA|MA|LL\.?M)\b',
            r'\b(B\.?Ed|M\.?Ed|Bachelor of Education)\b',
            r'\b(MBBS|MD|MS|BDS|GNM|ANM)\b',
            r'\b(Ph\.?D|Doctorate)\b',
            r'\b(High School|HSC|SSLC|12th|10th)\b'
        ]

        fields = [
            "Computer Science", "Information Technology", "Artificial Intelligence",
            "Data Science", "Software Engineering", "Electronics", "Electrical Engineering",
            "Mechanical Engineering", "Civil Engineering", "Cyber Security", "Nursing",
            "Pharmacy", "Medicine", "Accounting", "Finance", "Business Administration",
            "Marketing", "Human Resources", "Law", "Education", "Architecture", "Design"
        ]

        # Extract 4-digit graduation years (e.g. 2020, 2024, 2026)
        years = re.findall(r'\b(20[0-2][0-9])\b', text)
        grad_year = years[-1] if years else None

        for pattern in degree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                degree_name = match.group(0)
                field_found = None
                for f in fields:
                    if re.search(r'\b' + re.escape(f) + r'\b', text, re.IGNORECASE):
                        field_found = f
                        break
                
                education_list.append({
                    "degree": degree_name,
                    "field": field_found or "General Studies",
                    "institution": "University / College",
                    "graduation_year": grad_year
                })
                break

        return education_list

    @staticmethod
    def extract_projects(text):
        """Extract projects from Projects section."""
        projects = []
        if not text:
            return projects

        # Find Projects section text block
        proj_match = re.search(r'(?:projects|academic projects|key projects)\b(.*?)(?=\b(?:experience|education|skills|certifications|achievements)\b|$)', text, re.IGNORECASE | re.DOTALL)
        proj_text = proj_match.group(1).strip() if proj_match else text

        # Split into bullet points or paragraphs
        lines = [line.strip('-•* ') for line in proj_text.splitlines() if len(line.strip()) > 10]
        
        # Take top 3 project strings or bullet points
        for i, line in enumerate(lines[:3]):
            projects.append({
                "title": line.split(':')[0] if ':' in line else f"Project {i+1}",
                "description": line,
                "technologies": []
            })

        return projects

    @staticmethod
    def extract_certifications(text):
        """Extract certifications from Certifications section."""
        certifications = []
        if not text:
            return certifications

        cert_keywords = [
            "AWS", "Azure", "Google Cloud", "Coursera", "Udemy", "NPTEL",
            "Oracle", "Microsoft", "Certified", "Certificate", "RN", "CPA",
            "Tally", "AutoCAD", "PMP", "Six Sigma", "BLS", "ACLS"
        ]

        # Look for certification section
        cert_match = re.search(r'(?:certifications|certificates|professional certifications)\b(.*?)(?=\b(?:projects|experience|education|skills|achievements)\b|$)', text, re.IGNORECASE | re.DOTALL)
        cert_text = cert_match.group(1).strip() if cert_match else text

        lines = [line.strip('-•* ') for line in cert_text.splitlines() if line.strip()]
        for line in lines:
            if any(ck.lower() in line.lower() for ck in cert_keywords):
                certifications.append(line)
            if len(certifications) >= 5:
                break

        return certifications

    @staticmethod
    def extract_experience(text):
        """Extract work experience and internships."""
        experiences = []
        internships = []

        if not text:
            return {"work_experience": experiences, "internships": internships}

        exp_match = re.search(r'(?:experience|work experience|professional experience|internship|internships)\b(.*?)(?=\b(?:projects|education|skills|certifications|achievements)\b|$)', text, re.IGNORECASE | re.DOTALL)
        exp_text = exp_match.group(1).strip() if exp_match else text

        has_internship = bool(re.search(r'\b(intern|internship|trainee)\b', exp_text, re.IGNORECASE))
        lines = [line.strip('-•* ') for line in exp_text.splitlines() if len(line.strip()) > 10]

        for line in lines[:2]:
            extracted_title = line.split(':')[0] if ':' in line else ("Trainee / Intern" if has_internship else "Professional Role")
            item = {
                "company": "Organization",
                "role": extracted_title,
                "duration": "3 - 6 Months",
                "description": line
            }
            if has_internship:
                internships.append(item)
            else:
                experiences.append(item)

        return {"work_experience": experiences, "internships": internships}
