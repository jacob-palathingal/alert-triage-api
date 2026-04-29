from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Incident
from app.schemas import IncidentResponse

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("/", response_model=list[IncidentResponse])
def get_incidents(
    severity: Optional[str] = None,
    service: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns all incidents, newest first.
    Optionally filter by severity and/or service.

    Examples:
        GET /incidents/
        GET /incidents/?severity=high
        GET /incidents/?service=auth-service
        GET /incidents/?severity=high&service=auth-service
    """
    query = db.query(Incident)

    if severity:
        query = query.filter(Incident.severity == severity)
    if service:
        query = query.filter(Incident.service == service)

    return query.order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Returns a single incident by ID.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    return incident