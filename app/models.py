from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
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
    summary = Column(Text, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # One incident has many events
    events = relationship("Event", back_populates="incident")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, nullable=False, index=True)
    level = Column(String, nullable=False)        # raw log level 
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=True)      
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Foreign key to incidents
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    incident = relationship("Incident", back_populates="events")
