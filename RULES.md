# Saturn Room rules

## What this project is

Saturn Room is a local, multi-person facilitation agent for a physical room. People who choose to join the room contribute ideas, questions, and blockers from their devices. The agent turns that shared, opted-in context into decisions, risks, open questions, next actions, and a short pitch.

The core workflow is:

1. A person joins the room through its local network entry point.
2. They choose to add a note to the shared board.
3. Everyone in the room sees the shared board.
4. The room agent synthesizes the contributed notes into a useful handoff.

## What Saturn is

Saturn is pre-existing infrastructure created before this hackathon. It is a protocol and implementation for discovering OpenAI-compatible AI endpoints on a local network with DNS-SD/mDNS.

Saturn is a building block for Saturn Room, not the submitted project. Treat it like a library, framework, or service dependency. Do not claim that Saturn's protocol, router work, model discovery, service failover, or thesis research was created during the hackathon.

## What was built for Saturn Room

- The shared room-board experience and browser interface.
- The room-state API for ideas, questions, and blockers.
- The facilitation prompt and structured synthesis into decisions, risks, questions, actions, and a pitch.
- The integration that selects a local Saturn-discovered model endpoint or a configured direct fallback.
- The event-focused deployment and demo workflow.

## Eligibility statement

Existing templates, libraries, reusable components, prompts, and infrastructure are permitted. Saturn Room must be presented as a distinct application whose core functionality was built during the event—not as a resubmission or extension of Saturn itself.

Use this wording when needed:

> Saturn was pre-existing thesis work used as the local endpoint-discovery substrate. During the hackathon, we built Saturn Room: the multi-user room experience, shared state, facilitation workflow, synthesis interface, and event-network demo.

## Network and privacy rules

- Joining Wi-Fi does not give Saturn Room permission to inspect traffic, read devices, infer identity, or collect MAC addresses.
- The network is an invitation and local delivery mechanism, not a surveillance tool.
- Only notes deliberately submitted through the room interface become agent context.
- A captive portal may open the room page, but participation is voluntary.

## Demo truthfulness

Demo only features that work in the environment. State clearly when Saturn discovery succeeds, when a direct fallback is being used, and when a router/captive-portal behavior is not configured. Do not imply that the system sees everything happening on the Wi-Fi network.

## Why the room matters

The environment is not decoration: it supplies a zero-setup, shared entry point for people co-located in the same temporary workspace. The agent operates on a group-created room context and produces a group handoff. That is the value that a standalone one-person chatbot does not provide.
