from datetime import datetime
from bson import ObjectId
from app.db import get_collection

class ResumeAnalysisModel:
    """Resume Analysis Collection Model & Operations with in-memory fallback."""

    COLLECTION_NAME = 'resume_analysis'
    _in_memory_analyses = {}

    @staticmethod
    def get_collection():
        return get_collection(ResumeAnalysisModel.COLLECTION_NAME)

    @staticmethod
    def create_or_update_analysis(analysis_data):
        """Create or update a resume analysis document in MongoDB or in-memory fallback."""
        coll = ResumeAnalysisModel.get_collection()
        now = datetime.utcnow()

        resume_id_obj = ObjectId(analysis_data["resume_id"]) if isinstance(analysis_data["resume_id"], str) else analysis_data["resume_id"]
        user_id_obj = ObjectId(analysis_data["user_id"]) if isinstance(analysis_data["user_id"], str) else analysis_data["user_id"]

        doc = {
            "resume_id": resume_id_obj,
            "user_id": user_id_obj,
            "raw_text": analysis_data.get("raw_text", ""),
            "validation_status": analysis_data.get("validation_status", "VALID_RESUME"),
            "document_type": analysis_data.get("document_type", "RESUME"),
            "confidence": analysis_data.get("confidence", 1.0),
            "positive_signals": analysis_data.get("positive_signals", []),
            "negative_signals": analysis_data.get("negative_signals", []),
            "validation_reason": analysis_data.get("validation_reason", ""),
            "contact_information": analysis_data.get("contact_information", {}),
            "education": analysis_data.get("education", []),
            "technical_skills": analysis_data.get("technical_skills", []),
            "categorized_technical_skills": analysis_data.get("categorized_technical_skills", {}),
            "soft_skills": analysis_data.get("soft_skills", []),
            "projects": analysis_data.get("projects", []),
            "certifications": analysis_data.get("certifications", []),
            "internships": analysis_data.get("internships", []),
            "work_experience": analysis_data.get("work_experience", []),
            "sections_detected": analysis_data.get("sections_detected", []),
            "resume_score": analysis_data.get("resume_score"),
            "ats_score": analysis_data.get("ats_score"),
            "career_readiness_score": analysis_data.get("career_readiness_score"),
            "score_breakdown": analysis_data.get("score_breakdown"),
            "ats_score_breakdown": analysis_data.get("ats_score_breakdown"),
            "strengths": analysis_data.get("strengths", []),
            "improvements": analysis_data.get("improvements", []),
            "analysis_status": analysis_data.get("analysis_status", "completed"),
            "created_at": now,
            "updated_at": now
        }

        if coll is not None:
            # Upsert by resume_id
            coll.update_one(
                {"resume_id": resume_id_obj},
                {"$set": doc},
                upsert=True
            )
            updated_doc = coll.find_one({"resume_id": resume_id_obj})
            return updated_doc
        else:
            resume_id_str = str(resume_id_obj)
            doc["_id"] = ObjectId()
            ResumeAnalysisModel._in_memory_analyses[resume_id_str] = doc
            return doc

    @staticmethod
    def find_by_resume_id(resume_id):
        """Find analysis document by resume_id."""
        if not resume_id:
            return None
        resume_id_str = str(resume_id)
        coll = ResumeAnalysisModel.get_collection()

        if coll is not None:
            try:
                r_id = ObjectId(resume_id_str)
                return coll.find_one({"resume_id": r_id})
            except Exception:
                return None

        return ResumeAnalysisModel._in_memory_analyses.get(resume_id_str)

    @staticmethod
    def to_json(doc):
        """Format analysis document to JSON dictionary response."""
        if not doc:
            return None

        return {
            "id": str(doc.get("_id", "")),
            "resume_id": str(doc.get("resume_id", "")),
            "user_id": str(doc.get("user_id", "")),
            "raw_text": doc.get("raw_text", ""),
            "validation_status": doc.get("validation_status", "VALID_RESUME"),
            "document_type": doc.get("document_type", "RESUME"),
            "confidence": doc.get("confidence", 1.0),
            "positive_signals": doc.get("positive_signals", []),
            "negative_signals": doc.get("negative_signals", []),
            "validation_reason": doc.get("validation_reason", ""),
            "contact_information": doc.get("contact_information", {}),
            "education": doc.get("education", []),
            "technical_skills": doc.get("technical_skills", []),
            "categorized_technical_skills": doc.get("categorized_technical_skills", {}),
            "soft_skills": doc.get("soft_skills", []),
            "projects": doc.get("projects", []),
            "certifications": doc.get("certifications", []),
            "internships": doc.get("internships", []),
            "work_experience": doc.get("work_experience", []),
            "sections_detected": doc.get("sections_detected", []),
            "resume_score": doc.get("resume_score"),
            "ats_score": doc.get("ats_score"),
            "career_readiness_score": doc.get("career_readiness_score"),
            "score_breakdown": doc.get("score_breakdown"),
            "ats_score_breakdown": doc.get("ats_score_breakdown"),
            "strengths": doc.get("strengths", []),
            "improvements": doc.get("improvements", []),
            "analysis_status": doc.get("analysis_status", "completed"),
            "created_at": doc.get("created_at").isoformat() if isinstance(doc.get("created_at"), datetime) else str(doc.get("created_at", "")),
            "updated_at": doc.get("updated_at").isoformat() if isinstance(doc.get("updated_at"), datetime) else str(doc.get("updated_at", ""))
        }
