---
title: 'Whisper Fine-Tuned on My Voice and Vocabulary'
number: '03-039'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills:
  'Whisper LoRA fine-tuning (PEFT), word error rate measurement, CTranslate2 conversion for
  faster-whisper, rented-GPU training'
status: 'Not Started'
depends_on:
  - '03-037'
---

# Whisper Fine-Tuned on My Voice and Vocabulary

## Description

`03-037` deliberately starts with off-the-shelf models plus a vocabulary prompt and treats
fine-tuning as a fallback. This project is that fallback, done properly: a LoRA fine-tune of a
Whisper model on my own speech and my proper nouns (hestia, Talos, golinks, Vibrato), converted for
`faster-whisper` and served on the cluster CPUs like the stock model.

It only ships if it beats the prompted stock model on `03-037`'s benchmark — the benchmark is the
gate, not the fact that training worked.

## Data

- `03-037`'s fixed test set stays held out — never trained on.
- Training data: a few hours of me reading text dense with my vocabulary, plus HA-style commands. If
  `03-036`'s own-voice recordings exist, they are transcribed speech of me already.
- Recordings of my voice follow `03-036`'s rule: on hestia only, never in git.

## Where training runs

A rented 24 GB GPU via the same pattern as the `gjcourt/voice` harness (Runpod Secure Cloud, per-run
cap, guaranteed teardown). A LoRA on a `small` or `medium` Whisper should fit comfortably; measure
rather than assume.

## Exit Criteria

- [ ] Word error rate on `03-037`'s held-out set, fine-tuned vs prompted stock model, same size.
- [ ] If it wins: served on a cluster node with real-time factor measured, and selected in the
      Assist pipeline.
- [ ] If it doesn't: recorded here why, and the stock model stays.

## Plan

- [ ] Wait for `03-037` Phase 1's benchmark; only start if the prompt left a real gap.
- [ ] Record and transcribe the training set.
- [ ] Train the LoRA on a rented GPU; merge, convert to CTranslate2 int8.
- [ ] Benchmark against the prompted stock model; deploy only on a win.

## Related

- `03-037` — local STT, its benchmark and serving.
- `03-036` — the own-voice recordings and the training harness pattern.
