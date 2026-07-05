from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeadBase(BaseModel):
    name: str
    category: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = "OpenStreetMap"
    source_id: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    assigned_to: Optional[str] = None
    last_contacted: Optional[str] = None
    next_follow_up: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    status: str = "New"
    priority: str = "Medium"
    notes: Optional[str] = None
    tags: Optional[str] = None
    assigned_to: Optional[str] = None
    last_contacted: Optional[str] = None
    next_follow_up: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
