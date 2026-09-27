from datetime import datetime
from bson import ObjectId
from app.db import get_collection

class LearningRoadmapModel:
    """Learning Roadmap Collection Model & Persistence."""

    COLLECTION_NAME = 'learning_roadmaps'
    _in_memory_store = {}

    @staticmethod
    def get_collection():
        return get_collection(LearningRoadmapModel.COLLECTION_NAME)

    @staticmethod
    def create_or_update_roadmap(data):
        coll = LearningRoadmapModel.get_collection()
        now = datetime.utcnow()

        user_id_obj = ObjectId(data["user_id"]) if isinstance(data["user_id"], str) else data["user_id"]
        job_id_str = str(data["job_id"])

        doc = {
            "user_id": user_id_obj,
            "job_id": job_id_str,
            "roadmap_phases": data.get("roadmap_phases", []),
            "recommended_certifications": data.get("recommended_certifications", []),
            "match_improvement_simulation": data.get("match_improvement_simulation", []),
            "completed_skills": data.get("completed_skills", []),
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
            LearningRoadmapModel._in_memory_store[key] = doc
            return doc

    @staticmethod
    def to_json(doc):
        if not doc:
            return None
        return {
            "id": str(doc.get("_id", "")),
            "user_id": str(doc.get("user_id", "")),
            "job_id": str(doc.get("job_id", "")),
            "roadmap_phases": doc.get("roadmap_phases", []),
            "recommended_certifications": doc.get("recommended_certifications", []),
            "match_improvement_simulation": doc.get("match_improvement_simulation", []),
            "completed_skills": doc.get("completed_skills", []),
            "updated_at": str(doc.get("updated_at", ""))
        }
