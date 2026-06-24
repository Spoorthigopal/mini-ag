# STU-MINI Setup Guide

Complete step-by-step setup instructions for the entire platform.

## Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Git

## Frontend Setup

### 1. Navigate to Frontend
```bash
cd FRONTEND
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and set:
# VITE_API_BASE_URL=http://localhost:8000/api
```

### 4. Start Development Server
```bash
npm run dev
# Frontend runs on http://localhost:5173
```

## Backend Setup

### 1. Navigate to Backend
```bash
cd BACKEND
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt --break-system-packages
```

### 4. Setup PostgreSQL

Create database:
```sql
CREATE DATABASE stu_mini_db;
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with:
# - DATABASE_URL (PostgreSQL connection)
# - GEMINI_API_KEY
# - NVIDIA_NIM_API_KEY
# - PINECONE_API_KEY & PINECONE_ENVIRONMENT
# - JSEARCH_API_KEY
```

### 6. Run Database Migrations
```bash
alembic upgrade head
```

### 7. Seed Welfare Schemes (Optional)
```bash
python scripts/seed_welfare_schemes.py
```

### 8. Start Backend Server
```bash
uvicorn app.main:app --reload
# Backend runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

## Building with Prompts

After setup, execute the build prompts in sequence:

### Frontend (14 prompts)
1. Prompt 1: Project Setup & Folder Structure
2. Prompt 2: Global Styles & CSS Variables
3. Prompt 3: Redux Store & Slices
... (continue through Prompt 14)

### Backend (11 prompts)
15. Prompt 15: FastAPI Project Setup
16. Prompt 16: Database Setup & Models
... (continue through Prompt 25)

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -d stu_mini_db

# Update DATABASE_URL in .env if needed
```

### API Key Issues
- Ensure all API keys in .env are valid
- Check Pinecone index names match configuration
- Verify JSearch API key with RapidAPI

### Frontend Build Issues
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend Import Errors
```bash
# Reinstall with break-system-packages flag
pip install -r requirements.txt --break-system-packages
```

## Verification

Frontend running:
- http://localhost:5173 should load the app

Backend running:
- http://localhost:8000/health should return `{"status": "healthy"}`
- http://localhost:8000/docs shows interactive API docs

Both connected:
- Login form should communicate with backend
