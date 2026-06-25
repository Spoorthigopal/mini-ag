# STU-MINI Backend

FastAPI + PostgreSQL + Pinecone + LangChain backend for the university student assistance platform.

## 🚀 Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# → Fill in all required API keys in .env

# 4. Run database migrations
alembic -c migrations/alembic.ini upgrade head

# 5. Seed initial data (welfare schemes + sample jobs → DB + Pinecone)
python scripts/init_db.py

# 6. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server runs at:** http://localhost:8000  
**Swagger docs:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc  
**Health check:** http://localhost:8000/health  

---

## 📁 Project Structure

```
BACKEND/
├── app/
│   ├── auth/           # JWT auth: register, login, logout
│   ├── welfare/        # Welfare scheme navigator + RAG bot
│   ├── internships/    # Internship jobs + JSearch + resume parsing
│   ├── interview/      # AI interview coach (LangChain + Gemini)
│   ├── digilocker/     # AES-256-GCM encrypted document vault
│   ├── shared/         # Config, exceptions, dependencies, LLM, embeddings, scheduler
│   ├── config.py       # Pydantic Settings (all env vars)
│   ├── database.py     # SQLAlchemy engine + session factory
│   └── main.py         # FastAPI app, routers, lifespan events
├── migrations/
│   ├── versions/
│   │   └── 001_initial.py   # Full schema migration
│   └── env.py               # Alembic configuration
├── scripts/
│   ├── init_db.py           # Run migrations + seed all data
│   ├── seed_welfare_schemes.py
│   └── seed_sample_jobs.py
├── .env.example
└── requirements.txt
```

---

## 🔑 Required Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (min 32 chars) |
| `GOOGLE_API_KEY` | Google Gemini 2.0 API key |
| `NVIDIA_API_KEY` | NVIDIA NIM embeddings API key |
| `PINECONE_API_KEY` | Pinecone vector database key |
| `PINECONE_INDEX_NAME` | Pinecone index name (default: `studhelper`) |
| `JSEARCH_API_KEY` | JSearch via RapidAPI key |
| `ADMIN_API_KEY` | Admin route access key |

See `.env.example` for the complete list.

---

## 🗄 Database Setup

### PostgreSQL (create database)
```sql
CREATE DATABASE studhelper;
```

### Run Alembic Migrations
```bash
alembic -c migrations/alembic.ini upgrade head
```

### Seed Data (DB + Pinecone)
```bash
# Seed everything at once:
python scripts/init_db.py

# Or seed individually:
python scripts/seed_welfare_schemes.py
python scripts/seed_sample_jobs.py
```

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.104 |
| Database | PostgreSQL 14+ via SQLAlchemy 2.0 |
| Migrations | Alembic 1.12 |
| Authentication | JWT via python-jose |
| AI / LLM | Google Gemini 2.0 Flash via LangChain |
| Embeddings | NVIDIA NIM (`nvidia/nv-embed-v2`, 1024-dim) |
| Vector DB | Pinecone |
| Job Search | JSearch API via RapidAPI |
| Encryption | AES-256-GCM (cryptography library) |
| Scheduling | APScheduler (daily job sync at 2 AM) |

---

## 📋 API Endpoints Summary

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login & get JWT token |
| `GET` | `/api/welfare/schemes` | List welfare schemes |
| `POST` | `/api/welfare/chat` | RAG chatbot for schemes |
| `GET` | `/api/internships/jobs` | List internship jobs |
| `POST` | `/api/internships/upload-resume` | Parse PDF resume |
| `POST` | `/api/internships/chat` | Job recommendations |
| `POST` | `/api/internships/sync` | Sync from JSearch (admin) |
| `POST` | `/api/interview/start` | Start mock interview |
| `POST` | `/api/interview/answer` | Submit answer |
| `GET` | `/api/interview/feedback` | Get session scores |
| `POST` | `/api/digilocker/upload` | Encrypted file upload |
| `GET` | `/api/digilocker/documents` | List user documents |
| `GET` | `/api/digilocker/download/{id}` | Decrypt & download |
| `DELETE`| `/api/digilocker/{id}` | Delete document |

See `DOCS/API_DOCS.md` for complete documentation with curl examples.
