# Dataset Documentation

## 1. Dataset Overview
- **Dataset Name**: Synthetic Job Market Dataset (`sample_jobs.csv`)
- **Dataset Source**: Hand-curated synthetic job postings grounded in Indian & global tech hiring patterns (Chennai, Bengaluru, Hyderabad, Mumbai, Remote).
- **Location**: `backend/datasets/raw/sample_jobs.csv`
- **Record Count**: 30 comprehensive records
- **Purpose**: Base training/testing corpus for future NLP skill extraction, salary prediction model training, and job matching algorithms.

---

## 2. Schema Definition

| Field Name | Type | Description | Example |
|---|---|---|---|
| `job_id` | String | Unique job identifier | `JOB001` |
| `job_title` | String | Designation / role title | `Data Analyst` |
| `company` | String | Hiring company name | `TechMetrics Solutions` |
| `location` | String | Job city / location | `Chennai` |
| `salary_min` | Integer | Minimum annual salary (INR) | `500000` |
| `salary_max` | Integer | Maximum annual salary (INR) | `800000` |
| `job_description` | String | Comprehensive responsibility text | `Seeking a detail-oriented Data Analyst to...` |
| `skills` | String | Pipe-separated required skills | `Python|SQL|PowerBI|Excel|Data Visualization` |
| `experience` | String | Target experience level | `Fresher` |
| `industry` | String | Business sector | `Information Technology` |
| `posted_date` | Date | Posting date (YYYY-MM-DD) | `2026-08-01` |

---

## 3. Data Processing Roadmap (Future AI Modules)
- **NLP Tokenization & Skill Extraction**: Parse `job_description` and `skills` using TF-IDF / SpaCy NER models.
- **Salary Regression**: Train LightGBM / XGBoost models on `salary_min` & `salary_max` against required skills and experience.
- **Skill Demand Forecasting**: Perform time-series aggregation of skill occurrences over `posted_date`.
