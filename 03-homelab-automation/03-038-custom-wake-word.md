---
title: 'Custom Wake Word (my own phrase, detected on the satellite)'
number: '03-038'
category: 'homelab-automation'
difficulty: 'Easy'
time_commitment: '1-2 days'
target_skills:
  'microWakeWord / openWakeWord training, synthetic speech data, false-accept vs false-reject
  tuning, ESPHome'
status: 'Not Started'
depends_on:
  - '03-037'
---

# Custom Wake Word (my own phrase, detected on the satellite)

## Description

Replace the stock wake words ("Okay Nabu", "Hey Jarvis") with a phrase I choose, detected on the
voice satellite itself so no audio leaves it before the wake word.

Wake-word models are small and cheap to train. Both projects worth trying train largely on
**synthetic** speech — many TTS voices saying the phrase, mixed with background noise — so a few
real recordings of the household saying it are a top-up, not the bulk of the data:

- **microWakeWord** — runs on ESP32-S3 satellites (Home Assistant Voice Preview Edition); what
  `03-037` Phase 3 already assumes for on-device detection.
- **openWakeWord** — runs on a CPU host instead of the device, so the satellite streams audio to
  that host continuously. That breaks the "nothing leaves before the wake word" property above (and
  `03-037`'s risk), so it's a last-resort fallback, not an equal option.

Confirm each project's current training recipe before starting; this area moves quickly.

## Risks

**False accepts are worse than false rejects.** A wake word that fires on TV dialogue sends room
audio to STT. Measure false accepts per hour on a long recording of normal household sound before
deploying, not just whether it wakes when called.

**Phrase choice.** Three or four syllables, uncommon sounds, not a name anyone in the house is
called.

## Exit Criteria

- [ ] A custom phrase detected on at least one satellite, on-device.
- [ ] False accepts measured on several hours of ordinary household audio, at a rate I accept.
- [ ] Wakes reliably for everyone in the household, from across the room.

## Plan

- [ ] Pick the phrase; check the current microWakeWord training recipe.
- [ ] Train (a laptop or one cheap rented GPU is enough), with a few real household recordings.
- [ ] Measure false accepts and rejects; tune the threshold; flash one satellite.

## Related

- `03-037` — local STT and the satellites this runs on.
- `03-036` — local TTS; the reply side of the same pipeline.
