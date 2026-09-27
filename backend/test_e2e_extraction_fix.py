import os
import sys
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"
TEST_DIR = os.path.join(os.path.dirname(__file__), "test_pdfs")

def run_e2e_api_test():
    print("=" * 60)
    print("CAREER LENS - E2E API PDF EXTRACTION REGRESSION TEST")
    print("=" * 60)

    # 1. Register / Login test user
    test_hex = os.urandom(4).hex()
    user_email = f"pdf_fix_{test_hex}@example.com"
    user_pass = "TestPassword123!"

    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "PDF Fix Test Candidate",
        "email": user_email,
        "password": user_pass,
        "confirm_password": user_pass,
        "education": "Ph.D in Astrophysics"
    })

    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": user_email,
        "password": user_pass
    })

    if login_resp.status_code != 200:
        print(f"[FAIL] Login failed: {login_resp.text}")
        return False

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[AUTH] Successfully authenticated test candidate.")

    all_passed = True

    # 2. Test Scanned Image PDF (Type E)
    scanned_path = os.path.join(TEST_DIR, "E_scanned_image.pdf")
    with open(scanned_path, "rb") as f:
        up_resp = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files={"resume": f})
    resume_id_e = up_resp.json()["data"]["resume"]["id"]

    an_resp_e = requests.post(f"{BASE_URL}/resume/analyze/{resume_id_e}", headers=headers)
    res_e = an_resp_e.json()
    print(f"\n[TEST SCANNED PDF] Status Code: {an_resp_e.status_code}")
    print(f"  Response Status:  {res_e.get('status')}")
    print(f"  Response Message: {res_e.get('message')}")
    if res_e.get("status") == "OCR_REQUIRED" and "scanned" in res_e.get("message", "").lower():
        print("  [OK] Returned expected OCR_REQUIRED structured status.")
    else:
        print(f"  [FAIL] Unexpected response for scanned PDF: {res_e}")
        all_passed = False

    # 3. Test Password-Protected PDF (Type F)
    pwd_path = os.path.join(TEST_DIR, "F_password_protected.pdf")
    with open(pwd_path, "rb") as f:
        up_resp_f = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files={"resume": f})
    resume_id_f = up_resp_f.json()["data"]["resume"]["id"]

    an_resp_f = requests.post(f"{BASE_URL}/resume/analyze/{resume_id_f}", headers=headers)
    res_f = an_resp_f.json()
    print(f"\n[TEST PASSWORD PROTECTED PDF] Status Code: {an_resp_f.status_code}")
    print(f"  Response Status:  {res_f.get('status')}")
    print(f"  Response Message: {res_f.get('message')}")
    if res_f.get("status") == "PDF_PASSWORD_PROTECTED" and "password" in res_f.get("message", "").lower():
        print("  [OK] Returned expected PDF_PASSWORD_PROTECTED structured status.")
    else:
        print(f"  [FAIL] Unexpected response for password-protected PDF: {res_f}")
        all_passed = False

    # 4. Test Corrupted PDF (Type G)
    corrupt_path = os.path.join(TEST_DIR, "G_corrupted.pdf")
    with open(corrupt_path, "rb") as f:
        up_resp_g = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files={"resume": f})
    resume_id_g = up_resp_g.json()["data"]["resume"]["id"]

    an_resp_g = requests.post(f"{BASE_URL}/resume/analyze/{resume_id_g}", headers=headers)
    res_g = an_resp_g.json()
    print(f"\n[TEST CORRUPTED PDF] Status Code: {an_resp_g.status_code}")
    print(f"  Response Status:  {res_g.get('status')}")
    print(f"  Response Message: {res_g.get('message')}")
    if res_g.get("status") == "PDF_CORRUPTED" and "could not be read" in res_g.get("message", "").lower():
        print("  [OK] Returned expected PDF_CORRUPTED structured status.")
    else:
        print(f"  [FAIL] Unexpected response for corrupted PDF: {res_g}")
        all_passed = False

    # 5. Test Astrophysics Resume (Type J) & Verify Live Adzuna Recommendation Pipeline
    astro_path = os.path.join(TEST_DIR, "J_astrophysics_resume.pdf")
    with open(astro_path, "rb") as f:
        up_resp_j = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files={"resume": f})
    resume_id_j = up_resp_j.json()["data"]["resume"]["id"]

    an_resp_j = requests.post(f"{BASE_URL}/resume/analyze/{resume_id_j}", headers=headers)
    res_j = an_resp_j.json()
    print(f"\n[TEST ASTROPHYSICS RESUME] Status Code: {an_resp_j.status_code}")
    print(f"  Validation Status: {res_j.get('data', {}).get('analysis', {}).get('validation_status')}")
    print(f"  Detected Skills:   {res_j.get('data', {}).get('analysis', {}).get('technical_skills')}")

    if res_j.get("success") and res_j.get("data", {}).get("analysis", {}).get("validation_status") == "VALID_RESUME":
        print("  [OK] Astrophysics Resume parsed and validated successfully.")
    else:
        print(f"  [FAIL] Astrophysics resume failed analysis: {res_j}")
        all_passed = False

    # 6. Fetch Recommended Live Jobs
    jobs_resp = requests.get(f"{BASE_URL}/jobs/recommended", headers=headers)
    jobs_res = jobs_resp.json()
    cand_prof = jobs_res.get('candidate_profile', {})
    all_recs = jobs_res.get('data', {}).get('all_recommendations', [])

    print(f"\n[TEST LIVE ADZUNA JOB RECOMMENDATION PIPELINE]")
    print(f"  Status Code:            {jobs_resp.status_code}")
    print(f"  Response Status:        {jobs_res.get('status')}")
    print(f"  Inferred Identity:      {cand_prof.get('professional_identity')}")
    print(f"  Generated Queries:      {jobs_res.get('search_queries')}")
    print(f"  Live Jobs Returned:     {len(all_recs)}")
    
    first_job = all_recs[0] if all_recs else {}
    app_url = first_job.get('application_url', '')
    print(f"  Sample Job Card Title:  {first_job.get('title')}")
    print(f"  Sample Match Score:     {first_job.get('match_score')}%")
    print(f"  Sample Application URL: {app_url}")

    if jobs_res.get("status") == "LIVE_RECOMMENDATIONS_AVAILABLE" and len(all_recs) > 0 and app_url.startswith("http"):
        print("  [OK] Real live job recommendations generated with valid application URLs!")
    else:
        print(f"  [FAIL] Live job recommendation returned: status={jobs_res.get('status')}, jobs_count={len(all_recs)}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL END-TO-END REGRESSION TESTS PASSED CLEANLY!")
    else:
        print("[FAIL] E2E REGRESSION TEST FAILED!")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = run_e2e_api_test()
    sys.exit(0 if success else 1)
