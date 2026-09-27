from flask import Blueprint, request, jsonify
from app.routes.auth import jwt_required
from app.models.resume import ResumeModel
from app.models.resume_analysis import ResumeAnalysisModel
from app.models.user import UserModel
from app.models.skill_gap_analysis import SkillGapModel
from app.models.learning_roadmap import LearningRoadmapModel
from app.services.job_service import JobService
from app.services.job_matching import JobMatchingEngine
from app.services.skill_gap import SkillGapEngine
from app.services.learning_roadmap import LearningRoadmapEngine

skill_gap_bp = Blueprint('skill_gap', __name__, url_prefix='/api/skills')

@skill_gap_bp.route('/gap/<job_id>', methods=['GET'])
@jwt_required
def get_skill_gap(job_id):
    """
    Calculate & return detailed Skill Gap Analysis for candidate against target job.
    Includes validation guard.
    """
    user = getattr(request, 'current_user', None)
    user_id = str(user.get("_id", user.get("id")))

    # 1. Fetch user's latest resume
    my_resumes = ResumeModel.find_by_user(user_id)
    if not my_resumes:
        return jsonify({"success": False, "message": "Please upload a resume first."}), 400

    latest_resume_id = str(my_resumes[0].get("_id"))
    analysis_doc = ResumeAnalysisModel.find_by_resume_id(latest_resume_id)
    if not analysis_doc:
        return jsonify({"success": False, "message": "Please analyze your resume first."}), 400

    analysis_json = ResumeAnalysisModel.to_json(analysis_doc)

    # MANDATORY VALIDATION GUARD
    if analysis_json.get("validation_status") != "VALID_RESUME" or analysis_json.get("resume_score") is None:
        return jsonify({
            "success": False,
            "status": "GAP_ANALYSIS_BLOCKED",
            "message": "Skill Gap Analysis is unavailable because the uploaded document is not a valid resume.",
            "error": "INVALID_DOCUMENT"
        }), 400

    job = JobService.get_job_by_id(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found."}), 404

    user_json = UserModel.to_json(user)

    # Calculate gap analysis
    gap_res = SkillGapEngine.analyze_skill_gap(analysis_json, user_json, job)

    # Save to MongoDB
    gap_payload = {
        "user_id": user_id,
        "job_id": job_id,
        "required_coverage_percent": gap_res["required_coverage_percent"],
        "skill_gap_percent": gap_res["skill_gap_percent"],
        "matched_required_skills": gap_res["matched_required_skills"],
        "missing_required_skills": gap_res["missing_required_skills"],
        "matched_preferred_skills": gap_res["matched_preferred_skills"],
        "missing_preferred_skills": gap_res["missing_preferred_skills"],
        "prioritized_gaps": gap_res["prioritized_gaps"]
    }
    SkillGapModel.create_or_update_gap(gap_payload)

    return jsonify({
        "success": True,
        "data": {
            "skill_gap": gap_res
        }
    }), 200

@skill_gap_bp.route('/roadmap/<job_id>', methods=['GET'])
@jwt_required
def get_learning_roadmap(job_id):
    """
    Generate personalized learning roadmap, certification recommendations, and match simulation.
    """
    user = getattr(request, 'current_user', None)
    user_id = str(user.get("_id", user.get("id")))

    my_resumes = ResumeModel.find_by_user(user_id)
    if not my_resumes:
        return jsonify({"success": False, "message": "Please upload a resume first."}), 400

    latest_resume_id = str(my_resumes[0].get("_id"))
    analysis_doc = ResumeAnalysisModel.find_by_resume_id(latest_resume_id)
    if not analysis_doc:
        return jsonify({"success": False, "message": "Please analyze your resume first."}), 400

    analysis_json = ResumeAnalysisModel.to_json(analysis_doc)
    if analysis_json.get("validation_status") != "VALID_RESUME":
        return jsonify({"success": False, "message": "Roadmap unavailable for invalid document."}), 400

    job = JobService.get_job_by_id(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found."}), 404

    user_json = UserModel.to_json(user)

    # Calculate gap and current match score
    gap_res = SkillGapEngine.analyze_skill_gap(analysis_json, user_json, job)
    match_analysis = JobMatchingEngine.calculate_job_match(analysis_json, user_json, job)
    current_score = match_analysis["match_score"] if match_analysis else 75

    roadmap_res = LearningRoadmapEngine.generate_roadmap(gap_res, job, current_match_score=current_score)

    # Save roadmap to MongoDB
    roadmap_payload = {
        "user_id": user_id,
        "job_id": job_id,
        "roadmap_phases": roadmap_res["roadmap_phases"],
        "recommended_certifications": roadmap_res["recommended_certifications"],
        "match_improvement_simulation": roadmap_res["match_improvement_simulation"]
    }
    LearningRoadmapModel.create_or_update_roadmap(roadmap_payload)

    return jsonify({
        "success": True,
        "data": {
            "roadmap": roadmap_res
        }
    }), 200

@skill_gap_bp.route('/acquire', methods=['POST'])
@jwt_required
def acquire_skill():
    """
    Mark a missing skill as acquired and update candidate resume analysis profile.
    """
    user = getattr(request, 'current_user', None)
    user_id = str(user.get("_id", user.get("id")))

    data = request.get_json(silent=True) or {}
    skill_name = data.get("skill_name")
    if not skill_name:
        return jsonify({"success": False, "message": "skill_name is required."}), 400

    my_resumes = ResumeModel.find_by_user(user_id)
    if not my_resumes:
        return jsonify({"success": False, "message": "No resume found."}), 400

    latest_resume_id = str(my_resumes[0].get("_id"))
    analysis_doc = ResumeAnalysisModel.find_by_resume_id(latest_resume_id)
    if not analysis_doc:
        return jsonify({"success": False, "message": "No analysis found."}), 400

    tech_skills = analysis_doc.get("technical_skills", [])
    if skill_name not in tech_skills:
        tech_skills.append(skill_name)
        coll = ResumeAnalysisModel.get_collection()
        if coll is not None:
            coll.update_one({"_id": analysis_doc["_id"]}, {"$set": {"technical_skills": tech_skills}})

    return jsonify({
        "success": True,
        "message": f"Skill '{skill_name}' marked as acquired! Your candidate profile and match scores have been updated.",
        "data": {
            "acquired_skill": skill_name,
            "updated_technical_skills": tech_skills
        }
    }), 200
