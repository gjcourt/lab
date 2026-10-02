---
title: 'Local Text-to-Speech (stock voice first, my own voice later)'
number: '03-036'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'Wyoming protocol, Home Assistant voice pipeline, TTS evaluation; later, recording a speech
  dataset, Piper/VITS fine-tuning, rented-GPU training'
status: 'Not Started'
depends_on:
  - homelab/home-assistant
  - homelab/golinks
  - homelab/talos
---

# Local Text-to-Speech (stock voice first, my own voice later)

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

**Start with a voice that already exists, then train my own.** Phase 1 ships a stock, pre-trained
voice chosen by audition. A later phase records my own voice locally, fine-tunes a Piper voice from
it, and plugs it in — so the stock voice carries everything until mine beats it.

## Choosing the voice

| Candidate                                     | Where it runs                       | Notes                                                                                                                                                                                                                                                                                     |
| --------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Piper stock voices**                        | Cluster CPU, Wyoming                | Many English voices at low/medium/high quality. Each voice carries its own licence in its model card, separate from the engine's — check before settling on one.                                                                                                                          |
| **Kokoro presets** (`Kokoro-82M`, Apache-2.0) | Cluster CPU                         | Preset voices only; often described as more natural than Piper, but slower on CPU (published figures conflict) — both unmeasured here. No native Wyoming server confirmed; an OpenAI-compatible server (`Kokoro-FastAPI`) exists, and the Home Assistant integration path needs checking. |
| **My own voice** (later phase)                | Rented GPU to train, Piper to serve | Fine-tuned from local recordings of me.                                                                                                                                                                                                                                                   |

Cloud "voice design" services (generate a voice from a description) are out of scope — not local —
but are a fair reference point in the audition.

**The audition:** a fixed script (three announcements and one 30-second paragraph), every candidate
rendered from it, ranked blind, and synthesis time measured on a cluster node. The winner is the
default until my own voice wins a blind A/B against it.

## Later: my own voice

### Recording

