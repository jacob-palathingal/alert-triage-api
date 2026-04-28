from app.schemas import EventCreate


# Keywords that indicate high severity regardless of log level
HIGH_KEYWORDS = [
    "timeout", "connection refused", "out of memory", "oom",
    "disk full", "no space left", "fatal", "crash", "panic",
    "unauthorized", "forbidden", "certificate expired"
]

# Keywords that indicate medium severity
MEDIUM_KEYWORDS = [
    "retry", "retrying", "slow", "degraded", "high latency",
    "queue full", "rate limit", "deprecated", "failed attempt"
]


def classify(event: EventCreate) -> str:
    """
    Assigns a severity level to an incoming event using rule-based logic.
    Rules are evaluated in order — first match wins.

    Returns: "high", "medium", or "low"
    """
    level = event.level.upper()
    message = event.message.lower()

    # Rule 1: Critical log levels are always high
    if level in ("CRITICAL", "FATAL", "EMERGENCY"):
        return "high"

    # Rule 2: ERROR level is high by default
    if level == "ERROR":
        return "high"

    # Rule 3: Any level with a high-severity keyword gets bumped to high
    if any(keyword in message for keyword in HIGH_KEYWORDS):
        return "high"

    # Rule 4: WARN level is medium by default
    if level in ("WARN", "WARNING"):
        return "medium"

    # Rule 5: Any level with a medium-severity keyword gets bumped to medium
    if any(keyword in message for keyword in MEDIUM_KEYWORDS):
        return "medium"

    # Rule 6: Everything else is low
    return "low"