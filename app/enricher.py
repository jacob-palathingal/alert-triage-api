import os
from openai import OpenAI
from app.models import Incident

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def enrich_incident(incident: Incident, triggering_message: str) -> str | None:
    """
    Calls the OpenAI API to generate a plain-English incident summary
    based on the raw log message that triggered the incident.
    Non-critical — if it fails, ingestion continues and summary stays null.
    """
    try:
        prompt = (
            f"You are an on-call engineer triaging a production incident. "
            f"Based on the log message below, write one concise sentence describing "
            f"what is likely happening and what the engineer should investigate first. "
            f"Do not restate the log message — interpret it.\n\n"
            f"Service: {incident.service}\n"
            f"Severity: {incident.severity}\n"
            f"Log message: {triggering_message}\n"
            f"Event count: {incident.event_count}\n"
            f"Started: {incident.started_at}\n"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"[enricher] OpenAI API call failed: {e}")
        return None