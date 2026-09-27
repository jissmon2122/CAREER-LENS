# CareerLens — Production Deployment Guide

## Overview
**CareerLens** is an AI-Powered Skill Demand Forecasting and Career Intelligence Platform built with a React (Vite) frontend and a Python (Flask) backend API, utilizing MongoDB Atlas for data persistence, live Adzuna REST API for global job matching, PyMuPDF & RapidOCR for multi-stage resume extraction, and `sentence-transformers` for 60/40 deterministic + semantic hybrid matching.

---

## Technical Stack & Dependencies
- **Frontend**: React 18, Vite, Axios, React Router v6, `@react-oauth/google`
- **Backend**: Python 3.12, Flask 3.x, Gunicorn, Flask-CORS, PyJWT
- **Database**: MongoDB Atlas (Cloud) / MongoDB 4.4+ (Local)
- **Live Job Data**: Adzuna REST API (`https://api.adzuna.com/v1/api/jobs`)
- **Resume Parsing & OCR**: PyMuPDF (`fitz`), `pdfplumber`, RapidOCR ONNX Engine
- **AI & NLP**: spaCy (`en_core_web_sm`), `sentence-transformers` (`all-MiniLM-L6-v2`), scikit-learn

---

## Environment Variables Required

### Backend Environment Variables (`backend/.env`)
```env
FLASK_ENV=production
FLASK_APP=wsgi.py
PORT=5000
SECRET_KEY=
JWT_SECRET_KEY=
JWT_EXPIRATION_HOURS=24
MONGO_URI=
DATABASE_NAME=career_intelligence
UPLOAD_FOLDER=uploads/resumes
MAX_FILE_SIZE=5242880
GOOGLE_CLIENT_ID=

# Production CORS Settings
FRONTEND_URL=
CORS_ORIGINS=

# Live Job API Providers (Adzuna)
JOB_API_PROVIDERS=adzuna,jooble,indianapi
LIVE_JOB_CACHE_TTL=21600
LIVE_JOB_MAX_AGE_DAYS=30

ADZUNA_ENABLED=true
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
ADZUNA_COUNTRY=in
ADZUNA_BASE_URL=https://api.adzuna.com/v1/api/jobs
ADZUNA_RESULTS_PER_PAGE=50
ADZUNA_MAX_PAGES=2
ADZUNA_TIMEOUT=10
```

### Frontend Environment Variables (`frontend/.env`)
```env
VITE_API_BASE_URL=https://<your-backend-api-domain>/api
VITE_GOOGLE_CLIENT_ID=
```

> ⚠️ **SECURITY WARNING**: Never commit `.env` files or secrets to Git. Always pass secrets securely via your deployment platform's dashboard.

---

## Local Development Setup

### Backend Setup:
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
python run.py
```
*(Backend runs at: `http://127.0.0.1:5000`)*

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```
*(Frontend runs at: `http://localhost:5173`)*

---

## Production Deployment Options

### Option 1: Render.com (Recommended Blueprint)
This repository includes a `render.yaml` blueprint for one-click deployment:
1. Connect your repository to Render.
2. Click **New +** → **Blueprint**.
3. Select `render.yaml`.
4. Supply environment variables (`MONGO_URI`, `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`).

### Option 2: Docker / Docker Compose
Build and run the entire stack with Docker Compose:
```bash
docker compose up --build -d
```
- Frontend: `http://localhost:80`
- Backend API: `http://localhost:5000/api`

### Option 3: Separate Frontend (Vercel/Netlify) & Backend (Render/Railway/GCP)
1. **Frontend on Vercel**:
   - Framework preset: Vite
   - Root Directory: `frontend`
   - Build command: `npm run build`
   - Output directory: `dist`
   - Set environment variable `VITE_API_BASE_URL` to your live backend API URL.
2. **Backend on Render/Railway/GCP Cloud Run**:
   - Root Directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`

---

## Health Check Endpoint
To check if the API is active and healthy:
```http
GET /api/health
```
Response:
```json
{
  "success": true,
  "message": "Career Lens API is active",
  "data": {
    "status": "healthy",
    "database_connected": true,
    "ai_available": true
  }
}
```
