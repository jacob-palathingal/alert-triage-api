from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventResponse
from app.classifier import classify
from app.aggregator import aggregate
from app.enricher import enrich_incident
from datetime import datetime, timezone

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    # Step 1: classify
    severity = classify(payload)

    # Step 2: create event
    event = Event(
        service=payload.service,
        level=payload.level,
        message=payload.message,
        timestamp=payload.timestamp or datetime.now(timezone.utc),
        severity=severity,
    )
    db.add(event)
    db.flush()

    # Step 3: aggregate using caller-specified window
    incident = aggregate(db, event, window_minutes=payload.window_minutes)
    event.incident_id = incident.id

    # Step 4: enrich new incidents only
    if incident.event_count == 1:
        summary = enrich_incident(incident, payload.message)
        if summary:
            incident.summary = summary

    db.commit()
    db.refresh(event)

    return event