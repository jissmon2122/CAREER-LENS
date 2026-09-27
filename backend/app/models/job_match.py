from datetime import datetime
from bson import ObjectId
from app.db import get_collection

class JobMatchModel:
    """Job Match Collection Model & Operations with in-memory fallback."""

    COLLECTION_NAME = 'job_matches'
    _in_memory_matches = {}

    @staticmethod
    def get_collection():
        return get_collection(JobMatchModel.COLLECTION_NAME)

    @staticmethod
    def create_or_update_match(user_id, resume_id, job_id, match_data):
        """Create or update a job match document in MongoDB or in-memory fallback."""
        coll = JobMatchModel.get_collection()
        now = datetime.utcnow()

        user_obj_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        resume_obj_id = ObjectId(resume_id) if isinstance(resume_id, str) else resume_id

        doc = {
            "user_id": user_obj_id,
            "resume_id": resume_obj_id,
            "job_id": str(job_id),
            "match_score": match_data.get("match_score", 0),
            "match_category": match_data.get("match_category", "Moderate Match"),
            "matched_skills": match_data.get("matched_skills", []),
            "missing_required_skills": match_data.get("missing_required_skills", []),
            "missing_preferred_skills": match_data.get("missing_preferred_skills", []),
            "breakdown": match_data.get("breakdown", {}),
            "explainable_reasons": match_data.get("explainable_reasons", []),
            "algorithm_version": match_data.get("algorithm_version", "1.0"),
            "created_at": now
        }

        if coll is not None:
            coll.update_one(
                {"user_id": user_obj_id, "resume_id": resume_obj_id, "job_id": str(job_id)},
                {"$set": doc},
                upsert=True
            )
            return coll.find_one({"user_id": user_obj_id, "resume_id": resume_obj_id, "job_id": str(job_id)})
        else:
            match_key = f"{str(user_obj_id)}_{str(resume_obj_id)}_{str(job_id)}"
            doc["_id"] = ObjectId()
            JobMatchModel._in_memory_matches[match_key] = doc
            return doc

    @staticmethod
    def to_json(doc):
        """Format job match document into JSON dict response."""
        if not doc:
            return None
        return {
            "id": str(doc.get("_id", "")),
            "user_id": str(doc.get("user_id", "")),
            "resume_id": str(doc.get("resume_id", "")),
            "job_id": str(doc.get("job_id", "")),
            "match_score": doc.get("match_score", 0),
            "match_category": doc.get("match_category", "Moderate Match"),
            "matched_skills": doc.get("matched_skills", []),
            "missing_required_skills": doc.get("missing_required_skills", []),
            "missing_preferred_skills": doc.get("missing_preferred_skills", []),
            "breakdown": doc.get("breakdown", {}),
            "explainable_reasons": doc.get("explainable_reasons", []),
            "algorithm_version": doc.get("algorithm_version", "1.0"),
            "created_at": doc.get("created_at").isoformat() if isinstance(doc.get("created_at"), datetime) else str(doc.get("created_at", ""))
        }
