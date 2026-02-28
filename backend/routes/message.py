from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Enable CORS so the HTML file can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Message(BaseModel):
    id: int
    sender: str
    text: str
    url: Optional[str] = None

class ChatInput(BaseModel):
    text: str
    url: Optional[str] = None

# In-memory database
messages_db: List[Message] = [
    Message(id=1, sender="ai", text="Welcome. I am your learning companion. What tool or subject shall we master today? Please attach a URL to begin tracking your progress.")
]

# Request 1: Display messages on frontend
@app.get("/messages", response_model=List[Message])
async def get_messages():
    return messages_db

# Request 2: Take in frontend API request
@app.post("/chat")
async def receive_chat(chat_input: ChatInput):
    # Save user message
    user_msg = Message(id=int(time.time() * 1000), sender="user", text=chat_input.text, url=chat_input.url)
    messages_db.append(user_msg)
    
    # Generate AI response
    ai_msg = Message(id=int(time.time() * 1000) + 1, sender="ai", text=f"I have received your input regarding {chat_input.url if chat_input.url else 'this topic'}. Processing request...")
    messages_db.append(ai_msg)
    
    return {"status": "success"}