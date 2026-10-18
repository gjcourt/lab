---
title: 'Agent Desk: Plane tickets worked by bench-cloud agents'
number: '03-042'
category: 'homelab-automation'
difficulty: 'Hard'
time_commitment: '3-5 weeks'
target_skills:
  'Self-hosting (Plane CE on Kubernetes), webhooks and REST APIs, agent orchestration, playbook
  design, GitHub automation'
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

```
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

## Exit Criteria

- [ ] Plane runs on the homelab from Flux, staging then production, with a rehearsed restore.
- [ ] A merged plan PR produces draft tickets in Plane without manual copying.
- [ ] A startable ticket launches a bench-cloud Job, and the Job's PR is linked back to the ticket.
- [ ] An agent question on a ticket, answered by George, resumes the same work.
- [ ] At least three playbooks exist, each declaring its own ready rule, and at least one runs on
      its own.
- [ ] One full project goes plan → tickets → merged PRs through the loop, with George merging every
      PR.
- [ ] The dispatcher provably refuses homelab-repo tickets and duplicate pickups.

## Tasks

- [ ] Read Plane's current self-hosting docs; list components and versions
- [ ] Homelab PR: Plane on staging (CNPG, storage, Gateway route)
- [ ] Rehearse backup and restore; then production
- [ ] Write the planner as a bench-cloud skill
- [ ] Build the dispatcher (webhook receiver, quota, dedupe, deny list)
- [ ] Ticket ⇄ PR linking and state transitions
- [ ] Question loop
- [ ] First three playbooks
- [ ] Pilot on one real plan end to end
