---
title: 'Agent Desk: Plane tickets worked by bench-cloud agents'
number: '03-042'
category: 'homelab-automation'
difficulty: 'Hard'
time_commitment: '3-5 weeks (phase 1); 2-4 weeks (phase 2)'
target_skills:
  'Self-hosting (Plane CE, Matrix homeserver on Kubernetes), webhooks and REST APIs, Matrix bots,
  agent orchestration, playbook design, GitHub automation'
status: 'Not Started'
depends_on:
  - homelab/cnpg
  - homelab/bench-cloud
---

# Agent Desk: Plane tickets worked by bench-cloud agents

## Description

A home version of the Devin workflow George uses at work: write a plan, commit it to GitHub, turn it
into tickets, and let agents work the tickets into pull requests. The tracker is
**[Plane](https://plane.so)**, self-hosted on the homelab, because George wants Linear's UI and a
self-hosted service rather than a paid SaaS plan. The agents are the existing **bench-cloud** Jobs.

The loop:

```text
plan PR (docs/plans/)  ──merge──▶  planner agent  ──▶  Plane tickets (one project per repo)
                                                          │
                     playbook says auto, or George labels "ready"
                                                          ▼
                     dispatcher (webhook) ──▶ bench-cloud Job ──▶ PR linked to ticket
                                                          │
                    babysit + critique ──▶ ticket "In review" ──▶ George merges ──▶ "Done"
```

An agent that gets stuck asks its question as a **ticket comment** and parks the ticket in
"Blocked". George's reply on the ticket resumes it.

## Decisions (George, 2026-10-18)

- **Tracker: self-hosted Plane.** The draw is Linear's UI, so the tracker is Plane, not GitHub
  Issues.
- **Ready gate: per playbook.** Each playbook declares whether its tickets start on their own or
  wait for George's `ready` label.
- **Homelab repo out of scope for agent work** until bench-watch exists. Homelab merges are
  effectively cluster-admin, and nothing yet watches a rollout. Deploying Plane itself is ordinary
  homelab work through a normal PR.

## Design

### Plane on the homelab

- Plane Community Edition (AGPL-3.0), deployed through Flux like every other app, staging first.
- Postgres on CNPG. Redis/Valkey, RabbitMQ and S3-compatible object storage as Plane needs them;
  confirm the current component list against Plane's own self-hosting docs before writing manifests.
- Reached through the Cilium Gateway on a burntbytes.com hostname, LAN and VPN only to start.
- Backups: CNPG's S3 archive plus the object bucket. A restore is rehearsed before any real ticket
  lives there.

### Pieces to build

| Piece                | What it does                                                                                                                                                                                                                                              |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Planner**          | On a merged plan PR, reads `docs/plans/*.md` and drafts tickets: title, acceptance criteria, files likely touched, playbook. Opens them in "Triage" for George to accept.                                                                                 |
| **Dispatcher**       | Small service that receives Plane webhooks. When a ticket becomes startable under its playbook's rule, it launches a bench-cloud Job with the ticket as the brief. Respects the 5-Job quota and refuses to start a ticket that already has a running Job. |
| **Ticket ⇄ PR link** | The agent's PR names the ticket; the ticket gets the PR link and moves to "In review". Merge moves it to "Done".                                                                                                                                          |
| **Question loop**    | Agent comments a question and sets "Blocked"; a reply from George re-dispatches with the thread attached.                                                                                                                                                 |
| **Playbooks**        | A skill plus a ticket template: what the agent does, which repos it may touch, the ready rule, and how its work is verified.                                                                                                                              |
| **Automations**      | Triggers that create tickets without a plan: a failing main CI, a stale renovate hold, a recurring chore.                                                                                                                                                 |

### Talking to a running agent

Devin's Slack chat has no direct equivalent here. George doesn't use Slack outside work, and Claude
Code's Remote Control can't serve these Jobs: per the Remote Control docs it needs an interactive or
`claude remote-control` process signed in with a full claude.ai login, and it rejects the model-only
OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`) and API keys that headless Jobs use.

So **the ticket is the chat**, made live:

- George writes on the ticket from Plane's web or mobile app.
- While a Job runs, a Claude Code hook checks its ticket for new comments after each tool call and
  feeds them to the agent as input, so a comment lands mid-task, not only at the next dispatch.
- The agent answers on the ticket. Plane's notifications are the push channel.
- When no Job is running, a comment re-dispatches the ticket (the question loop above).

Everything said stays on the ticket, which is also the record. The hook reads from a **conversation
channel** interface, not from Plane directly, so phase 2 can swap in Matrix without rewriting it.

### Guardrails (non-negotiable)

- Agents never merge. Branch protection is never bypassed; George merges.
- Every agent PR gets a babysit and a critique pass before it reaches "In review".
- The homelab repo is on the dispatcher's deny list until bench-watch exists.
- The Plane API token the dispatcher holds is scoped to the workspace; it holds no GitHub write
  scope beyond what bench-cloud already has.
- Ticket text is untrusted input to the agent, the same as any issue body.

## Open questions

- Plane CE's built-in GitHub integration versus a custom link via webhooks: which exists in the
  self-hosted edition today? Verify before building the link piece.
- Whether Plane's MCP server is good enough for agents to read and update tickets directly, or the
  dispatcher should pass everything in the brief.
- Which playbooks start with auto-start. Candidates: dependency-hold investigation and docs-only
  fixes. Everything else waits for `ready`.

## Phase 2: sessions over Matrix

George, 2026-10-18: "Matrix feels like it would be the better long term fit for my needs. And then
we could also build sessions in top of it like sessions in Devin". Phase 1 ships first on ticket
comments; phase 2 moves the conversation to Matrix and adds Devin-style sessions.

### Matrix homeserver

- A homeserver on the homelab, deployed through Flux, staging first. Candidates: Synapse (mature,
  Postgres on CNPG) or a lighter Rust server. Choose after checking current support for Element X,
  the mobile app, which needs the newer sync API.
- Federation off and reachable on LAN and VPN only to start. Opening it up is a later, separate
  decision.
- Clients: Element on phone and desktop.
- Useful beyond agents: Matrix bridges (Signal, WhatsApp) could later carry homelab alerts, whose
  Signal routing was removed in 2026-06. Out of scope here; noted so the server choice doesn't rule
  it out.

### Sessions

- **One session is one Matrix room.** A session starts from a ticket (the dispatcher creates the
  room) or from chat (George messages the agent bot, e.g. "fix the flaky test in vitals").
- **The room is the live chat.** The phase-1 hook reads the room through the conversation channel
  interface; the agent posts progress, questions and the PR link back into it.
- **The ticket stays the record.** A session started from chat creates its Plane ticket
  automatically. The room links the ticket and the ticket links the room. Decisions made in chat are
  summarised onto the ticket when the session ends.
- **The session list is the room list:** active rooms are running sessions, archived rooms are
  finished ones.
- **Starting from chat goes through the same gate as tickets:** the playbook's ready rule, the Job
  quota, the dedupe check and the homelab deny list. Only George's Matrix account can start a
  session.

### Phase 2 risks

- **Encryption.** Encrypted rooms mean the bot must manage its own keys and device verification.
  Start with unencrypted rooms on the unfederated server; revisit once the loop works.
- **Bot identity.** The bot's Matrix access token is a new secret; it goes through SOPS like every
  other, operator-only.
- **Two records.** Chat and ticket can drift. The summary-onto-ticket step is what keeps the ticket
  authoritative; test it.

## Exit Criteria

- [ ] Plane runs on the homelab from Flux, staging then production, with a rehearsed restore.
- [ ] A merged plan PR produces draft tickets in Plane without manual copying.
- [ ] A startable ticket launches a bench-cloud Job, and the Job's PR is linked back to the ticket.
- [ ] An agent question on a ticket, answered by George, resumes the same work.
- [ ] A comment George writes on a ticket reaches its running Job mid-task, and the reply appears on
      the ticket.
- [ ] At least three playbooks exist, each declaring its own ready rule, and at least one runs on
      its own.
- [ ] One full project goes plan → tickets → merged PRs through the loop, with George merging every
      PR.
- [ ] The dispatcher provably refuses homelab-repo tickets and duplicate pickups.

Phase 2:

- [ ] A Matrix homeserver runs on the homelab from Flux, staging then production, with a rehearsed
      restore, reachable from Element on George's phone.
- [ ] Starting a ticket opens a room; a message there reaches the running Job and its reply appears
      in the room.
- [ ] Messaging the bot starts a session, which creates its own Plane ticket and passes the same
      gates as a ticket.
- [ ] A finished session's decisions are summarised onto its ticket, and the room is archived.

## Tasks

- [ ] Read Plane's current self-hosting docs; list components and versions
- [ ] Homelab PR: Plane on staging (CNPG, storage, Gateway route)
- [ ] Rehearse backup and restore; then production
- [ ] Write the planner as a bench-cloud skill
- [ ] Build the dispatcher (webhook receiver, quota, dedupe, deny list)
- [ ] Ticket ⇄ PR linking and state transitions
- [ ] Question loop
- [ ] Live chat: comment hook that feeds new ticket comments into a running Job
- [ ] First three playbooks
- [ ] Pilot on one real plan end to end

Phase 2:

- [ ] Choose the homeserver (check Element X support); homelab PR for staging
- [ ] Bot account and token (SOPS, operator-only)
- [ ] Matrix implementation of the conversation channel interface
- [ ] Session rooms: create from ticket, start from chat, archive and summarise on finish
- [ ] Pilot one session started from chat, end to end
