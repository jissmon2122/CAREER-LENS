import unittest
from app.services.extraction_service import ExtractionService
from app.services.role_inference_service import RoleInferenceEngine
from app.services.role_taxonomy import RoleTaxonomy
from app.services.role_relevance_service import RoleRelevanceService
from app.services.eligibility_service import EligibilityService
from app.services.scoring_service import ScoringService

class TestUniversalProfessions(unittest.TestCase):

    def test_electrician_resume_inference(self):
        text = """
        John Doe
        Email: john.doe@example.com | Phone: 555-123-4567 | LinkedIn: linkedin.com/in/johndoe
        Certified Journeyman Electrician with 6 years of experience in residential, commercial, and industrial electrical systems.
        
        EXPERIENCE
        Senior Electrician - Apex Electrical Services (2020 - Present)
        - Installed conduit, electrical wiring, switchgear, and circuit breakers in accordance with the National Electrical Code (NEC).
        - Performed troubleshooting, load calculation, and diagnostic testing using multimeters and insulation testers.
        - Managed electrical maintenance and blueprint reading for high-voltage industrial installations.
        
        Apprentice Electrician - City Power & Light (2018 - 2020)
        - Assisted journeyman electricians in conduit bending, wire pulling, and sub-panel installations.
        
        EDUCATION & LICENSES
        - Trade Certificate in Electrical Installation - ITI / State Vocational Institute
        - Licensed Journeyman Electrician - State Electrical Board
        - OSHA 10 Certification
        
        SKILLS
        Electrical wiring, conduit, National Electrical Code (NEC), circuit breakers, switchgear, blueprint reading, multimeters, troubleshooting, lock out tag out (LOTO)
        """
        skills_res = ExtractionService.extract_skills(text)
        extracted_skills = skills_res.get("technical_skills", [])
        self.assertIn("electrical wiring", [s.lower() for s in extracted_skills])
        self.assertIn("conduit", [s.lower() for s in extracted_skills])
        self.assertTrue(any("national electrical code" in s.lower() for s in extracted_skills))

        analysis_mock = {
            "extracted_text": text,
            "technical_skills": extracted_skills,
            "work_experience": [
                {"title": "Senior Electrician", "company": "Apex Electrical Services"},
                {"title": "Apprentice Electrician", "company": "City Power & Light"}
            ],
            "certifications": ["Licensed Journeyman Electrician", "OSHA 10 Certification"],
            "education": [{"degree": "Trade Certificate", "institution": "ITI"}]
        }

        profile = RoleInferenceEngine.infer_candidate_profile(analysis_mock)
        self.assertEqual(profile["professional_domain"], "SKILLED_TRADES_ELECTRICAL")
        self.assertIn("Electrician", profile["inferred_roles"])
        self.assertIn("Electrician", profile["persona"])
        self.assertNotIn("Software Engineer", profile["inferred_roles"])
        self.assertNotIn("Data Analyst", profile["inferred_roles"])

    def test_electrician_relevance_and_strict_software_exclusion(self):
        cand_profile = {
            "professional_domain": "SKILLED_TRADES_ELECTRICAL",
            "target_role": "Electrician",
            "inferred_roles": ["Electrician", "Electrical Maintenance Technician", "Journeyman Electrician"],
            "core_skills": ["electrical wiring", "conduit", "nec", "circuit breakers"]
        }

        # 1. Real Electrician job should match
        electrician_job = {
            "title": "Journeyman Electrician - Commercial Construction",
            "company": "Titan Electric",
            "raw_description": "Seeking experienced commercial electrician for conduit bending, wiring, and panel installation."
        }
        rel_match = RoleRelevanceService.evaluate_role_relevance(cand_profile, electrician_job)
        self.assertTrue(rel_match["eligible"])
        self.assertIn(rel_match["role_relevance_status"], ["DIRECT_ROLE_MATCH", "RELATED_ROLE"])

        # 2. Software Developer job MUST be strictly excluded and classified UNRELATED
        software_job = {
            "title": "Full Stack Software Engineer",
            "company": "Tech Corp",
            "raw_description": "Develop React and Python web applications and microservices."
        }
        rel_soft = RoleRelevanceService.evaluate_role_relevance(cand_profile, software_job)
        self.assertFalse(rel_soft["eligible"])
        self.assertEqual(rel_soft["role_relevance_status"], "UNRELATED")

    def test_nurse_resume_inference(self):
        text = """
        Sarah Smith, RN, BSN
        Email: sarah.nurse@example.com | Phone: 555-987-6543 | LinkedIn: linkedin.com/in/sarahnurse
        Registered Nurse with 4 years of clinical experience in acute care and hospital ICU settings.
        
        EXPERIENCE
        Staff Nurse - Metro General Hospital (2021 - Present)
        - Provided direct patient care, monitored vital signs, administered IV medications, and performed wound dressing.
        - Collaborated with physicians on clinical care plans and maintained electronic health records (EHR).
        
        EDUCATION & LICENSES
        - Bachelor of Science in Nursing (BSN) - University Medical College
        - Registered Nurse (RN License) - State Nursing Board
        - Basic Life Support (BLS), Advanced Cardiovascular Life Support (ACLS)
        
        SKILLS
        Patient care, vital signs, wound dressing, medication administration, iv therapy, clinical triage, basic life support (bls)
        """
        skills_res = ExtractionService.extract_skills(text)
        extracted_skills = skills_res.get("technical_skills", [])
        self.assertIn("patient care", [s.lower() for s in extracted_skills])
        self.assertIn("vital signs", [s.lower() for s in extracted_skills])

        analysis_mock = {
            "extracted_text": text,
            "technical_skills": extracted_skills,
            "work_experience": [{"title": "Staff Nurse", "company": "Metro General Hospital"}],
            "certifications": ["Registered Nurse (RN License)", "BLS", "ACLS"],
            "education": [{"degree": "Bachelor of Science in Nursing (BSN)", "institution": "University Medical College"}]
        }

        profile = RoleInferenceEngine.infer_candidate_profile(analysis_mock)
        self.assertEqual(profile["professional_domain"], "HEALTHCARE")
        self.assertIn("Staff Nurse", profile["inferred_roles"])
        self.assertNotIn("Software Engineer", profile["inferred_roles"])

    def test_teacher_resume_inference(self):
        text = """
        Emily Davis, M.Ed.
        Email: emily.teacher@example.com | Phone: 555-333-2222
        High School Teacher with 5 years experience in secondary education and curriculum development.
        
        EXPERIENCE
        School Teacher - Oakridge High School (2019 - Present)
        - Designed and implemented classroom curriculum, lesson planning, and standardized student evaluations.
        - Mentored student projects, facilitated parent-teacher conferences, and managed classroom discipline.
        
        EDUCATION & LICENSES
        - Master of Education (M.Ed) - State Teachers College
        - State Teaching License - Grades 9-12
        
        SKILLS
        Lesson planning, curriculum development, classroom management, student assessment, pedagogy, educational technology
        """
        analysis_mock = {
            "extracted_text": text,
            "technical_skills": ExtractionService.extract_skills(text).get("technical_skills", []),
            "work_experience": [{"title": "School Teacher", "company": "Oakridge High School"}],
            "certifications": ["State Teaching License"],
            "education": [{"degree": "Master of Education", "institution": "State Teachers College"}]
        }
        profile = RoleInferenceEngine.infer_candidate_profile(analysis_mock)
        self.assertEqual(profile["professional_domain"], "EDUCATION")
        self.assertIn("School Teacher", profile["inferred_roles"])

    def test_accountant_resume_inference(self):
        text = """
        Michael Brown, CPA
        Email: michael@cpa-example.com | Phone: 555-444-1111
        Certified Public Accountant with 7 years of corporate accounting, tax preparation, and audit experience.
        
        EXPERIENCE
        Senior Accountant - Global Financial Advisory (2019 - Present)
        - Managed general ledger accounting, accounts payable (AP), accounts receivable (AR), and month-end close.
        - Conducted internal financial audits and prepared corporate tax filings in compliance with GAAP.
        
        EDUCATION & CREDENTIALS
        - B.Com in Accounting and Finance
        - Certified Public Accountant (CPA)
        
        SKILLS
        Financial reporting, auditing, taxation, accounts payable, accounts receivable, general ledger, tally, quickbooks, gaap
        """
        analysis_mock = {
            "extracted_text": text,
            "technical_skills": ExtractionService.extract_skills(text).get("technical_skills", []),
            "work_experience": [{"title": "Senior Accountant", "company": "Global Financial Advisory"}],
            "certifications": ["Certified Public Accountant (CPA)"],
            "education": [{"degree": "B.Com in Accounting", "institution": "University"}]
        }
        profile = RoleInferenceEngine.infer_candidate_profile(analysis_mock)
        self.assertEqual(profile["professional_domain"], "ACCOUNTING_FINANCE")
        self.assertIn("Accountant", profile["inferred_roles"])

    def test_welder_resume_inference(self):
        text = """
        Robert Miller
        Email: robert.welder@example.com | Phone: 555-777-8888
        Certified Welder Fabricator with expertise in structural steel and pipe welding.
        
        EXPERIENCE
        Structural Welder - Apex Metal Fab (2020 - Present)
        - Performed MIG welding, TIG welding, and flux-cored arc welding on heavy industrial components.
        - Interpreted blueprints, weld symbols, and performed beveling and fit-up inspection.
        
        CERTIFICATIONS
        - AWS D1.1 Structural Welding Certification
        - OSHA 10 Construction Safety
        """
        analysis_mock = {
            "extracted_text": text,
            "technical_skills": ExtractionService.extract_skills(text).get("technical_skills", []),
            "work_experience": [{"title": "Structural Welder", "company": "Apex Metal Fab"}],
            "certifications": ["AWS D1.1 Structural Welding Certification"],
            "education": []
        }
        profile = RoleInferenceEngine.infer_candidate_profile(analysis_mock)
        self.assertEqual(profile["professional_domain"], "SKILLED_TRADES_WELDING")
        self.assertIn("Welder", profile["inferred_roles"])

    def test_non_it_contact_score_not_penalized_for_missing_github(self):
        # Electrician or nurse with email, phone, and linkedin should get 10/10 without github
        contact_info = {
            "email_present": True,
            "phone_present": True,
            "linkedin_present": True,
            "github_present": False
        }
        score = ScoringService.calculate_contact_score(contact_info)
        self.assertEqual(score, 10, "Candidate with email, phone, and LinkedIn must receive full 10/10 contact score without GitHub.")

        # Recommendations should not tell an electrician to create GitHub
        strengths, improvements = ScoringService.generate_strengths_and_improvements(
            score_breakdown={},
            contact_info=contact_info,
            technical_skills=["electrical wiring", "conduit", "nec", "circuit breakers"],
            projects=[],
            certifications=["Journeyman Electrician License"],
            work_exp=[{"title": "Electrician"}],
            internships=[]
        )
        for imp in improvements:
            self.assertNotIn("GitHub", imp, f"Electrician should not be told to add GitHub: {imp}")

    def test_mandatory_license_check(self):
        # Candidate has wiring but lacks required license
        cand_skills = ["electrical wiring", "conduit"]
        required_skills = ["electrical wiring", "journeyman electrician"]
        res = EligibilityService.evaluate_eligibility(cand_skills, required_skills)
        self.assertEqual(res["status"], EligibilityService.MISSING_MANDATORY_REQUIREMENT)

        # Candidate possesses mandatory license
        cand_skills_licensed = ["electrical wiring", "conduit", "journeyman electrician"]
        res_ok = EligibilityService.evaluate_eligibility(cand_skills_licensed, required_skills)
        self.assertEqual(res_ok["status"], EligibilityService.ELIGIBLE)

if __name__ == "__main__":
    unittest.main()
