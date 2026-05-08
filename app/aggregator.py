from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Incident, Event

DEFAULT_WINDOW_MINUTES = 5


def get_open_incident(
    db: Session, service: str, severity: str, window_minutes: int, event_timestamp: datetime
) -> Incident | None:
    cutoff = event_timestamp - timedelta(minutes=window_minutes)
    return (
        db.query(Incident)
        .filter(
            Incident.service == service,
            Incident.severity == severity,
            Incident.is_open == "true",
            Incident.ended_at >= cutoff,
        )
        .first()
    )


def aggregate(db: Session, event: Event, window_minutes: int = DEFAULT_WINDOW_MINUTES) -> Incident:
    existing = get_open_incident(db, event.service, event.severity, window_minutes, event.timestamp)

    if existing:
        existing.event_count += 1
        existing.ended_at = event.timestamp
        db.flush()
        return existing

    stale = (
        db.query(Incident)
        .filter(
            Incident.service == event.service,
            Incident.severity == event.severity,
            Incident.is_open == "true",
        )
        .first()
    )
    if stale:
        stale.is_open = None
        db.flush()

    try:
        incident = Incident(
            service=event.service,
            severity=event.severity,
            event_count=1,
            started_at=event.timestamp,
            ended_at=event.timestamp,
            is_open="true",
        )
        db.add(incident)
        db.flush()
        return incident

    except IntegrityError:
        db.rollback()
        existing = get_open_incident(db, event.service, event.severity, window_minutes, event.timestamp)
        if existing:
            existing.event_count += 1
            existing.ended_at = event.timestamp
            db.flush()
            return existing
        raise