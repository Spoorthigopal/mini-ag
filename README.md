# STU-MINI — AI-Powered University Student Platform

A complete full-stack AI platform helping Indian university students discover scholarships, find internships, prepare for interviews, and securely store academic documents.

---

## 📁 Project Structure

```
STU-MINI/
├── FRONTEND/          # React 19 + TypeScript + Vite + Redux Toolkit
├── BACKEND/           # FastAPI + PostgreSQL + Pinecone + LangChain
└── DOCS/              # Complete documentation
    ├── SETUP.md           ← Step-by-step setup
    ├── API_DOCS.md        ← Full API reference + curl examples
    ├── INTEGRATION_GUIDE.md ← Frontend-backend contract
    └── DESIGN_SYSTEM.md   ← Design system specs
```

---

## 🧠 Modules and Workflow Detailed Explanation

The STU-MINI platform is composed of four primary modules. Here is an in-depth look at their features, technical background, and workflow.

### 1. Welfare Navigator (Scholarships & Schemes)
**Purpose:** Helps students discover and apply for government and private scholarships relevant to their profile.
**Features:**
- **Scheme Browsing:** Users can view a list of available welfare schemes, filtered by type (Scholarship, Fellowship, Grant), amount, provider, and status.
- **Welfare RAG Bot:** An AI-powered chatbot that answers questions about scholarship eligibility, criteria, and document requirements.

**Technical Background:**
- **RAG (Retrieval-Augmented Generation):** The bot uses Pinecone for vector search and Google Gemini for natural language generation. 
- **Embeddings:** Scheme details are converted into dense vector representations using NVIDIA NIM (`nvidia/nv-embed-v2`) and stored in Pinecone.

**Workflow:**
1. The student submits a natural language query in the chat interface.
2. The backend converts the query into vector embeddings.
3. Pinecone performs a similarity search to retrieve the most relevant scheme documents.
4. LangChain orchestrates feeding these documents as context to the Gemini LLM.
5. The LLM formulates a highly accurate, context-aware response which is sent back to the user.

### 2. Internship Portal
**Purpose:** Connects students with live internship and job listings while providing AI-driven career matching based on their resume.
**Features:**
- **Job Listings:** Real-time paginated list of internships and full-time jobs with advanced filtering (company, location, stipend, job type).
- **Resume Parsing & Upload:** Allows students to upload their PDF resumes to automatically extract skills and experience.
- **Internship Coach Chat:** A specialized chatbot that provides personalized internship suggestions based on the student's parsed resume context.

**Technical Background:**
- **Live Scraping:** Uses the JSearch API via RapidAPI to fetch real-time job listings, synced periodically using APScheduler.
- **PDF Parsing:** Utilizes `pdfplumber` to extract text from resumes, which is then processed by Gemini to extract structured skills and experience.

**Workflow:**
1. The user uploads their resume (PDF).
2. The backend parses the PDF and extracts key skills and experience.
3. The user queries the Internship Coach for matching jobs.
4. The system combines the user's parsed resume context with available job listings in the database to recommend the best-fit opportunities.

### 3. AI Interview Coach
**Purpose:** Prepares students for technical and behavioral interviews through interactive mock sessions tailored to specific job roles.
**Features:**
- **Mock Interviews:** Dynamic, real-time interview sessions tailored to a selected internship or job description.
- **Real-Time Evaluation:** Immediate feedback on answers based on technical accuracy, communication clarity, and relevance to the job.
- **Comprehensive Feedback Summary:** Aggregated post-session metrics detailing strengths, areas for improvement, and sample ideal answers for every question.

**Technical Background:**
- **LangChain & Gemini LLM:** Orchestrates the flow of the interview, dynamically generating follow-up questions and evaluating answers based on the job context.

**Workflow:**
1. The user selects a job application and starts an interview session.
2. The backend generates an initial question based on the job description.
3. The user submits their answer.
4. The LLM evaluates the answer, calculating scores for clarity and accuracy, and formulates the next question.
5. Upon completion, a detailed performance summary is generated and stored for the user's review.

