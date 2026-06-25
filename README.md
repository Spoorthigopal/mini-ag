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

## 🧠 Modules

| Module | Description | Tech |
|---|---|---|
| **Welfare Navigator** | RAG-powered scholarship discovery | Pinecone + Gemini |
| **Internship Portal** | Live job listings + resume matching | JSearch + NVIDIA NIM |
| **AI Interview Coach** | Mock interviews with real-time feedback | LangChain + Gemini |
| **DigiLocker** | Encrypted academic document vault | AES-256-GCM |

---

## 🛠 Tech Stack

**Frontend:**
- React 19, TypeScript, Vite
- Redux Toolkit, Axios
- Dark glassmorphism design

**Backend:**
- FastAPI, PostgreSQL, SQLAlchemy 2.0
- Alembic (migrations)
- Google Gemini 2.0 Flash (AI/LLM)
- NVIDIA NIM `nvidia/nv-embed-v2` (1024-dim embeddings)
- Pinecone (vector search)
- LangChain (RAG pipelines)
- JSearch via RapidAPI (job scraping)
- AES-256-GCM encryption (DigiLocker)
- APScheduler (daily background jobs)

---

## 🔑 Required API Keys

| Service | Where to Get |
|---|---|
| Google Gemini | https://aistudio.google.com/app/apikey |
| NVIDIA NIM | https://build.nvidia.com |
| Pinecone | https://app.pinecone.io |
| JSearch | https://rapidapi.com (letscrape-6bRBa3QguO5/jsearch) |

---

## 🔐 Security Features

- JWT authentication (HS256, 60-min expiry)
- AES-256-GCM client-side encryption for documents
- PBKDF2 key derivation
- Constant-time admin key comparison
- Per-IP rate limiting (5 req/min)
- CORS origin allowlist

---

## 📚 Documentation

| File | Contents |
|---|---|
| [SETUP.md](DOCS/SETUP.md) | Step-by-step installation, migration, seeding |
| [API_DOCS.md](DOCS/API_DOCS.md) | All endpoints with curl examples |
| [INTEGRATION_GUIDE.md](DOCS/INTEGRATION_GUIDE.md) | Frontend-backend contract, JWT flow |
| [DESIGN_SYSTEM.md](DOCS/DESIGN_SYSTEM.md) | UI components, tokens |

---

## 🏃 Running the Full Stack

1. Start PostgreSQL
2. Start backend: `uvicorn app.main:app --reload` (port 8000)
3. Start frontend: `npm run dev` (port 5173)
4. Open http://localhost:5173
5. API docs at http://localhost:8000/docs
