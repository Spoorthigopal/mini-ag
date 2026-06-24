# STU-MINI Backend

FastAPI + PostgreSQL backend for university student assistance platform.

## Setup

1. Copy `.env.example` to `.env` and configure all keys
2. Install dependencies: `pip install -r requirements.txt --break-system-packages`
3. Setup database: `alembic upgrade head`
4. Seed data: `python scripts/seed_welfare_schemes.py`
5. Run server: `uvicorn app.main:app --reload`

## Structure

- `app/auth/` - Authentication module
- `app/welfare/` - Welfare scheme navigator
- `app/internships/` - Internship portal
- `app/interview/` - Interview coach
- `app/digilocker/` - Document storage
- `app/shared/` - Shared utilities
- `migrations/` - Database migrations
- `scripts/` - Setup and seed scripts

## API Base URL

http://localhost:8000/api

## Technologies

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pinecone (vector DB)
- LangChain
- Google Gemini API
- NVIDIA NIM (embeddings)
- JSearch API (job scraping)
