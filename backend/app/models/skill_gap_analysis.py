from datetime import datetime
from bson import ObjectId
from app.db import get_collection

class SkillGapModel:
    """Skill Gap Collection Model & Persistence."""

    COLLECTION_NAME = 'skill_gaps'
    _in_memory_store = {}

    @staticmethod
    def get_collection():
        return get_collection(SkillGapModel.COLLECTION_NAME)

    @staticmethod
    def create_or_update_gap(data):
        coll = SkillGapModel.get_collection()
        now = datetime.utcnow()

        user_id_obj = ObjectId(data["user_id"]) if isinstance(data["user_id"], str) else data["user_id"]
        job_id_str = str(data["job_id"])

        doc = {
            "user_id": user_id_obj,
            "job_id": job_id_str,
            "required_coverage_percent": data.get("required_coverage_percent"),
            "skill_gap_percent": data.get("skill_gap_percent"),
            "matched_required_skills": data.get("matched_required_skills", []),
            "missing_required_skills": data.get("missing_required_skills", []),
            "matched_preferred_skills": data.get("matched_preferred_skills", []),
            "missing_preferred_skills": data.get("missing_preferred_skills", []),
            "prioritized_gaps": data.get("prioritized_gaps", []),
            "updated_at": now
        }

        if coll is not None:
            coll.update_one(
                {"user_id": user_id_obj, "job_id": job_id_str},
                {"$set": doc},
                upsert=True
            )
            return coll.find_one({"user_id": user_id_obj, "job_id": job_id_str})
        else:
            key = f"{user_id_obj}_{job_id_str}"
            doc["_id"] = ObjectId()
            SkillGapModel._in_memory_store[key] = doc
            return doc

    @staticmethod
    def to_json(doc):
        if not doc:
            return None
        return {
            "id": str(doc.get("_id", "")),
            "user_id": str(doc.get("user_id", "")),
            "job_id": str(doc.get("job_id", "")),
            "required_coverage_percent": doc.get("required_coverage_percent"),
            "skill_gap_percent": doc.get("skill_gap_percent"),
            "matched_required_skills": doc.get("matched_required_skills", []),
            "missing_required_skills": doc.get("missing_required_skills", []),
            "matched_preferred_skills": doc.get("matched_preferred_skills", []),
            "missing_preferred_skills": doc.get("missing_preferred_skills", []),
            "prioritized_gaps": doc.get("prioritized_gaps", []),
            "updated_at": str(doc.get("updated_at", ""))
        }
