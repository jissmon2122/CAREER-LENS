from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_collection

class UserModel:
    """User Collection Model & Operations with local and Google OAuth support."""
    
    COLLECTION_NAME = 'users'
    _in_memory_users = {}

    @staticmethod
    def get_collection():
        return get_collection(UserModel.COLLECTION_NAME)

    @staticmethod
    def create_user(data):
        """Hash password and insert local user into MongoDB or in-memory fallback."""
        coll = UserModel.get_collection()
        now = datetime.utcnow()
        email = data.get("email").lower().strip()
        
        user_doc = {
            "name": data.get("name"),
            "email": email,
            "password_hash": generate_password_hash(data.get("password")),
            "auth_provider": "local",
            "google_id": None,
            "profile_picture": None,
            "education": data.get("education", ""),
            "degree": data.get("degree", ""),
            "preferred_job_role": data.get("preferred_job_role", ""),
            "preferred_location": data.get("preferred_location", ""),
            "experience_level": data.get("experience_level", "Student"),
            "created_at": now,
            "updated_at": now
        }
        
        if coll is not None:
            result = coll.insert_one(user_doc)
            user_doc["_id"] = result.inserted_id
        else:
            obj_id = ObjectId()
            user_doc["_id"] = obj_id
            UserModel._in_memory_users[str(obj_id)] = user_doc
            UserModel._in_memory_users[email] = user_doc

        return user_doc

    @staticmethod
    def create_google_user(google_id, email, name, picture=None):
        """Create a user authenticated via Google OAuth."""
        coll = UserModel.get_collection()
        now = datetime.utcnow()
        clean_email = email.lower().strip()

        user_doc = {
            "name": name,
            "email": clean_email,
            "password_hash": None,
            "auth_provider": "google",
            "google_id": str(google_id),
            "profile_picture": picture,
            "education": "",
            "degree": "",
            "preferred_job_role": "",
            "preferred_location": "",
            "experience_level": "Fresher",
            "created_at": now,
            "updated_at": now
        }

        if coll is not None:
            result = coll.insert_one(user_doc)
            user_doc["_id"] = result.inserted_id
        else:
            obj_id = ObjectId()
            user_doc["_id"] = obj_id
            UserModel._in_memory_users[str(obj_id)] = user_doc
            UserModel._in_memory_users[clean_email] = user_doc
            UserModel._in_memory_users[f"google_{google_id}"] = user_doc

        return user_doc

    @staticmethod
    def link_google_account(user_id, google_id, picture=None):
        """Link or update Google OAuth info on an existing user account for seamless login."""
        user_id_str = str(user_id)
        now = datetime.utcnow()
        update_fields = {
            "google_id": str(google_id),
            "updated_at": now
        }
        if picture:
            update_fields["profile_picture"] = picture
        
        coll = UserModel.get_collection()
        if coll is not None:
            try:
                obj_id = ObjectId(user_id_str)
                coll.update_one({"_id": obj_id}, {"$set": update_fields})
                return coll.find_one({"_id": obj_id})
            except Exception:
                return None

        user_doc = UserModel._in_memory_users.get(user_id_str)
        if user_doc:
            user_doc.update(update_fields)
        return user_doc

    @staticmethod
    def find_by_email(email):
        """Find candidate by email address."""
        if not email:
            return None
        clean_email = email.lower().strip()
        coll = UserModel.get_collection()
        if coll is not None:
            return coll.find_one({"email": clean_email})
        return UserModel._in_memory_users.get(clean_email)

    @staticmethod
    def find_by_google_id(google_id):
        """Find candidate by Google OAuth sub ID."""
        if not google_id:
            return None
        gid_str = str(google_id)
        coll = UserModel.get_collection()
        if coll is not None:
            return coll.find_one({"google_id": gid_str})
        return UserModel._in_memory_users.get(f"google_{gid_str}")

    @staticmethod
    def find_by_id(user_id):
        """Find candidate by ObjectId string."""
        user_id_str = str(user_id)
        coll = UserModel.get_collection()
        if coll is not None:
            try:
                obj_id = ObjectId(user_id_str)
                return coll.find_one({"_id": obj_id})
            except Exception:
                return None
        return UserModel._in_memory_users.get(user_id_str)

    @staticmethod
    def update_profile(user_id, profile_data):
        """Update candidate profile fields (education, degree, role, location, experience)."""
        user_id_str = str(user_id)
        now = datetime.utcnow()

        update_fields = {
            "updated_at": now
        }
        allowed_keys = ['education', 'degree', 'preferred_job_role', 'preferred_location', 'experience_level', 'name']
        for key in allowed_keys:
            if key in profile_data:
                update_fields[key] = profile_data[key]

        coll = UserModel.get_collection()
        if coll is not None:
            try:
                obj_id = ObjectId(user_id_str)
                coll.update_one({"_id": obj_id}, {"$set": update_fields})
                return coll.find_one({"_id": obj_id})
            except Exception:
                return None
        
        user_doc = UserModel._in_memory_users.get(user_id_str)
        if user_doc:
            user_doc.update(update_fields)
        return user_doc

    @staticmethod
    def verify_password(stored_hash, password):
        """Verify plain password against stored hash."""
        if not stored_hash or not password:
            return False
        return check_password_hash(stored_hash, password)

    @staticmethod
    def to_json(user_doc):
        """Format MongoDB user document into JSON API dict."""
        if not user_doc:
            return None
        return {
            "id": str(user_doc.get("_id", "")),
            "name": user_doc.get("name", ""),
            "email": user_doc.get("email", ""),
            "auth_provider": user_doc.get("auth_provider", "local"),
            "google_id": user_doc.get("google_id"),
            "profile_picture": user_doc.get("profile_picture"),
            "education": user_doc.get("education", ""),
            "degree": user_doc.get("degree", ""),
            "preferred_job_role": user_doc.get("preferred_job_role", ""),
            "preferred_location": user_doc.get("preferred_location", ""),
            "experience_level": user_doc.get("experience_level", ""),
            "created_at": user_doc.get("created_at").isoformat() if isinstance(user_doc.get("created_at"), datetime) else str(user_doc.get("created_at", ""))
        }
