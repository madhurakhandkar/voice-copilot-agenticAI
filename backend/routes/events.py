import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/events", tags=["events"])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class EventBatch(BaseModel):
    sessionId: str
    domain: str
    timestamp: int
    events: list[dict[str, Any]]


@router.post("")
def receive_events(batch: EventBatch):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / f"{batch.sessionId}.json"

    if file_path.exists():
        existing = json.loads(file_path.read_text(encoding="utf-8"))
        existing["events"].extend([e for e in batch.events])
        existing["lastUpdated"] = batch.timestamp
        file_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    else:
        data = {
            "sessionId": batch.sessionId,
            "domain": batch.domain,
            "createdAt": batch.timestamp,
            "lastUpdated": batch.timestamp,
            "events": list(batch.events),
        }
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {"status": "ok", "events_received": len(batch.events)}


@router.get("")
def list_sessions():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    sessions = []
    for f in sorted(DATA_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sessions.append({
                "sessionId": data.get("sessionId"),
                "domain": data.get("domain"),
                "eventCount": len(data.get("events", [])),
                "createdAt": data.get("createdAt"),
                "lastUpdated": data.get("lastUpdated"),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    return {"sessions": sessions, "total": len(sessions)}


@router.get("/{session_id}")
def get_session(session_id: str):
    file_path = DATA_DIR / f"{session_id}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Session not found")

    return json.loads(file_path.read_text(encoding="utf-8"))
