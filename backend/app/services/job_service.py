import os
import csv
from app.models.job import JobModel
from app.services.extraction_service import ExtractionService

class JobService:
    """Service for loading, parsing, and caching dataset job profiles."""

    _jobs_cache = None

    @classmethod
    def get_all_jobs(cls):
        """
        Load all jobs from sample_jobs.csv or MongoDB jobs collection.
        Returns a list of clean structured job profiles.
        """
        if cls._jobs_cache is not None:
            return cls._jobs_cache

        jobs = []
        
        # 1. Attempt to load from MongoDB Atlas collection 'jobs' first
        coll = JobModel.get_collection()
        if coll is not None:
            try:
                db_jobs = list(coll.find({}))
                if db_jobs and len(db_jobs) >= 5:
                    for dj in db_jobs:
                        jobs.append(cls._format_job_dict(dj))
                    cls._jobs_cache = jobs
                    return jobs
            except Exception:
                pass

        # 2. Fallback to raw dataset CSV at backend/datasets/raw/sample_jobs.csv
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'raw', 'sample_jobs.csv')
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    jobs.append(cls._format_csv_row(row))
        
        cls._jobs_cache = jobs
        return jobs

    @classmethod
    def get_job_by_id(cls, job_id):
        """Retrieve a specific job profile by job_id (e.g. 'JOB001' or BSON ObjectId string)."""
        all_jobs = cls.get_all_jobs()
        job_id_str = str(job_id)

        for job in all_jobs:
            if str(job.get("job_id")) == job_id_str or str(job.get("id")) == job_id_str:
                return job
        return None

    @classmethod
    def find_verified_jobs(cls, target_role=None, keyword=None, location=None, country=None, is_remote=None, experience=None, limit=30, allow_general_fallback=False):
        """
        Query verified active jobs from MongoDB Atlas jobs collection.
        Uses RoleTaxonomy allowed patterns, title regex, and skill matching.
        Returns a list of clean, normalized job dictionaries ready for matching and ranking.
        """
        import re
        from app.services.role_taxonomy import RoleTaxonomy
        coll = JobModel.get_collection()
        if coll is None:
            return []

        search_term = (target_role or keyword or "").strip()
        query_parts = [{"is_live": True}]

        if search_term:
            tax_entry = RoleTaxonomy.ROLE_TAXONOMY.get(search_term)
            patterns = []
            if tax_entry and tax_entry.get("allowed_patterns"):
                patterns = tax_entry["allowed_patterns"][:6]
            else:
                tokens = [re.escape(t.strip()) for t in search_term.split() if len(t.strip()) > 2]
                if tokens:
                    patterns = [r"\b" + r"\s+".join(tokens) + r"\b"] + [r"\b" + t + r"\b" for t in tokens]

            if patterns:
                combined = "|".join(patterns)
                query_parts.append({
                    "$or": [
                        {"normalized_title": {"$regex": combined, "$options": "i"}},
                        {"title": {"$regex": combined, "$options": "i"}},
                        {"required_skills": {"$regex": combined, "$options": "i"}}
                    ]
                })

        if location and location.strip():
            loc_str = location.strip()
            query_parts.append({
                "$or": [
                    {"location": {"$regex": re.escape(loc_str), "$options": "i"}},
                    {"country": {"$regex": re.escape(loc_str), "$options": "i"}},
                    {"candidate_required_location": {"$regex": re.escape(loc_str), "$options": "i"}}
                ]
            })

        if is_remote is True:
            query_parts.append({
                "$or": [
                    {"workplace_type": "REMOTE"},
                    {"remote_type": "REMOTE"},
                    {"location": {"$regex": "remote", "$options": "i"}}
                ]
            })

        full_query = {"$and": query_parts} if len(query_parts) > 1 else query_parts[0]

        try:
            cursor = coll.find(full_query).limit(limit)
            raw_docs = list(cursor)

            # If exact query with location yielded 0, relax location to find general verified vacancies for the role
            if not raw_docs and location and search_term:
                relaxed_parts = [p for p in query_parts if "location" not in str(p) and "candidate_required_location" not in str(p)]
                relaxed_query = {"$and": relaxed_parts} if len(relaxed_parts) > 1 else (relaxed_parts[0] if relaxed_parts else {"is_live": True})
                cursor = coll.find(relaxed_query).limit(limit)
                raw_docs = list(cursor)

            # If still 0 and search_term is present, try tokenized matching on title
            if not raw_docs and search_term:
                tokens = [re.escape(t.strip()) for t in search_term.split() if len(t.strip()) > 2]
                if tokens:
                    token_query = {"is_live": True, "title": {"$regex": "|".join(tokens), "$options": "i"}}
                    cursor = coll.find(token_query).limit(limit)
                    raw_docs = list(cursor)

            # If still 0 and allow_general_fallback is requested, fallback to general verified live vacancies
            if not raw_docs and (allow_general_fallback or not search_term):
                cursor = coll.find({"is_live": True}).limit(limit)
                raw_docs = list(cursor)

            results = []
            for doc in raw_docs:
                formatted = cls._format_verified_db_job(doc)
                if formatted:
                    results.append(formatted)
            return results
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error querying verified database jobs: {e}")
            return []

    @classmethod
    def _format_verified_db_job(cls, doc):
        """Format a MongoDB job document into normalized structure matching live provider schema."""
        if not doc:
            return None
        doc_copy = dict(doc)
        doc_copy['_id'] = str(doc_copy.get('_id', ''))
        if not doc_copy.get('job_id'):
            doc_copy['job_id'] = f"JOB_{doc_copy['_id']}"
        if not doc_copy.get('title') and doc_copy.get('job_title'):
            doc_copy['title'] = doc_copy['job_title']
        doc_copy['company'] = (doc_copy.get('company') or doc_copy.get('company_name') or '').strip() or 'Verified Hiring Organization'

        clean_desc = doc_copy.get('clean_description') or doc_copy.get('description') or doc_copy.get('raw_description') or ''
        doc_copy['clean_description'] = clean_desc
        doc_copy['raw_description'] = doc_copy.get('raw_description') or clean_desc

        req_skills = doc_copy.get('required_skills') or []
        if isinstance(req_skills, str):
            req_skills = [s.strip() for s in req_skills.split('|') if s.strip()]
        if not req_skills and clean_desc:
            extracted = ExtractionService.extract_skills(clean_desc)
            req_skills = extracted.get('technical_skills', [])
        doc_copy['required_skills'] = req_skills
        doc_copy['preferred_skills'] = doc_copy.get('preferred_skills') or []

        workplace = doc_copy.get('workplace_type') or doc_copy.get('remote_type') or 'ON_SITE'
        loc = doc_copy.get('location', '')
        if 'remote' in loc.lower():
            workplace = 'REMOTE'
        doc_copy['workplace_type'] = workplace
        doc_copy['remote_type'] = workplace
        doc_copy['is_live'] = True
        doc_copy['status'] = 'LIVE'
        doc_copy['source_type'] = 'VERIFIED_DATABASE'
        doc_copy['source_name'] = doc_copy.get('source_name') or doc_copy.get('provider') or 'Verified Database Store'
        if not doc_copy.get('application_url'):
            doc_copy['application_url'] = doc_copy.get('source_url') or f"https://www.google.com/search?q={doc_copy.get('title')}+{doc_copy.get('company')}+jobs"
        return doc_copy

    @classmethod
    def _format_csv_row(cls, row):
        """Format a CSV row into a structured job profile with normalized skills."""
        raw_skills = [s.strip() for s in row.get("skills", "").split("|") if s.strip()]
        
        # Normalize skill names using skills dictionary
        aliases = ExtractionService.get_skills_dictionary().get("aliases", {})
        normalized_skills = []
        for sk in raw_skills:
            norm = aliases.get(sk.lower(), sk)
            if norm not in normalized_skills:
                normalized_skills.append(norm)

        # First 70% skills treated as required, remaining as preferred
        split_idx = max(1, int(len(normalized_skills) * 0.7)) if len(normalized_skills) > 1 else len(normalized_skills)
        required_skills = normalized_skills[:split_idx]
        preferred_skills = normalized_skills[split_idx:]

        return {
            "id": row.get("job_id"),
            "job_id": row.get("job_id"),
            "job_title": row.get("job_title"),
            "company": row.get("company"),
            "location": row.get("location"),
            "salary_min": int(row.get("salary_min", 0)),
            "salary_max": int(row.get("salary_max", 0)),
            "job_description": row.get("job_description", ""),
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "all_skills": normalized_skills,
            "experience_required": row.get("experience", "Fresher"),
            "education_required": "Bachelor's Degree / B.Tech / BCA",
            "job_role_category": row.get("job_title"),
            "industry": row.get("industry", "IT"),
            "posted_date": row.get("posted_date", "")
        }

    @classmethod
    def _format_job_dict(cls, doc):
        """Format a MongoDB job document into a structured job profile."""
        job_id = str(doc.get("_id", doc.get("job_id", "")))
        title = doc.get("title", doc.get("job_title", ""))
        skills = doc.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split("|") if s.strip()]

        aliases = ExtractionService.get_skills_dictionary().get("aliases", {})
        normalized = [aliases.get(s.lower(), s) for s in skills]

        split_idx = max(1, int(len(normalized) * 0.7)) if len(normalized) > 1 else len(normalized)

        return {
            "id": job_id,
            "job_id": job_id,
            "job_title": title,
            "company": doc.get("company", ""),
            "location": doc.get("location", ""),
            "salary_min": int(doc.get("salary_min", 0)),
            "salary_max": int(doc.get("salary_max", 0)),
            "job_description": doc.get("description", doc.get("job_description", "")),
            "required_skills": normalized[:split_idx],
            "preferred_skills": normalized[split_idx:],
            "all_skills": normalized,
            "experience_required": doc.get("experience_required", doc.get("experience", "Fresher")),
            "education_required": "Bachelor's Degree / B.Tech / BCA",
            "job_role_category": title,
            "industry": doc.get("industry", "IT"),
            "posted_date": str(doc.get("posted_date", ""))
        }
