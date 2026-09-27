from datetime import datetime
from bson import ObjectId
from app.db import get_collection

class SkillModel:
    """Skills Collection Model & Operations."""
    
    COLLECTION_NAME = 'skills'

    @staticmethod
    def get_collection():
        return get_collection(SkillModel.COLLECTION_NAME)

    @staticmethod
    def create_skill(name, category, description=""):
        """Create a master skill document."""
        coll = SkillModel.get_collection()
        now = datetime.utcnow()
        doc = {
            "name": name.strip(),
            "category": category,  # Programming, Database, Cloud, Data Science, Machine Learning, Web Development, Soft Skill, Tools
            "description": description,
            "created_at": now
        }
        if coll is not None:
            res = coll.insert_one(doc)
            doc["_id"] = res.inserted_id
        return doc

class UserSkillModel:
    """User Skills Junction Collection Model."""
    
    COLLECTION_NAME = 'user_skills'

    @staticmethod
    def get_collection():
        return get_collection(UserSkillModel.COLLECTION_NAME)

    @staticmethod
    def add_user_skill(user_id, skill_id, source="manual", proficiency="Intermediate"):
        """Associate a skill with a user."""
        coll = UserSkillModel.get_collection()
        now = datetime.utcnow()
        doc = {
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "skill_id": ObjectId(skill_id) if isinstance(skill_id, str) else skill_id,
            "source": source,  # resume, manual, assessment, ai
            "proficiency": proficiency,
            "created_at": now
        }
        if coll is not None:
            coll.insert_one(doc)
        return doc
