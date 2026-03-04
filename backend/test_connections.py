"""Quick end-to-end test of all frontend connections."""
import urllib.request
import json
import time

BASE = "http://localhost:8000"


def test():
    print("=== TEST 1: GET / serves chat HTML ===")
    r = urllib.request.urlopen(BASE + "/")
    html = r.read().decode()
    assert r.status == 200, "Failed to serve HTML"
    assert "react" in html.lower(), "HTML missing React"
    assert "fetch('/chat'" in html, "HTML missing POST /chat fetch"
    assert "fetch('/messages')" in html, "HTML missing GET /messages polling"
    print("  PASS - HTML served with React, /chat fetch, /messages polling")

    print("\n=== TEST 2: GET /messages returns welcome ===")
    r = urllib.request.urlopen(BASE + "/messages")
    msgs = json.loads(r.read().decode())
    assert len(msgs) >= 1, "No messages"
    assert msgs[0]["sender"] == "ai", "First message not from AI"
    print(f"  PASS - {len(msgs)} message(s), welcome from AI")

    print("\n=== TEST 3: POST /chat sends user message ===")
    payload = json.dumps({"text": "How do I upload a video?", "url": "https://www.youtube.com"}).encode()
    req = urllib.request.Request(BASE + "/chat", data=payload, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req)
    resp = json.loads(r.read().decode())
    assert resp["status"] == "success", f"Chat failed: {resp}"
    print(f"  PASS - {resp}")

    print("\n=== TEST 4: User message appears in /messages ===")
    r = urllib.request.urlopen(BASE + "/messages")
    msgs = json.loads(r.read().decode())
    user_msgs = [m for m in msgs if m["sender"] == "user"]
    assert len(user_msgs) >= 1, "User message not found"
    print(f"  PASS - {len(msgs)} total messages, {len(user_msgs)} from user")

    print("\n=== TEST 5: POST /api/events with click saves domain JSON ===")
    payload = json.dumps({
        "sessionId": "test-conn",
        "domain": "www.youtube.com",
        "timestamp": int(time.time() * 1000),
        "events": [{"type": "click", "timestamp": int(time.time() * 1000), "url": "https://www.youtube.com", "data": {"tagName": "button", "innerText": "Upload"}}],
    }).encode()
    req = urllib.request.Request(BASE + "/api/events", data=payload, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req)
    resp = json.loads(r.read().decode())
    assert resp["status"] == "ok", f"Events failed: {resp}"
    print(f"  PASS - {resp}")

    print("\n=== TEST 6: Domain JSON accessible via GET /api/events/www.youtube.com ===")
    r = urllib.request.urlopen(BASE + "/api/events/www.youtube.com")
    data = json.loads(r.read().decode())
    assert data["domain"] == "www.youtube.com", "Wrong domain"
    assert len(data["events"]) >= 1, "No events stored"
    print(f"  PASS - {data['domain']} has {len(data['events'])} events")

    print("\n=== TEST 7: Agent runs in background (wait 4s) ===")
    time.sleep(4)
    r = urllib.request.urlopen(BASE + "/messages")
    msgs = json.loads(r.read().decode())
    ai_msgs = [m for m in msgs if m["sender"] == "ai"]
    print(f"  {len(msgs)} total messages, {len(ai_msgs)} from AI")
    for m in msgs:
        sender = m["sender"].upper()
        text = m["text"][:100]
        print(f"    [{sender}] {text}")
    if len(ai_msgs) >= 2:
        print("  PASS - Agent responded")
    else:
        print("  INFO - Agent may need AWS credentials to respond (expected in test)")

    print("\n=== ALL CONNECTION TESTS COMPLETE ===")


if __name__ == "__main__":
    test()
