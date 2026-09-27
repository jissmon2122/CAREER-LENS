from datetime import datetime
from bson import ObjectId
from app.db import get_collection

class ResumeModel:
    """Resumes Collection Model & Operations with fallback in-memory store."""
    
    COLLECTION_NAME = 'resumes'
    _in_memory_resumes = []

    @staticmethod
    def get_collection():
        return get_collection(ResumeModel.COLLECTION_NAME)

    @staticmethod
    def create_resume(user_id, original_filename, stored_filename, file_path, file_type, file_size, file_data_base64=None):
        """Create a resume document in MongoDB or in-memory fallback."""
        coll = ResumeModel.get_collection()
        now = datetime.utcnow()
        user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        
        doc = {
            "user_id": user_obj_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_path": file_path,
            "file_type": file_type,
            "file_size": file_size,
            "file_data_base64": file_data_base64,
            "uploaded_at": now,
            "status": "uploaded"  # Statuses: uploaded -> processing -> processed / failed
        }
        
        if coll is not None:
            res = coll.insert_one(doc)
            doc["_id"] = res.inserted_id
        else:
            doc["_id"] = ObjectId()
            ResumeModel._in_memory_resumes.append(doc)

        return doc

    @staticmethod
    def find_by_user(user_id):
        """Retrieve all resumes owned by a specific user (User Data Isolation)."""
        user_id_str = str(user_id)
        coll = ResumeModel.get_collection()
        if coll is not None:
            try:
                user_obj_id = ObjectId(user_id_str)
                cursor = coll.find({"user_id": user_obj_id}).sort("uploaded_at", -1)
                return list(cursor)
            except Exception:
                return []
        
        # In-memory filter
        return [
            r for r in sorted(ResumeModel._in_memory_resumes, key=lambda x: x["uploaded_at"], reverse=True)
            if str(r.get("user_id")) == user_id_str
        ]

    @staticmethod
    def find_by_id_and_user(resume_id, user_id):
        """Find a specific resume owned by user."""
        resume_id_str = str(resume_id)
        user_id_str = str(user_id)
        coll = ResumeModel.get_collection()
        if coll is not None:
            try:
                r_id = ObjectId(resume_id_str)
                u_id = ObjectId(user_id_str)
                return coll.find_one({"_id": r_id, "user_id": u_id})
            except Exception:
                return None

        for r in ResumeModel._in_memory_resumes:
            if str(r.get("_id")) == resume_id_str and str(r.get("user_id")) == user_id_str:
                return r
        return None

    @staticmethod
    def to_json(doc):
        """Format resume MongoDB document to API response dict."""
        if not doc:
            return None
        return {
            "id": str(doc.get("_id", "")),
            "user_id": str(doc.get("user_id", "")),
            "original_filename": doc.get("original_filename", ""),
            "stored_filename": doc.get("stored_filename", ""),
            "file_path": doc.get("file_path", ""),
            "file_type": doc.get("file_type", ""),
            "file_size": doc.get("file_size", 0),
            "uploaded_at": doc.get("uploaded_at").isoformat() if isinstance(doc.get("uploaded_at"), datetime) else str(doc.get("uploaded_at", "")),
            "status": doc.get("status", "uploaded")
        }
