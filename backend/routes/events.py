import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from agent import run_agent

router = APIRouter(prefix="/api/events", tags=["events"])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class EventBatch(BaseModel):
    sessionId: str
    domain: str
    timestamp: int
    events: list[dict[str, Any]]


@router.post("")
def receive_events(batch: EventBatch, background_tasks: BackgroundTasks):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / f"{batch.domain}.json"

    if file_path.exists():
        existing = json.loads(file_path.read_text(encoding="utf-8"))
        existing["events"].extend(batch.events)
        existing["lastUpdated"] = batch.timestamp
        if batch.sessionId not in existing.get("sessionIds", []):
            existing.setdefault("sessionIds", []).append(batch.sessionId)
        file_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    else:
        data = {
            "domain": batch.domain,
            "sessionIds": [batch.sessionId],
            "createdAt": batch.timestamp,
            "lastUpdated": batch.timestamp,
            "events": list(batch.events),
        }
        file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    has_click = any(e.get("type") == "click" for e in batch.events)
    if has_click:
        background_tasks.add_task(run_agent, batch.domain)

    return {"status": "ok", "events_received": len(batch.events)}


@router.get("")
def list_sessions():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    sessions = []
    for f in sorted(DATA_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sessions.append({
                "domain": data.get("domain"),
                "eventCount": len(data.get("events", [])),
                "createdAt": data.get("createdAt"),
                "lastUpdated": data.get("lastUpdated"),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    return {"sessions": sessions, "total": len(sessions)}


@router.get("/{domain}")
def get_session(domain: str):
    file_path = DATA_DIR / f"{domain}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Domain data not found")

    return json.loads(file_path.read_text(encoding="utf-8"))
