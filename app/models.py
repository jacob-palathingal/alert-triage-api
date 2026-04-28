from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)  # "high", "medium", "low"
    event_count = Column(Integer, default=1, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=False)
    summary = Column(Text, nullable=True)  # filled in by Claude API (Phase 4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_open = Column(String, default="true", nullable=True)  

    # Prevents two concurrent requests from both creating the same open incident.
    # Only one open incident per service+severity combo can exist at a time.
    # is_open is set to null when an incident closes, which lets the constraint
    # allow multiple closed incidents for the same service+severity.
    __table_args__ = (
        UniqueConstraint("service", "severity", "is_open", name="uq_open_incident_per_service_severity"),
    )

    events = relationship("Event", back_populates="incident")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, nullable=False, index=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    incident = relationship("Incident", back_populates="events")