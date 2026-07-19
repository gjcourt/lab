---
title: 'SFPL Borrow-and-Rip Pipeline'
number: '03-029'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'Web-App Reverse-Engineering (BiblioCommons), Authenticated Session Automation, Taste-Ranked Queue
  Modeling, State-Tracking (sqlite/CSV), Lossless CD Ripping into Navidrome'
status: 'Not Started'
depends_on: ['03-028 media library', '03-026 rip pipeline']
---

# SFPL Borrow-and-Rip Pipeline

## Goal

Automate borrowing the SFPL-held albums from the [03-028](03-028-media-library-buildout.md) music
catalog so they can be ripped into **Navidrome**, ranked by the owner's actual taste, with a
deliberate **exploration stream** mixed in. The input queue is the ~127 SFPL-held albums surfaced in
03-028 **Track 3b** plus the **Track 3c** genre-gap buckets, taste-ranked. Where 03-028 decided
_which_ albums are worth acquiring and _from where_, and
[03-026](03-026-rip-owned-4k-uhd-blurays-to-nas-jellyfin.md) turns a disc into a correctly-named
file on the NAS, this project is the **acquisition-logistics engine** in between: it keeps a steady
stream of the right CDs flowing from the library shelf to the ripper without manual
queue-babysitting.

## SFPL constraints (current, verified via [sfpl.libanswers.com/faq/94381](https://sfpl.libanswers.com/faq/94381))

- **Holds: 30 max concurrent** — this is the real pacing constraint on the whole pipeline.
- **Checkouts: 100 max physical items** — shared with movies/DVDs and personal books, but
  effectively non-binding for the CD stream.
- **Loan: 21 days + up to 5 renewals** (~18 weeks total). Renewal auto-succeeds unless someone else
  has placed a hold on the item — rare for catalog CDs — so the ripping cycle is unhurried.
- Owner's local branch = **Sacramento St** (a 5-minute walk) → free, frequent pickups. Pickup is
  routed there for every hold.

The takeaway: **holds are scarce (30), checkouts and loan time are abundant.** The design squeezes
throughput out of the 30-hold ceiling while letting checked-out discs sit as long as needed to rip
at leisure.

## Design — two-stage queue

```text
taste-ranked queue → Holds (≤30) → Checkouts (≤100) → rip → return
```

Keep **30 holds in flight** at all times, pulled off the top of the taste-ranked queue. When a hold
comes ready and gets picked up, it converts to a **checkout** and frees a hold slot → immediately
**refill back to 30** from the queue. The result is **waves of ~30 albums**: rip at leisure,
auto-renew anything not yet ripped, return when done, refill the freed slots. The 30-hold ceiling
becomes a rolling window rather than a hard batch limit.

## Automation (owner chose the AUTOMATED route)

- **v1 target = full-auto hold placement** via **BiblioCommons** (`sfpl.bibliocommons.com`):
  establish an authenticated session (library card # + PIN), then issue a place-hold POST per bib
  with **pickup branch = Sacramento St**. The same session also **auto-renews** due items and
  **detects ready-for-pickup** state to trigger refills.
- **Caveats — document honestly:**
  - BiblioCommons has **no official public API**. The login / hold / renew flow must be
    reverse-engineered from the web app. The search endpoint is already known
    (`?f_FORMAT=MUSIC_CD`); the write flows are not yet mapped.
  - Fragile surface: CSRF tokens, session cookies, or a CAPTCHA can appear and break the flow. Treat
    breakage as expected and fail loudly.
  - **Store credentials in env/secret, never in the repo.**
  - **Personal use only. Throttle politely** — human-paced request rate, no scraping bursts.
- **Fallback = semi-auto:** if full-auto breaks, generate the next **30 one-click hold deep-links**
  (pickup branch pre-set) that the owner clicks through manually. Same queue, degraded automation.

## Taste ranking

Lead lanes: **Jazz / Swing** and **Funk-Soul** first, then **Classic Rock / Blues**. Hip-hop is
**capped to the canon** (no deep-cut fan-out). Reserve **~20% of each wave for exploration picks**
drawn from cold zones the owner rarely listens to (**Electronic / Classical / World**) — a
deliberate discovery stream rather than pure preference reinforcement. The ranking reads from the
**taste profile built from the owner's Spotify export**.

## Tool components

Lives in `~/src/utility/` alongside `valet` and `portfolio`.

1. **Queue ranker** — reads the 03-028 catalog and emits a taste-ranked queue of the SFPL-held
   albums (taste lanes + the ~20% exploration allotment).
2. **Hold placer** — BiblioCommons authenticated session + place-hold POST (pickup = Sacramento St),
   or the one-click deep-link generator in the semi-auto fallback.
3. **State tracker** — sqlite or CSV persisting each album through
   `queued → held → ready → checked-out → ripped → returned`.
4. **Ready/renewal surfacer** — flags items ready for pickup (→ refill a hold slot) and items
   nearing their due date that still need renewing.

## SFPL availability reality

SFPL is strong on the **rock / classical / jazz canon** but **thin on the owner's core lanes**:
funk/soul is only **7 of 30** held, electronic only **8 of 35**. Those two lanes should be flagged
**"buy used elsewhere"** (LINK+, discogs, lossless digital) rather than waited on — the pipeline
handles the **borrowable subset only** and shouldn't stall the queue chasing discs SFPL doesn't
stock.

## Exit Criteria

The pipeline reliably keeps the owner's taste-ranked SFPL queue flowing into Navidrome with minimal
manual babysitting:

- [ ] **Queue ranker built** — reads the 03-028 catalog, applies taste lanes + ~20% exploration,
      emits a ranked held-album queue.
- [ ] **Hold placement working** — full-auto BiblioCommons place-hold (pickup = Sacramento St), or
      the semi-auto one-click deep-link fallback verified end-to-end.
- [ ] **State tracker** — persists every album through queued → held → ready → checked-out → ripped
      → returned.
- [ ] **First 30-hold wave placed** — the hold window is saturated at 30 off the top of the queue.
- [ ] **First rip cycle completed** — a ready hold → checkout → FLAC rip → Navidrome → returned,
      with the freed slot auto-refilled.
- [ ] **Renewal handling verified** — an un-ripped due item auto-renews and stays checked out.

## Progress

- **2026-07-09** — Design pinned (this doc). Input queue = 03-028 Track 3b (~127 SFPL-held albums) +
  Track 3c gap buckets. Automated route chosen; BiblioCommons write-flow reverse-engineering not yet
  started. No code written.

## Related

- Catalog / acquisition source of truth (the input queue):
  [03-028 — Household Media Library Build-Out](03-028-media-library-buildout.md)
- Rip pipeline (disc → correctly-named file on the NAS):
  [03-026 — Rip Owned 4K UHD Blu-rays to the NAS](03-026-rip-owned-4k-uhd-blurays-to-nas-jellyfin.md)
- CD-rip step for this pipeline (audio disc → AccurateRip FLAC in the music library):
  [03-032 — Audio CD Ripping on macOS](03-032-audio-cd-ripping-macos.md)
