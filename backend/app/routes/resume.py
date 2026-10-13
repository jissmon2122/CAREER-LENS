import os
import base64
import logging
from flask import Blueprint, request, jsonify, current_app

from app.routes.auth import jwt_required
from app.models.resume import ResumeModel
from app.models.resume_analysis import ResumeAnalysisModel
from app.services.pdf_service import PDFService
from app.services.resume_validator import ResumeValidator
from app.services.extraction_service import ExtractionService
from app.services.scoring_service import ScoringService

logger = logging.getLogger(__name__)
resume_bp = Blueprint('resume', __name__, url_prefix='/api/resume')

def execute_resume_analysis_pipeline(resume: dict, user_id: str) -> dict:
    """
    Core reusable logic to parse, validate, extract, score, and persist resume analysis.
    """
    resume_id = str(resume.get("_id", resume.get("id", "")))
    file_path = resume.get("file_path", "")
    full_path = os.path.join(os.path.dirname(__file__), '..', '..', file_path)

    # Reconstruct from base64 if local file missing
    if not os.path.exists(full_path) and resume.get("file_data_base64"):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(base64.b64decode(resume.get("file_data_base64")))

    # 1. PDF Text Extraction
    pdf_res = PDFService.extract_text(full_path)
    if not pdf_res.get("is_valid"):
        logger.warning(f"PDF extraction failed for resume_id={resume_id}: status={pdf_res.get('status')}, message={pdf_res.get('message')}")
        return {
            "is_extraction_failure": True,
            "status": pdf_res.get("status", "PDF_EXTRACTION_FAILED"),
            "message": pdf_res.get("message", "Unable to extract text from PDF file."),
            "error_details": pdf_res.get("error_details")
        }

    raw_text = pdf_res.get("text", "")

    # 2. Hard Gate: Document Validation
    validation = ResumeValidator.validate_document(raw_text)
    if validation.get("status") != "VALID_RESUME":
        analysis_payload = {
            "resume_id": resume_id,
            "user_id": user_id,
            "raw_text": raw_text,
            "validation_status": validation.get("status"),
            "document_type": validation.get("document_type"),
            "confidence": validation.get("confidence"),
            "positive_signals": validation.get("positive_signals", []),
            "negative_signals": validation.get("negative_signals", []),
            "validation_reason": validation.get("reason"),
            "resume_score": None,
            "ats_score": None,
            "technical_skills": [],
            "analysis_status": "INVALID_DOCUMENT"
        }
        return ResumeAnalysisModel.create_or_update_analysis(analysis_payload)

    # 3. Extraction & Scoring
    contact_info = ExtractionService.extract_contact_info(raw_text)
    sections_detected = ExtractionService.detect_sections(raw_text)
    skills_res = ExtractionService.extract_skills(raw_text)
    education_list = ExtractionService.extract_education(raw_text)
    projects_list = ExtractionService.extract_projects(raw_text)
    certifications_list = ExtractionService.extract_certifications(raw_text)
    exp_res = ExtractionService.extract_experience(raw_text)
    work_exp = exp_res.get("work_experience", [])
    internships = exp_res.get("internships", [])

    tech_skills = skills_res.get("technical_skills", [])
    categorized_tech = skills_res.get("categorized_technical_skills", {})
    soft_skills = skills_res.get("soft_skills", [])

    resume_score, score_breakdown = ScoringService.calculate_resume_score(
        contact_info=contact_info,
        education_list=education_list,
        technical_skills=tech_skills,
        projects=projects_list,
        certifications=certifications_list,
        work_exp=work_exp,
        internships=internships,
        sections_detected=sections_detected
    )

    ats_score, ats_breakdown = ScoringService.calculate_ats_score(
        pdf_valid=pdf_res.get("is_valid"),
        text=raw_text,
        sections_detected=sections_detected,
        technical_skills=tech_skills,
        contact_info=contact_info
    )

    strengths, improvements = ScoringService.generate_strengths_and_improvements(
        score_breakdown=score_breakdown,
        contact_info=contact_info,
        technical_skills=tech_skills,
        projects=projects_list,
        certifications=certifications_list,
        work_exp=work_exp,
        internships=internships
    )

    analysis_payload = {
        "resume_id": resume_id,
        "user_id": user_id,
        "raw_text": raw_text,
        "validation_status": "VALID_RESUME",
        "document_type": "RESUME",
        "confidence": validation.get("confidence"),
        "positive_signals": validation.get("positive_signals", []),
        "negative_signals": validation.get("negative_signals", []),
        "validation_reason": validation.get("reason"),
        "contact_information": contact_info,
        "education": education_list,
        "technical_skills": tech_skills,
        "categorized_technical_skills": categorized_tech,
        "soft_skills": soft_skills,
        "projects": projects_list,
        "certifications": certifications_list,
        "internships": internships,
        "work_experience": work_exp,
        "sections_detected": sections_detected,
        "resume_score": resume_score,
        "ats_score": ats_score,
        "score_breakdown": score_breakdown,
        "ats_score_breakdown": ats_breakdown,
        "strengths": strengths,
        "improvements": improvements,
        "analysis_status": "completed"
    }

    res = ResumeAnalysisModel.create_or_update_analysis(analysis_payload)
    try:
        from app.routes.job import clear_recommendations_cache
        clear_recommendations_cache(user_id)
    except Exception as e:
        logger.warning(f"Failed to clear recommendations cache: {e}")
    return res

