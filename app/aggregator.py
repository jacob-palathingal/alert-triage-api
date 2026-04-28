from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Incident, Event

# How long an incident stays open after the last event.
# If no new matching event arrives within this window, the incident is considered closed.
INCIDENT_WINDOW_MINUTES = 5


def get_open_incident(db: Session, service: str, severity: str) -> Incident | None:
    """
    Look for an existing open incident matching this service and severity
    that is still within the time window.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=INCIDENT_WINDOW_MINUTES)

    return (
        db.query(Incident)
        .filter(
            Incident.service == service,
            Incident.severity == severity,
            Incident.is_open == "true",
            Incident.ended_at >= cutoff,  # still within the window
        )
        .first()
    )


def aggregate(db: Session, event: Event) -> Incident:
    """
    Groups the event into an existing open incident or creates a new one.

    Logic:
    - If an open incident exists for this service+severity within the time window:
        update it (increment event_count, extend ended_at)
    - Otherwise:
        close any stale open incident for this service+severity, then create a new one

    Returns the incident the event was assigned to.
    """
    existing = get_open_incident(db, event.service, event.severity)

    if existing:
        # Extend the incident window and increment event count
        existing.event_count += 1
        existing.ended_at = event.timestamp
        db.flush()
        return existing

    # Close any stale open incident for this service+severity before creating a new one.
    # This handles cases where the window expired but is_open was never cleared.
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
        stale.is_open = None  # null allows the unique constraint to permit a new open incident
        db.flush()

    # Create a new incident
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
        db.flush()  # flush to get the incident id without committing yet
        return incident

    except IntegrityError:
        # Two concurrent requests raced to create the same incident.
        # Roll back and fetch the one that won.
        db.rollback()
        existing = get_open_incident(db, event.service, event.severity)
        if existing:
            existing.event_count += 1
            existing.ended_at = event.timestamp
            db.flush()
            return existing
        raise  # something unexpected — re-raise