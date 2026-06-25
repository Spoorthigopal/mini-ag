# STU-MINI API Documentation

Welcome to the STU-MINI Backend API reference. The backend service is built with FastAPI, PostgreSQL, Pinecone, and LangChain. 

## 🔐 Authentication & Headers

Most API endpoints require a JWT token passed in the `Authorization` header.

```http
Authorization: Bearer <JWT_TOKEN>
```

Admin-only endpoints require the `X-API-Key` header:
```http
X-API-Key: <ADMIN_API_KEY>
```

---

## 📁 Auth Module

### 1. Register User
Register a new student account.

- **URL:** `/api/auth/register`
- **Method:** `POST`
- **Authentication:** None
- **Request Body:**
  ```json
  {
    "email": "student@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "student@example.com",
      "role": "student",
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
  ```

- **cURL Example:**
  ```bash
  curl -X POST http://localhost:8000/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email": "student@example.com", "password": "SecurePassword123"}'
  ```

### 2. Login User
Authenticate credentials and obtain a JWT access token.

- **URL:** `/api/auth/login`
- **Method:** `POST`
- **Authentication:** None
- **Request Body:**
  ```json
  {
    "email": "student@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response (200 OK):** Same as Register User.

- **cURL Example:**
  ```bash
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "student@example.com", "password": "SecurePassword123"}'
  ```

---

## 🌾 Welfare Module (Scholarships & Schemes)

### 1. List Welfare Schemes
Retrieve a list of available welfare schemes with optional filters.

- **URL:** `/api/welfare/schemes`
- **Method:** `GET`
- **Authentication:** Required (Bearer Token)
- **Query Parameters:**
  - `scheme_type` (string, optional) - Scholarship, Fellowship, Grant
  - `amount_min` (float, optional) - Minimum amount limit
  - `amount_max` (float, optional) - Maximum amount limit
  - `provider` (string, optional) - Provider name search
  - `status` (string, optional) - active, inactive
- **Response (200 OK):**
  ```json
  [
    {
      "id": "scheme-uuid-here",
      "name": "National Scholarship Portal (NSP)",
      "description": "Central government scholarship...",
      "scheme_type": "Scholarship",
      "amount": 50000.0,
      "provider": "Ministry of Education",
      "application_deadline": "October 31",
      "application_url": "https://scholarships.gov.in",
      "contact_email": "helpdesk@nsp.gov.in",
      "benefits": ["Tuition fee reimbursement", "Maintenance allowance"],
      "documents_required": ["Aadhar Card", "Income Certificate"],
      "processing_time": "45-60 days",
      "scheme_status": "active"
    }
  ]
  ```

### 2. Chat with Welfare RAG Bot
Ask questions about scholarship eligibilities and criteria. Powered by Pinecone vector search + Gemini.

- **URL:** `/api/welfare/chat`
- **Method:** `POST`
- **Authentication:** Required (Bearer Token)
- **Request Body:**
  ```json
  {
    "user_query": "What scholarships are available for girl students with income below 8 LPA?",
    "filters": {
      "scheme_type": "Scholarship"
    },
    "session_id": "optional-session-id"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "bot_response": "Based on your search, the AICTE Pragati Scholarship for Girls is available...",
    "retrieved_schemes": [
      {
        "id": "scheme-uuid",
        "name": "AICTE Pragati Scholarship for Girls",
        "amount": 50000.0
      }
    ],
    "session_id": "session-uuid"
  }
  ```

---

## 💼 Internship Module

### 1. List Internship Jobs
Retrieve paginated internship jobs.

- **URL:** `/api/internships/jobs`
- **Method:** `GET`
- **Authentication:** Required (Bearer Token)
- **Query Parameters:**
  - `company_name` (string, optional)
  - `location` (string, optional)
  - `stipend_min` (float, optional)
  - `job_type` (string, optional) - internship, full-time
  - `page` (int, default=1)
  - `limit` (int, default=10)
- **Response (200 OK):** Array of job listings.

### 2. Parse & Upload Resume
Extract skills and experience from a PDF resume.

- **URL:** `/api/internships/upload-resume`
- **Method:** `POST`
- **Authentication:** Required (Bearer Token)
- **Request (Multipart Form):**
  - `file`: (binary PDF file)
- **Response (200 OK):**
  ```json
  {
    "filename": "my_resume.pdf",
    "extracted_skills": ["Python", "React", "SQL", "Git"],
    "extracted_experience": "Software development student...",
    "parsed_successfully": true
  }
  ```

### 3. Chat with Internship Coach
Obtain personalized internship suggestions using resume context.

- **URL:** `/api/internships/chat`
- **Method:** `POST`
- **Authentication:** Required (Bearer Token)
- **Request Body:**
  ```json
  {
    "user_query": "Which jobs match my python skills?",
    "resume_text": "Optionally pass custom resume summary..."
  }
  ```
- **Response (200 OK):** Returns career recommendations and matching job IDs.

### 4. JSearch API Sync (Admin-only)
Manually trigger job scraper ingestion.

- **URL:** `/api/internships/sync`
- **Method:** `POST`
- **Headers:** `X-API-Key: <ADMIN_API_KEY>`
- **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Successfully synchronized jobs list from JSearch API."
  }
  ```

