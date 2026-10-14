import datetime
import functools
import jwt
from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests

from app.config import Config
from app.models.user import UserModel
from app.utils.validators import validate_registration_data, validate_login_data

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def jwt_required(f):
    """Decorator to enforce JWT authentication on protected endpoints."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # Allow preflight OPTIONS requests without requiring authentication
        if request.method == 'OPTIONS':
            return ('', 204)

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                "success": False,
                "message": "Authorization header missing",
                "error": "Authentication token required"
            }), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                "success": False,
                "message": "Invalid Authorization header format",
                "error": "Header must be in 'Bearer <token>' format"
            }), 401

        token = parts[1]
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")
            user = UserModel.find_by_id(user_id)
            if not user:
                return jsonify({
                    "success": False,
                    "message": "User associated with token no longer exists",
                    "error": "User not found"
                }), 401
            request.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Authentication token has expired. Please login again.",
                "error": "Token expired"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid authentication token",
                "error": "Token invalid"
            }), 401

        return f(*args, **kwargs)
    return decorated

def generate_app_jwt(user):
    """Generate application JWT token for authenticated candidate."""
    user_id_str = str(user.get("_id"))
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": user_id_str,
        "email": user.get("email"),
        "name": user.get("name"),
        "iat": now,
        "exp": now + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Register local candidate user account."""
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    
    is_valid, error_msg = validate_registration_data(data)
    if not is_valid:
        return jsonify({
            "success": False,
            "message": error_msg,
            "error": "Validation error"
        }), 400

    email = data.get('email').strip().lower()
    existing_user = UserModel.find_by_email(email)
    if existing_user:
        return jsonify({
            "success": False,
            "message": "An account with this email address already exists. Please log in.",
            "error": "Duplicate email"
        }), 409

    user_doc = UserModel.create_user(data)
    user_json = UserModel.to_json(user_doc)

    return jsonify({
        "success": True,
        "message": "Account created successfully. Please login to continue.",
        "data": {
            "user": user_json
        }
    }), 201

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Authenticate candidate via local credentials and issue JWT token."""
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}

    is_valid, error_msg = validate_login_data(data)
    if not is_valid:
        return jsonify({
            "success": False,
            "message": error_msg,
            "error": "Validation error"
        }), 400

    email = data.get('email').strip().lower()
    user = UserModel.find_by_email(email)

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid email or password credentials.",
            "error": "Authentication failed"
        }), 401

    if user.get("auth_provider") == "google" and not user.get("password_hash"):
        return jsonify({
            "success": False,
            "message": "This account was created using Google Sign-In. Please click 'Continue with Google' to log in.",
            "error": "Google auth required"
        }), 400

    if not UserModel.verify_password(user.get("password_hash", ""), data.get("password")):
        return jsonify({
            "success": False,
            "message": "Invalid email or password credentials.",
            "error": "Authentication failed"
        }), 401

    token = generate_app_jwt(user)
    user_json = UserModel.to_json(user)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "data": {
            "token": token,
            "user": user_json
        }
    }), 200

@auth_bp.route('/google', methods=['POST', 'OPTIONS'])
def google_auth():
    """
    Authenticate candidate via Google OAuth credential token.
    Verifies Google ID token signature & audience, creates or retrieves user, and returns application JWT.
    """
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    token = data.get('credential')

    if not token:
        return jsonify({
            "success": False,
            "message": "Google authentication credential is required",
            "error": "Missing credential"
        }), 400

    try:
        # Verify Google ID Token with Google Auth Library
        # Note: If client_id is default placeholder during dev, we verify token signature without enforcing exact audience
        client_id_to_check = Config.GOOGLE_CLIENT_ID if "your_google_oauth" not in Config.GOOGLE_CLIENT_ID else None
        
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=client_id_to_check
        )

        google_id = id_info.get('sub')
        email = id_info.get('email')
        name = id_info.get('name') or email.split('@')[0]
        picture = id_info.get('picture')

        if not email:
            return jsonify({
                "success": False,
                "message": "Unable to retrieve verified email from Google account",
                "error": "Email missing"
            }), 400

        # Check existing user by email
        existing_user = UserModel.find_by_email(email)

        if existing_user:
            # Existing account with same email -> Log in seamlessly and update Google profile details
            user = UserModel.link_google_account(
                user_id=existing_user.get("_id"),
                google_id=google_id,
                picture=picture
            ) or existing_user
        else:
            # New Google user -> Create account
            user = UserModel.create_google_user(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture
            )

        app_token = generate_app_jwt(user)
        user_json = UserModel.to_json(user)

        return jsonify({
            "success": True,
            "message": "Google authentication successful",
            "data": {
                "token": app_token,
                "user": user_json
            }
        }), 200

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": "Invalid Google credential token or token expired.",
            "error": str(e)
        }), 401
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An error occurred during Google authentication.",
            "error": str(e)
        }), 500

@auth_bp.route('/me', methods=['GET', 'OPTIONS'])
@jwt_required
def get_me():
    """Fetch current authenticated candidate profile."""
    if request.method == 'OPTIONS':
        return ('', 204)

    user_json = UserModel.to_json(request.current_user)
    return jsonify({
        "success": True,
        "message": "User profile retrieved successfully",
        "data": {
            "user": user_json
        }
    }), 200
