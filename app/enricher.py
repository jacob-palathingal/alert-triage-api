from app.models import Incident


def enrich_incident(incident: Incident) -> str | None:
    """
    Generates a plain-English incident summary.
    Currently uses a structured template — designed to be swapped for
    an LLM API call (OpenAI/Anthropic) with no changes to the calling code.
    """
    try:
        return (
            f"{incident.event_count} {incident.severity}-severity event(s) detected "
            f"on {incident.service} starting at {incident.started_at.strftime('%Y-%m-%d %H:%M UTC')}."
        )
    except Exception as e:
        print(f"[enricher] Enrichment failed: {e}")
        return None