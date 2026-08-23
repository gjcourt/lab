---
title: 'Household Chat Service (open-webui on a hosted API backend)'
number: '03-034'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills: 'open-webui, API translation layers, Gateway API auth, cost control'
status: 'Not Started'
---

# Household Chat Service (open-webui on a hosted API backend)

## Description

Restore `chat.burntbytes.com` — a self-hosted chat UI the whole household can use — on a hosted API
backend instead of local GPU inference.

It has been scaled to zero since the 2× RTX 4090 were sold. The deployment manifest still carries
the reason in a comment: the local inference endpoint is gone, restore replicas once a backend
exists. `STATUS.md` already names the two options: new GPU hardware, or a hosted API.

## Why this rather than everyone using the vendor's own app

A personal subscription covers one person's chat and covers it better. The case for self-hosting is
**multiple people off one credit pool**: a second seat costs real money every month, whereas a
shared backend converts an employer learning budget into household utility. That is the whole
argument, and it collapses if only one person uses it.

Adoption is therefore the risk, not cost. Household services die from nobody using them far more
often than from running out of money. The honest first milestone is _someone other than the person
who built it uses it unprompted for a week_.

## Economics

Roughly, for two people at twenty turns a day each:

| Model tier | Approx. annual |
| ---------- | -------------- |
| Frontier   | ~$330          |
| Mid        | ~$200          |
| Small      | ~$60           |

Default to the mid tier and keep the frontier model selectable. Household questions do not need the
expensive model, and the difference is close to a factor of two on the runway.

## What has to be true before it serves traffic

**The gateway auth layer cannot be assumed to be enforcing.** There is a known upstream issue with
HTTP filter injection into Gateway API listeners, and a standing TODO tracking it. Verify
enforcement by request before relying on it — do not infer it from the config being correct.

That makes the application's own auth settings load-bearing. And those settings are read from
environment **on first launch only**, then served from a database on the persistent volume — which
already holds state from the previous run. Forcing a re-read is a one-variable difference between
hardening that works and hardening that only looks right in Git.

A spend limit set on the API account is the second control: exceeding a self-set limit fails the
request rather than draining the balance.

## Exit Criteria

- [ ] `chat.burntbytes.com` serves a working chat backed by a hosted API.
- [ ] A second household member has used it unprompted for a week without being reminded.
- [ ] Unauthenticated access is refused — demonstrated by request, not by reading config.
- [ ] A spend limit is set on the API account below the credit balance.
- [ ] Default model is the mid tier, with the frontier model selectable.
- [ ] Monthly spend recorded here after the first full month.

## Tasks

- [ ] Land the auth hardening (app-layer settings, forced re-read, SSO rule for when it works again)
- [ ] Choose the translation layer — the API is not OpenAI-compatible and the UI speaks OpenAI. An
      in-house multiplexer already exists and is the obvious candidate over a third-party proxy
- [ ] Land the API key as an encrypted secret
- [ ] Bump the container image off a pin that is four months stale
- [ ] Restore replicas and verify unauthenticated access is actually refused
- [ ] Set the account spend limit
- [ ] Onboard one other household member and leave it alone for a week

## Related

- `03-033` — the same credit pool funds the dependency review agent, which is a far smaller
  consumer. If both run, this is the one that determines whether the balance is used.
