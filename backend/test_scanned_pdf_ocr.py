import os
import sys
import io
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
from app.services.pdf_service import PDFService
from app.services.resume_validator import ResumeValidator

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_ocr_pdfs")
os.makedirs(TEST_DIR, exist_ok=True)

def create_scanned_pdf_image(text: str, width: int = 850, height: int = 1100) -> bytes:
    """Helper to render text into a high-contrast raster image and encapsulate it in PDF bytes."""
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Render line by line
    lines = text.split('\n')
    y_offset = 50
    for line in lines:
        if line.strip():
            draw.text((50, y_offset), line.strip(), fill='black')
        y_offset += 24

    buf = io.BytesIO()
    img.save(buf, format='PNG')

    doc = fitz.open()
    page = doc.new_page(width=width, height=height)
    page.insert_image(page.rect, stream=buf.getvalue())
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def create_all_12_test_pdfs():
    files = {}

    # 1. Normal text-based resume
    doc_1 = fitz.open()
    p1 = doc_1.new_page()
    p1.insert_text((50, 50), "Alex Mercer\nEmail: alex.m@tech.com | Phone: 555-0100\n\nSUMMARY\nSoftware Engineer with experience in Python, Flask, and React.\n\nEDUCATION\nB.Tech in Computer Science, State University, 2021\n\nSKILLS\nPython, JavaScript, React, SQL, Docker, Git\n\nEXPERIENCE\nSoftware Engineer - CloudTech (2021-Present)")
    path_1 = os.path.join(TEST_DIR, "01_normal_text.pdf")
    doc_1.save(path_1)
    doc_1.close()
    files[1] = (path_1, "SUCCESS", "PyMuPDF")

    # 2. Multi-page text resume
    doc_2 = fitz.open()
    p2_1 = doc_2.new_page()
    p2_1.insert_text((50, 50), "Sarah Jenkins\nEmail: sjenkins@corp.com | Phone: 555-0144\n\nSUMMARY\nSenior Project Manager with 8+ years leading cross-functional teams.\n\nEDUCATION\nMBA in Business Administration, Business School, 2016")
    p2_2 = doc_2.new_page()
    p2_2.insert_text((50, 50), "EXPERIENCE\nLead Project Manager - Apex Global (2019-2023)\n- Managed $5M product roadmap.\n\nSKILLS\nAgile, Scrum, JIRA, Risk Management")
    path_2 = os.path.join(TEST_DIR, "02_multipage_text.pdf")
    doc_2.save(path_2)
    doc_2.close()
    files[2] = (path_2, "SUCCESS", "PyMuPDF")

    # 3. Scanned one-page resume (Software Engineer image)
    path_3 = os.path.join(TEST_DIR, "03_scanned_one_page_cse.pdf")
    bytes_3 = create_scanned_pdf_image("James Wilson\nEmail: jwilson@dev.org | Phone: 555-0199\n\nSUMMARY\nFull Stack Developer specializing in Python, React, and MongoDB.\n\nEDUCATION\nBachelor of Computer Applications (BCA), 2020\n\nTECHNICAL SKILLS\nPython, React, Node.js, MongoDB, Express, Git\n\nEXPERIENCE\nFull Stack Engineer - WebApps Inc (2020-Present)")
    with open(path_3, "wb") as f:
        f.write(bytes_3)
    files[3] = (path_3, "SUCCESS", "PyMuPDF+RapidOCR")

    # 4. Scanned multi-page resume (Nurse multi-page image)
    doc_4 = fitz.open()
    b4_1 = create_scanned_pdf_image("Emily Watson\nEmail: emily.nurse@hospital.org | Phone: 555-0188\n\nSUMMARY\nRegistered Staff Nurse with 6+ years in ICU care.\n\nEDUCATION\nBachelor of Science in Nursing (B.Sc Nursing), 2017")
    b4_2 = create_scanned_pdf_image("CLINICAL SKILLS\nPatient Care, Wound Dressing, Medication Admin, EHR, BLS\n\nWORK HISTORY\nStaff Nurse - Metro General Hospital (2018-Present)\n- Managed 15+ critical care patients daily in ICU.")
    d4_1 = fitz.open("pdf", b4_1)
    d4_2 = fitz.open("pdf", b4_2)
    doc_4.insert_pdf(d4_1)
    doc_4.insert_pdf(d4_2)
    path_4 = os.path.join(TEST_DIR, "04_scanned_multipage_nurse.pdf")
    doc_4.save(path_4)
    doc_4.close()
    files[4] = (path_4, "SUCCESS", "PyMuPDF+RapidOCR")

    # 5. Low-quality scanned resume (Blank image page)
    path_5 = os.path.join(TEST_DIR, "05_low_quality_blank_scanned.pdf")
    doc_5 = fitz.open()
    p5 = doc_5.new_page()
    pix5 = fitz.Pixmap(fitz.csRGB, fitz.Rect(0, 0, 100, 100), False)
    pix5.clear_with(255)
    p5.insert_image(p5.rect, pixmap=pix5)
    doc_5.save(path_5)
    doc_5.close()
    files[5] = (path_5, "OCR_FAILED", "PyMuPDF+RapidOCR")

    # 6. Resume with tables
    doc_6 = fitz.open()
    p6 = doc_6.new_page()
    p6.insert_text((50, 50), "Alex Rivera\nEmail: alex.r@corp.com | Phone: 555-0188\n\nCAREER OBJECTIVE\nFinance Executive with expertise in financial modeling.\n\nEDUCATION\nDegree: B.Com in Accounting | University: Central College\n\nSKILLS\nCategory: Accounting | Skills: Tally Prime, GST, Auditing")
    path_6 = os.path.join(TEST_DIR, "06_table_resume.pdf")
    doc_6.save(path_6)
    doc_6.close()
    files[6] = (path_6, "SUCCESS", "PyMuPDF")

    # 7. Resume with columns
    doc_7 = fitz.open()
    p7 = doc_7.new_page()
    p7.insert_text((50, 50), "Elena Rostova\nEmail: elena.r@health.org | Phone: 555-0192\n\nSUMMARY\nStaff Nurse with 5 years in emergency care.\n\nEDUCATION\nB.Sc Nursing, State Medical University\n\nCLINICAL SKILLS\nTriage, Patient Assessment, EHR")
    path_7 = os.path.join(TEST_DIR, "07_column_resume.pdf")
    doc_7.save(path_7)
    doc_7.close()
    files[7] = (path_7, "SUCCESS", "PyMuPDF")

    # 8. Non-IT scanned resume (Nursing)
    path_8 = os.path.join(TEST_DIR, "08_scanned_nursing.pdf")
    bytes_8 = create_scanned_pdf_image("Hannah Abbott\nEmail: hannah.n@hospital.org | Phone: 555-4321\n\nSUMMARY\nCompassionate Clinical Nurse with expertise in ICU and patient assessment.\n\nEDUCATION\nBachelor of Science in Nursing (B.Sc Nursing), 2019\n\nCLINICAL SKILLS\nPatient Care, IV Administration, EHR, Vital Signs, Triage\n\nEXPERIENCE\nClinical Staff Nurse - City Care Hospital (2019-Present)")
    with open(path_8, "wb") as f:
        f.write(bytes_8)
    files[8] = (path_8, "SUCCESS", "PyMuPDF+RapidOCR")

    # 9. Astronomy / Astrophysics scanned resume
    path_9 = os.path.join(TEST_DIR, "09_scanned_astrophysics.pdf")
    bytes_9 = create_scanned_pdf_image("Dr. Arthur Pendelton\nEmail: arthur.astrophysics@observatory.edu | Phone: 555-9876\n\nSUMMARY\nAstrophysicist & Research Fellow specializing in radio astronomy data analysis.\n\nEDUCATION\nPh.D in Astrophysics, Institute for Astronomy, 2021\n\nTECHNICAL SKILLS\nPython, Astropy, MATLAB, Spectroscopic Analysis, Data Reduction\n\nRESEARCH EXPERIENCE\nPostdoctoral Research Fellow - Radio Astronomy Observatory (2021-Present)")
    with open(path_9, "wb") as f:
        f.write(bytes_9)
    files[9] = (path_9, "SUCCESS", "PyMuPDF+RapidOCR")

    # 10. Nursing scanned resume
    path_10 = os.path.join(TEST_DIR, "10_scanned_nurse_detail.pdf")
    bytes_10 = create_scanned_pdf_image("Rachel Adams\nEmail: rachel.a@clinic.org | Phone: 555-8765\n\nSUMMARY\nStaff Nurse specializing in pediatric care and clinical triage.\n\nEDUCATION\nB.Sc Nursing, General Nursing Diploma, 2018\n\nSKILLS\nPatient Assessment, Wound Dressing, Medication Admin, EHR\n\nEXPERIENCE\nRegistered Staff Nurse - Childrens Clinic (2018-Present)")
    with open(path_10, "wb") as f:
        f.write(bytes_10)
    files[10] = (path_10, "SUCCESS", "PyMuPDF+RapidOCR")

    # 11. Accounting scanned resume
    path_11 = os.path.join(TEST_DIR, "11_scanned_accounting.pdf")
    bytes_11 = create_scanned_pdf_image("Marcus Vance\nEmail: marcus.v@finance.com | Phone: 555-7654\n\nSUMMARY\nAccounts Executive experienced in financial auditing and GST compliance.\n\nEDUCATION\nBachelor of Commerce (B.Com in Accounting), 2020\n\nTECHNICAL SKILLS\nTally Prime, GST Filing, Balance Sheet, Excel, Auditing\n\nEXPERIENCE\nAccounts Executive - Financial Services Ltd (2020-Present)")
    with open(path_11, "wb") as f:
        f.write(bytes_11)
    files[11] = (path_11, "SUCCESS", "PyMuPDF+RapidOCR")

    # 12. CSE scanned resume
    path_12 = os.path.join(TEST_DIR, "12_scanned_cse_developer.pdf")
    bytes_12 = create_scanned_pdf_image("Kevin Patel\nEmail: kevin.p@code.io | Phone: 555-6543\n\nSUMMARY\nBackend Software Engineer specializing in Python, Flask, and PostgreSQL.\n\nEDUCATION\nB.Tech in Computer Science, 2021\n\nSKILLS\nPython, Flask, PostgreSQL, REST APIs, Docker, Git\n\nEXPERIENCE\nSoftware Engineer - DevSolutions (2021-Present)")
    with open(path_12, "wb") as f:
        f.write(bytes_12)
    files[12] = (path_12, "SUCCESS", "PyMuPDF+RapidOCR")

    return files

