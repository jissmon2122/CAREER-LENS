import datetime
import functools
import logging
import time
import jwt
from flask import Blueprint, request, jsonify, current_app
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
    Verifies Google ID token signature, issuer, audience, and expiration,
    enforces email_verified claims, prevents account takeover,
    creates or retrieves user, and returns application JWT.
    """
    if request.method == 'OPTIONS':
        return ('', 204)

    t0 = time.time()
    data = request.get_json(silent=True) or {}
    token = data.get('credential') or data.get('id_token') or data.get('token')

    if not token:
        return jsonify({
            "success": False,
            "message": "Google authentication credential is required",
            "error": "Missing credential"
        }), 400

    # Verify Google OAuth configuration
    client_id = Config.GOOGLE_CLIENT_ID
    is_placeholder = not client_id or "your_google_oauth" in client_id
    if is_placeholder and not current_app.config.get('TESTING'):
        return jsonify({
            "success": False,
            "message": "Google OAuth is not configured on the server. Please set GOOGLE_CLIENT_ID in the server environment.",
            "error": "GOOGLE_OAUTH_UNCONFIGURED"
        }), 503

    try:
        # Determine whether token is JWT (ID token) or OAuth2 Access Token
        is_jwt = isinstance(token, str) and token.count('.') == 2
        id_info = None

        if is_jwt:
            # Verify Google ID Token with Google Auth Library
            client_id_to_check = None if (is_placeholder and current_app.config.get('TESTING')) else client_id
            id_info = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                audience=client_id_to_check
            )
            # Verify issuer
            issuer = id_info.get('iss')
            if issuer not in ['accounts.google.com', 'https://accounts.google.com']:
                return jsonify({
                    "success": False,
                    "message": "Invalid Google credential issuer.",
                    "error": "INVALID_ISSUER"
                }), 401
        else:
            # Verify OAuth2 Access Token against Google UserInfo API
            import urllib.request
            import urllib.error
            import json as py_json
            try:
                userinfo_req = urllib.request.Request(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    headers={'Authorization': f'Bearer {token}'}
                )
                with urllib.request.urlopen(userinfo_req, timeout=5) as u_res:
                    if u_res.status == 200:
                        id_info = py_json.loads(u_res.read().decode('utf-8'))
                    else:
                        raise ValueError("Userinfo returned non-200 status")
            except Exception as e:
                raise ValueError(f"Failed to verify Google access token: {e}")

        if not id_info:
            raise ValueError("Empty Google credential payload")

        google_id = id_info.get('sub')
        email = (id_info.get('email') or '').lower().strip()
        name = id_info.get('name') or (email.split('@')[0] if email else 'Google User')
        picture = id_info.get('picture')

        if not email or not google_id:
            return jsonify({
                "success": False,
                "message": "Unable to retrieve verified email or identity from Google account",
                "error": "Email or sub missing"
            }), 400

        # Enforce verified email requirement
        email_verified = id_info.get('email_verified')
        is_verified = (email_verified is True) or (str(email_verified).lower() == 'true')
        if not is_verified:
            return jsonify({
                "success": False,
                "message": "Google account email is not verified. Please verify your email with Google or sign in using email and password.",
                "error": "EMAIL_NOT_VERIFIED"
            }), 400

        # Safe Account Linking and Takeover Prevention:
        user_by_gid = UserModel.find_by_google_id(google_id)
        user_by_email = UserModel.find_by_email(email)

        # Hijacking Check 1: Google ID belongs to one user, but email matches a different user
        if user_by_gid and user_by_email and str(user_by_gid.get("_id")) != str(user_by_email.get("_id")):
            logger.warning(f"[AUTH GOOGLE CONFLICT] Cross-account conflict between google_id and email in {round(time.time() - t0, 3)}s")
            return jsonify({
                "success": False,
                "message": "An account conflict occurred during Google authentication. Please sign in with email and password.",
                "error": "ACCOUNT_LINKING_CONFLICT"
            }), 409

        if user_by_email:
            # Hijacking Check 2: Email is already linked to a different Google account
            existing_gid = user_by_email.get("google_id")
            if existing_gid and str(existing_gid) != str(google_id):
                logger.warning(f"[AUTH GOOGLE CONFLICT] Email already linked to different google_id in {round(time.time() - t0, 3)}s")
                return jsonify({
                    "success": False,
                    "message": "This email address is already linked to a different Google account.",
                    "error": "ACCOUNT_LINKING_CONFLICT"
                }), 409

            # Safely link Google info to existing user account
            user = UserModel.link_google_account(
                user_id=user_by_email.get("_id"),
                google_id=google_id,
                picture=picture
            ) or user_by_email
        elif user_by_gid:
            user = user_by_gid
        else:
            # New verified Google user -> Create account safely
            user = UserModel.create_google_user(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture
            )

        app_token = generate_app_jwt(user)
        user_json = UserModel.to_json(user)

        logger.info(f"[AUTH GOOGLE SUCCESS] user_id='{user.get('_id')}' verified in {round(time.time() - t0, 3)}s")

        return jsonify({
            "success": True,
            "message": "Google authentication successful",
            "data": {
                "token": app_token,
                "user": user_json
            }
        }), 200

    except ValueError as e:
        logger.warning(f"[AUTH GOOGLE FAILED] Invalid token: {str(e)[:100]}")
        return jsonify({
            "success": False,
            "message": "Invalid Google credential token or token expired.",
            "error": str(e)
        }), 401
    except Exception as e:
        logger.error(f"[AUTH GOOGLE ERROR] Unexpected error: {str(e)[:100]}")
        return jsonify({
            "success": False,
            "message": "An error occurred during Google authentication.",
            "error": "INTERNAL_AUTH_ERROR"
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
