from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ── Incoming request ──────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    """
    Payload for POST /events.
    The caller sends this when submitting a log event.
    """
    service: str = Field(..., example="auth-service")
    level: str = Field(..., example="ERROR")
    message: str = Field(..., example="Database connection timeout after 30s")
    timestamp: Optional[datetime] = Field(
    default=None,
    description="Event timestamp. Defaults to current UTC time if not provided.",
    example="2026-04-28T10:00:00Z"
    )
    window_minutes: int = Field(
        default=5,
        ge=1,
        le=1440,
        description="Time window in minutes for grouping events into the same incident. Defaults to 5. Max 1440 (24 hours).",
        example=5
    )


# ── Outgoing responses ────────────────────────────────────────────────────────

class EventResponse(BaseModel):
    """
    What we return after a successful POST /events.
    """
    id: int
    service: str
    level: str
    message: str
    severity: Optional[str]       
    incident_id: Optional[int]    
    timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class IncidentResponse(BaseModel):
    """
    Used in Phase 5 for GET /incidents responses.
    Defined here now so the schema file is complete.
    """
    id: int
    service: str
    severity: str
    event_count: int
    started_at: datetime
    ended_at: datetime
    summary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
