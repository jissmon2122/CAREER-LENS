import logging
from datetime import datetime, timezone
from app.db import Database
from app.config import Config
from app.services.job_cleaner import JobDescriptionCleaner
from app.services.extraction_service import ExtractionService
from app.ai.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class DeduplicationAndCacheEngine:
    """
    Multi-Level Deduplication Engine & Freshness Cache Manager.
    Deduplicates incoming provider listings and updates MongoDB 'jobs' collection
    with first_seen_at, last_seen_at, and last_verified_at timestamps.
    """

    STATUS_LIVE = "LIVE"
    STATUS_STALE = "STALE"
    STATUS_EXPIRED = "EXPIRED"
    STATUS_REMOVED = "REMOVED"
    STATUS_UNKNOWN = "UNKNOWN"

    @classmethod
    def process_and_cache_jobs(cls, provider_jobs: list) -> list:
        if not provider_jobs:
            return []

        db = Database.get_db()
        jobs_collection = db["jobs"]
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        ttl_seconds = Config.JOB_CACHE_TTL

        processed_jobs = []
        batch_url_to_id = {}
        batch_comp_title_loc_to_id = {}

        for raw_job in provider_jobs:
            provider = raw_job.get("provider", "unknown")
            provider_job_id = str(raw_job.get("provider_job_id", ""))
            title = raw_job.get("title", "").strip()
            company = raw_job.get("company", "").strip()
            location = raw_job.get("location", "").strip()
            raw_desc = raw_job.get("raw_description", "") or raw_job.get("description", "")

            # 1. HTML Cleaning Pipeline
            clean_desc = JobDescriptionCleaner.clean(raw_desc)

            # 2. Extract & Normalize Skills
            extracted_skills = ExtractionService.extract_skills(clean_desc)
            req_skills = raw_job.get("required_skills") or extracted_skills.get("technical_skills", [])
            pref_skills = raw_job.get("preferred_skills") or []

            # 3. Normalized Title & Company
            norm_title = title.lower().strip()
            norm_company = company.lower().strip()
            app_url = str(raw_job.get("application_url", "")).strip()

            # Level 1 Duplicate Check: provider + provider_job_id
            existing_doc = None
            if provider_job_id:
                existing_doc = jobs_collection.find_one({
                    "provider": provider,
                    "provider_job_id": provider_job_id
                })

            # Level 2 Duplicate Check: canonical application_url (DB or in-memory batch)
            if not existing_doc and app_url:
                if app_url in batch_url_to_id:
                    existing_doc = jobs_collection.find_one({"_id": batch_url_to_id[app_url]})
                else:
                    existing_doc = jobs_collection.find_one({"application_url": app_url})

            # Level 3 Duplicate Check: normalized_company + normalized_title + location (DB or in-memory batch)
            if not existing_doc and norm_company and norm_title:
                comp_key = (norm_company, norm_title, location)
                if comp_key in batch_comp_title_loc_to_id:
                    existing_doc = jobs_collection.find_one({"_id": batch_comp_title_loc_to_id[comp_key]})
                else:
                    existing_doc = jobs_collection.find_one({
                        "normalized_company": norm_company,
                        "normalized_title": norm_title,
                        "location": location
                    })

            # Determine workplace_type / remote_type cleanly
            raw_remote = str(raw_job.get("remote_type") or raw_job.get("workplace_type") or "").upper().strip()
            loc_lower = location.lower()
            cand_req_lower = str(raw_job.get("candidate_required_location", "")).lower()

            if provider == "remotive" or "remote" in loc_lower or "remote" in cand_req_lower or raw_job.get("is_remote") is True:
                if "hybrid" in loc_lower or "hybrid" in title.lower():
                    resolved_workplace = "HYBRID"
                else:
                    resolved_workplace = "REMOTE"
            elif raw_remote in ["REMOTE", "HYBRID", "ON_SITE"]:
                resolved_workplace = raw_remote
            elif "hybrid" in loc_lower:
                resolved_workplace = "HYBRID"
            elif loc_lower and "remote" not in loc_lower:
                resolved_workplace = "ON_SITE"
            else:
                resolved_workplace = "UNKNOWN"

            if existing_doc:
                # Update existing document (Level 1 or Level 2 matched)
                doc_id = existing_doc["_id"]
                
                # Embedding Reuse Check
                job_emb = existing_doc.get("job_embedding")
                if not job_emb and clean_desc and embedding_service.is_available():
                    job_emb = embedding_service.get_embedding(clean_desc)
                    if job_emb is not None:
                        job_emb = job_emb.tolist()

                update_fields = {
                    "last_seen_at": now_iso,
                    "last_verified_at": now_iso,
                    "status": cls.STATUS_LIVE,
                    "is_live": True,
                    "clean_description": clean_desc,
                    "required_skills": req_skills,
                    "preferred_skills": pref_skills,
                    "candidate_required_location": raw_job.get("candidate_required_location") or existing_doc.get("candidate_required_location"),
                    "application_url": raw_job.get("application_url") or existing_doc.get("application_url"),
                    "source_name": raw_job.get("source_name") or existing_doc.get("source_name"),
                    "remote_type": resolved_workplace,
                    "workplace_type": resolved_workplace,
                    "data_type": "LIVE"
                }
                if job_emb:
                    update_fields["job_embedding"] = job_emb
                    update_fields["embedding_model"] = Config.AI_MODEL_NAME
                    update_fields["embedding_version"] = 1

                jobs_collection.update_one({"_id": doc_id}, {"$set": update_fields})
                updated_job = jobs_collection.find_one({"_id": doc_id})
                if app_url:
                    batch_url_to_id[app_url] = doc_id
                if norm_company and norm_title:
                    batch_comp_title_loc_to_id[(norm_company, norm_title, location)] = doc_id
                processed_jobs.append(cls._format_job_output(updated_job))

            else:
                # Insert New Normalized Job Document
                job_emb = None
                if clean_desc and embedding_service.is_available():
                    emb_arr = embedding_service.get_embedding(clean_desc)
                    if emb_arr is not None:
                        job_emb = emb_arr.tolist()

                new_doc = {
                    "job_id": f"JOB_{provider}_{provider_job_id}" if provider_job_id else f"JOB_{now.strftime('%Y%m%d%H%M%S')}",
                    "provider": provider,
                    "provider_job_id": provider_job_id,
                    "title": title,
                    "normalized_title": norm_title,
                    "company": company,
                    "normalized_company": norm_company,
                    "raw_description": raw_desc,
                    "clean_description": clean_desc,
                    "location": location,
                    "candidate_required_location": raw_job.get("candidate_required_location", ""),
                    "country": raw_job.get("country", "IN"),
                    "city": raw_job.get("city", ""),
                    "remote_type": resolved_workplace,
                    "workplace_type": resolved_workplace,
                    "employment_type": raw_job.get("employment_type", "FULL_TIME"),
                    "experience_level": raw_job.get("experience_level", "0-2 Years"),
                    "salary_min": raw_job.get("salary_min"),
                    "salary_max": raw_job.get("salary_max"),
                    "salary_currency": raw_job.get("salary_currency", "INR"),
                    "required_skills": req_skills,
                    "preferred_skills": pref_skills,
                    "status": cls.STATUS_LIVE,
                    "is_live": True,
                    "first_seen_at": now_iso,
                    "last_seen_at": now_iso,
                    "last_verified_at": now_iso,
                    "posted_at": raw_job.get("posted_at") or now_iso,
                    "expires_at": raw_job.get("expires_at"),
                    "application_url": raw_job.get("application_url", ""),
                    "source_url": raw_job.get("source_url", ""),
                    "source_name": raw_job.get("source_name", "Live API Provider"),
                    "data_type": "LIVE",
                    "job_embedding": job_emb,
                    "embedding_model": Config.AI_MODEL_NAME if job_emb else None,
                    "embedding_version": 1 if job_emb else None
                }

                res = jobs_collection.insert_one(new_doc)
                new_doc["_id"] = res.inserted_id
                inserted_id = res.inserted_id
                if app_url:
                    batch_url_to_id[app_url] = inserted_id
                if norm_company and norm_title:
                    batch_comp_title_loc_to_id[(norm_company, norm_title, location)] = inserted_id
                processed_jobs.append(cls._format_job_output(new_doc))

        return processed_jobs

    @classmethod
    def _format_job_output(cls, doc: dict) -> dict:
        if not doc:
            return {}
        doc["_id"] = str(doc["_id"])
        # Do not expose raw vector array to frontend
        doc.pop("job_embedding", None)
        return doc
