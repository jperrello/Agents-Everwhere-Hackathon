# Saturn Room

Saturn Room is a local, multi-person facilitation agent for a physical room. People join the room network, contribute notes from the shared board, and leave with a concrete team handoff. Saturn discovers the shared cloud-compatible AI service on the local network when one is available.

Saturn is pre-existing infrastructure. Saturn Room is the application built on top of it: shared state, live collaboration, diagnostic room pulses, and handoff. Saturn is not the point of the product; it is the room's model lane. The room remains useful without it, which is important for an event network demo.

## Run

```sh
python3 -m pip install -r requirements.txt
SATURN_HOST=192.168.8.50 SATURN_PORT=8400 SATURN_MODEL=your-cloud-model python3 room.py
```

`SATURN_HOST` is optional when mDNS discovery works. It is a direct cloud-endpoint fallback for a Saturn service reachable on the room network. You can also set `SATURN_DIRECT_URL` to an OpenAI-compatible `/v1` base URL and `OPENAI_API_KEY` for a configured cloud fallback.

Do not use a local Ollama or llama endpoint for this demo. If no Saturn service or cloud fallback is available, the board enters local brief mode: notes, pulse, and handoff still work deterministically, and the UI says that the model lane is offline.

Open the board from the room network at `http://<companion-lan-ip>:8000`. The app is bound to all interfaces. When `room.py` starts, it prints the LAN URL, advertises `saturn-room.local` over Bonjour, and prints a QR code for scanning from a phone. Scanning requires the phone to already be connected to the room Wi-Fi. Automatic opening after Wi-Fi association requires the router's captive portal configuration; `/portal` and `/.well-known/captive-portal` are provided for that integration.

The board is persisted in `saturn-room.sqlite3` by default. Set `ROOM_DB` to choose another database path and `ROOM_HOST` if the machine has multiple LAN addresses and the automatically selected address is not the room Wi-Fi address.

## Working demo features

- mDNS discovery of `_saturn._tcp.local.` services, with direct cloud fallback.
- Live shared updates through Server-Sent Events.
- Room notes from the browser, labeled by source, with comments and threaded replies.
- A fast AI board summary refreshed whenever a note arrives, preferring a discovered Haiku model. It summarizes and diagnoses the notes without inventing opportunities or commitments.
- A Room Pulse after every three notes: current situation, emerging decision, unresolved tension, and open question.
- A “Turn into actionable items” control that generates grounded, separate tasks from the current notes.
- Markdown/JSON handoff with decisions, volunteers, blockers, actions, and unresolved items.
- Generic connector ingestion endpoint for future Slack, Discord, Teams, and other adapters.
- Optional Exa web research with source links and a Saturn-generated research brief.
- Local brief mode so the end-to-end room workflow does not fail when mDNS or model inference is unavailable.

## The judging story

The demo is not “we found a model.” It is “a temporary room can create a shared, opted-in context and turn it into a usable handoff.” Saturn makes the model discoverable from the room network and lets the facilitator show a real failover story; the room board, approval boundary, and handoff are the application.

Suggested three-minute run:

1. Open the board on two devices and add an idea, question, and blocker as different people.
2. Show the live board and Room Pulse appearing without a page refresh.
3. Turn the pulse into actionable items, then create and download the handoff.
4. Retry Saturn discovery or stop the model lane. Explain that the room stays operational in local brief mode rather than losing the group's work.

## Web research

Set `EXA_API_KEY` in the companion service environment to enable the Web research panel. Without it, the room remains fully usable and reports that research is not configured. Research results stay separate from room commitments; Saturn summarizes them when a Saturn model is available.

## Connector demo ingress

The future connector layer can post an intentionally selected message into the room:

```sh
curl -X POST http://localhost:8000/api/connectors/slack/ingest \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alex","text":"We should test the local room flow","external_id":"demo-1"}'
```

Set `CONNECTOR_TOKEN` to require `Authorization: Bearer <token>`. Only connect explicitly configured channels. The board stays LAN-only; a connector can maintain an outbound connection to its service from the companion machine.

## Captive portal

The app now serves the common Apple, Android, and Windows connectivity-check paths (`/hotspot-detect.html`, `/generate_204`, `/ncsi.txt`, `/connecttest.txt`, and `/success.txt`) from the portal page. The router still must intercept those requests and redirect unauthenticated clients to this companion service. For openNDS, set the gateway interface and portal URL to the companion LAN address, then test with an iPhone that has cellular data temporarily disabled; the exact config varies by router firmware.

## Still to build

- Router-specific captive portal configuration and a real-room rehearsal.
- A Slack Socket Mode adapter using the connector ingress contract.
- Discord and Teams adapters using the same normalized note shape.
- Persistence and room identity for multiple rooms.
- Authentication and moderator controls for connector messages.
