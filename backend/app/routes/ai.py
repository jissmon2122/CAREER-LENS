from flask import Blueprint, request, jsonify
from app.ai.embedding_service import embedding_service
from app.ai.semantic_matcher import semantic_matcher

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/status', methods=['GET'])
def ai_status():
    """Check AI / NLP model status."""
    return jsonify({
        "success": True,
        "data": {
            "ai_available": embedding_service.is_available(),
            "model_name": embedding_service._model_name,
            "device": "cpu"
        }
    }), 200

@ai_bp.route('/semantic-match', methods=['POST'])
def compute_semantic_match():
    """
    Standalone endpoint to compute AI semantic similarity and skill categorization.
    Expects JSON body:
    {
      "resume_text": "...",
      "job_description": "...",
      "candidate_skills": ["Python", "Flask", ...],
      "job_skills": ["Python", "PyTorch", ...]
    }
    """
    data = request.get_json() or {}
    resume_text = data.get('resume_text', '')
    job_description = data.get('job_description', '')
    candidate_skills = data.get('candidate_skills', [])
    job_skills = data.get('job_skills', [])

    result = semantic_matcher.compute_semantic_match(
        resume_text=resume_text,
        job_description=job_description,
        candidate_skills=candidate_skills,
        job_skills=job_skills
    )

    return jsonify({
        "success": True,
        "data": result
    }), 200
