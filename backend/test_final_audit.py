import os
import io
import json
import requests
import fitz  # PyMuPDF

BASE_URL = "http://127.0.0.1:5000/api"

def create_pdf(text_content: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text_content)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

AUDIT_RESUMES = {
    "Healthcare/Nursing": {
        "text": """Mary Smith
Registered Staff Nurse
Email: mary@example.com | Phone: 9876543211
Education: B.Sc Nursing
Clinical Skills: Patient care, medication administration, IV administration, wound dressing, vital signs, ICU
Experience: Staff Nurse at City Hospital with 3 years clinical patient care experience."""
    },
    "Accounting/Finance": {
        "text": """Robert Johnson
Senior Accountant
Email: robert@example.com | Phone: 9876543212
Education: B.Com Accounting and Finance
Financial Skills: Tally, GST, Tally Prime, Bookkeeping, Accounts Payable, Accounts Receivable, Taxation, Excel
Experience: Accounts Executive managing ledger entries, GST filing, and financial reporting."""
    },
    "Mechanical Engineering": {
        "text": """David Miller
Mechanical Design Engineer
Email: david@example.com | Phone: 9876543213
Education: B.E Mechanical Engineering
Engineering Skills: AutoCAD, SolidWorks, CATIA, ANSYS, Manufacturing, Machining, CAD Design
Experience: Mechanical Engineer with 2 years experience in 3D CAD modeling and manufacturing quality control."""
    },
    "Education/Teaching": {
        "text": """Emily Davis
High School Science Teacher
Email: emily@example.com | Phone: 9876543215
Education: B.Ed Education, B.Sc Physics
Teaching Skills: Curriculum development, classroom management, lesson planning, pedagogy, student assessment
Experience: Subject Teacher delivering high school physics curriculum and interactive learning."""
    },
    "Marketing/Digital Marketing": {
        "text": """Alex Turner
Digital Marketing Specialist
Email: alex@example.com | Phone: 9876543216
Education: BBA Marketing
Skills: Digital Marketing, SEO, Google Ads, Content Marketing, Social Media Marketing, Copywriting
Experience: Digital Marketing Executive leading SEO strategies and Google Ad campaigns."""
    },
    "Civil Engineering": {
        "text": """James Wilson
Civil Site Engineer
Email: james@example.com | Phone: 9876543218
Education: B.E Civil Engineering
Skills: AutoCAD Civil 3D, Revit, STAAD Pro, Structural Design, Site Management, Quantity Surveying
Experience: Civil Engineer supervising residential construction sites and quantity estimation."""
    },
    "Human Resources (HR)": {
        "text": """Sarah Jenkins
Human Resources Executive
Email: sarah.hr@example.com | Phone: 9876543219
Education: MBA Human Resources
Skills: Talent Acquisition, Recruitment, Onboarding, Employee Relations, HRIS, Payroll Management
Experience: HR Generalist managing full lifecycle recruitment, onboarding, and employee relations."""
    },
    "Sales/Business Development": {
        "text": """Michael Brown
Sales & Business Development Executive
Email: michael.sales@example.com | Phone: 9876543220
Education: Bachelor of Business Administration
Skills: B2B Sales, Lead Generation, CRM, Salesforce, Cold Calling, Account Management, Negotiation
Experience: Sales Executive driving B2B client acquisition and account retention."""
    },
    "Software/IT": {
        "text": """John Doe
Software Engineer
Email: john@example.com | Phone: 9876543210
Education: B.E Computer Science and Engineering
Technical Skills: Python, Flask, SQL, React, MongoDB, REST APIs, Git, Docker
Experience: Software Developer with 2 years experience building Python web applications and microservices."""
    },
    "Science/Research (Astrophysics PhD)": {
        "text": """Dr. Elena Rostova
Astrophysicist & Astronomer
Email: elena@example.com | Phone: 9876543217
Education: Ph.D Astrophysics, M.Sc Physics
Research Skills: Stargazing, telescope alignment, astrophysical modeling, optical spectroscopy, Python astrophysics, observational data analysis
Experience: Postdoctoral Research Astronomer analyzing optical spectroscopy data, stellar evolution models, and cosmological observations."""
    },
    "General/Other (Legal)": {
        "text": """Patricia Vance
Legal Associate / Lawyer
Email: patricia@example.com | Phone: 9876543221
Education: LL.B Corporate Law
Skills: Contract Drafting, Corporate Law, Litigation, Compliance, Legal Research, Due Diligence
Experience: Legal Counsel assisting in commercial contract drafting and legal risk compliance."""
    }
}

