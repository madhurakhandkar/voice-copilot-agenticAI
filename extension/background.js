const BACKEND_URL = "http://localhost:8000/api/events";

let sessionId = null;

async function getSessionId() {
  if (sessionId) return sessionId;
  try {
    const result = await chrome.storage.session.get("sessionId");
    if (result.sessionId) {
      sessionId = result.sessionId;
    } else {
      sessionId = crypto.randomUUID();
      await chrome.storage.session.set({ sessionId });
    }
  } catch (_) {
    sessionId = crypto.randomUUID();
  }
  return sessionId;
}

function getDomain(url) {
  try {
    return new URL(url).hostname;
  } catch (_) {
    return "unknown";
  }
}

async function sendEvent(event) {
  const sid = await getSessionId();
  const domain = event.url ? getDomain(event.url) : "unknown";

  const payload = {
    sessionId: sid,
    domain: domain,
    timestamp: Date.now(),
    events: [event],
  };

  try {
    await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (_) {
    // Backend unreachable — event is dropped silently
  }
}

// Listen for events from content scripts and send immediately
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "track_event" && message.event) {
    sendEvent(message.event);
  }
  sendResponse({ ok: true });
});

// Initialize session ID eagerly
getSessionId();
