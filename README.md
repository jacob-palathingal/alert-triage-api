# Alert Triage & Incident Summarization API

A backend service that ingests application logs and alerts, classifies them by severity, groups related events into incidents, and enriches incidents with plain-English summaries via the Claude API.

**Stack:** Python, FastAPI, PostgreSQL, Docker, Claude API, Railway

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/alert-triage-api.git
cd alert-triage-api

# 2. Copy env file and fill in your values
cp .env.example .env

# 3. Start PostgreSQL via Docker
docker compose up -d db

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the API
uvicorn app.main:app --reload
```

API docs available at http://localhost:8000/docs

## Live URL
Coming soon.
