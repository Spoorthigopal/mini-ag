from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "SecurePassword123"
            }
        }


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "SecurePassword123"
            }
        }


class UserResponse(BaseModel):
    id: str
    email: str
    role: str = "student"
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "student@example.com",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "student@example.com",
                    "created_at": "2024-01-15T10:30:00Z"
                }
            }
        }


class TokenPayload(BaseModel):
    user_id: str
    exp: Optional[datetime] = None
