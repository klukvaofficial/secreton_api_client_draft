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

    id: UUID
    name: str
    service_type: str
    status: str
    price: float = Field(ge=0)
    reward: float = Field(ge=0)
    created_at: datetime
    audio_file: Optional[str] = None
    text_file: Optional[str] = None
    tags: List[OrderTagModel] = Field(default_factory=list)
    comments: List[OrderCommentModel] = Field(default_factory=list)

class OrderCreateResponse(BaseModel):
    """Response from order creation."""

    order_id: UUID
    message: Optional[str] = None

class ServiceType(BaseModel):
    """Available service type."""

    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None