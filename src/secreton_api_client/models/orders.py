"""Order-related data models."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OrderTagModel(BaseModel):
    """Order tag model."""

    id: UUID
    name: str


class OrderCommentModel(BaseModel):
    """Order comment model."""

    id: UUID
    text: str
    created_at: Optional[datetime] = None


class OrderViewModel(BaseModel):
    """Complete order view model."""

    order_id: UUID
    service_type: UUID
    status: str
    price: float = Field(ge=0)
    created_at: datetime
    tags: List[OrderTagModel] = Field(default_factory=list)
    comments: List[OrderCommentModel] = Field(default_factory=list)


class OrderCreateResponse(BaseModel):
    """Response from order creation."""

    order_id: UUID
    message: Optional[str] = None


class ServiceType(BaseModel):
    """Available service type."""

    id: UUID
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
