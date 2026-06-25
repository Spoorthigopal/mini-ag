# STU-MINI Setup Guide

Complete step-by-step setup instructions for the entire platform.

---

## Prerequisites

| Tool | Min Version |
|---|---|
| Node.js | 18+ |
| Python | 3.10+ |
| PostgreSQL | 14+ |
| Git | Latest |

---

## 🖥 Frontend Setup

### 1. Navigate to frontend
```bash
cd FRONTEND
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment
```bash
cp .env.example .env
```
Edit `.env` and set:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Start development server
```bash
npm run dev
# Frontend runs at: http://localhost:5173
```

---

## ⚙️ Backend Setup

### 1. Navigate to backend
```bash
cd BACKEND
```

### 2. Create virtual environment
```bash
python -m venv venv

# Activate (Windows):
venv\Scripts\activate

# Activate (macOS/Linux):
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** If you encounter version conflicts, install key packages manually:
> ```bash
> pip install pydantic-settings python-jose[cryptography] email-validator
> ```

### 4. Setup PostgreSQL

**Install PostgreSQL** and create the database:
```bash
psql -U postgres
```
```sql
CREATE DATABASE studhelper;
\q
```

### 5. Configure environment
```bash
cp .env.example .env
```

Edit `.env` and fill in **all required values**:

```env
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/studhelper

# JWT (must be 32+ characters)
SECRET_KEY=your-very-long-random-secret-key-at-least-32-chars

# API Keys
GOOGLE_API_KEY=your_google_gemini_api_key
NVIDIA_API_KEY=your_nvidia_nim_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=studhelper
JSEARCH_API_KEY=your_jsearch_rapidapi_key
ADMIN_API_KEY=your_admin_secret_key
```

### 6. Run Database Migrations

```bash
# Run Alembic migrations (creates all tables)
alembic -c migrations/alembic.ini upgrade head
```

> **Troubleshooting:** If alembic.ini is not found:
> ```bash
> cd migrations
> alembic upgrade head
> ```

### 7. Seed Data (PostgreSQL + Pinecone)

```bash
# Option A — Seed everything at once (recommended):
python scripts/init_db.py

# Option B — Seed individually:
python scripts/seed_welfare_schemes.py
python scripts/seed_sample_jobs.py
```

> **Note:** Seeding requires live API keys for NVIDIA NIM (embeddings) and Pinecone. If keys are missing, DB entries are created but Pinecone upsertion is skipped with a warning.

### 8. Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| URL | Purpose |
|---|---|
| http://localhost:8000/health | Health check |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |

---

## 🔑 Getting API Keys

| Service | URL | Notes |
|---|---|---|
| Google Gemini | https://aistudio.google.com/app/apikey | Free tier available |
| NVIDIA NIM | https://build.nvidia.com | Register for API access |
| Pinecone | https://app.pinecone.io | Free starter tier |
| JSearch | https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch | Free 500 req/month |

---

## 🗂 Pinecone Index Setup

Create a Pinecone index before seeding:

1. Login to https://app.pinecone.io
2. Create an index with:
   - **Name:** `studhelper`
   - **Dimensions:** `1024` (for NVIDIA NV-Embed-v2)
   - **Metric:** `cosine`
   - **Cloud:** Serverless (AWS / GCP)

---

## 🔄 Re-running Migrations

To reset and re-apply all migrations:
```bash
# Downgrade to base (drops all tables)
alembic -c migrations/alembic.ini downgrade base

# Re-apply all migrations
alembic -c migrations/alembic.ini upgrade head

# Re-seed data
python scripts/init_db.py
```

---

## 🚦 Verification Checklist

| Step | Check |
|---|---|
| Frontend | http://localhost:5173 loads the app |
| Backend health | `curl http://localhost:8000/health` → `{"status":"healthy"}` |
| Auth works | POST `/api/auth/register` returns a JWT token |
| Welfare schemes | GET `/api/welfare/schemes` returns scheme list |
| DB connected | No `OperationalError` in backend logs |

---

## 🛠 Troubleshooting

### PostgreSQL Connection Refused
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL (Windows)
net start postgresql-x64-14

# Start PostgreSQL (macOS)
brew services start postgresql
```

### ModuleNotFoundError: pydantic_settings
```bash
pip install pydantic-settings
```

### ImportError: email-validator
```bash
pip install email-validator
```

### Pinecone 404 / Index Not Found
Make sure your index name in `.env` matches the one created in Pinecone dashboard:
```env
PINECONE_INDEX_NAME=studhelper
```

### Frontend CORS Errors
Verify the backend allows the frontend origin in `app/config.py`:
```python
CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
```
