"""Authentication-related data models."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RegisterResponse(BaseModel):
    """Response from user registration."""

    request_id: UUID


class LoginResponse(BaseModel):
    """Response from user login."""

    request_id: Optional[UUID] = None
    token: Optional[str] = None
    user_id: Optional[UUID] = None


class PhoneConfirmationResponse(BaseModel):
    """Response from phone confirmation."""

    success: bool
    message: Optional[str] = None


class PasswordSetResponse(BaseModel):
    """Response from password setting."""

    success: bool
    token: Optional[str] = None
