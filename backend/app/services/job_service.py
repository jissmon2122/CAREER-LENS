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
