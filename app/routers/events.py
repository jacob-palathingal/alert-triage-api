from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    """
    Ingest a single log event.

    Phase 1: Persists the raw event. Severity and incident_id are null for now.
    Phase 2: Classifier will set severity before saving.
    Phase 3: Aggregator will set incident_id before saving.
    """
    event = Event(
        service=payload.service,
        level=payload.level,
        message=payload.message,
        timestamp=payload.timestamp,
        severity=None,      
        incident_id=None,  
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event
