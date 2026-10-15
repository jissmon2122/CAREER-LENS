import datetime
import functools
import logging
import time
import jwt
from flask import Blueprint, request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests

from app.config import Config
from app.db import Database
from app.models.user import UserModel
from app.utils.validators import validate_registration_data, validate_login_data

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def jwt_required(f):
    """Decorator to enforce JWT authentication on protected endpoints."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # Allow preflight OPTIONS requests without requiring authentication
        if request.method == 'OPTIONS':
            return ('', 204)

        t0 = time.time()
        path = request.path
        method = request.method
        logger.info(f"[AUTH VERIFY START] Path='{path}', Method='{method}'")

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.info(f"[AUTH VERIFY FAILED] Missing Authorization header for {method} {path} in {round(time.time() - t0, 3)}s")
            return jsonify({
                "success": False,
                "message": "Authorization header missing",
                "error": "Authentication token required"
            }), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            logger.info(f"[AUTH VERIFY FAILED] Invalid Authorization header format for {method} {path} in {round(time.time() - t0, 3)}s")
            return jsonify({
                "success": False,
                "message": "Invalid Authorization header format",
                "error": "Header must be in 'Bearer <token>' format"
            }), 401

        token = parts[1]
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id:
                logger.info(f"[AUTH VERIFY FAILED] Token missing subject payload for {method} {path}")
                return jsonify({
                    "success": False,
                    "message": "Invalid authentication token",
                    "error": "Token invalid"
                }), 401

            # Check database connection state before attempting lookup
            if not Database.is_connected():
                # Allow fallback if in-memory user exists (e.g. dev/mock test)
                in_mem_user = UserModel._in_memory_users.get(str(user_id))
                if in_mem_user:
                    request.current_user = in_mem_user
                    logger.info(f"[AUTH VERIFY IN-MEMORY] user_id='{user_id}' verified via in-memory store in {round(time.time() - t0, 3)}s")
                    return f(*args, **kwargs)

                logger.warning(f"[AUTH VERIFY ERROR] Database offline during token verification for user_id='{user_id}' for {method} {path}")
                return jsonify({
                    "success": False,
                    "message": "Database is temporarily unavailable. Please try again shortly.",
                    "error": "Database unavailable"
                }), 503

            try:
                user = UserModel.find_by_id(user_id)
            except Exception as db_exc:
                logger.error(f"[AUTH VERIFY DB ERROR] Database error looking up user_id='{user_id}' for {method} {path}: {db_exc}")
                return jsonify({
                    "success": False,
                    "message": "Database is temporarily unavailable. Please try again shortly.",
                    "error": "Database unavailable"
                }), 503

            if not user:
                logger.info(f"[AUTH VERIFY FAILED] User not found for user_id='{user_id}' for {method} {path} in {round(time.time() - t0, 3)}s")
                return jsonify({
                    "success": False,
                    "message": "User associated with token no longer exists",
                    "error": "User not found"
                }), 401

            request.current_user = user
            logger.info(f"[AUTH VERIFY SUCCESS] user_id='{user_id}' verified for {method} {path} in {round(time.time() - t0, 3)}s")
        except jwt.ExpiredSignatureError:
            logger.info(f"[AUTH VERIFY EXPIRED] Token expired for {method} {path} in {round(time.time() - t0, 3)}s")
            return jsonify({
                "success": False,
                "message": "Authentication token has expired. Please login again.",
                "error": "Token expired"
            }), 401
        except jwt.InvalidTokenError:
            logger.info(f"[AUTH VERIFY INVALID] Invalid token for {method} {path} in {round(time.time() - t0, 3)}s")
            return jsonify({
                "success": False,
                "message": "Invalid authentication token",
                "error": "Token invalid"
            }), 401
        except Exception as e:
            logger.exception(f"[AUTH VERIFY ERROR] Unexpected error verifying token for {method} {path}: {e}")
            return jsonify({
                "success": False,
                "message": "Authentication error occurred.",
                "error": "Authentication error"
            }), 500

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

    t0 = time.time()
    logger.info("[AUTH REGISTER START] POST /api/auth/register")

    data = request.get_json(silent=True) or {}
    
    is_valid, error_msg = validate_registration_data(data)
    if not is_valid:
        logger.info(f"[AUTH REGISTER FAILED] Validation error in {round(time.time() - t0, 3)}s: {error_msg}")
        return jsonify({
            "success": False,
            "message": error_msg,
            "error": "Validation error"
        }), 400

    email = data.get('email').strip().lower()
    
    if not Database.is_connected() and email not in UserModel._in_memory_users:
        logger.warning(f"[AUTH REGISTER ERROR] Database offline during registration attempt in {round(time.time() - t0, 3)}s")
        return jsonify({
            "success": False,
            "message": "Database is temporarily unavailable. Please try again shortly.",
            "error": "Database unavailable"
        }), 503

    try:
        existing_user = UserModel.find_by_email(email)
    except Exception as db_exc:
        logger.error(f"[AUTH REGISTER DB ERROR] Database error checking existing email in {round(time.time() - t0, 3)}s: {db_exc}")
        return jsonify({
            "success": False,
            "message": "Database is temporarily unavailable. Please try again shortly.",
            "error": "Database unavailable"
        }), 503

    if existing_user:
        logger.info(f"[AUTH REGISTER FAILED] Duplicate email in {round(time.time() - t0, 3)}s")
        return jsonify({
            "success": False,
            "message": "An account with this email address already exists. Please log in.",
            "error": "Duplicate email"
        }), 409

    try:
        user_doc = UserModel.create_user(data)
    except Exception as db_exc:
        logger.error(f"[AUTH REGISTER DB ERROR] Database error creating user in {round(time.time() - t0, 3)}s: {db_exc}")
        return jsonify({
            "success": False,
            "message": "Database is temporarily unavailable. Please try again shortly.",
            "error": "Database unavailable"
        }), 503

    user_json = UserModel.to_json(user_doc)
    logger.info(f"[AUTH REGISTER SUCCESS] Account created successfully in {round(time.time() - t0, 3)}s")

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

    t0 = time.time()
    logger.info("[AUTH LOGIN START] POST /api/auth/login")

    data = request.get_json(silent=True) or {}

    is_valid, error_msg = validate_login_data(data)
    if not is_valid:
        logger.info(f"[AUTH LOGIN FAILED] Validation error in {round(time.time() - t0, 3)}s: {error_msg}")
        return jsonify({
            "success": False,
            "message": error_msg,
            "error": "Validation error"
        }), 400

    email = data.get('email').strip().lower()

    if not Database.is_connected() and email not in UserModel._in_memory_users:
        logger.warning(f"[AUTH LOGIN ERROR] Database offline during login attempt in {round(time.time() - t0, 3)}s")
        return jsonify({
            "success": False,
            "message": "Database is temporarily unavailable. Please try again shortly.",
            "error": "Database unavailable"
        }), 503

    try:
        user = UserModel.find_by_email(email)
    except Exception as db_exc:
        logger.error(f"[AUTH LOGIN DB ERROR] Database error looking up email in {round(time.time() - t0, 3)}s: {db_exc}")
        return jsonify({
            "success": False,
            "message": "Database is temporarily unavailable. Please try again shortly.",
            "error": "Database unavailable"
        }), 503

    if not user:
        logger.info(f"[AUTH LOGIN FAILED] User not found in {round(time.time() - t0, 3)}s")
        return jsonify({
            "success": False,
            "message": "Invalid email or password credentials.",
            "error": "Authentication failed"
        }), 401

    if user.get("auth_provider") == "google" and not user.get("password_hash"):
        logger.info(f"[AUTH LOGIN FAILED] Account requires Google Sign-In in {round(time.time() - t0, 3)}s")
        return jsonify({
            "success": False,
            "message": "This account was created using Google Sign-In. Please click 'Continue with Google' to log in.",
            "error": "Google auth required"
        }), 400

    if not UserModel.verify_password(user.get("password_hash", ""), data.get("password")):
        logger.info(f"[AUTH LOGIN FAILED] Invalid password in {round(time.time() - t0, 3)}s")
        return jsonify({
            "success": False,
            "message": "Invalid email or password credentials.",
            "error": "Authentication failed"
        }), 401

    token = generate_app_jwt(user)
    user_json = UserModel.to_json(user)

    logger.info(f"[AUTH LOGIN SUCCESS] Login successful in {round(time.time() - t0, 3)}s")
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

    t0 = time.time()
    user_id = str(request.current_user.get("_id", "unknown"))
    logger.info(f"[AUTH ME START] Fetching profile for user_id='{user_id}'")

    user_json = UserModel.to_json(request.current_user)
    logger.info(f"[AUTH ME SUCCESS] Profile retrieved for user_id='{user_id}' in {round(time.time() - t0, 3)}s")
    return jsonify({
        "success": True,
        "message": "User profile retrieved successfully",
        "data": {
            "user": user_json
        }
    }), 200
