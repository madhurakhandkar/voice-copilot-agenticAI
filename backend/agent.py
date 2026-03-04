import json
import time
import logging
from pathlib import Path

from aimodels import claude3_tuff

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"

SYSTEM_PROMPT = """You are a learning curve assistant helping a user learn how to use a website or software tool.

You receive a complete log of the user's browsing activity: every click, navigation, scroll, and time spent on each page.

Your job:
1. Analyze what the user just did (their latest action).
2. Determine if they are on the right track, going in circles, or doing something premature/incorrect.
3. Tell them what to do next in plain, friendly language.

Keep your explanation concise (2-3 sentences max). Be encouraging but direct."""


def run_agent(domain: str, user_query: str | None = None):
    """Read the domain's event JSON, call claude3_tuff, append AI response to messages_db."""
    from routes.message import messages_db, Message

    data_file = DATA_DIR / f"{domain}.json"
    if not data_file.exists():
        logger.warning("No data file for domain %s", domain)
        return

    browsing_data = data_file.read_text(encoding="utf-8")

    query_part = user_query if user_query else "The user just performed a new action. Analyze their progress."

    user_message = f"User query: {query_part}\n\nComplete browsing activity log:\n{browsing_data}"

    conversation = [{"role": "user", "content": user_message}]

    try:
        result = claude3_tuff(SYSTEM_PROMPT, conversation, max_tokens=500, temperature=0.3)
    except Exception as e:
        logger.error("Agent call failed: %s", e)
        ai_msg = Message(
            id=int(time.time() * 1000),
            sender="ai",
            text=f"I encountered an error while analyzing your activity: {e}",
        )
        messages_db.append(ai_msg)
        return

    if isinstance(result, dict) and "error" not in result:
        explanation = result.get("explanation", "")
        current_step = result.get("current_step", "")
        action_status = result.get("action_status", "")
        next_action = result.get("next_action", "")

        text = explanation
        if current_step:
            text = f"**Step:** {current_step}\n**Status:** {action_status}\n\n{explanation}\n\n**Next:** {next_action}"

        ai_msg = Message(id=int(time.time() * 1000), sender="ai", text=text)
        messages_db.append(ai_msg)
    elif isinstance(result, dict) and "error" in result:
        ai_msg = Message(
            id=int(time.time() * 1000),
            sender="ai",
            text=f"I had trouble analyzing that: {result['error']}",
        )
        messages_db.append(ai_msg)
    else:
        ai_msg = Message(
            id=int(time.time() * 1000),
            sender="ai",
            text=str(result),
        )
        messages_db.append(ai_msg)