@resume_bp.route('/upload', methods=['POST'])
@jwt_required
def upload_resume():
    """Upload PDF resume endpoint."""
    user_id = str(request.current_user.get("_id"))
    if 'resume' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded", "error": "Missing file"}), 400

    file = request.files['resume']
    if not file or file.filename == '':
        return jsonify({"success": False, "message": "No file selected", "error": "Empty filename"}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"success": False, "message": "Only PDF files are allowed", "error": "Invalid format"}), 400

    file_bytes = file.read()
    file_size = len(file_bytes)

    if file_size > current_app.config['MAX_FILE_SIZE']:
        return jsonify({"success": False, "message": "File exceeds maximum size limit (5MB)", "error": "File too large"}), 400

    original_filename = file.filename
    stored_filename = f"{user_id}_{int(os.urandom(4).hex(), 16)}.pdf"
    relative_path = os.path.join("uploads", "resumes", stored_filename)
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "wb") as f:
        f.write(file_bytes)

    file_base64 = base64.b64encode(file_bytes).decode('utf-8')

    resume_doc = ResumeModel.create_resume(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=relative_path,
        file_type="application/pdf",
        file_size=file_size,
        file_data_base64=file_base64
    )

    resume_json = ResumeModel.to_json(resume_doc)

    return jsonify({
        "success": True,
        "message": "Resume uploaded successfully",
        "data": {
            "resume": resume_json
        }
    }), 201

@resume_bp.route('/my-resumes', methods=['GET'])
@jwt_required
def get_my_resumes():
    user_id = str(request.current_user.get("_id"))
    resumes_list = ResumeModel.find_by_user(user_id)
    resumes_json = [ResumeModel.to_json(r) for r in resumes_list]
    return jsonify({
        "success": True,
        "message": "Resumes retrieved successfully",
        "data": {
            "resumes": resumes_json
        }
    }), 200

@resume_bp.route('/analyze/<resume_id>', methods=['POST'])
@jwt_required
def analyze_resume(resume_id):
    user_id = str(request.current_user.get("_id"))
    resume = ResumeModel.find_by_id_and_user(resume_id, user_id)
    if not resume:
        return jsonify({"success": False, "message": "Resume not found or access denied", "error": "Not found"}), 404

    analysis_doc = execute_resume_analysis_pipeline(resume, user_id)
    if not analysis_doc or (isinstance(analysis_doc, dict) and analysis_doc.get("is_extraction_failure")):
        status_code = analysis_doc.get("status", "PDF_EXTRACTION_FAILED") if isinstance(analysis_doc, dict) else "PDF_EXTRACTION_FAILED"
        msg = analysis_doc.get("message", "Unable to extract text from PDF file.") if isinstance(analysis_doc, dict) else "Unable to extract text from PDF file."
        return jsonify({
            "success": False,
            "status": status_code,
            "message": msg,
            "error": status_code
        }), 400

    analysis_json = ResumeAnalysisModel.to_json(analysis_doc)
    if analysis_json.get("validation_status") != "VALID_RESUME":
        return jsonify({
            "success": False,
            "status": "NOT_SCORED",
            "message": analysis_json.get("validation_reason", "Uploaded document is not a valid resume."),
            "data": {"analysis": analysis_json}
        }), 200

    return jsonify({
        "success": True,
        "message": "Resume analyzed successfully",
        "data": {"analysis": analysis_json}
    }), 200

@resume_bp.route('/analysis/<resume_id>', methods=['GET'])
@jwt_required
def get_resume_analysis(resume_id):
    user_id = str(request.current_user.get("_id"))
    analysis = ResumeAnalysisModel.find_by_resume_id(resume_id)
    if not analysis or str(analysis.get("user_id")) != user_id:
        return jsonify({"success": False, "message": "Analysis not found or access denied", "error": "Not found"}), 404

    analysis_json = ResumeAnalysisModel.to_json(analysis)
    return jsonify({
        "success": True,
        "data": {"analysis": analysis_json}
    }), 200
