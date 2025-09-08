"""Profile-related data models."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    """User profile information."""

    id: UUID
    email: Optional[str] = None
    phone: Optional[int] = Field(None, ge=79000000000, le=79999999999)
    balance: float = Field(ge=0)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[str] = None  # datetime as string

class BalanceTopupResponse(BaseModel):
    """Response from balance top-up."""

    payment_id: UUID
    amount: float = Field(ge=0)
    status: str
    payment_url: Optional[str] = None