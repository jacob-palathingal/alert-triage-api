from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventResponse
from app.classifier import classify
from app.aggregator import aggregate

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    """
    Ingest a single log event.

    Phase 1: Persists the raw event.
    Phase 2: Classifier sets severity before saving.
    Phase 3: Aggregator groups event into an incident before saving.
    Phase 4: Enricher will call Claude API to summarize the incident.
    """
    # Step 1: classify
    severity = classify(payload)

    # Step 2: create the event object (not yet committed)
    event = Event(
        service=payload.service,
        level=payload.level,
        message=payload.message,
        timestamp=payload.timestamp,
        severity=severity,
    )
    db.add(event)
    db.flush()  # get event.id without committing, needed before aggregation

    # Step 3: aggregate into an incident
    incident = aggregate(db, event)
    event.incident_id = incident.id

    # Step 4: commit everything together
    db.commit()
    db.refresh(event)

    return event