def run_final_audit():
    print("==================================================")
    print("CAREER LENS — FINAL ACCURACY AND PERSONALIZATION AUDIT")
    print("==================================================\n")

    import time
    ts = int(time.time())
    auth_payload = {
        "name": "Audit Tester",
        "email": f"audit_tester_{ts}@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }

    reg_res = requests.post(f"{BASE_URL}/auth/register", json=auth_payload)
    reg_data = reg_res.json().get("data", {}) if reg_res.status_code in [200, 201] else {}
    token = reg_data.get("access_token") or reg_data.get("token")

    if not token:
        login_res = requests.post(f"{BASE_URL}/auth/login", json={"email": auth_payload["email"], "password": auth_payload["password"]})
        log_data = login_res.json().get("data", {}) if login_res.status_code == 200 else {}
        token = log_data.get("access_token") or log_data.get("token")

    if not token:
        print(f"FAILED to authenticate test user: {reg_res.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}
    print("[AUTH] Successfully authenticated test user with JWT token.\n")

    audit_summary = []

    for category, info in AUDIT_RESUMES.items():
        print(f"--------------------------------------------------", flush=True)
        print(f"AUDITING CATEGORY ({len(audit_summary)+1}/11): {category}", flush=True)
        print(f"--------------------------------------------------", flush=True)

        pdf_bytes = create_pdf(info["text"])
        files = {"resume": (f"{category.replace('/', '_').replace(' ', '_')}_resume.pdf", pdf_bytes, "application/pdf")}

        # 1. Upload
        up_res = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files=files)
        if up_res.status_code != 201:
            print(f"[FAIL] Upload failed: {up_res.text}", flush=True)
            continue

        resume_id = up_res.json()["data"]["resume"]["id"]

        # 2. Analyze
        an_res = requests.post(f"{BASE_URL}/resume/analyze/{resume_id}", headers=headers)
        if an_res.status_code != 200:
            print(f"[FAIL] Analysis failed: {an_res.text}", flush=True)
            continue

        # 3. Live Job Recommendations
        rec_res = requests.get(f"{BASE_URL}/jobs/recommended", headers=headers)
        if rec_res.status_code != 200:
            print(f"[FAIL] Recommendation API failed: {rec_res.text}", flush=True)
            continue

        res_data = rec_res.json()
        cand_prof = res_data.get("candidate_profile", {})
        prov_status = res_data.get("provider_status", {})
        prov_used = res_data.get("providers_used", [])
        telemetry = res_data.get("debug_telemetry", {})
        jobs_data = res_data.get("data", {})
        all_recs = jobs_data.get("all_recommendations", [])
        primary_recs = jobs_data.get("recommended_jobs", [])

        # 4. Forecast Recommendations
        fc_res = requests.get(f"{BASE_URL}/forecasting/recommendations", headers=headers)
        fc_data = fc_res.json().get("data", {}) if fc_res.status_code == 200 else {}
        fc_recs = fc_data.get("recommendations", [])

        urls_present = sum(1 for j in all_recs if j.get("application_url"))

        raw_rec = telemetry.get("raw_jobs_received", 0)
        norm_rec = telemetry.get("normalized_jobs", 0)
        dedup_rec = telemetry.get("duplicates_removed", 0)
        geo_el = telemetry.get("geo_eligible_count", norm_rec - telemetry.get("geo_rejected_count", 0))
        role_rel = telemetry.get("role_relevant_count", telemetry.get("eligible_jobs_count", 0))
        qual_comp = telemetry.get("qualification_compatible_count", max(0, role_rel - telemetry.get("qualification_rejected_count", 0)))

        # Verify Funnel Sequential Integrity: Role Relevant >= Qualification Compatible
        funnel_integrity = (role_rel >= qual_comp)

        record = {
            "category": category,
            "detected_domain": cand_prof.get("professional_domain", "UNKNOWN"),
            "detected_identity": cand_prof.get("professional_identity", "UNKNOWN"),
            "queries": res_data.get("search_queries", []),
            "providers_status": prov_status,
            "providers_used": prov_used,
            "raw_jobs_received": raw_rec,
            "normalized_jobs": norm_rec,
            "duplicates_removed": dedup_rec,
            "geo_eligible_count": geo_el,
            "role_relevant_jobs": role_rel,
            "qualification_compatible": qual_comp,
            "funnel_integrity_valid": funnel_integrity,
            "final_recommendations": len(primary_recs),
            "total_vacancies": res_data.get("total_vacancies", 0),
            "urls_present": urls_present,
            "forecast_recommendations_count": len(fc_recs),
            "top_forecast_recommendation": fc_recs[0] if fc_recs else None,
            "system_status": res_data.get("status")
        }
        audit_summary.append(record)

        print(f"  Detected Domain:        {record['detected_domain']}", flush=True)
        print(f"  Professional Identity:  {record['detected_identity']}", flush=True)
        print(f"  Search Queries:         {record['queries']}", flush=True)
        print(f"  Raw Jobs Received:      {record['raw_jobs_received']}", flush=True)
        print(f"  Normalized / Deduped:   {record['normalized_jobs']} (deduped {record['duplicates_removed']})", flush=True)
        print(f"  Geo Eligible Jobs:      {record['geo_eligible_count']}", flush=True)
        print(f"  Role Relevant Jobs:     {record['role_relevant_jobs']}", flush=True)
        print(f"  Qual Compatible Jobs:   {record['qualification_compatible']} (Funnel Sequential: {funnel_integrity})", flush=True)
        print(f"  Final Recommendations: {record['final_recommendations']}", flush=True)
        print(f"  Application URLs:       {record['urls_present']}/{len(all_recs)}", flush=True)
        if fc_recs:
            print(f"  Forecast Skill Rec:     {fc_recs[0]['skill']} ({fc_recs[0]['priority']}) - {fc_recs[0]['recommendation_reason']}", flush=True)
        print(f"  Response Status:        {record['system_status']}\n", flush=True)

    print("==================================================")
    print("FINAL AUDIT SUMMARY RESULT")
    print("==================================================")
    print(json.dumps(audit_summary, indent=2), flush=True)

if __name__ == "__main__":
    run_final_audit()
