from datetime import datetime
from bson import ObjectId
from app.db import get_collection

class DatasetMetadataModel:
    """Job Dataset Ingestion Metadata Collection Model."""

    COLLECTION_NAME = 'dataset_metadata'
    _in_memory_store = {}

    @staticmethod
    def get_collection():
        return get_collection(DatasetMetadataModel.COLLECTION_NAME)

    @staticmethod
    def log_ingestion(data):
        coll = DatasetMetadataModel.get_collection()
        now = datetime.utcnow()

        version_str = data.get("version", "v1.0")

        doc = {
            "version": version_str,
            "source": data.get("source", "sample_jobs.csv"),
            "total_records": data.get("total_records", 0),
            "valid_jobs": data.get("valid_jobs", 0),
            "duplicate_count": data.get("duplicate_count", 0),
            "status": data.get("status", "SUCCESS"),
            "ingested_at": now
        }

        if coll is not None:
            coll.update_one(
                {"version": version_str},
                {"$set": doc},
                upsert=True
            )
            return coll.find_one({"version": version_str})
        else:
            doc["_id"] = ObjectId()
            DatasetMetadataModel._in_memory_store[version_str] = doc
            return doc

    @staticmethod
    def to_json(doc):
        if not doc:
            return None
        return {
            "id": str(doc.get("_id", "")),
            "version": doc.get("version"),
            "source": doc.get("source"),
            "total_records": doc.get("total_records"),
            "valid_jobs": doc.get("valid_jobs"),
            "duplicate_count": doc.get("duplicate_count"),
            "status": doc.get("status"),
            "ingested_at": str(doc.get("ingested_at", ""))
        }
