import importlib.util
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


class MissionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        cls.saved = os.environ.get("ROOM_DB")
        os.environ["ROOM_DB"] = str(Path(cls.dir.name) / "room.sqlite3")
        spec = importlib.util.spec_from_file_location("testroom", Path(__file__).with_name("room.py"))
        cls.room = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.room)

    @classmethod
    def tearDownClass(cls):
        if cls.saved is None:
            os.environ.pop("ROOM_DB", None)
        if cls.saved is not None:
            os.environ["ROOM_DB"] = cls.saved
        cls.dir.cleanup()

    def setUp(self):
        self.client = self.room.app.test_client()

    def test_mission_ballot_and_expiry(self):
        response = self.client.post("/api/mission", json={"title": "Pick the demo moment", "owner": "Mina", "duration": 15})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["status"], "active")

        self.assertEqual(self.client.post("/api/items", json={"name": "Mina", "kind": "idea", "text": "Show the handoff before the timer ends."}).status_code, 201)
        self.assertEqual(self.client.post("/api/items", json={"name": "Leo", "kind": "blocker", "text": "The judging Wi-Fi may block multicast."}).status_code, 201)

        response = self.client.post("/api/synthesize")
        self.assertEqual(response.status_code, 200)
        action = response.get_json()["synthesis"]["actions"][0]
        self.assertEqual(self.client.post("/api/launch").status_code, 400)
        self.assertEqual(self.client.post("/api/votes", json={"name": "Mina", "action": action}).status_code, 400)

        self.assertEqual(self.client.post("/api/votes", json={"name": "Mina", "action": action, "participant": "mina-browser"}).status_code, 200)
        response = self.client.post("/api/votes", json={"name": "Mina again", "action": action, "participant": "mina-browser"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["votes"][0]["votes"], 1)

        self.assertEqual(self.client.post("/api/votes", json={"name": "Leo", "action": action, "participant": "leo-browser"}).status_code, 200)
        self.assertEqual(self.client.post("/api/items", json={"name": "Nia", "kind": "idea", "text": "Keep a deterministic offline demo path."}).status_code, 201)
        response = self.client.post("/api/synthesize")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/room").get_json()["votes"], [])
        action = response.get_json()["synthesis"]["actions"][0]
        self.assertEqual(self.client.post("/api/launch").status_code, 400)
        self.assertEqual(self.client.post("/api/votes", json={"name": "Mina", "action": action, "participant": "mina-browser"}).status_code, 200)
        response = self.client.post("/api/launch")
        self.assertEqual(response.status_code, 200)
        card = response.get_json()["launch"]
        self.assertEqual(card["mission"]["title"], "Pick the demo moment")
        self.assertEqual(card["mission"]["status"], "launched")
        self.assertEqual(card["actions"][0]["votes"], 1)

        response = self.client.post("/api/handoff")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Launch Card", response.get_json()["markdown"])

        with self.room.lock:
            self.room.room["mission"] = None
            self.room.room["synthesis"] = None
            self.room.room["votes"] = []
            self.room.room["launch"] = None
        self.room.loadroom()
        self.assertEqual(self.room.room["mission"]["status"], "launched")
        self.assertEqual(self.room.room["launch"]["owner"], "Mina")
        self.assertEqual(self.room.room["synthesis"]["actions"][0], action)

        response = self.client.post("/api/mission", json={"title": "Expired mission", "owner": "Nia", "duration": 5})
        self.assertEqual(response.status_code, 201)
        started = (datetime.now(timezone.utc) - timedelta(minutes=6)).isoformat()
        with self.room.database() as conn:
            conn.execute("UPDATE missions SET started_at = ? WHERE id = ?", (started, response.get_json()["id"]))
        with self.room.lock:
            self.room.room["mission"]["started_at"] = started
        state = self.client.get("/api/room").get_json()
        self.assertEqual(state["mission"]["status"], "expired")
        self.assertEqual(self.client.post("/api/votes", json={"name": "Nia", "action": action, "participant": "nia-browser"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
