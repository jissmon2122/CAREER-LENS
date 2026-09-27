# API Endpoint Documentation

Base URL: `http://localhost:5000/api`

---

## 1. Authentication Endpoints (`/auth`)

### `POST /api/auth/register`
Creates a new candidate user account.

**Request Header:** `Content-Type: application/json`

**Request Body:**
```json
{
  "name": "Rahul Sharma",
  "email": "rahul.sharma@example.com",
  "password": "Password123",
  "confirm_password": "Password123",
  "education": "B.Tech / B.E.",
  "degree": "Computer Science and Engineering",
  "preferred_job_role": "Data Analyst",
  "preferred_location": "Chennai",
  "experience_level": "Fresher"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "64d1f2a1e8a9b123456789ab",
      "name": "Rahul Sharma",
      "email": "rahul.sharma@example.com",
      "education": "B.Tech / B.E.",
      "degree": "Computer Science and Engineering",
      "preferred_job_role": "Data Analyst",
      "preferred_location": "Chennai",
      "experience_level": "Fresher"
    }
  }
}
```

---

### `POST /api/auth/login`
Authenticates candidate credentials and issues a JWT token.

**Request Header:** `Content-Type: application/json`

**Request Body:**
```json
{
  "email": "rahul.sharma@example.com",
  "password": "Password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "64d1f2a1e8a9b123456789ab",
      "name": "Rahul Sharma",
      "email": "rahul.sharma@example.com",
      "preferred_job_role": "Data Analyst"
    }
  }
}
```

---

### `GET /api/auth/me`
Retrieves current authenticated candidate profile.

**Request Header:** `Authorization: Bearer <JWT_TOKEN>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User profile fetched successfully",
  "data": {
    "user": {
      "id": "64d1f2a1e8a9b123456789ab",
      "name": "Rahul Sharma",
      "email": "rahul.sharma@example.com",
      "education": "B.Tech / B.E.",
      "degree": "Computer Science and Engineering",
      "preferred_job_role": "Data Analyst",
      "preferred_location": "Chennai",
      "experience_level": "Fresher"
    }
  }
}
```

---

## 2. Resume Endpoints (`/resume`)

### `POST /api/resume/upload`
Uploads a PDF resume file for the authenticated candidate.

**Request Header:** 
- `Authorization: Bearer <JWT_TOKEN>`
- `Content-Type: multipart/form-data`

**Form Body:**
- `resume`: PDF file (Max 5 MB)

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Resume uploaded successfully",
  "data": {
    "resume": {
      "id": "64d1f2b5e8a9b123456789ac",
      "filename": "Rahul_Resume.pdf",
      "size": 1843200,
      "uploaded_at": "2026-08-13T10:00:00.000Z",
      "status": "uploaded"
    }
  }
}
```

---

### `GET /api/resume/my-resumes`
Retrieves all uploaded resumes for the authenticated user (enforcing user data isolation).

**Request Header:** `Authorization: Bearer <JWT_TOKEN>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Resumes retrieved successfully",
  "data": {
    "resumes": [
      {
        "id": "64d1f2b5e8a9b123456789ac",
        "original_filename": "Rahul_Resume.pdf",
        "stored_filename": "64d1f2a1e8a9b123456789ab_1723552800_Rahul_Resume.pdf",
        "file_size": 1843200,
        "uploaded_at": "2026-08-13T10:00:00.000Z",
        "status": "uploaded"
      }
    ]
  }
}
```

---

### `GET /api/resume/<resume_id>`
Retrieves single resume metadata owned by the authenticated user.

**Request Header:** `Authorization: Bearer <JWT_TOKEN>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Resume metadata retrieved",
  "data": {
    "resume": {
      "id": "64d1f2b5e8a9b123456789ac",
      "original_filename": "Rahul_Resume.pdf",
      "file_size": 1843200,
      "uploaded_at": "2026-08-13T10:00:00.000Z",
      "status": "uploaded"
    }
  }
}
```
