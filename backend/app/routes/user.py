from flask import Blueprint, jsonify, request
from app.routes.auth import jwt_required
from app.models.user import UserModel

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@jwt_required
def get_user_profile():
    """Retrieve authenticated user's profile information."""
    user_json = UserModel.to_json(request.current_user)
    return jsonify({
        "success": True,
        "message": "User profile retrieved successfully",
        "data": {
            "user": user_json
        }
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required
def update_user_profile():
    """Update candidate profile details (education, degree, role, location, experience)."""
    data = request.get_json(silent=True) or {}
    user_id = str(request.current_user.get("_id"))

    updated_user = UserModel.update_profile(user_id, data)
    if not updated_user:
        return jsonify({
            "success": False,
            "message": "Failed to update profile",
            "error": "Update failed"
        }), 400

    return jsonify({
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "user": UserModel.to_json(updated_user)
        }
    }), 200
