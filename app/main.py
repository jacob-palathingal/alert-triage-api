from fastapi import FastAPI
from app.database import engine, Base
from app.routers import events, incidents

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Alert Triage & Incident Summarization API",
    description=(
        "Ingests application logs and alerts, classifies them by severity, "
        "groups related events into incidents, and enriches incidents with "
        "plain-English summaries via the OpenAI API."
    ),
    version="0.1.0",
)

app.include_router(events.router)
app.include_router(incidents.router)



@app.get("/health", tags=["Health"])
def health_check():
    """Simple liveness check. Returns 200 if the API is running."""
    return {"status": "ok"}

@app.get("/", tags=["Root"])
def root():
    return {
        "service": "Alert Triage & Incident Summarization API",
        "docs": "/docs",
        "health": "/health"
    }