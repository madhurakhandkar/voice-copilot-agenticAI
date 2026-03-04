import time
from typing import List, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from agent import run_agent

router = APIRouter(tags=["chat"])


class Message(BaseModel):
    id: int
    sender: str
    text: str
    url: Optional[str] = None


class ChatInput(BaseModel):
    text: str
    url: Optional[str] = None


messages_db: List[Message] = [
    Message(
        id=1,
        sender="ai",
        text="Welcome. I am your learning companion. What tool or subject shall we master today? Please attach a URL to begin tracking your progress.",
    )
]


def get_domain(url: str) -> str | None:
    """Extract hostname from a URL string."""
    if not url:
        return None
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return urlparse(url).hostname
    except Exception:
        return None


@router.get("/messages", response_model=List[Message])
async def get_messages():
    return messages_db


@router.post("/chat")
async def receive_chat(chat_input: ChatInput, background_tasks: BackgroundTasks):
    user_msg = Message(
        id=int(time.time() * 1000),
        sender="user",
        text=chat_input.text,
        url=chat_input.url,
    )
    messages_db.append(user_msg)

    domain = get_domain(chat_input.url) if chat_input.url else None

    if domain:
        background_tasks.add_task(run_agent, domain, chat_input.text)
    else:
        ai_msg = Message(
            id=int(time.time() * 1000) + 1,
            sender="ai",
            text="Please provide a URL so I can track your activity and help you learn. Paste the website URL in the link field below.",
        )
        messages_db.append(ai_msg)

    return {"status": "success"}
