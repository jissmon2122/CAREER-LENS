from app.services.role_inference_service import RoleInferenceEngine

cases = {
    'Nursing': 'Mary Smith B.Sc Nursing Staff Nurse Patient care medication administration IV dressing vital signs hospital ICU',
    'Accounting': 'Robert Johnson B.Com Accounting Finance Tally GST Tally Prime Bookkeeping Accounts Payable Taxation Excel',
    'Mechanical': 'David Miller B.E Mechanical Engineering AutoCAD SolidWorks CATIA ANSYS Manufacturing Machining CAD Design',
    'Education': 'Emily Davis B.Ed Education B.Sc Physics Curriculum development classroom management lesson planning pedagogy',
    'Marketing': 'Alex Turner BBA Marketing Digital Marketing SEO Google Ads Content Marketing Social Media Copywriting',
    'Civil': 'James Wilson B.E Civil Engineering AutoCAD Civil 3D Revit STAAD Pro Structural Design Site Management',
    'HR': 'Sarah Jenkins MBA Human Resources Talent Acquisition Recruitment Onboarding Employee Relations HRIS Payroll',
    'Sales': 'Michael Brown BBA Sales B2B Sales Lead Generation CRM Salesforce Cold Calling Account Management',
    'Software': 'John Doe B.E Computer Science Python Flask SQL React MongoDB REST APIs Git Docker Software Engineer',
    'Astrophysics': 'Dr. Elena Rostova Ph.D Astrophysics M.Sc Physics Stargazing telescope alignment astrophysical optical spectroscopy',
    'Legal': 'Patricia Vance LL.B Contract Drafting Corporate Law Litigation Compliance Legal Research Due Diligence'
}

for k, v in cases.items():
    res = RoleInferenceEngine.infer_candidate_profile({"raw_text": v})
    print(f"{k:14} -> Domain: {res['professional_domain']:24} | Identity: {res['professional_identity']}")
