from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventResponse
from app.classifier import classify
from app.aggregator import aggregate
from app.enricher import enrich_incident

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    # Step 1: classify
    severity = classify(payload)

    # Step 2: create the event object
    event = Event(
        service=payload.service,
        level=payload.level,
        message=payload.message,
        timestamp=payload.timestamp,
        severity=severity,
    )
    db.add(event)
    db.flush()

    # Step 3: aggregate into an incident
    incident = aggregate(db, event)
    event.incident_id = incident.id

    # Step 4: enrich on new incidents only, passing the triggering log message
    if incident.event_count == 1:
        summary = enrich_incident(incident, payload.message)
        if summary:
            incident.summary = summary

    # Step 5: commit everything
    db.commit()
    db.refresh(event)

    return event