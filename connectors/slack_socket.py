import json
import os
import urllib.request

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


room = os.getenv("ROOM_URL", "http://127.0.0.1:8000").rstrip("/")
channel = os.getenv("CONNECTOR_CHANNEL_ID", "").strip()
token = os.getenv("CONNECTOR_TOKEN", "").strip()
app = App(token=os.environ["SLACK_BOT_TOKEN"])


def post(event):
    if channel and event.get("channel") != channel:
        return
    if event.get("subtype") or event.get("bot_id") or not event.get("text", "").strip():
        return
    body = json.dumps({
        "name": event.get("user", "Slack guest"),
        "text": event["text"].strip(),
        "kind": "idea",
        "external_id": event.get("client_msg_id") or event.get("ts"),
    }).encode()
    request = urllib.request.Request(f"{room}/api/connectors/slack/ingest", data=body, headers={"Content-Type": "application/json"})
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=5):
        return


@app.event("message")
def message(body, logger):
    try:
        post(body.get("event", {}))
    except Exception as error:
        logger.error("Could not forward Slack message: %s", error)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
