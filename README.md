# STU-MINI - University Student Assistance Platform

A complete AI-powered platform helping university students with scholarships, internships, interview preparation, and document management.

## 📁 Project Structure

```
STU-MINI-COMPLETE/
├── FRONTEND/          # React 19 + TypeScript + Vite
├── BACKEND/           # FastAPI + PostgreSQL
└── DOCS/              # Complete documentation
```

## 🚀 Quick Start

### Frontend
```bash
cd FRONTEND
npm install
cp .env.example .env
npm run dev
```

### Backend
```bash
cd BACKEND
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure PostgreSQL and API keys in .env
alembic upgrade head
python scripts/seed_welfare_schemes.py
uvicorn app.main:app --reload
```

## 📋 Modules

1. **Welfare Scheme Navigator** - RAG-powered scholarship discovery
2. **Internship Portal** - Job listings with resume matching
3. **AI Interview Coach** - LangChain-powered interview prep
4. **DigiLocker** - Encrypted document storage

## 🛠 Tech Stack

**Frontend:**
- React 19, TypeScript, Vite
- Redux Toolkit, Axios, Lucide-react
- Dark glassmorphism design

**Backend:**
- FastAPI, PostgreSQL, SQLAlchemy
- Pinecone (vector DB), LangChain
- Google Gemini 2.0 Flash API
- NVIDIA NIM (embeddings)

## 📚 Documentation

See the `DOCS/` folder for:
- **SETUP.md** - Installation guide
- **API_DOCS.md** - API reference
- **INTEGRATION_GUIDE.md** - Integration details
- **DESIGN_SYSTEM.md** - Design specifications

## 🔐 Security

- JWT authentication
- AES-256-GCM encryption (DigiLocker)
- PBKDF2 key derivation
- CORS enabled
- Input validation (Pydantic)

## 📈 Next Steps

1. Configure environment variables (.env files)
2. Setup PostgreSQL database
3. Install dependencies (frontend + backend)
4. Follow SETUP.md in DOCS folder
5. Run frontend and backend servers
6. Execute build prompts to populate code

## 📝 Build Instructions

This is a skeleton structure. Use the provided prompts to generate all code:
1. Frontend: 14 prompts (sequential)
2. Backend: 11 prompts (sequential)

See DOCS/SETUP.md for detailed build workflow.
