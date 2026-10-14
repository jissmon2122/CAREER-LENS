from flask import Flask, jsonify, request
from flask_cors import CORS
from app.config import Config
from app.db import Database

def create_app():
    """Application factory for Flask app initialization."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS with configurable origins and credentials
    cors_origins = app.config.get('CORS_ORIGINS') or Config.DEFAULT_CORS_ORIGINS
    CORS(
        app,
        resources={r"/*": {"origins": cors_origins}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
        max_age=86400
    )

    @app.before_request
    def handle_cors_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            origin = request.headers.get('Origin')
            if origin:
                clean_origin = origin.strip().rstrip('/')
                is_allowed = (
                    clean_origin in cors_origins
                    or clean_origin.endswith('.vercel.app')
                    or 'localhost' in clean_origin
                    or '127.0.0.1' in clean_origin
                )
                if is_allowed:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
                    response.headers['Access-Control-Max-Age'] = '86400'
            return response

    @app.after_request
    def apply_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin:
            clean_origin = origin.strip().rstrip('/')
            is_allowed = (
                clean_origin in cors_origins
                or clean_origin.endswith('.vercel.app')
                or 'localhost' in clean_origin
                or '127.0.0.1' in clean_origin
            )
            if is_allowed:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
                response.headers['Access-Control-Max-Age'] = '86400'
        return response

    # Initialize MongoDB connection
    Database.initialize(app)

    # Initialize AI Embedding Service on Startup (lazy load on first inference)
    if app.config.get('AI_ENABLED', True):
        from app.ai.embedding_service import embedding_service
        embedding_service.initialize(app.config.get('AI_MODEL_NAME'), preload=False)

    # Import and register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.resume import resume_bp
    from app.routes.user import user_bp
    from app.routes.job import job_bp
    from app.routes.skill_gap import skill_gap_bp
    from app.routes.forecasting import forecasting_bp
    from app.routes.admin import admin_bp
    from app.routes.ai import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(job_bp, url_prefix='/api/jobs')
    app.register_blueprint(skill_gap_bp)
    app.register_blueprint(forecasting_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)

    # Base Health Check Routes (Root, /health, /api/health)
    @app.route('/', methods=['GET'])
    @app.route('/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from app.ai.embedding_service import embedding_service
        return jsonify({
            "success": True,
            "message": "Career Lens API is active",
            "service": "CareerLens Backend API",
            "data": {
                "status": "healthy",
                "database_connected": Database.is_connected(),
                "ai_available": embedding_service.is_available()
            }
        }), 200

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message": "Bad request",
            "error": str(error)
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "The requested API endpoint was not found",
            "error": "Endpoint not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "message": "HTTP method not allowed for this endpoint",
            "error": "Method not allowed"
        }), 405

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "success": False,
            "message": "File upload exceeds maximum 5 MB size limit",
            "error": "File size too large"
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "message": "An internal server error occurred",
            "error": str(error)
        }), 500

    return app
