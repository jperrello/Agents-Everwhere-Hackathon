import json
import os
import threading
import urllib.request
from datetime import datetime, timezone
from uuid import uuid4

from flask import Flask, jsonify, request, send_file
from openai import OpenAI
from zeroconf import ServiceBrowser, ServiceInfo, ServiceListener, Zeroconf

app = Flask(__name__)
lock = threading.Lock()
room = {"items": [], "synthesis": None, "saturn": {"status": "not checked", "service": None, "endpoint": None, "model": None}}


def props(info):
    return {key.decode(): value.decode(errors="replace") for key, value in info.properties.items()}


def url(info, data):
    host = info.server.rstrip(".")
    path = data.get("path", "").strip()
    endpoint = f"{data.get('scheme', 'http')}://{host}:{info.port}"
    return endpoint + (f"/{path.lstrip('/')}" if path else "")


class Listener(ServiceListener):
    def __init__(self, zc):
        self.zc = zc
        self.services = []

    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            self.services.append((name, info))

    def update_service(self, zc, type_, name):
        self.add_service(zc, type_, name)

    def remove_service(self, zc, type_, name):
        return


def models(endpoint):
    target = endpoint.rstrip("/")
    if not target.endswith("/v1"):
        target += "/v1"
    try:
        with urllib.request.urlopen(f"{target}/models", timeout=2) as response:
            data = json.load(response)
        return target, data.get("data", [{}])[0].get("id")
    except (OSError, ValueError, IndexError, KeyError):
        return None, None


def discover():
    zc = Zeroconf()
    listener = Listener(zc)
    browser = ServiceBrowser(zc, "_saturn._tcp.local.", listener)
    try:
        import time
        time.sleep(2)
        choices = []
        for name, info in listener.services:
            data = props(info)
            endpoint, model = models(url(info, data))
            if endpoint:
                try:
                    priority = int(data.get("priority", data.get("prio", "100")))
                except ValueError:
                    priority = 100
                choices.append((priority, name, endpoint, model, data))
        if not choices:
            return None
        priority, name, endpoint, model, data = sorted(choices, key=lambda item: item[0])[0]
        return {"status": "discovered", "service": name.rstrip("."), "endpoint": endpoint, "model": model or data.get("model"), "priority": priority}
    finally:
        browser.cancel()
        zc.close()


def direct():
    endpoint = os.getenv("SATURN_DIRECT_URL", "").strip()
    if not endpoint:
        return None
    endpoint, model = models(endpoint)
    if not endpoint:
        return None
    return {"status": "direct fallback", "service": "SATURN_DIRECT_URL", "endpoint": endpoint, "model": model}


def update_saturn():
    selected = discover() or direct() or {"status": "unavailable", "service": None, "endpoint": None, "model": None}
    with lock:
        room["saturn"] = selected
    return selected


def synthesize():
    with lock:
        items = list(room["items"])
        selected = dict(room["saturn"])
    if not selected.get("endpoint"):
        update_saturn()
        selected = dict(room["saturn"])
    if not selected.get("endpoint"):
        raise RuntimeError("No Saturn endpoint was found. Set SATURN_DIRECT_URL for a manual fallback.")
    if not items:
        raise ValueError("Add at least one room item before synthesizing.")
    notes = "\n".join(f"[{item['kind']}] {item['text']}" for item in items)
    prompt = "You are the facilitator for a hackathon room. Return only valid JSON with string-array keys decisions, risks, questions, actions, and string key pitch. Be concise and concrete.\n\nRoom notes:\n" + notes
    client = OpenAI(base_url=selected["endpoint"], api_key=os.getenv("OPENAI_API_KEY", "saturn-room"))
    result = client.chat.completions.create(model=os.getenv("SATURN_MODEL") or selected.get("model") or "gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.2)
    content = (result.choices[0].message.content or "{}").strip().removeprefix("```json").removesuffix("```").strip()
    brief = json.loads(content)
    with lock:
        room["synthesis"] = brief
    return brief


@app.get("/")
def home():
    return send_file("index.html")


@app.get("/api/room")
def getroom():
    with lock:
        return jsonify(room)


@app.post("/api/items")
def additem():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    kind = data.get("kind", "idea")
    if not text or kind not in {"idea", "question", "blocker"}:
        return jsonify({"error": "A non-empty text and valid kind are required."}), 400
    item = {"id": str(uuid4()), "name": str(data.get("name", "Guest")).strip() or "Guest", "kind": kind, "text": text, "created_at": datetime.now(timezone.utc).isoformat()}
    with lock:
        room["items"].append(item)
    return jsonify(item), 201


@app.post("/api/synthesize")
def runsynthesis():
    try:
        return jsonify({"synthesis": synthesize(), "saturn": room["saturn"]})
    except (RuntimeError, ValueError, json.JSONDecodeError, OSError) as error:
        return jsonify({"error": str(error)}), 503


@app.post("/api/discover")
def run_discovery():
    return jsonify(update_saturn())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
