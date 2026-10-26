"""
Salary Prediction and Labor Market Analysis Blueprint.
Endpoints:
- POST /api/salary/predict : Generate salary prediction & progression analysis
- GET  /api/salary/market  : Broad labor market benchmark overview for a role
- GET  /api/salary/roles   : Supported canonical roles grouped by domain
- GET  /api/salary/locations : Supported countries, currencies, and city hubs
- GET  /api/salary/autofill : Profile autofill from authenticated user's resume
"""

import logging
from flask import Blueprint, request, jsonify
from app.services.salary.salary_service import SalaryService
from app.routes.auth import jwt_required

logger = logging.getLogger(__name__)

salary_bp = Blueprint("salary", __name__, url_prefix="/api/salary")

@salary_bp.route("/roles", methods=["GET"])
def get_roles():
    """Return all supported canonical roles and domain groupings."""
    try:
        data = SalaryService.get_supported_roles()
        return jsonify({"success": True, **data}), 200
    except Exception as e:
        logger.error("Error retrieving salary roles: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500

@salary_bp.route("/locations", methods=["GET"])
def get_locations():
    """Return supported countries, currencies, and cities."""
    try:
        data = SalaryService.get_supported_locations()
        return jsonify({"success": True, **data}), 200
    except Exception as e:
        logger.error("Error retrieving salary locations: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500

@salary_bp.route("/predict", methods=["POST"])
def predict():
    """
    Generate comprehensive salary prediction based on professional profile inputs.
    Request JSON body:
    {
      "role": "Software Engineer",
      "country": "IN",
      "city": "Bengaluru",
      "experience_years": 4.5,
      "seniority": "mid",
      "education": "bachelor",
      "skills": ["Python", "FastAPI", "Docker", "AWS"],
      "industry": "Information Technology",
      "company_type": "standard"
    }
    """
    try:
        payload = request.get_json(silent=True) or {}
        role = payload.get("role") or payload.get("job_title") or payload.get("profession")
        if not role:
            return jsonify({"success": False, "error": "Missing required field: 'role'"}), 400

        country = payload.get("country", "IN")
        city = payload.get("city", "")
        experience_years = float(payload.get("experience_years", 3.0))
        seniority = payload.get("seniority", "mid")
        education = payload.get("education", "bachelor")
        skills = payload.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]
        industry = payload.get("industry", "Technology")
        company_type = payload.get("company_type", "standard")

        prediction = SalaryService.predict_salary(
            role_title=role,
            country=country,
            city=city,
            experience_years=experience_years,
            seniority=seniority,
            education=education,
            skills=skills,
            industry=industry,
            company_type=company_type
        )

        return jsonify({"success": True, "data": prediction}), 200
    except Exception as e:
        logger.error("Error generating salary prediction: %s", e, exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@salary_bp.route("/market", methods=["GET"])
def market():
    """
    Return labor market benchmark overview for a role across experience tiers.
    Query parameters:
    - role: "Data Scientist" (required)
    - country: "US" (default: "IN")
    """
    try:
        role = request.args.get("role", "").strip()
        if not role:
            return jsonify({"success": False, "error": "Query parameter 'role' is required"}), 400

        country = request.args.get("country", "IN").strip()
        data = SalaryService.get_market_overview(role_title=role, country=country)
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        logger.error("Error retrieving market overview: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500

@salary_bp.route("/autofill", methods=["GET"])
@jwt_required
def autofill():
    """
    Extract profile parameters from the authenticated user's latest parsed resume.
    """
    try:
        current_user = getattr(request, "current_user", {})
        user_id = str(current_user.get("_id") or current_user.get("user_id") or "")
        if not user_id:
            return jsonify({"success": False, "error": "Invalid user context"}), 401

        result = SalaryService.extract_autofill_from_user(user_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error("Error in salary autofill endpoint: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500
