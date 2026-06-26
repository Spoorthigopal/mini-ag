from fastapi import Depends, HTTPException, status, Query, Header, Request, FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Generator, Optional, Callable
import logging
import hmac

from app.config import settings
from app.shared.exceptions import (
    AppException,
    AuthenticationError,
    InvalidTokenError,
    TokenExpiredError,
    InvalidCredentialsError,
    AuthorizationError,
    InsufficientPermissionsError,
    ValidationError,
    DatabaseConnectionError
)
from app.database import SessionLocal
from app.auth.models import User
from app.shared.models import RateLimitLog

logger = logging.getLogger(__name__)

# Security Scheme
security = HTTPBearer()

# Standard try-except imports to support jose/jwt dynamically
try:
    from jose import jwt, JWTError as PyJWTError, ExpiredSignatureError
except ImportError:
    try:
        from jwt import decode as jwt_decode, PyJWTError, ExpiredSignatureError
        # Define wrapper for jwt
        class jwt:
            @staticmethod
            def decode(token, key, algorithms):
                return jwt_decode(token, key, algorithms=algorithms)
    except ImportError:
        # Fallback dummy class so the imports don't fail at runtime
        class PyJWTError(Exception):
            pass
        class ExpiredSignatureError(Exception):
            pass
        class jwt:
            @staticmethod
            def decode(token, key, algorithms):
                raise ImportError("Neither python-jose nor PyJWT is installed.")

# DEPENDENCY 1: get_db() -> Generator[Session, None, None]
def get_db() -> Generator[Session, None, None]:
    """Database session dependency with error handling and rollback."""
    db = None
    try:
        db = SessionLocal()
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise DatabaseConnectionError(f"Database connection failed: {str(e)}")
        
    try:
        yield db
        # Commit if active and no exception occurred
        if db.is_active:
            db.commit()
    except (AppException, HTTPException):
        # Let AppException subclasses (AIServiceError, etc.) and FastAPI HTTPExceptions
        # propagate as-is without wrapping them in DatabaseConnectionError
        if db:
            db.rollback()
        raise
    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"Database error during session: {e}")
        raise DatabaseConnectionError(f"Database connection error: {str(e)}")
    finally:
        if db:
            db.close()

# DEPENDENCY 2: get_current_user(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate JWT token, return current user."""
    token = credentials.credentials
    if not token:
        raise AuthenticationError("Authorization credentials missing")
        
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("Missing 'sub' claim in token")
    except ExpiredSignatureError as e:
        logger.error(f"Token expired: {e}")
        raise TokenExpiredError("Token has expired")
    except PyJWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise InvalidTokenError("Invalid token")
    except Exception as e:
        logger.error(f"Token decoding failure: {e}")
        raise InvalidTokenError("Could not decode token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AuthenticationError("User not found")
        
    return user

# DEPENDENCY 3: verify_admin_api_key(api_key: str = Header(...)) -> bool
def verify_admin_api_key(api_key: str = Header(..., alias="X-API-Key")) -> bool:
    """Verify admin API key for protected endpoints."""
    if not settings.ADMIN_API_KEY:
        logger.error("ADMIN_API_KEY is not configured in settings")
        raise AuthorizationError("Admin API key is not configured")
        
    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(api_key, settings.ADMIN_API_KEY):
        raise AuthorizationError("Invalid API key")
        
    return True

# DEPENDENCY 4: get_pagination(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50)) -> tuple
def get_pagination(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
) -> tuple[int, int]:
    """Validate and return pagination parameters (offset, limit)."""
    if page < 1:
        raise ValidationError("Page number must be 1 or greater")
    if limit < 1 or limit > 50:
        raise ValidationError("Limit must be between 1 and 50")
        
    offset = (page - 1) * limit
    return offset, limit

# DEPENDENCY 5: check_rate_limit(request: Request, db: Session = Depends(get_db)) -> bool
async def check_rate_limit(request: Request, db: Session = Depends(get_db)) -> bool:
    """Simple rate limiting (5 requests/minute per IP)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip_address = forwarded.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else "unknown"

    now = datetime.utcnow()
    one_minute_ago = now - timedelta(seconds=60)
    
    count = db.query(RateLimitLog).filter(
        RateLimitLog.ip_address == ip_address,
        RateLimitLog.timestamp >= one_minute_ago
    ).count()

    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 5 requests per minute."
        )

    log_entry = RateLimitLog(ip_address=ip_address, timestamp=now)
    db.add(log_entry)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error logging rate limit: {e}")
        
    return True

# DEPENDENCY 6: get_current_user_with_role(required_role: str = None) -> Callable
def get_current_user_with_role(required_role: str = None) -> Callable:
    """Returns a dependency that validates user role."""
    def dependency(user: User = Depends(get_current_user)) -> User:
        user_role = getattr(user, "role", "student")
        if required_role and user_role != required_role:
            raise InsufficientPermissionsError(
                f"Insufficient role permissions. Required: {required_role}"
            )
        return user
    return dependency

# ERROR HANDLER SETUP
def setup_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with FastAPI."""
    from fastapi.responses import JSONResponse
    from app.shared.exceptions import format_error_response

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.error(f"AppException {exc.error_code} handled: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response(exc)
        )

    @app.exception_handler(PyJWTError)
    async def jwt_exception_handler(request: Request, exc: Exception):
        logger.error(f"Uncaught JWT error: {exc}")
        if "expired" in str(exc).lower():
            wrapped_exc = TokenExpiredError("Token has expired")
        else:
            wrapped_exc = InvalidTokenError("Invalid token format")
        return JSONResponse(
            status_code=wrapped_exc.status_code,
            content=format_error_response(wrapped_exc)
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled system exception: {exc}")
        generic_exc = AppException(
            message="An unexpected server error occurred",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )
        return JSONResponse(
            status_code=500,
            content=format_error_response(generic_exc)
        )
