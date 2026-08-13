from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Import all models so SQLAlchemy can register them before create_all
from app.auth.models import User  # noqa: F401
from app.welfare.models import WelfareScheme  # noqa: F401
from app.internships.models import InternshipJob  # noqa: F401
from app.interview.models import InterviewSession, InterviewFeedback  # noqa: F401
from app.digilocker.models import Document  # noqa: F401
from app.shared.models import Conversation, RateLimitLog  # noqa: F401

from app.database import init_db

# Import routers
from app.auth.routes import router as auth_router
from app.welfare.routes import router as welfare_router
from app.internships.routes import router as internships_router
from app.interview.routes import router as interview_router
from app.digilocker.routes import router as digilocker_router

app = FastAPI(
    title="STU-MINI API",
    description="University Student Assistance Platform API — Welfare, Internships, Interview Prep & DigiLocker",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(welfare_router)
app.include_router(internships_router)
app.include_router(interview_router)
app.include_router(digilocker_router)


# Exception handlers
from app.shared.dependencies import setup_exception_handlers
setup_exception_handlers(app)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})



# Startup / shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting STU-MINI API...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"DB init failed (ensure PostgreSQL is running): {e}")

    from app.shared.scheduler import start_scheduler
    start_scheduler()
    logger.info("GradSphere API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    from app.shared.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("GradSphere API shutdown complete")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
