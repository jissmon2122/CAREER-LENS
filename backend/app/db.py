import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import Config

logger = logging.getLogger(__name__)

class Database:
    """MongoDB connection manager utilizing PyMongo with instant fallback & automated indexing."""
    _client = None
    _db = None
    _initialized = False

    @classmethod
    def initialize(cls, app=None):
        """Initialize MongoDB client connection & automated collection indexing."""
        if cls._initialized:
            return

        cls._initialized = True
        mongo_uri = Config.MONGO_URI
        db_name = Config.DATABASE_NAME
        
        try:
            import threading
            client_options = {
                "serverSelectionTimeoutMS": 3000,
                "connectTimeoutMS": 3000,
                "socketTimeoutMS": 5000,
                "maxIdleTimeMS": 45000,
                "waitQueueTimeoutMS": 5000,
                "retryWrites": True,
                "retryReads": True,
            }
            if "mongodb+srv://" in mongo_uri or "ssl=true" in mongo_uri.lower() or "tls=true" in mongo_uri.lower():
                try:
                    import certifi
                    client_options["tlsCAFile"] = certifi.where()
                except Exception:
                    pass

            cls._client = MongoClient(mongo_uri, **client_options)
            cls._client.admin.command('ping')
            cls._db = cls._client[db_name]
            logger.info(f"Successfully connected to MongoDB: {db_name}")
            print(f"[OK] Connected to MongoDB ({db_name})")
            
            # Create automated database indexes in background to keep worker startup non-blocking
            threading.Thread(target=cls._create_indexes, daemon=True, name="DBIndexInitThread").start()
        except Exception as err:
            sanitized_host = mongo_uri.split('@')[-1].split('?')[0] if '@' in mongo_uri else mongo_uri.split('?')[0]
            logger.warning(f"MongoDB connection warning ({sanitized_host}): {err}. Running in in-memory mode.")
            print(f"[WARNING] MongoDB connection offline (host: {sanitized_host}). Using in-memory database fallback.")
            cls._client = None
            cls._db = False

    @classmethod
    def _create_indexes(cls):
        """Create database performance indexes safely."""
        if cls._db is None or cls._db is False:
            return
        try:
            cls._db['users'].create_index([("email", ASCENDING)], unique=True)
            cls._db['resumes'].create_index([("user_id", ASCENDING), ("is_active", DESCENDING)])
            cls._db['resume_analysis'].create_index([("resume_id", ASCENDING)], unique=True)
            cls._db['resume_analysis'].create_index([("user_id", ASCENDING)])
            cls._db['jobs'].create_index([("posted_at", DESCENDING)])
            cls._db['jobs'].create_index([("title", ASCENDING)])
            cls._db['skill_gaps'].create_index([("user_id", ASCENDING), ("job_id", ASCENDING)], unique=True)
            cls._db['learning_roadmaps'].create_index([("user_id", ASCENDING), ("job_id", ASCENDING)], unique=True)
            cls._db['skill_forecasts'].create_index([("skill", ASCENDING)], unique=True)
            cls._db['dataset_metadata'].create_index([("version", ASCENDING)], unique=True)
            print("[OK] Database indexes verified & created successfully.")
        except Exception as err:
            logger.warning(f"Index creation notice: {err}")

    @classmethod
    def get_db(cls):
        """Retrieve database instance."""
        if not cls._initialized:
            cls.initialize()
        if cls._db is False:
            return None
        return cls._db

    @classmethod
    def is_connected(cls):
        """Check if active MongoDB connection is available."""
        return cls.get_db() is not None

def get_collection(name):
    """Retrieve collection reference safely."""
    db = Database.get_db()
    if db is not None:
        return db[name]
    return None
