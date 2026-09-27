from datetime import datetime
from bson import ObjectId
from app.db import get_collection

class JobModel:
    """Jobs Collection Model & Schema Helper."""
    
    COLLECTION_NAME = 'jobs'

    @staticmethod
    def get_collection():
        return get_collection(JobModel.COLLECTION_NAME)

    @staticmethod
    def create_job(data):
        """Create a job document in MongoDB."""
        coll = JobModel.get_collection()
        now = datetime.utcnow()
        doc = {
            "title": data.get("title"),
            "company": data.get("company"),
            "location": data.get("location"),
            "description": data.get("description", ""),
            "salary_min": data.get("salary_min", 0),
            "salary_max": data.get("salary_max", 0),
            "experience_required": data.get("experience_required", "Fresher"),
            "industry": data.get("industry", "IT"),
            "source": data.get("source", "dataset"),
            "posted_date": data.get("posted_date", now.strftime("%Y-%m-%d")),
            "created_at": now
        }
        if coll is not None:
            res = coll.insert_one(doc)
            doc["_id"] = res.inserted_id
        return doc

class JobSkillModel:
    """Job Skills Junction Collection Model."""
    
    COLLECTION_NAME = 'job_skills'

    @staticmethod
    def get_collection():
        return get_collection(JobSkillModel.COLLECTION_NAME)

    @staticmethod
    def link_job_skill(job_id, skill_id, importance="required"):
        """Link a skill to a job with importance rating."""
        coll = JobSkillModel.get_collection()
        doc = {
            "job_id": ObjectId(job_id) if isinstance(job_id, str) else job_id,
            "skill_id": ObjectId(skill_id) if isinstance(skill_id, str) else skill_id,
            "importance": importance  # 'required', 'preferred', 'optional'
        }
        if coll is not None:
            coll.insert_one(doc)
        return doc
