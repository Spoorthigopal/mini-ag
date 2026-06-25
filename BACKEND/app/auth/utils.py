from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, expires_in: int = None) -> str:
    """Create JWT access token"""
    if expires_in is None:
        expires_in = settings.jwt_expire_minutes
    expire = datetime.utcnow() + timedelta(minutes=expires_in)
    to_encode = {"sub": user_id, "exp": expire}
    try:
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise


def decode_access_token(token: str) -> str:
    """Decode JWT token and return user_id"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token payload")
        return user_id
    except JWTError as e:
        logger.error(f"Invalid token: {e}")
        raise
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        raise
