from datetime import datetime, timezone
from bson import ObjectId
from app.db import Database

class UserJobActionModel:
    """
    MongoDB persistence for Candidate Job Actions: SAVED, APPLIED, INTERVIEW, REJECTED, HIDDEN.
    Retains application history even when live jobs become EXPIRED or REMOVED.
    """

    COLLECTION_NAME = "user_job_actions"

    @classmethod
    def get_collection(cls):
        return Database.get_db()[cls.COLLECTION_NAME]

    @classmethod
    def record_action(cls, user_id: str, job_id: str, action: str, notes: str = "") -> dict:
        collection = cls.get_collection()
        now_iso = datetime.now(timezone.utc).isoformat()
        action_clean = action.upper().strip()

        doc = {
            "user_id": str(user_id),
            "job_id": str(job_id),
            "action": action_clean,
            "notes": notes,
            "created_at": now_iso,
            "updated_at": now_iso
        }

        collection.update_one(
            {"user_id": str(user_id), "job_id": str(job_id)},
            {"$set": doc},
            upsert=True
        )

        return doc

    @classmethod
    def get_user_actions(cls, user_id: str) -> list:
        collection = cls.get_collection()
        cursor = collection.find({"user_id": str(user_id)}).sort("updated_at", -1)
        actions = []
        for item in cursor:
            item["_id"] = str(item["_id"])
            actions.append(item)
        return actions
