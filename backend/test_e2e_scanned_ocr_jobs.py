import os
import sys
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"
TEST_DIR = os.path.join(os.path.dirname(__file__), "test_ocr_pdfs")

def run_scanned_e2e_live_jobs_test():
    print("=" * 60)
    print("CAREER LENS - E2E SCANNED RESUME TO LIVE ADZUNA JOBS TEST")
    print("=" * 60)

    # 1. Register candidate
    hex_id = os.urandom(4).hex()
    user_email = f"scanned_test_{hex_id}@example.com"
    user_pass = "TestPass123!"

    requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Scanned Candidate Tester",
        "email": user_email,
        "password": user_pass,
        "confirm_password": user_pass
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
    print("[AUTH] Successfully authenticated scanned candidate test user.")

    scanned_resumes_to_test = [
        ("09_scanned_astrophysics.pdf", "Astrophysics / Science"),
        ("08_scanned_nursing.pdf", "Nursing / Healthcare"),
        ("11_scanned_accounting.pdf", "Accounting / Finance"),
        ("12_scanned_cse_developer.pdf", "Software / CSE")
    ]

    all_passed = True

    for filename, label in scanned_resumes_to_test:
        fpath = os.path.join(TEST_DIR, filename)
        print(f"\n--------------------------------------------------")
        print(f"TESTING SCANNED RESUME: {label} ({filename})")
        print(f"--------------------------------------------------")

        with open(fpath, "rb") as f:
            up_resp = requests.post(f"{BASE_URL}/resume/upload", headers=headers, files={"resume": f})

        if up_resp.status_code != 201:
            print(f"  [FAIL] Failed to upload {filename}: {up_resp.text}")
            all_passed = False
            continue

        resume_id = up_resp.json()["data"]["resume"]["id"]
        print(f"  [OK] Uploaded Scanned PDF (resume_id={resume_id})")

        # Trigger analysis (runs OCR fallback engine automatically)
        an_resp = requests.post(f"{BASE_URL}/resume/analyze/{resume_id}", headers=headers)
        if an_resp.status_code != 200:
            print(f"  [FAIL] Analysis failed for scanned PDF: {an_resp.text}")
            all_passed = False
            continue

        an_data = an_resp.json().get("data", {}).get("analysis", {})
        val_status = an_data.get("validation_status")
        skills = an_data.get("technical_skills", [])
        print(f"  [OK] OCR & Resume Analysis Completed")
        print(f"    Validation Status: {val_status}")
        print(f"    Extracted Skills:  {skills[:8]}")

        # Fetch Live Job Recommendations
        jobs_resp = requests.get(f"{BASE_URL}/jobs/recommended", headers=headers)
        if jobs_resp.status_code != 200:
            print(f"  [FAIL] Live job recommendation endpoint error: {jobs_resp.text}")
            all_passed = False
            continue

        jobs_data = jobs_resp.json()
        cand_prof = jobs_data.get("candidate_profile", {})
        recs = jobs_data.get("data", {}).get("all_recommendations", [])
        status_code = jobs_data.get("status")

        inferred_domain = cand_prof.get("professional_domain")
        inferred_identity = cand_prof.get("professional_identity")
        queries = jobs_data.get("search_queries", [])

        print(f"  [OK] Live Recommendation Engine Triggered")
        print(f"    Inferred Domain:        {inferred_domain}")
        print(f"    Professional Identity:  {inferred_identity}")
        print(f"    Generated Queries:      {queries[:4]}")
        print(f"    Live Jobs Returned:     {len(recs)}")

        if len(recs) > 0:
            first_job = recs[0]
            app_url = first_job.get("application_url", "")
            print(f"    Sample Job Title:       {first_job.get('title')}")
            print(f"    Sample Match Score:      {first_job.get('match_score')}%")
            print(f"    Sample Application URL:  {app_url}")

            if status_code == "LIVE_RECOMMENDATIONS_AVAILABLE" and app_url.startswith("http"):
                print(f"  [OK] PASS: Scanned {label} resume generated live job cards with valid application URLs!")
            else:
                print(f"  [FAIL] Invalid recommendation status or application URL for scanned {label}")
                all_passed = False
        else:
            print(f"  [FAIL] No live jobs returned for scanned {label}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL SCANNED RESUMES END-TO-END LIVE RECOMMENDATIONS PASSED!")
    else:
        print("[FAIL] E2E SCANNED RESUME TEST FAILED!")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = run_scanned_e2e_live_jobs_test()
    sys.exit(0 if success else 1)
