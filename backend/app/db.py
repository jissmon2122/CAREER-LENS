import logging
import time
import threading
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import Config

logger = logging.getLogger(__name__)

class Database:
    """MongoDB connection manager utilizing PyMongo with connection pooling, automated recovery & indexing."""
    _client = None
    _db = None
    _initialized = False
    _last_connect_attempt = 0
    _reconnect_cooldown = 5.0  # seconds between reconnect retries

    @classmethod
    def _build_client_options(cls, mongo_uri):
        client_options = {
            "serverSelectionTimeoutMS": 3000,
            "connectTimeoutMS": 3000,
            "socketTimeoutMS": 5000,
            "maxIdleTimeMS": 45000,
            "waitQueueTimeoutMS": 5000,
            "maxPoolSize": 25,
            "minPoolSize": 2,
            "retryWrites": True,
            "retryReads": True,
        }
        if "mongodb+srv://" in mongo_uri or "ssl=true" in mongo_uri.lower() or "tls=true" in mongo_uri.lower():
            try:
                import certifi
                client_options["tlsCAFile"] = certifi.where()
            except Exception:
                pass
        return client_options

    @classmethod
    def initialize(cls, app=None):
        """Initialize MongoDB client connection & automated collection indexing."""
        cls._last_connect_attempt = time.time()
        cls._initialized = True
        mongo_uri = Config.MONGO_URI
        db_name = Config.DATABASE_NAME
        
        try:
            client_options = cls._build_client_options(mongo_uri)
            client = MongoClient(mongo_uri, **client_options)
            client.admin.command('ping')
            cls._client = client
            cls._db = client[db_name]
            logger.info(f"Successfully connected to MongoDB: {db_name}")
            print(f"[OK] Connected to MongoDB ({db_name})")
            
            # Create automated database indexes in background to keep worker startup non-blocking
            threading.Thread(target=cls._create_indexes, daemon=True, name="DBIndexInitThread").start()
        except Exception as err:
            sanitized_host = mongo_uri.split('@')[-1].split('?')[0] if '@' in mongo_uri else mongo_uri.split('?')[0]
            logger.warning(f"MongoDB connection warning ({sanitized_host}): {err}. Running with graceful fallback.")
            print(f"[WARNING] MongoDB connection offline (host: {sanitized_host}). Graceful fallback active.")
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
        """Retrieve database instance with self-healing reconnection."""
        if not cls._initialized:
            cls.initialize()
            return cls._db if cls._db is not False else None

        # Self-healing: if client was disconnected, attempt reconnect after cooldown
        if cls._db is False or cls._client is None:
            now = time.time()
            if now - cls._last_connect_attempt >= cls._reconnect_cooldown:
                cls._last_connect_attempt = now
                try:
                    mongo_uri = Config.MONGO_URI
                    db_name = Config.DATABASE_NAME
                    client_options = cls._build_client_options(mongo_uri)
                    client = MongoClient(mongo_uri, **client_options)
                    client.admin.command('ping')
                    cls._client = client
                    cls._db = client[db_name]
                    logger.info("Successfully recovered connection to MongoDB.")
                    threading.Thread(target=cls._create_indexes, daemon=True, name="DBIndexInitThread").start()
                except Exception as e:
                    logger.debug(f"MongoDB reconnection attempt failed: {e}")
                    cls._client = None
                    cls._db = False

        if cls._db is False:
            return None
        return cls._db

    @classmethod
    def is_connected(cls):
        """Check if active MongoDB connection is available."""
        return cls.get_db() is not None

    @classmethod
    def ping(cls):
        """Perform an active connectivity ping to the database."""
        db = cls.get_db()
        if db is None or cls._client is None:
            return False
        try:
            cls._client.admin.command('ping')
            return True
        except Exception:
            return False

def get_collection(name):
    """Retrieve collection reference safely."""
    db = Database.get_db()
    if db is not None:
        return db[name]
    return None
