---
title: 'Local Text-to-Speech (stock voice first, custom voice optional)'
number: '03-036'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'Wyoming protocol, Home Assistant voice pipeline, TTS evaluation; optionally speech dataset
  curation (source separation, diarization, forced transcription), Piper/VITS fine-tuning,
  rented-GPU training'
status: 'Not Started'
depends_on:
  - homelab/home-assistant
  - homelab/golinks
  - homelab/talos
---

# Local Text-to-Speech (stock voice first, custom voice optional)

## Description

Run text-to-speech locally, fast enough for interactive use, for two jobs:

- **Home Assistant announcements** — "the garage door has been open for 20 minutes".
- **Reading things aloud** — articles and notes, from a small page behind a golink (`go/read`).

A spoken assistant also needs speech-to-text; that is `03-037`, and the assistant gets its own brief
once both exist.

The constraint that shapes everything: **the homelab has no discrete GPU** (the 2× RTX 4090 were
sold 2026-05-16), so inference has to be fast on CPU. That points at **Piper**, which is built for
CPU — secondary sources report roughly 5× faster than real time on a desktop CPU and real time on a
Raspberry Pi 5 (not stated in Piper's own docs; Phase 1 measures it here) — and which Home Assistant
speaks natively through the Wyoming protocol. Piper moved to
[`OHF-Voice/piper1-gpl`](https://github.com/OHF-Voice/piper1-gpl) (GPL-3.0) in October 2025.

**Start with a voice that already exists.** A custom voice means a dataset, a rented GPU and days of
work; a good stock voice may be enough. The custom track below runs only if the audition says it's
worth it.

## Choosing the voice

| Candidate                                     | Where it runs                       | Notes                                                                                                                                                                                                                                                                                     |
| --------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Piper stock voices**                        | Cluster CPU, Wyoming                | Many English voices at low/medium/high quality. Each voice carries its own licence in its model card, separate from the engine's — check before settling on one.                                                                                                                          |
| **Kokoro presets** (`Kokoro-82M`, Apache-2.0) | Cluster CPU                         | Preset voices only; often described as more natural than Piper, but slower on CPU (published figures conflict) — both unmeasured here. No native Wyoming server confirmed; an OpenAI-compatible server (`Kokoro-FastAPI`) exists, and the Home Assistant integration path needs checking. |
| **A custom voice** (track below)              | Rented GPU to train, Piper to serve | My own voice, or someone else's **with their explicit, written consent**. Never a public figure or anyone who hasn't agreed.                                                                                                                                                              |

Cloud "voice design" services (generate a voice from a description) are out of scope — not local —
but are a fair reference point in the audition.

**The audition:** a fixed script (three announcements and one 30-second paragraph), every candidate
rendered from it, ranked blind, and synthesis time measured on a cluster node. The winner becomes
the default; the custom track starts only if no candidate is good enough.

## Optional: a custom voice

### Whose voice

- **My own.** If my published YouTube and Spotify audio holds enough me-only speech, that is the
  head start — Phase 3 inventories it before anything depends on it.
- **Someone else's, with consent.** A family member or friend who agrees in writing to how the voice
  will be used. They record with
  [`piper-recording-studio`](https://github.com/rhasspy/piper-recording-studio), which records
  against per-language prompt lists.

### Source material

For published audio, three rules apply:

- **Use the originals, not the published streams.** Project files, YouTube Studio's download of my
  own uploads, or the podcast host's masters, where they exist. Streamed copies are
  lossy-compressed, and pulling them with a scraper can breach the platforms' terms even for my own
  content — so no downloaders against YouTube or Spotify.
- **Only the target speaker.** Guests and co-hosts are diarized _out_, never trained on.
- **Published audio is not training audio until it is cleaned.** It carries music beds, guests,
  crosstalk, and whatever room it was recorded in.

The cleaning pipeline, all open-source:

1. **Demucs** — strip music and intro stings.
2. **pyannote** — diarize; keep only segments where the target speaker is talking. The library is
   MIT; its pretrained pipelines on Hugging Face are gated behind a per-model user agreement.
3. Segment on silence into 2–15 s clips.
4. **Whisper** — transcribe each clip; drop low-confidence, overlapping, or laughing segments.
5. Normalize to 22.05 kHz mono and write the LJSpeech-style `metadata.csv` (`clip.wav|text`) that
   Piper's trainer expects.

**How much:** an estimate, not a sourced figure — aim for one to two hours of clean single-speaker
audio; a secondary source cites ~1,300 phrases as the recommended fine-tune size (not confirmed
against Piper's own docs). If the cleaned set comes up short, record 30–60 minutes with
`piper-recording-studio`. Consistent mic and room matter more than raw hours.

**Plan B for thin or noisy data:** a documented hobbyist workflow uses a slower, higher-quality
cloning model (Chatterbox, MIT-licensed, a few seconds of reference audio) to synthesize ~1,300
clean phrases in the target voice, then fine-tunes Piper on those
([Cal Bryant](https://calbryant.uk/blog/training-a-new-ai-voice-for-piper-tts-with-only-4-words/)).
Real recordings are the preference; this is the fallback, not the plan.

### Where training can run

Piper's [training guide](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/TRAINING.md)
fine-tunes from an existing **medium** checkpoint. It names NVIDIA hardware (A6000 / 3090) and says
users report success with as little as 8 GB of VRAM and alternative GPUs like the RX 7600. Training
on Apple Silicon (MPS) is undocumented — assume CUDA or ROCm. One hobbyist fine-tune took about five
days on an old Tesla P4; a modern 24 GB card should be much faster, but there is no confirmed
figure.

| Option                                                                                                       | Verdict      | Why                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **winpc-5600x discrete GPU** — Radeon RX 580, 8 GB (read from the box 2026-10-02)                            | **No**       | CUDA is NVIDIA-only. ROCm on WSL2 supports only RX 7700 / 7800 XT / 7900-series / 9060 / 9070-class consumer cards ([AMD matrix](https://rocm.docs.amd.com/projects/radeon/en/latest/docs/compatibility/wsl/wsl_compatibility.html)), and Polaris (`gfx803`) is not in current ROCm's supported list on native Linux either — community reports disagree on exactly when it was dropped.                            |
| **Talos nodes' integrated GPU** (all four are HP EliteDesk 805 G6 Mini, Ryzen 5 PRO 4650GE, Radeon `gfx90c`) | **No**       | Not officially supported by ROCm; the `HSA_OVERRIDE_GFX_VERSION=9.0.0` spoof has crash reports ([ROCm#5121](https://github.com/ROCm/ROCm/issues/5121)). It shares system DDR4 and already does Immich/Jellyfin VAAPI transcoding on production nodes. Talos _can_ load AMD GPU extensions, so it's possible — just not worth it. The Mini chassis has no PCIe x16 slot, so adding a card to a node isn't an option. |
| **Rented cloud GPU**                                                                                         | **The plan** | A 24 GB NVIDIA card for the length of the fine-tune; duration unknown until measured. The voice data then sits on someone else's box — delete it afterwards.                                                                                                                                                                                                                                                        |

Inference needs none of these: Piper on the existing CPUs is the point.

## Serving it

- **Home Assistant:** a `wyoming-piper` Deployment in the homelab; HA's TTS points at it on
  port 10200. A custom voice later is a file swap, not a redesign.
- **Read-aloud:** a small HTTP service on the same voice. Low-latency streaming synthesis is
  proposed in an open piper1-gpl PR ([#302](https://github.com/OHF-Voice/piper1-gpl/pull/302)) and
  was not in a release as of 2026-10; until it ships, synthesize sentence by sentence.
- **Long-form narration (optional):** Chatterbox on CPU, rendered in the background. Expected to be
  too slow for live use and fine for batch — unmeasured.

## Risks

**A model of a real person's voice is a credential.** It can make that person say anything. Keep any
custom ONNX file and its dataset private — on hestia, never on Hugging Face or a public repo. The
TTS endpoint stays LAN-only, and anything reachable from a browser (the read-aloud page) needs auth
— decide what that is in Phase 2 rather than assuming the intranet already has it. If it's my voice
and a bank uses voice verification, turn that off. None of this applies to a stock voice, which is
one more reason to start there.

**Licences differ between engine and voices.** piper1-gpl is GPL-3.0 (fine for personal use). Each
stock voice, and any fine-tune, inherits the terms of its checkpoint's training data, so check the
model card before treating a voice as unencumbered. Several high-quality cloners have non-commercial
weights — XTTS-v2 (CPML), F5-TTS (CC-BY-NC-4.0) — fine for a personal plan B, not for anything
shared.

**Garbage in, robot out** (custom track). Diarization errors that leak another voice into the
dataset, or transcripts that don't match the audio, degrade the voice silently. Spot-check by
listening, not just by Whisper confidence.

## Open questions

- **Is a stock voice good enough?** The audition decides whether the custom track runs at all.
- **Can Kokoro reach Home Assistant cleanly?** Through an OpenAI-compatible TTS integration or a
  Wyoming wrapper — needs checking before it's a fair audition candidate.
- **Custom track only:** whose voice; how many hours of clean audio exist and whether the originals
  are available; and rent, or buy a used NVIDIA card for winpc? Renting is the default; buying only
  makes sense if more training runs are likely.

## Exit Criteria

- [ ] Home Assistant announces through a local TTS voice chosen by blind audition.
- [ ] Synthesis on the cluster CPU is faster than real time for a 30-second paragraph, measured.
- [ ] Read-aloud works end to end from `go/read`, with auth decided deliberately.
- [ ] The TTS endpoint is not reachable from outside the LAN — verified, not assumed.
- [ ] Either a custom voice wins a blind A/B against the chosen stock voice and replaces it, or the
      project records why the custom track was skipped.

## Plan

Every phase ends in a PR (homelab, lab, or a new private repo) or a recorded measurement; nothing is
merged by an agent.

**Where things live.** Code goes in a new **private** repo (working name `gjcourt/voice`): the
audition script, the read-aloud service and — if the custom track runs — the dataset pipeline and
training configs. Audio, datasets, checkpoints and custom models live on **hestia only**, in a
private dataset George creates (e.g. `/mnt/main/voice/{raw,dataset,checkpoints,models}`) — never in
git, never in an image. The cluster reads a custom voice the same way Jellyfin reads media: a static
NFS PV, read-only. Agents can't read that dataset (under the bench-cloud agent design their hestia
access is `agent-inbox` and media only), so audio work runs on George's machine.

### Phase 1 — Plumbing and audition (homelab PR + George)

- [ ] `apps/base/wyoming-piper/`: Deployment, Service on 10200 (cluster-internal only, no
      HTTPRoute), NetworkPolicy admitting only the Home Assistant namespace (`homeassistant-prod`,
      or `homeassistant-stage` in the staging overlay), a default English medium voice.
- [ ] George adds the Wyoming integration in Home Assistant's UI (it's a config-flow integration,
      not YAML) and makes it the default TTS.
- [ ] Render the audition script with every candidate; measure synthesis time for the 30-second
      paragraph on a cluster node; rank blind.

**Gate:** a voice chosen and set as default; synthesis faster than real time. Decide whether the
custom track runs.

### Phase 2 — Read-aloud (private repo + homelab PR)

- [ ] Small HTTP service: URL → readable text → Piper → audio, sentence by sentence until
      piper1-gpl's streaming ships in a release.
- [ ] Intranet-only route and a golink `go/read` pointing at the page. golinks does not forward
      query strings and its wildcard only captures one `A–Z a–z 0–9 . _ -` path segment, so the
      article URL is entered on the page, not passed through the golink. Decide its auth first: an
      endpoint that speaks in a chosen voice must not be open to everything on the LAN.

### Custom track (only if Phase 1 says so)

**Phase 3 — Decide and inventory (George, ~1 hour).**

- [ ] Choose the speaker: my voice, or a consenting person's (consent recorded).
- [ ] Record the winpc-5600x GPU (Radeon RX 580, 8 GB) in `hosts/winpc-5600x` — homelab PR.
- [ ] Inventory the source audio; locate the originals; estimate clean single-speaker hours.
- [ ] Create the private hestia dataset and its NFS export, readable from the cluster nodes only.

**Gate:** rented-GPU provider chosen (winpc's RX 580 rules out local training). Data path chosen —
real recordings if ≥ 1 h of clean audio is likely, otherwise plan B (record with
`piper-recording-studio`, or synthesize with Chatterbox).

**Phase 4 — Dataset (private repo + George's machine).**

- [ ] Pipeline in `gjcourt/voice`: Demucs → pyannote → silence segmentation → Whisper → filter →
      22.05 kHz mono → `metadata.csv`. Pinned dependencies; one command per stage; every stage
      idempotent and resumable.
- [ ] Run one episode end to end and listen to the output before batching.
- [ ] Run the full set; listen to a random 5 % of clips; tighten filters and re-run.
- [ ] Write a dataset card: source list, total minutes kept, rejection counts per filter.

**Gate:** ≥ 1 h of clean single-speaker clips that survive the listening check. If not, fall back to
plan B and re-enter this phase.

**Phase 5 — Train and ship (rented GPU + homelab PR).**

- [ ] Environment on the provider chosen in Phase 3; record versions in the repo.
- [ ] Fine-tune piper1-gpl from the medium English checkpoint, saving checkpoints regularly. Render
      the same fixed test sentences at each checkpoint to hear progress.
- [ ] Export the best checkpoint to ONNX plus its JSON config; copy to `hestia:…/models/`.
- [ ] Blind A/B against Phase 1's chosen voice with someone who knows the speaker. **Gate:** the
      custom voice wins; if not, stop and record why — the stock voice already works.
- [ ] Static NFS PV/PVC (read-only) for the models path, mounted into `wyoming-piper`; select the
      custom voice; re-measure synthesis speed; verify the endpoint is unreachable from outside the
      LAN and from namespaces other than Home Assistant's.

## Related

- `03-037` — local speech-to-text; with this brief, the local half of a spoken assistant.
- `03-034` — the household chat service plans a hosted LLM API backend; a spoken assistant would put
  these voices in front of the same backend.
