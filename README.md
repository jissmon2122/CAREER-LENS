# 🌟 CAREER LENS PLATFORM
## AI-Powered Skill Demand Forecasting and Career Intelligence Platform

A complete, production-hardened career intelligence platform that provides an end-to-end explainable workflow from candidate registration, PDF resume extraction, strict document validation, deterministic resume quality & ATS scoring, real job dataset matching, skill-gap analysis, personalized learning roadmaps, verified resources, match improvement simulations, to historical skill-demand analysis and time-series forecasting.

---

## 📐 System Architecture & End-to-End Workflow

```text
User Registration / Login / Google OAuth
                   │
                   ▼
             Resume Upload
                   │
                   ▼
     Strict Resume Validation (ResumeValidator)
        ├── If Invalid (Paper/Invoice/Scanned) ➔ STOP Processing (Scores = null, Match Blocked)
        └── If Valid Resume ➔ PDF PyMuPDF Text Extraction & Section Parsing
                   │
                   ▼
Skill Extraction (Regex Word Boundaries & Alias Normalization)
                   │
                   ▼
Deterministic Resume Scoring (Quality 0-100 & ATS 0-100)
                   │
                   ▼
Resume-to-Job Matching (6-Component Weighted Engine)
                   │
                   ▼
Skill Gap Analysis (Required Coverage % & Priority Tiers)
                   │
                   ▼
Personalized Learning Roadmap & Industry Certifications
                   │
                   ▼
Match Improvement Simulator (Hypothetical Match Score Comparison)
                   │
                   ▼
Time-Series Skill Demand Forecasting (Naive, Moving Avg, Linear, Exp Smoothing + MAE/RMSE)
                   │
                   ▼
Interactive Candidate Intelligence Dashboard
```

---

## 🛠️ Methodologies & Formulas

### 1. Resume Quality Scoring Formula (0 – 100)
Evaluated deterministically across 6 components:
- **Contact Information (15%)**: Email, phone, online profile URL.
- **Education (20%)**: Degree keywords, university name, completion year.
- **Technical Skills (25%)**: Categorized technical skill count & coverage.
- **Projects (15%)**: Academic & personal project descriptions.
- **Certifications (10%)**: Recognized industry credentials.
- **Work Experience / Internships (15%)**: Work history & internship entries.

`Resume Quality Score = Sum of 6 Component Scores`

### 2. ATS Compatibility Scoring Formula (0 – 100)
Evaluated across 5 ATS formatting components:
- **PDF Parsing Validity (20%)**: Text readability & structural integrity.
- **Text Readability (20%)**: Character density & word structure.
- **Standard Headings (25%)**: Standard ATS section headings (Education, Skills, Experience, Projects).
- **Technical Skill Keywords (20%)**: Match density of standard industry skill keywords.
- **Contact Details (15%)**: Standard header contact placement.

### 3. Resume-to-Job Matching Formula (6 Components)
- **Required Skill Match (40%)**: `(Matched Required Skills / Total Required Skills) * 40`
- **Preferred Skill Match (10%)**: `(Matched Preferred Skills / Total Preferred Skills) * 10`
- **Experience Level Match (15%)**: Match between candidate level & job level.
- **Education Match (10%)**: Degree & field compatibility.
- **Role Match (15%)**: Preferred role vs. job title similarity.
- **Location Match (10%)**: City, country, and remote/hybrid/on-site compatibility.

`Total Job Match Score = Sum of 6 Component Scores`

### 4. Skill Gap Analysis Formula
- **Required Skill Coverage (%)** = `(Matched Required Skills / Total Required Skills) * 100`
- **Required Skill Gap (%)** = `100 - Required Skill Coverage (%)`
- **Priority Tiers**:
  - 🔴 **CRITICAL**: Missing required skill present in target job + high market demand.
  - 🟠 **HIGH**: Missing required skill in target job.
  - 🟡 **MEDIUM**: Missing preferred skill.
  - 🟢 **LOW**: Optional skill.

### 5. Time-Series Forecasting Models & Evaluation
Evaluates 4 algorithms across chronological validation splits:
1. **Baseline Naive Model**: `y_hat_t+h = y_t`
2. **Moving Average Model**: `y_hat_t+h = mean(y_t-k..y_t)`
3. **Linear Trend Model**: Ordinary Least Squares (OLS) linear trend line.
4. **Exponential Smoothing Model**: Holt's linear exponential smoothing model.

`MAE (Mean Absolute Error) = mean(|y_actual - y_pred|)`  
`RMSE (Root Mean Squared Error) = sqrt(mean((y_actual - y_pred)^2))`

---

## 🔌 REST API Directory

| Endpoint | Method | Auth | Purpose |
| :--- | :--- | :--- | :--- |
| `/api/health` | `GET` | Public | API Health & Database Status |
| `/api/auth/register` | `POST` | Public | Candidate Registration |
| `/api/auth/login` | `POST` | Public | Candidate JWT Login |
| `/api/auth/google` | `POST` | Public | Google OAuth Sign-In |
| `/api/user/profile` | `GET/PUT` | Bearer | Get/Update Candidate Profile |
| `/api/resume/upload` | `POST` | Bearer | Upload PDF Resume |
| `/api/resume/my-resumes` | `GET` | Bearer | Get Uploaded Resumes |
| `/api/resume/analyze/<id>` | `POST` | Bearer | Trigger Full Resume Pipeline |
| `/api/jobs/recommended` | `GET` | Bearer | Top 10 Job Matches |
| `/api/jobs/<id>/match` | `GET` | Bearer | 6-Component Match Reasons |
| `/api/jobs/simulate-match` | `POST` | Bearer | Hypothetical Match Simulator |
| `/api/skills/gap/<job_id>` | `GET` | Bearer | Calculate Skill Gap |
| `/api/skills/roadmap/<job_id>`| `GET` | Bearer | Personalized Learning Roadmap |
| `/api/skills/acquire` | `POST` | Bearer | Mark Skill Acquired |
| `/api/forecasting/top-skills` | `GET` | Public | Top Rising/Stable/Emerging |
| `/api/forecasting/skill/<name>`| `GET` | Public | Specific Skill Forecast |
| `/api/forecasting/recommendations` | `GET` | Bearer | Personalized Future Skills |
| `/api/admin/system-health` | `GET` | Public | System Administration Status |
| `/api/admin/datasets/ingest` | `POST` | Bearer | Ingest Job Dataset |
| `/api/admin/forecast/train` | `POST` | Bearer | Train Time-Series Models |

---

## 🛠️ Local Setup & Commands

### 1. Backend Server Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### 2. Frontend Development Setup
```powershell
cd frontend
npm install
npm run dev
```

### 3. Automated Test Suite Execution
```powershell
cd backend
.\venv\Scripts\python.exe test_backend.py
```

### 4. Production Build Verification
```powershell
cd frontend
npm run build
```
