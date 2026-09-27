import os
import sys
import fitz  # PyMuPDF
from app.services.pdf_service import PDFService
from app.services.resume_validator import ResumeValidator

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_pdfs")
os.makedirs(TEST_DIR, exist_ok=True)

def create_test_pdfs():
    """Generate sample test PDFs for categories A through J."""
    pdf_files = {}

    # A. Normal text-based one-page resume
    doc_a = fitz.open()
    page_a = doc_a.new_page()
    page_a.insert_text((50, 50), "John Doe\nEmail: john.doe@gmail.com | Phone: +1-555-0199\nLinkedIn: linkedin.com/in/johndoe\n\nSUMMARY\nExperienced Software Engineer specializing in Python, Flask, and PostgreSQL.\n\nEDUCATION\nB.Tech in Computer Science, State University, 2020\n\nSKILLS\nPython, JavaScript, React, SQL, Docker, Git\n\nEXPERIENCE\nSoftware Engineer - TechCorp (2020-Present)\n- Built RESTful microservices for high throughput.\n- Optimized SQL queries reducing latency by 40%.")
    path_a = os.path.join(TEST_DIR, "A_normal_one_page.pdf")
    doc_a.save(path_a)
    doc_a.close()
    pdf_files['A'] = (path_a, "SUCCESS")

    # B. Normal text-based multi-page resume
    doc_b = fitz.open()
    p1 = doc_b.new_page()
    p1.insert_text((50, 50), "Sarah Jenkins\nEmail: sjenkins@gmail.com | Phone: +1-555-0144\n\nSUMMARY\nSenior Project Manager with 8+ years leading cross-functional teams.\n\nEDUCATION\nMaster of Business Administration (MBA), Business School, 2016\nBachelor of Science in Industrial Engineering, 2014")
    p2 = doc_b.new_page()
    p2.insert_text((50, 50), "EXPERIENCE\nLead Project Manager - Apex Global (2019-2023)\n- Managed $5M product roadmap across 4 remote engineering teams.\n- Improved sprint delivery velocity by 25%.\n\nSKILLS\nAgile, Scrum, JIRA, Risk Management, Stakeholder Communication\n\nCERTIFICATIONS\nPMP Certified, Certified Scrum Master (CSM)")
    path_b = os.path.join(TEST_DIR, "B_multi_page.pdf")
    doc_b.save(path_b)
    doc_b.close()
    pdf_files['B'] = (path_b, "SUCCESS")

    # C. Resume containing tables
    doc_c = fitz.open()
    p_c = doc_c.new_page()
    p_c.insert_text((50, 50), "Alex Rivera\nEmail: alex.rivera@corp.com | Phone: 555-0188\n\nCAREER OBJECTIVE\nFinance Executive with expertise in financial modeling and auditing.\n\nEDUCATION & QUALIFICATION\nDegree: B.Com in Accounting | University: Central College | Year: 2021\n\nSKILLS & COMPETENCIES\nCategory: Accounting | Skills: Tally Prime, GST, Balance Sheet, Auditing\nCategory: Tools | Skills: Advanced Excel, SAP, Financial Reporting\n\nWORK EXPERIENCE\nAccounts Executive - Financial Services (2021-Present)\n- Handled monthly GST filings and account reconciliations.")
    path_c = os.path.join(TEST_DIR, "C_table_resume.pdf")
    doc_c.save(path_c)
    doc_c.close()
    pdf_files['C'] = (path_c, "SUCCESS")

    # D. Resume containing columns
    doc_d = fitz.open()
    p_d = doc_d.new_page()
    p_d.insert_text((50, 50), "DR. ELENA ROSTOVA\nEmail: elena.rostova@healthnet.org | Phone: +1-555-0192\n\nPROFILE SUMMARY\nDedicated Registered Staff Nurse with 6+ years in ICU and emergency care.\n\nEDUCATION & CERTIFICATIONS\n- Bachelor of Science in Nursing (B.Sc Nursing), 2017\n- BLS & ACLS Certified Nurse Practitioner\n\nCLINICAL SKILLS\n- Patient Assessment & Triage\n- Medication Administration & IV Therapy\n- Electronic Health Records (EHR)\n\nWORK HISTORY\nStaff Nurse - Metro General Hospital (2018-Present)\n- Managed critical care patients in 20-bed Intensive Care Unit.")
    path_d = os.path.join(TEST_DIR, "D_column_resume.pdf")
    doc_d.save(path_d)
    doc_d.close()
    pdf_files['D'] = (path_d, "SUCCESS")

    # E. Image/scanned PDF (No selectable text)
    doc_e = fitz.open()
    p_e = doc_e.new_page()
    pix = fitz.Pixmap(fitz.csRGB, fitz.Rect(0, 0, 200, 200), False)
    pix.clear_with(255)
    p_e.insert_image(p_e.rect, pixmap=pix)
    path_e = os.path.join(TEST_DIR, "E_scanned_image.pdf")
    doc_e.save(path_e)
    doc_e.close()
    pdf_files['E'] = (path_e, "OCR_REQUIRED")

    # F. Password-protected PDF
    doc_f = fitz.open()
    p_f = doc_f.new_page()
    p_f.insert_text((50, 50), "Protected Resume Text")
    path_f = os.path.join(TEST_DIR, "F_password_protected.pdf")
    doc_f.save(path_f, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="owner123", user_pw="secret123")
    doc_f.close()
    pdf_files['F'] = (path_f, "PDF_PASSWORD_PROTECTED")

    # G. Corrupted/invalid PDF
    path_g = os.path.join(TEST_DIR, "G_corrupted.pdf")
    with open(path_g, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<>>\nTHIS_IS_INVALID_CORRUPTED_PDF_HEADER_DATA_BYTES")
    pdf_files['G'] = (path_g, "PDF_CORRUPTED")

    # H. Very short but valid resume
    doc_h = fitz.open()
    p_h = doc_h.new_page()
    p_h.insert_text((50, 50), "David Kim\nEmail: david.k@tech.io | Phone: 555-0123\nEducation: B.S. Computer Science\nSkills: Python, SQL, Git\nExperience: Software Intern at Startup (2023)")
    path_h = os.path.join(TEST_DIR, "H_short_valid_resume.pdf")
    doc_h.save(path_h)
    doc_h.close()
    pdf_files['H'] = (path_h, "SUCCESS")

    # I. Resume from a non-IT profession (Nursing / Healthcare)
    doc_i = fitz.open()
    p_i = doc_i.new_page()
    p_i.insert_text((50, 50), "Maria Fernandez\nEmail: maria.nurse@hospital.org | Phone: 555-9876\n\nSUMMARY\nCompassionate Registered Nurse with 5 years clinical experience.\n\nEDUCATION\nBachelor of Science in Nursing (B.Sc Nursing), State Medical University, 2018\n\nSKILLS & COMPETENCIES\nPatient Care, Wound Dressing, IV Administration, EHR Software, Triage\n\nEXPERIENCE\nClinical Staff Nurse - City Health Hospital (2018-2023)\n- Administered medications to 15+ acute care patients daily.")
    path_i = os.path.join(TEST_DIR, "I_nursing_non_it.pdf")
    doc_i.save(path_i)
    doc_i.close()
    pdf_files['I'] = (path_i, "SUCCESS")

    # J. Astronomy / Astrophysics resume
    doc_j = fitz.open()
    p_j = doc_j.new_page()
    p_j.insert_text((50, 50), "Dr. Arthur Pendelton\nEmail: arthur.astrophysics@observatory.edu | Phone: 555-4321\n\nSUMMARY\nAstrophysicist & Research Fellow specializing in stellar evolution and radio astronomy data analysis.\n\nEDUCATION\nPh.D in Astrophysics, Institute for Astronomy, 2021\nM.Sc in Physics & Astronomy, State University, 2017\n\nTECHNICAL SKILLS\nPython, Astropy, MATLAB, Spectroscopic Analysis, Radio Interferometry, Data Reduction\n\nRESEARCH EXPERIENCE & PROJECTS\nPostdoctoral Research Fellow - National Radio Astronomy Observatory (2021-Present)\n- Processed high-resolution radio spectrum datasets from ALMA observatory.\n- Published 4 peer-reviewed papers on cosmic microwave background radiation.")
    path_j = os.path.join(TEST_DIR, "J_astrophysics_resume.pdf")
    doc_j.save(path_j)
    doc_j.close()
    pdf_files['J'] = (path_j, "SUCCESS")

    return pdf_files

def run_pdf_extraction_test_suite():
    print("=" * 60)
    print("CAREER LENS - MULTI-FORMAT PDF EXTRACTION TEST SUITE")
    print("=" * 60)

    pdf_test_cases = create_test_pdfs()
    all_passed = True

    for case_id, (file_path, expected_status) in pdf_test_cases.items():
        print(f"\n[TEST CASE {case_id}] {os.path.basename(file_path)}")
        res = PDFService.extract_text(file_path)

        actual_status = res.get("status")
        is_valid = res.get("is_valid")
        extracted_text = res.get("text", "")
        message = res.get("message", "")
        method = res.get("extraction_method")

        print(f"  Expected Status:   {expected_status}")
        print(f"  Actual Status:     {actual_status}")
        print(f"  Extraction Valid:  {is_valid}")
        print(f"  Extraction Method: {method}")
        print(f"  Char Count:        {res.get('extracted_char_count')}")
        print(f"  Word Count:        {res.get('extracted_word_count')}")
        print(f"  User Message:      {message}")

        if expected_status == "SUCCESS":
            if not is_valid or actual_status != "SUCCESS":
                print(f"  [FAIL] Expected successful extraction but got status '{actual_status}'")
                all_passed = False
            else:
                # Run Resume Validator test
                val_res = ResumeValidator.validate_document(extracted_text)
                val_status = val_res.get("status")
                print(f"  Resume Validation: {val_status} (Doc Type: {val_res.get('document_type')})")
                if val_status != "VALID_RESUME":
                    print(f"  [FAIL] Resume validation rejected text: {val_res.get('reason')}")
                    all_passed = False
                else:
                    print(f"  [OK] Successful extraction & valid resume status.")
        else:
            if actual_status != expected_status:
                print(f"  [FAIL] Expected '{expected_status}' but got '{actual_status}'")
                all_passed = False
            else:
                print(f"  [OK] Correctly identified status '{actual_status}'.")

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL 10 PDF TEST CASES PASSED SUCCESSFULLY!")
    else:
        print("[FAIL] SOME TEST CASES FAILED!")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = run_pdf_extraction_test_suite()
    sys.exit(0 if success else 1)
