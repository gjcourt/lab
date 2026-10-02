---
title: 'Local Speech-to-Text (Home Assistant commands and dictation on CPU)'
number: '03-037'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills:
  'Wyoming protocol, Home Assistant Assist pipeline, ASR benchmarking (real-time factor, word error
  rate), ESPHome voice satellites'
status: 'Not Started'
depends_on:
  - homelab/home-assistant
  - homelab/talos
---

# Local Speech-to-Text (Home Assistant commands and dictation on CPU)

## Description

Transcribe speech locally, fast enough for interactive use, for two jobs:

- **Home Assistant commands** — "turn off the office lights", "is the garage door open?".
- **Open dictation** — free-form speech for the eventual spoken assistant and for notes.

Same constraint as `03-036`: **no GPU in the cluster**, so everything runs on the cluster CPUs.
Unlike TTS, the starting assumption is that nothing needs training on my voice — off-the-shelf
models are expected to handle a single adult English speaker well enough, and the benchmark checks
that. The work is choosing models by measurement and wiring them into Home Assistant.

## Two jobs, two kinds of model

| Job                    | Candidate                                          | Why                                                                                                                                                                        |
| ---------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **HA commands**        | **Speech-to-Phrase** (Open Home Foundation)        | Recognizes only phrases built from my actual entities and areas, so it's fast and accurate on a modest CPU — but it can't transcribe arbitrary speech.                     |
| **Open dictation**     | **faster-whisper** via `wyoming-faster-whisper`    | Whisper on CTranslate2, int8 on CPU. Small/base for snappy turns; large-v3-turbo if accuracy matters more than latency.                                                    |
| Benchmark alternatives | **NVIDIA Parakeet** via sherpa-onnx; **Moonshine** | Both pitched as fast on CPU — Parakeet TDT v2 is English-only and v3 covers 25 European languages; Moonshine targets short edge utterances. In the benchmark, not assumed. |

An Assist pipeline has one STT engine; Home Assistant has no built-in "try Speech-to-Phrase, fall
back to Whisper" (as of a March 2026 community thread). Community workarounds exist — a Wyoming
`stt-fallback` add-on and an ASR proxy — so the choice is one pipeline per job, or a fallback proxy
in front of both; the benchmark decides whether the proxy is worth it. Confirm each project's
current repository and Wyoming support before Phase 1; this area moves quickly (Speech-to-Phrase's
development has moved to a rewrite in `OHF-Voice/apps`, and `wyoming-faster-whisper` now offers
other backends, including sherpa/Parakeet).

**Vocabulary beats fine-tuning.** Most errors on my speech will be proper nouns — hestia, Talos,
golinks, Vibrato. Whisper's initial prompt (`--initial-prompt` in `wyoming-faster-whisper`) or a
hotword list is the first thing to try, and the benchmark measures how much it helps. Fine-tuning
Whisper on my voice is possible, but only worth considering if the prompt doesn't close the gap.

## Audio in

STT needs microphones and a wake word, which is where most of the real-world latency and frustration
live:

- **Satellites:** Home Assistant Voice Preview Edition or ESP32-S3 boards on ESPHome, with on-device
  wake-word detection (microWakeWord), or the HA Companion app on a phone.
- **The full chain:** satellite → wake word → STT → intent (or an LLM) → TTS from `03-036` → back to
  the satellite. Everything local except the LLM.

## Risks

**Always-listening hardware.** Wake-word detection runs on the satellite; audio should only leave it
after the wake word. Verify that on the device, don't assume it from the documentation.

**Benchmarks on someone else's audio mislead.** Published word-error rates come from other people's
speech, mics and rooms. Measure on my voice, my rooms and my vocabulary.

## Open questions

- **Which recognizer wins on my speech?** The benchmark decides — not published numbers.
- **How many satellites, and where?** Room coverage decides hardware cost.
- **Does dictation need a GPU after all?** Only if large-model latency on CPU is unacceptable and
  the small models' accuracy is too.

## Exit Criteria

- [ ] A benchmark on a cluster node, on my own speech, recording real-time factor and word error
      rate for every candidate.
- [ ] Home Assistant commands work by voice end to end with local STT, from at least one satellite.
- [ ] Dictation produces usable text for a 30-second free-form utterance, latency measured.
- [ ] Verified that satellites send audio only after the wake word.

## Plan

### Phase 1 — Benchmark (private repo `gjcourt/voice`, cluster node)

- [ ] A fixed test set: ~50 HA commands and ~10 free-form 30-second clips in my voice, with
      reference transcripts. If `03-036`'s custom track runs, its cleaned dataset is a larger test
      set for free. The clips are my voice, so they follow `03-036`'s storage rule: on hestia only,
      never in git.
- [ ] Run each candidate on a cluster node: real-time factor and word error rate, with and without a
      vocabulary prompt.

**Gate:** a command recognizer and a dictation model chosen on measurement.

### Phase 2 — Deploy (homelab PR + George)

- [ ] Wyoming STT Deployments (cluster-internal, NetworkPolicy admitting only the Home Assistant
      namespace — `homeassistant-prod`, or `homeassistant-stage` in staging), same pattern as
      `wyoming-piper`.
- [ ] George adds them in Home Assistant's UI and builds an Assist pipeline: STT here, TTS from
      `03-036`.

**Gate:** a typed-then-spoken command round trip works from the HA app.

### Phase 3 — Satellites

- [ ] One satellite in one room; wake word on the device; latency measured end to end.
- [ ] Verify audio leaves the device only after the wake word.
- [ ] Expand room by room only once one room is reliable.

## Related

- `03-036` — local TTS; the other half of the voice pipeline.
- `03-034` — the hosted LLM a spoken assistant would talk to.
