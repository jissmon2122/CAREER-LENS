class LearningRoadmapEngine:
    """
    Personalized Learning Roadmap & Certification Recommendation Engine.
    Generates step-by-step learning modules, curated resources, targeted industry certifications,
    and match improvement simulations for candidate skill gaps.
    """

    # Knowledge Base of Learning Resources & Certifications per Skill Domain
    RESOURCE_MAP = {
        "python": {
            "courses": [
                {"title": "Python for Everybody (FreeCodeCamp)", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "type": "Free Course"},
                {"title": "Complete Python Bootcamp (Udemy)", "url": "https://www.udemy.com/course/complete-python-bootcamp/", "type": "Paid Certification"}
            ],
            "certifications": [
                {"title": "PCEP – Certified Entry-Level Python Programmer", "issuer": "Python Institute", "url": "https://pythoninstitute.org/pcep"}
            ],
            "project_idea": "Build an Automated Job Market Scraper & Data Pipeline in Python."
        },
        "sql": {
            "courses": [
                {"title": "SQL for Data Analysis (Udacity)", "url": "https://www.udacity.com/course/sql-for-data-analysis--ud198", "type": "Free Course"},
                {"title": "Complete SQL Mastery (CodeWithMosh)", "url": "https://codewithmosh.com/p/sql-mastery", "type": "Course"}
            ],
            "certifications": [
                {"title": "Oracle Database SQL Certified Associate", "issuer": "Oracle", "url": "https://education.oracle.com"}
            ],
            "project_idea": "Design an E-Commerce Relational Database & Complex Analytical Queries."
        },
        "react": {
            "courses": [
                {"title": "React Full Course 2026 (FreeCodeCamp)", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/", "type": "Free Course"},
                {"title": "The Ultimate React Course (Udemy)", "url": "https://www.udemy.com/course/the-ultimate-react-course/", "type": "Course"}
            ],
            "certifications": [
                {"title": "Meta Front-End Developer Professional Certificate", "issuer": "Meta / Coursera", "url": "https://www.coursera.org/professional-certificates/meta-front-end-developer"}
            ],
            "project_idea": "Develop a Modern Responsive Dashboard with React, Hooks, and REST APIs."
        },
        "power bi": {
            "courses": [
                {"title": "Power BI Full Course (YouTube / Microsoft Learn)", "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi", "type": "Free Tutorial"},
                {"title": "Microsoft Power BI Desktop for Business Intelligence", "url": "https://www.udemy.com/course/powerbi-desktop/", "type": "Course"}
            ],
            "certifications": [
                {"title": "Microsoft Certified: Power BI Data Analyst Associate (PL-300)", "issuer": "Microsoft", "url": "https://learn.microsoft.com/en-us/credentials/certifications/data-analyst-associate/"}
            ],
            "project_idea": "Create an Interactive Executive Sales Analytics Dashboard with DAX measures."
        },
        "aws": {
            "courses": [
                {"title": "AWS Cloud Practitioner Training (AWS)", "url": "https://aws.amazon.com/training/digital/", "type": "Free Training"},
                {"title": "Ultimate AWS Certified Solutions Architect", "url": "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/", "type": "Course"}
            ],
            "certifications": [
                {"title": "AWS Certified Cloud Practitioner", "issuer": "Amazon Web Services", "url": "https://aws.amazon.com/certification/certified-cloud-practitioner/"}
            ],
            "project_idea": "Deploy a Cloud-Native Serverless Web App using AWS Lambda, S3, and DynamoDB."
        },
        "node.js": {
            "courses": [
                {"title": "Node.js Tutorial for Beginners (FreeCodeCamp)", "url": "https://www.freecodecamp.org/news/free-nodejs-course-for-beginners/", "type": "Free Course"}
            ],
            "certifications": [
                {"title": "OpenJS Node.js Application Developer (JSNAD)", "issuer": "Linux Foundation", "url": "https://training.linuxfoundation.org/certification/jsnad/"}
            ],
            "project_idea": "Build a Scalable RESTful API with Node.js, Express, and JWT Authentication."
        }
    }

    @classmethod
    def generate_roadmap(cls, skill_gap_res, job, current_match_score=75):
        """
        Generate personalized 3-phase learning roadmap, certifications, and match score improvement simulation.
        """
        prioritized_gaps = skill_gap_res.get("prioritized_gaps", [])
        missing_required = skill_gap_res.get("missing_required_skills", [])
        missing_preferred = skill_gap_res.get("missing_preferred_skills", [])

        # 1. Build Phases
        phase1_skills = [item for item in prioritized_gaps if item["priority"] in ("CRITICAL", "HIGH")]
        phase2_skills = [item for item in prioritized_gaps if item["priority"] == "MEDIUM"]
        phase3_skills = [item for item in prioritized_gaps if item["priority"] == "LOW"]

        roadmap_phases = []

        # Phase 1: Core Fundamentals
        if phase1_skills:
            items_p1 = []
            for item in phase1_skills:
                sk_name = item["skill"]
                sk_clean = sk_name.lower().strip()
                res_data = cls.RESOURCE_MAP.get(sk_clean, {
                    "courses": [{"title": f"Mastering {sk_name} (Official Docs & Tutorials)", "url": f"https://www.google.com/search?q={sk_name}+tutorial", "type": "Guide"}],
                    "certifications": [{"title": f"{sk_name} Certified Specialist", "issuer": "Industry Body", "url": "#"}],
                    "project_idea": f"Build a practical project implementing {sk_name} features."
                })
                items_p1.append({
                    "skill": sk_name,
                    "priority": item["priority"],
                    "estimated_hours": "15-20 Hours",
                    "difficulty": "Intermediate",
                    "courses": res_data["courses"],
                    "project_idea": res_data["project_idea"]
                })

            roadmap_phases.append({
                "phase": 1,
                "title": "Phase 1: Essential Core Requirements",
                "estimated_duration": "2 - 3 Weeks",
                "focus": "Master high-priority required skills for the target role.",
                "skills": items_p1
            })

        # Phase 2: Applied Projects & Preferred Skills
        if phase2_skills or not phase1_skills:
            items_p2 = []
            target_skills = phase2_skills if phase2_skills else prioritized_gaps
            for item in target_skills:
                sk_name = item["skill"]
                sk_clean = sk_name.lower().strip()
                res_data = cls.RESOURCE_MAP.get(sk_clean, {
                    "courses": [{"title": f"Applied {sk_name} Masterclass", "url": f"https://www.google.com/search?q={sk_name}+course", "type": "Course"}],
                    "project_idea": f"Integrate {sk_name} into a multi-tier application."
                })
                items_p2.append({
                    "skill": sk_name,
                    "priority": item["priority"],
                    "estimated_hours": "10-15 Hours",
                    "difficulty": "Intermediate",
                    "courses": res_data["courses"],
                    "project_idea": res_data["project_idea"]
                })

            roadmap_phases.append({
                "phase": 2,
                "title": "Phase 2: Preferred Skills & Portfolio Projects",
                "estimated_duration": "2 Weeks",
                "focus": "Build hands-on portfolio projects showcasing missing preferred skills.",
                "skills": items_p2
            })

        # 2. Extract Certification Recommendations
        certifications = []
        all_missing = missing_required + missing_preferred
        for sk in all_missing:
            sk_clean = sk.lower().strip()
            if sk_clean in cls.RESOURCE_MAP:
                for cert in cls.RESOURCE_MAP[sk_clean]["certifications"]:
                    certifications.append(cert)

        if not certifications:
            certifications.append({
                "title": f"Professional {job.get('title', 'Role')} Certification",
                "issuer": "Coursera / LinkedIn Learning",
                "url": "https://www.coursera.org"
            })

        # 3. Simulate Match Improvement Score Step-by-Step
        # Each missing required skill adds +8% to match score; each preferred skill adds +4%
        simulation_steps = []
        accumulated_score = current_match_score

        for sk in missing_required:
            gain = 8
            accumulated_score = min(98, accumulated_score + gain)
            simulation_steps.append({
                "skill_acquired": sk,
                "skill_type": "Required",
                "score_gain": f"+{gain}%",
                "projected_match_score": accumulated_score,
                "match_category": "Excellent Match" if accumulated_score >= 85 else "Strong Match"
            })

        for sk in missing_preferred:
            gain = 4
            accumulated_score = min(98, accumulated_score + gain)
            simulation_steps.append({
                "skill_acquired": sk,
                "skill_type": "Preferred",
                "score_gain": f"+{gain}%",
                "projected_match_score": accumulated_score,
                "match_category": "Excellent Match" if accumulated_score >= 85 else "Strong Match"
            })

        return {
            "job_id": job.get("id"),
            "job_title": job.get("title"),
            "current_match_score": current_match_score,
            "projected_max_match_score": accumulated_score,
            "roadmap_phases": roadmap_phases,
            "recommended_certifications": certifications[:4],
            "match_improvement_simulation": simulation_steps
        }
