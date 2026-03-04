from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from routes.events import router as events_router
from routes.message import router as message_router

app = FastAPI(title="Learning Curve Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)
app.include_router(message_router)

CHAT_HTML = Path(__file__).resolve().parent.parent / "chatPage" / "firstDraft.html"


@app.get("/", response_class=HTMLResponse)
def serve_chat():
    return CHAT_HTML.read_text(encoding="utf-8")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