Record locally with [`piper-recording-studio`](https://github.com/rhasspy/piper-recording-studio),
which records against per-language prompt lists and exports the LJSpeech-style dataset Piper's
trainer expects — the prompt is the transcript, so no transcription step is needed. Same mic, same
room, same distance every session; consistency matters more than raw hours.

**How much:** an estimate, not a sourced figure — aim for one to two hours of clean speech; a
secondary source cites ~1,300 phrases as the recommended fine-tune size (not confirmed against
Piper's own docs).

**Optional extra source — my published audio.** If my published YouTube and Spotify audio holds
enough me-only speech, it can top up the recordings. Use the originals (project files, YouTube
Studio's download of my own uploads, the podcast host's masters) — no downloaders against YouTube or
Spotify. It needs cleaning first: **Demucs** to strip music, **pyannote** to diarize guests and
co-hosts _out_ (the library is MIT; its pretrained pipelines on Hugging Face are gated behind a
per-model user agreement), silence segmentation into 2–15 s clips, and **Whisper** for transcripts.

**Plan B for thin data:** a documented hobbyist workflow uses a slower, higher-quality cloning model
(Chatterbox, MIT-licensed, a few seconds of reference audio) to synthesize ~1,300 clean phrases in
the target voice, then fine-tunes Piper on those
([Cal Bryant](https://calbryant.uk/blog/training-a-new-ai-voice-for-piper-tts-with-only-4-words/)).
Real recordings are the preference.

**Pluggable, lightly:** each training run is a folder of recordings plus a small config, and each
result lands in its own `models/<name>/` directory that `wyoming-piper` loads alongside the stock
voice. Retraining, or adding another take, is a new folder and a training run, not new code.

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
| **Rented cloud GPU**                                                                                         | **The plan** | A 24 GB NVIDIA card for the length of the fine-tune; duration unknown until measured. My recordings then sit on someone else's box — delete them afterwards.                                                                                                                                                                                                                                                        |

Inference needs none of these: Piper on the existing CPUs is the point.

## Serving it

- **Home Assistant:** a `wyoming-piper` Deployment in the homelab; HA's TTS points at it on
  port 10200. My voice later is a file added to its voice directory, not a redesign.
- **Read-aloud:** a small HTTP service on the same voice. Low-latency streaming synthesis is
  proposed in an open piper1-gpl PR ([#302](https://github.com/OHF-Voice/piper1-gpl/pull/302)) and
  was not in a release as of 2026-10; until it ships, synthesize sentence by sentence.
- **Long-form narration (optional):** Chatterbox on CPU, rendered in the background. Expected to be
  too slow for live use and fine for batch — unmeasured.

## Risks

**A model of my voice can make "me" say anything.** Keep the trained ONNX file and recordings
private — on hestia, never on Hugging Face or a public repo. The TTS endpoint stays LAN-only, and
anything reachable from a browser (the read-aloud page) needs auth — decide what that is in Phase 2
rather than assuming the intranet already has it. If a bank uses voice verification, turn it off.

**Licences differ between engine and voices.** piper1-gpl is GPL-3.0 (fine for personal use). Each
stock voice, and any fine-tune, inherits the terms of its checkpoint's training data, so check the
model card before treating a voice as unencumbered.

**Garbage in, robot out.** Misread prompts, clipped takes, or (in published audio) a guest's voice
leaking past diarization degrade the voice silently. Spot-check by listening.

## Open questions

- **Can Kokoro reach Home Assistant cleanly?** Through an OpenAI-compatible TTS integration or a
  Wyoming wrapper — needs checking before it's a fair audition candidate.
- **How much to record, and does published audio add anything?** Recording time is the main cost of
  the later phase.
- **Rent, or buy a used NVIDIA card for winpc?** Renting is the default; buying only makes sense if
  more training runs are likely.

## Exit Criteria

- [ ] Home Assistant announces through a local TTS voice chosen by blind audition.
- [ ] Synthesis on the cluster CPU is faster than real time for a 30-second paragraph, measured.
- [ ] Read-aloud works end to end from `go/read`, with auth decided deliberately.
- [ ] The TTS endpoint is not reachable from outside the LAN — verified, not assumed.
- [ ] A Piper voice fine-tuned on my recordings either wins a blind A/B against the stock voice and
      is swapped in, or the project records why it didn't.

## Plan

Every phase ends in a PR (homelab, lab, or a new private repo) or a recorded measurement; nothing is
merged by an agent.

**Where things live.** Code goes in a new **private** repo (working name `gjcourt/voice`): the
audition script, the read-aloud service and the training setup. Recordings, checkpoints and trained
models live on **hestia only**, in a private dataset George creates (e.g.
`/mnt/main/voice/{recordings,checkpoints,models}`) — never in git, never in an image. The cluster
reads trained voices the same way Jellyfin reads media: a static NFS PV, read-only. Agents can't
read that dataset (under the bench-cloud agent design their hestia access is `agent-inbox` and media
only), so audio work runs on George's machine.

### Phase 1 — Plumbing and audition (homelab PR + George)

- [ ] `apps/base/wyoming-piper/`: Deployment, Service on 10200 (cluster-internal only, no
      HTTPRoute), NetworkPolicy admitting only the Home Assistant namespace (`homeassistant-prod`,
      or `homeassistant-stage` in the staging overlay), a default English medium voice.
- [ ] George adds the Wyoming integration in Home Assistant's UI (it's a config-flow integration,
      not YAML) and makes it the default TTS.
- [ ] Render the audition script with every candidate; measure synthesis time for the 30-second
      paragraph on a cluster node; rank blind.

**Gate:** a stock voice chosen and set as default; synthesis faster than real time.

### Phase 2 — Read-aloud (private repo + homelab PR)

- [ ] Small HTTP service: URL → readable text → Piper → audio, sentence by sentence until
      piper1-gpl's streaming ships in a release.
- [ ] Intranet-only route and a golink `go/read` pointing at the page. golinks does not forward
      query strings and its wildcard only captures one `A–Z a–z 0–9 . _ -` path segment, so the
      article URL is entered on the page, not passed through the golink. Decide its auth first: an
      endpoint that speaks in a chosen voice must not be open to everything on the LAN.

### Later phases — my own voice

**Phase 3 — Record (George).**

- [ ] Record the winpc-5600x GPU (Radeon RX 580, 8 GB) in `hosts/winpc-5600x` — homelab PR.
- [ ] Create the private hestia dataset and its NFS export, readable from the cluster nodes only.
- [ ] Record with `piper-recording-studio` in sessions, same setup each time; listen to a few takes
      from each session before the next.

**Gate:** ≥ 1 h of clean recordings (or top up from published originals / plan B); rented-GPU
provider chosen — winpc's RX 580 rules out local training.

**Phase 4 — Train and ship (rented GPU + homelab PR).**

- [ ] Training setup in `gjcourt/voice`: pinned environment, a small per-run config (recordings
      folder, base checkpoint, output name); record versions.
- [ ] Fine-tune piper1-gpl from the medium English checkpoint, saving checkpoints regularly. Render
      the same fixed test sentences at each checkpoint to hear progress.
- [ ] Export the best checkpoint to ONNX plus its JSON config; copy to `hestia:…/models/<name>/`.
- [ ] Blind A/B against Phase 1's chosen voice with someone who knows my voice. **Gate:** mine wins;
      if not, record why and keep the stock voice — it already works.
- [ ] Static NFS PV/PVC (read-only) for the models path, mounted into `wyoming-piper` so trained
      voices are selectable; re-measure synthesis speed; verify the endpoint is unreachable from
      outside the LAN and from namespaces other than Home Assistant's.

## Related

- `03-037` — local speech-to-text; with this brief, the local half of a spoken assistant.
- `03-034` — the household chat service plans a hosted LLM API backend; a spoken assistant would put
  these voices in front of the same backend.
