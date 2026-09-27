# Database Schema Documentation

## Database System
**MongoDB** (NoSQL Document Store)  
Database Name: `career_intelligence`

---

## 1. `users` Collection

Stores candidate account and profile information.

```json
{
  "_id": ObjectId("64d1f2a1e8a9b123456789ab"),
  "name": "Rahul Sharma",
  "email": "rahul.sharma@example.com",
  "password_hash": "scrypt:32768:8:1$w7X...$...",
  "education": "B.Tech / B.E.",
  "degree": "Computer Science and Engineering",
  "preferred_job_role": "Data Analyst",
  "preferred_location": "Chennai",
  "experience_level": "Fresher",
  "created_at": ISODate("2026-08-13T10:00:00.000Z"),
  "updated_at": ISODate("2026-08-13T10:00:00.000Z")
}
```

---

## 2. `resumes` Collection

Stores uploaded PDF resume metadata and file storage references.

```json
{
  "_id": ObjectId("64d1f2b5e8a9b123456789ac"),
  "user_id": ObjectId("64d1f2a1e8a9b123456789ab"),
  "original_filename": "Rahul_Resume.pdf",
  "stored_filename": "64d1f2a1e8a9b123456789ab_1723552800_Rahul_Resume.pdf",
  "file_path": "uploads/resumes/64d1f2a1e8a9b123456789ab_1723552800_Rahul_Resume.pdf",
  "file_type": "application/pdf",
  "file_size": 1843200,
  "uploaded_at": ISODate("2026-08-13T10:00:00.000Z"),
  "status": "uploaded"
}
```

*Note: Status lifecycle for future modules: `uploaded` → `processing` → `processed` | `failed`.*

---

## 3. `skills` Collection

Master taxonomy of technical and soft skills.

```json
{
  "_id": ObjectId("64d1f2c9e8a9b123456789ad"),
  "name": "Python",
  "category": "Programming",
  "description": "High-level object-oriented programming language widely used in data analytics and ML",
  "created_at": ISODate("2026-08-13T10:00:00.000Z")
}
```

---

## 4. `user_skills` Collection

Junction collection linking candidate users to identified skills (ready for future NLP extraction).

```json
{
  "_id": ObjectId("64d1f2dce8a9b123456789ae"),
  "user_id": ObjectId("64d1f2a1e8a9b123456789ab"),
  "skill_id": ObjectId("64d1f2c9e8a9b123456789ad"),
  "source": "manual",
  "proficiency": "Intermediate",
  "created_at": ISODate("2026-08-13T10:00:00.000Z")
}
```

---

## 5. `jobs` Collection

Stores job postings for market analysis and matching.

```json
{
  "_id": ObjectId("64d1f2eee8a9b123456789af"),
  "title": "Data Analyst",
  "company": "TechMetrics Solutions",
  "location": "Chennai",
  "description": "Analyze complex datasets, construct dashboards using SQL and PowerBI...",
  "salary_min": 500000,
  "salary_max": 800000,
  "experience_required": "Fresher",
  "industry": "IT",
  "source": "dataset",
  "posted_date": "2026-08-01",
  "created_at": ISODate("2026-08-13T10:00:00.000Z")
}
```

---

## 6. `job_skills` Collection

Links jobs to required or preferred skills for job-matching algorithms.

```json
{
  "_id": ObjectId("64d1f301e8a9b123456789b0"),
  "job_id": ObjectId("64d1f2eee8a9b123456789af"),
  "skill_id": ObjectId("64d1f2c9e8a9b123456789ad"),
  "importance": "required"
}
```
