class ScoringService:
    """Service for calculating deterministic Resume Quality Scores and ATS Compatibility Scores."""

    @staticmethod
    def calculate_contact_score(contact_info):
        """Contact score out of 10."""
        score = 0
        if contact_info.get("email_present"):
            score += 4
        if contact_info.get("phone_present"):
            score += 4
        if contact_info.get("linkedin_present"):
            score += 2
        elif contact_info.get("github_present"):
            score += 2
        return min(score, 10)

    @staticmethod
    def calculate_education_score(education_list):
        """Education score out of 10."""
        if not education_list:
            return 0
        score = 0
        edu = education_list[0]
        if edu.get("degree"):
            score += 5
        if edu.get("institution"):
            score += 3
        if edu.get("graduation_year"):
            score += 2
        return min(score, 10)

    @staticmethod
    def calculate_skill_score(technical_skills):
        """Technical skills score out of 20."""
        count = len(set(technical_skills or []))
        if count == 0:
            return 0
        elif 1 <= count <= 2:
            return 5
        elif 3 <= count <= 5:
            return 10
        elif 6 <= count <= 8:
            return 15
        else:
            return 20

    @staticmethod
    def calculate_project_score(projects):
        """Project score out of 20."""
        count = len(projects or [])
        if count == 0:
            return 0
        elif count == 1:
            return 10
        elif count == 2:
            return 15
        else:
            return 20

    @staticmethod
    def calculate_certification_score(certifications):
        """Certification score out of 10."""
        count = len(certifications or [])
        if count == 0:
            return 0
        elif count == 1:
            return 5
        else:
            return 10

    @staticmethod
    def calculate_experience_score(work_exp, internships):
        """Experience score out of 15."""
        w_count = len(work_exp or [])
        i_count = len(internships or [])

        if w_count >= 2 or (w_count >= 1 and i_count >= 1):
            return 15
        elif w_count >= 1:
            return 12
        elif i_count >= 1:
            return 8
        else:
            return 0

    @staticmethod
    def calculate_structure_score(sections_detected):
        """Structure score out of 10."""
        secs = set(sections_detected or [])
        score = 0
        if "education" in secs:
            score += 2
        if "skills" in secs:
            score += 2
        if "projects" in secs:
            score += 2
        if "experience" in secs or "internships" in secs:
            score += 2
        if "certifications" in secs:
            score += 1
        if "contact" in secs:
            score += 1
        return min(score, 10)

    @staticmethod
    def calculate_keyword_score(technical_skills):
        """Keyword score out of 5."""
        count = len(set(technical_skills or []))
        if count >= 6:
            return 5
        elif count >= 3:
            return 3
        elif count >= 1:
            return 2
        return 0

    @classmethod
    def calculate_resume_score(cls, contact_info, education_list, technical_skills, projects, certifications, work_exp, internships, sections_detected):
        """Calculate total Resume Quality Score (0–100) and full component breakdown."""
        contact = cls.calculate_contact_score(contact_info)
        education = cls.calculate_education_score(education_list)
        skills = cls.calculate_skill_score(technical_skills)
        proj = cls.calculate_project_score(projects)
        certs = cls.calculate_certification_score(certifications)
        exp = cls.calculate_experience_score(work_exp, internships)
        structure = cls.calculate_structure_score(sections_detected)
        keywords = cls.calculate_keyword_score(technical_skills)

        total = contact + education + skills + proj + certs + exp + structure + keywords
        total = max(0, min(100, total))

        breakdown = {
            "contact": contact,
            "education": education,
            "technical_skills": skills,
            "projects": proj,
            "certifications": certs,
            "experience": exp,
            "structure": structure,
            "keywords": keywords,
            "total": total
        }

        return total, breakdown

    @staticmethod
    def calculate_ats_score(pdf_valid, text, sections_detected, technical_skills, contact_info):
        """Calculate ATS Compatibility Score (0–100) and breakdown."""
        text_extractability = 20 if pdf_valid and text else 0

        # Section Structure (max 20)
        sec_count = len(set(sections_detected or []))
        section_structure = min(20, sec_count * 4)

        # Keyword Presence (max 25)
        k_count = len(set(technical_skills or []))
        if k_count >= 5:
            keyword_presence = 25
        elif 3 <= k_count <= 4:
            keyword_presence = 15
        elif 1 <= k_count <= 2:
            keyword_presence = 10
        else:
            keyword_presence = 0

        # Contact Info (max 15)
        contact_information = 0
        if contact_info.get("email_present"):
            contact_information += 8
        if contact_info.get("phone_present"):
            contact_information += 7

        # Format Compatibility (max 10)
        format_compatibility = 10 if text_extractability == 20 else 0

        # Readability & Length (max 10)
        words = text.split() if text else []
        word_count = len(words)
        if 80 <= word_count <= 1500:
            readability = 10
        elif 40 <= word_count:
            readability = 6
        else:
            readability = 0

        ats_total = text_extractability + section_structure + keyword_presence + contact_information + format_compatibility + readability
        ats_total = max(0, min(100, ats_total))

        ats_breakdown = {
            "text_extractability": text_extractability,
            "section_structure": section_structure,
            "keyword_presence": keyword_presence,
            "contact_information": contact_information,
            "format_compatibility": format_compatibility,
            "readability": readability,
            "total": ats_total
        }

        return ats_total, ats_breakdown

    @staticmethod
    def generate_strengths_and_improvements(score_breakdown, contact_info, technical_skills, projects, certifications, work_exp, internships):
        """Generate rule-based strengths and actionable recommendations."""
        strengths = []
        improvements = []

        # Technical Skills
        tech_count = len(technical_skills or [])
        if tech_count >= 6:
            strengths.append("Strong technical skill coverage detected.")
        elif tech_count < 3:
            improvements.append("Add relevant technical skills and frameworks that you genuinely possess.")

        # Contact Info
        if contact_info.get("email_present") and contact_info.get("phone_present"):
            if contact_info.get("linkedin_present"):
                strengths.append("Complete professional contact information and online profile detected.")
            else:
                strengths.append("Primary contact details (Email & Phone) detected.")
        
        if not contact_info.get("linkedin_present"):
            improvements.append("Consider adding a LinkedIn profile link to enhance recruiter visibility.")

        software_keywords = {"python", "javascript", "java", "c++", "c#", "html", "css", "react", "node", "sql", "git", "coding", "software", "frontend", "backend"}
        is_software = any(any(sk in str(s).lower() for sk in software_keywords) for s in (technical_skills or []))
        if not contact_info.get("github_present") and is_software:
            improvements.append("Consider adding a GitHub profile link to showcase your code repositories.")

        # Projects
        proj_count = len(projects or [])
        if proj_count >= 2:
            strengths.append("Good project or practical work portfolio present.")
        elif proj_count == 0:
            improvements.append("Add 1–2 relevant projects or practical work examples demonstrating hands-on domain experience.")

        # Certifications
        cert_count = len(certifications or [])
        if cert_count >= 1:
            strengths.append("Professional certifications strengthen the resume profile.")
        else:
            improvements.append("Consider earning and adding relevant technical certifications.")

        # Experience
        if len(work_exp or []) > 0 or len(internships or []) > 0:
            strengths.append("Practical internship or work experience included.")

        return strengths, improvements