def run_scanned_pdf_ocr_test_suite():
    print("=" * 60)
    print("CAREER LENS - MULTI-FORMAT SCANNED PDF OCR TEST SUITE")
    print("=" * 60)

    test_files = create_all_12_test_pdfs()
    all_passed = True

    for test_idx, (path, expected_status, expected_method) in test_files.items():
        fname = os.path.basename(path)
        print(f"\n[TEST CASE {test_idx:02d}] {fname}")
        res = PDFService.extract_text(path)

        act_status = res.get("status")
        is_val = res.get("is_valid")
        act_method = res.get("extraction_method")
        text = res.get("text", "")
        msg = res.get("message", "")

        print(f"  Expected Status: {expected_status}")
        print(f"  Actual Status:   {act_status}")
        print(f"  Method Used:     {act_method}")
        print(f"  Char Count:      {res.get('extracted_char_count')}")
        print(f"  Word Count:      {res.get('extracted_word_count')}")
        print(f"  User Message:    {msg}")

        if expected_status == "SUCCESS":
            if not is_val or act_status != "SUCCESS":
                print(f"  [FAIL] Expected successful extraction but got status '{act_status}'")
                all_passed = False
            else:
                val_res = ResumeValidator.validate_document(text)
                val_status = val_res.get("status")
                print(f"  Validation:      {val_status} (Doc Type: {val_res.get('document_type')})")
                if val_status != "VALID_RESUME":
                    print(f"  [FAIL] Document validation rejected text: {val_res.get('reason')}")
                    all_passed = False
                else:
                    print(f"  [OK] Successfully extracted and validated text!")
        else:
            if act_status != expected_status:
                print(f"  [FAIL] Expected '{expected_status}' but got '{act_status}'")
                all_passed = False
            else:
                print(f"  [OK] Correctly handled error status '{act_status}'.")

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL 12 SCANNED PDF OCR TEST CASES PASSED SUCCESSFULLY!")
    else:
        print("[FAIL] SOME TEST CASES FAILED!")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    success = run_scanned_pdf_ocr_test_suite()
    sys.exit(0 if success else 1)
