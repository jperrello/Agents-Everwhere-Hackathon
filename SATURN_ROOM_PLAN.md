# Saturn Room
## One-line pitch

Saturn Room turns a Wi-Fi router into an ambient collaboration agent: join the network and enter a shared, local AI workspace with no AI account, API key, endpoint setup, or app install.

## Why this fits the theme

Saturn already moves AI out of the chatbox at the infrastructure layer. A router advertises nearby AI services with mDNS/DNS-SD, the same way a network exposes printers. Saturn Room adds the missing situated behavior: the router is the physical room's doorway, capability registry, and agent host.

## User experience

1. A person joins the `Saturn Room` Wi-Fi network.
2. Their OS presents its standard captive-portal sheet, like hotel Wi-Fi.
3. The portal opens the shared room board and they choose a display name.
4. They add an idea, question, blocker, or image; the agent continuously creates a live brief: decisions, open questions, risks, next actions, and a demo pitch.

The QR code is only a fallback for devices that do not present the portal sheet.

## Architecture

```text
phone joins Wi-Fi -> OpenWrt router + openNDS captive portal
                              |-> Saturn beacon: _saturn._tcp.local.
                              |-> Saturn Room companion service (laptop/Pi)
browser <-> WebSocket room board <-> Saturn discovery and model routing
```

- The router uses `openNDS` to announce the captive portal through normal connectivity detection and DHCP captive-portal metadata.
- Saturn continues to advertise locally available and cloud-backed endpoints, including capability and health information.
- A small companion service hosts the web UI, shared room state, and agent orchestration. This keeps concurrent UI and inference work off the resource-constrained router.
- Clients opt into the room through the browser; do not infer identity from MAC addresses or inspect private traffic.

## MVP

- Captive portal redirects to a polished local room board.
- Real-time shared cards for ideas and blockers.
- `Synthesize room` generates decisions, risks, actions, and a 30-second pitch from board content.
- Model/service status is visible: discovered, selected, failed over.
- Image input becomes available only when Saturn advertises a vision-capable endpoint.

## Demo beat

Join Wi-Fi, watch the agent space open, add a team idea from a phone, and show it becoming a shared action card. Start or stop a Saturn backend mid-demo: the room visibly discovers, adapts, or fails over without anyone changing configuration.

## Build order

1. Ship the room board and Saturn-backed synthesis locally.
2. Add WebSocket synchronization and service-status display.
3. Configure openNDS portal handoff on the router.
4. Rehearse discovery, join, and failover on the actual hardware.