---

## 🎙 AI Interview Coach

### 1. Start Interview Session
Initiate a mock interview session tailored to an internship/job description.

- **URL:** `/api/interview/start`
- **Method:** `POST`
- **Authentication:** Required (Bearer Token)
- **Request Body:**
  ```json
  {
    "job_id": "internship-job-uuid-here"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "session_id": "session-uuid-here",
    "message": "Interview session started successfully.",
    "question": "Question 1: Can you explain your experience building REST APIs with React?"
  }
  ```

### 2. Submit Answer
Submit your response to the current question. Real-time feedback will be evaluated.

- **URL:** `/api/interview/answer`
- **Method:** `POST`
- **Authentication:** Required (Bearer Token)
- **Request Body:**
  ```json
  {
    "session_id": "session-uuid-here",
    "answer": "I have built several React applications using Fetch API and Redux to consume backend endpoints..."
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "session_id": "session-uuid-here",
    "next_question": "Question 2: How do you handle state management across components?",
    "feedback": {
      "technical_accuracy": 8.5,
      "communication_clarity": 9.0,
      "relevance_to_job": 8.0,
      "strengths": ["Clear explanation of asynchronous state", "Proper context mapping"],
      "improvement_areas": ["Mention Redux Thunk or Saga middleware usage for api side effects"],
      "sample_answer": "An ideal answer would include..."
    },
    "interview_complete": false,
    "message": "Response processed successfully."
  }
  ```

### 3. Get Session Feedback Summary
Retrieve final aggregated scores and performance metrics once the session ends.

- **URL:** `/api/interview/feedback`
- **Method:** `GET`
- **Authentication:** Required (Bearer Token)
- **Query Parameters:**
  - `sessionId` (string, required)
- **Response (200 OK):**
  ```json
  {
    "summary": {
      "session_id": "session-uuid",
      "average_accuracy": 8.2,
      "average_clarity": 8.8,
      "overall_score": 85.0
    },
    "feedback": [
      {
        "question": "Question 1: ...",
        "user_answer": "...",
        "technical_accuracy": 8.5,
        "communication_clarity": 9.0,
        "relevance_to_job": 8.0,
        "strengths": [...],
        "improvement_areas": [...]
      }
    ]
  }
  ```

---

## 🔒 DigiLocker Module (Secure Storage)

### 1. Upload Encrypted Document
Upload and encrypt client-side metadata + stream file using AES-256-GCM.

- **URL:** `/api/digilocker/upload`
- **Method:** `POST`
- **Authentication:** Required (Bearer Token)
- **Request (Multipart Form):**
  - `file`: (binary document file)
  - `category`: "certificates" | "transcripts" | "documents" | "certificates_backup"
  - `document_name`: (string, optional)
  - `description`: (string, optional)
- **Response (200 OK):**
  ```json
  {
    "document_id": "document-uuid",
    "filename": "degree_certificate.pdf",
    "category": "certificates",
    "file_size": 2048576,
    "checksum": "sha256-hash-value",
    "upload_date": "2024-01-20T11:45:00Z"
  }
  ```

### 2. Download Secure Document
Decrypt and download the document as a stream.

- **URL:** `/api/digilocker/download/{doc_id}`
- **Method:** `GET`
- **Authentication:** Required (Supports Bearer token OR `?token=<JWT_TOKEN>` query parameter for anchor tags download)
- **Response (200 OK):** Binary file stream with `Content-Disposition: attachment; filename="..."` header.

### 3. Delete Secure Document
Remove the document permanently from the vault.

- **URL:** `/api/digilocker/{doc_id}`
- **Method:** `DELETE`
- **Authentication:** Required (Bearer Token)
- **Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Document securely deleted"
  }
  ```

---

## 🛑 Error Codes

StudHelper returns structured JSON error responses:

```json
{
  "error": "TokenExpiredError",
  "message": "Token has expired",
  "status_code": 401,
  "error_code": "TOKEN_EXPIRED",
  "timestamp": "2026-06-25T16:55:00Z"
}
```

| HTTP Status | Error Code | Description |
|---|---|---|
| `400` | `VALIDATION_ERROR` | Request validation fails (e.g. invalid query param) |
| `401` | `AUTHENTICATION_FAILED` | Token missing or incorrect credentials |
| `401` | `INVALID_TOKEN` | JWT decoding failed or signature invalid |
| `401` | `TOKEN_EXPIRED` | JWT lifetime has expired |
| `403` | `AUTHORIZATION_FAILED` | Accessing unauthorized endpoints |
| `403` | `INSUFFICIENT_PERMISSIONS`| Lacking user roles (e.g., admin) |
| `404` | `NOT_FOUND` | User, Job, Session, or Document missing |
| `409` | `ALREADY_EXISTS` | Registered email already in use |
| `429` | | Rate Limit Exceeded (max 5 requests/min) |
| `500` | `INTERNAL_ERROR` | General server failure |
| `502` | `EXTERNAL_SERVICE_ERROR` | Network failures contacting Gemini, Pinecone, or JSearch |
