# Saturn Room MVP

This is intentionally a minimal two-code-file prototype:

- `server.py` owns the shared in-memory room, direct DNS-SD Saturn discovery, AI synthesis,
  and the HTTP API.
- `index.html` is the shared room board.
- `requirements.txt` contains dependencies; it is not application code.

The client does not use `saturn-ai`. It uses `zeroconf` to browse
`_saturn._tcp.local.`, resolve each service, read its TXT metadata, and probe
`/v1/models`. Set `SATURN_DIRECT_URL` if multicast discovery is blocked.

## MVP scope

The demo should let multiple browser tabs add ideas, questions, and blockers to
one shared room. Pressing **Synthesize room** should produce decisions, risks,
open questions, next actions, and a short pitch.

Saturn discovers an OpenAI-compatible endpoint on the local network. A direct
endpoint fallback is available if mDNS is unavailable at the venue.

The following are intentionally deferred: OpenWrt configuration, captive
portal implementation, WebSockets, images, authentication, persistence,
multiple rooms, and a full failover UI.

## Intended run command

```sh
python3 -m pip install -r requirements.txt
python3 server.py
```

Optional fallback configuration:

```sh
SATURN_DIRECT_URL=http://localhost:11434 SATURN_MODEL=llama3.2 python3 server.py
```

Then open `http://localhost:8000`. For phone testing, open the computer's LAN
address on the same network. A QR code can be added later; it is not required
to prove the core workflow.