### 4. DigiLocker (Secure Document Vault)
**Purpose:** Provides a highly secure vault for students to store sensitive academic documents like transcripts and certificates.
**Features:**
- **Secure Upload & Categorization:** Upload documents categorized as certificates, transcripts, etc.
- **Encrypted Storage:** Documents are encrypted before being stored on the server.
- **Secure Retrieval & Deletion:** Decrypt and download files as streams, or securely delete them from the vault.

**Technical Background:**
- **AES-256-GCM Encryption:** Advanced Encryption Standard in Galois/Counter Mode guarantees both confidentiality and authenticity of the documents.
- **Checksums:** Ensures document integrity.

**Workflow:**
1. The student uploads a document via the frontend.
2. The backend receives the file, encrypts it using AES-256-GCM, generates a checksum, and securely stores the binary blob.
3. When requested, the backend decrypts the document on-the-fly and streams it securely to the authorized user.

---

## 🛠 Tech Stack

**Frontend:**
- **Framework:** React 19 with TypeScript, powered by Vite for blazing-fast builds.
- **State Management:** Redux Toolkit.
- **Styling:** Dark glassmorphism design with Vanilla CSS/Modules.
- **HTTP Client:** Axios.

**Backend:**
- **Framework:** FastAPI (Python) for asynchronous, high-performance API endpoints.
- **Database:** PostgreSQL with SQLAlchemy 2.0 ORM.
- **Migrations:** Alembic.
- **AI & LLMs:** Google Gemini 2.0 Flash.
- **Embeddings:** NVIDIA NIM `nvidia/nv-embed-v2` (1024-dimensional embeddings).
- **Vector Database:** Pinecone.
- **AI Orchestration:** LangChain.
- **Background Jobs:** APScheduler for automated tasks (like syncing jobs).
- **PDF Parsing:** `pdfplumber`.

**Third-Party Services:**
- JSearch via RapidAPI for live job scraping.

---

## 🔐 Security Features

- **Authentication:** JWT (JSON Web Tokens) using the HS256 algorithm with a strict 60-minute expiry.
- **Data Encryption:** AES-256-GCM encryption for all documents stored in the DigiLocker.
- **Password Hashing:** PBKDF2 key derivation (via `passlib` and `bcrypt`).
- **Admin Security:** Constant-time admin key comparison to prevent timing attacks.
- **Rate Limiting:** Per-IP rate limiting (5 requests/minute) to prevent brute force and DDoS attacks.
- **CORS:** Strict origin allowlisting to prevent cross-site request forgery.

---

## 🚀 Quick Start

### Backend
```bash
cd BACKEND
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env  # Fill in API keys
alembic -c migrations/alembic.ini upgrade head
python scripts/init_db.py
uvicorn app.main:app --reload
# → Runs on http://localhost:8000
```

### Frontend
```bash
cd FRONTEND
npm install
cp .env.example .env  # Set VITE_API_BASE_URL=http://localhost:8000
npm run dev
# → Runs on http://localhost:5173
```

---

## 🔑 Required API Keys

| Service | Where to Get |
|---|---|
| Google Gemini | https://aistudio.google.com/app/apikey |
| NVIDIA NIM | https://build.nvidia.com |
| Pinecone | https://app.pinecone.io |
| JSearch | https://rapidapi.com (letscrape-6bRBa3QguO5/jsearch) |

---

## 📚 Documentation

| File | Contents |
|---|---|
| [SETUP.md](DOCS/SETUP.md) | Step-by-step installation, migration, seeding |
| [API_DOCS.md](DOCS/API_DOCS.md) | All endpoints with curl examples |
| [INTEGRATION_GUIDE.md](DOCS/INTEGRATION_GUIDE.md) | Frontend-backend contract, JWT flow |
| [DESIGN_SYSTEM.md](DOCS/DESIGN_SYSTEM.md) | UI components, tokens |
