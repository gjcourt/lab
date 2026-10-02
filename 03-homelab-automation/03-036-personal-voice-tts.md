---
title: 'Personal Voice TTS (train on my own voice, serve on CPU)'
number: '03-036'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'Speech dataset curation (source separation, diarization, forced transcription), Piper/VITS
  fine-tuning, CUDA/ROCm on WSL2, Wyoming protocol, Home Assistant voice pipeline'
status: 'Not Started'
---

# Personal Voice TTS (train on my own voice, serve on CPU)

## Description

Train a text-to-speech voice on my own recordings and run it locally, fast enough for interactive
use, for three jobs:

- **Home Assistant announcements** — "the garage door has been open for 20 minutes".
- **Reading things aloud** — articles and notes, behind a golink (`go/read?url=…`).
- **A spoken voice assistant** — speech in, LLM, speech out.

The constraint that shapes everything: **the homelab has no discrete GPU** (the 2× RTX 4090 were
sold 2026-05-16). Training has to happen somewhere with a GPU; inference has to be fast on CPU. That
points at **Piper**, which is built for CPU — reported around 5× faster than real time on a desktop
CPU and real time on a Raspberry Pi 5 — and which Home Assistant speaks natively through the Wyoming
protocol. Piper moved to [`OHF-Voice/piper1-gpl`](https://github.com/OHF-Voice/piper1-gpl) (GPL-3.0)
in October 2025; its
[training guide](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/TRAINING.md) fine-tunes from
an existing **medium** checkpoint, which is far cheaper than training from scratch.

## The source material already exists

Hours of my own speech are already published on YouTube and Spotify. That is the head start, with
two rules:

- **Use the originals, not the published streams.** Project files, YouTube Studio's download of my
  own uploads, or the podcast host's masters. Streamed copies are lossy-compressed, and pulling them
  with a scraper can breach the platforms' terms even for my own content.
- **Published audio is not training audio until it is cleaned.** It carries music beds, guests,
  crosstalk, and whatever room it was recorded in.

The cleaning pipeline, all open-source:

1. **Demucs** — strip music and intro stings.
2. **pyannote** — diarize; keep only segments where I am the speaker.
3. Segment on silence into 2–15 s clips.
4. **Whisper** — transcribe each clip; drop low-confidence, overlapping, or laughing segments.
5. Normalize to 22.05 kHz mono and write the LJSpeech-style `metadata.csv` (`clip.wav|text`) that
   Piper's trainer expects.

**How much:** one to two hours of clean single-speaker audio is a solid fine-tune; a secondary
source cites ~1,300 phrases as the recommended fine-tune size (not confirmed against Piper's own
docs). If the cleaned set comes up short, record 30–60 minutes with
[`piper-recording-studio`](https://github.com/rhasspy/piper-recording-studio), which prompts
phonetically varied sentences. Consistent mic and room matter more than raw hours.

**Plan B for thin or noisy data:** a documented hobbyist workflow uses a slower, higher-quality
cloning model (Chatterbox, MIT-licensed, a few seconds of reference audio) to synthesize ~1,300
clean phrases in the target voice, then fine-tunes Piper on those
([Cal Bryant](https://calbryant.uk/blog/training-a-new-ai-voice-for-piper-tts-with-only-4-words/)).
Real recordings beat synthetic ones; this is the fallback, not the plan.

## Where training can run

Piper's training guide documents only NVIDIA hardware (A6000 / 3090), with community reports of 8 GB
VRAM and one AMD RX 7600 on Linux. Training on Apple Silicon (MPS) is undocumented — assume CUDA or
ROCm. One hobbyist fine-tune took about five days on an old Tesla P4; a modern 24 GB card should be
much faster, but there is no confirmed figure.

| Option                                                                                       | Verdict                                                  | Why                                                                                                                                                                                                                                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **winpc-5600x discrete GPU**                                                                 | **Best, if NVIDIA with ≥ 8 GB** — model not yet recorded | CUDA under WSL2 needs only the normal Windows driver ([NVIDIA](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)). If it's a Radeon, ROCm on WSL2 supports only RX 7800 XT / 7900-series / 9060 / 9070-class cards ([AMD matrix](https://rocm.docs.amd.com/projects/radeon/en/latest/docs/compatibility/wsl/wsl_compatibility.html)); anything older means booting Linux natively or renting.      |
| **Talos nodes' integrated GPU** (HP EliteDesk 805 G6, Ryzen PRO 4000G, Radeon Vega `gfx90c`) | **No**                                                   | Not officially supported by ROCm ([ROCm#5121](https://github.com/ROCm/ROCm/issues/5121)); the `HSA_OVERRIDE_GFX_VERSION=9.0.0` spoof has crash reports, and native support is preliminary. It runs on shared DDR4 (~30–40 GB/s) and already does Immich/Jellyfin transcoding on production nodes. Talos _can_ expose `/dev/kfd` and documents a ROCm GPU Operator, so it's possible — just not worth it. |
| **A low-profile card in an 805 G6 SFF**                                                      | Maybe, later                                             | The SFF chassis has one PCIe x16 slot and a 180/250 W PSU, so only slot-powered (≤ 75 W) low-profile cards fit. The Mini has no slot. A purchase decision, and it would also put a GPU back into the cluster — out of scope here.                                                                                                                                                                        |
| **Rented cloud GPU**                                                                         | Fallback                                                 | A few hours on a 24 GB card. My voice data then sits on someone else's box — delete it afterwards.                                                                                                                                                                                                                                                                                                       |

Inference needs none of these: Piper on the existing CPUs is the point.

## Serving it

- **Home Assistant:** a `wyoming-piper` Deployment in the homelab loading my ONNX voice; HA's TTS
  points at it on port 10200. Start with a stock Piper voice so the plumbing is proven before the
  custom voice exists — then swapping voices is replacing a file.
- **Read-aloud:** a small HTTP service on the same voice. piper1-gpl documents waveform streaming
  (audio starts before the sentence finishes); confirm it has shipped in a release.
- **Assistant:** latency is speech-to-text (faster-whisper on CPU) + the LLM + Piper. Piper is not
  the slow part. The LLM has to be a hosted API — no on-prem inference without a GPU.
- **Long-form narration (optional):** Chatterbox on CPU, rendered in the background. Too slow for
  live use, fine for batch.

## Risks

**A model of my voice is a credential.** It can make "me" say anything. Keep the ONNX file and the
dataset private — on hestia, never on Hugging Face or a public repo. The TTS endpoint stays
LAN-only, and anything reachable from a browser (the read-aloud page) needs auth — decide what that
is in Phase 5 rather than assuming the intranet already has it. If a bank uses voice verification,
turn it off.

**Licences differ between engine and weights.** piper1-gpl is GPL-3.0 (fine for personal use; the
voice model itself is mine). Several high-quality cloners have non-commercial weights — XTTS-v2
(CPML), F5-TTS (CC-BY-NC-4.0) — fine for a personal plan B, not for anything shared.

**Garbage in, robot out.** Diarization errors that leak a guest's voice into the dataset, or
transcripts that don't match the audio, degrade the voice silently. Spot-check by listening, not
just by Whisper confidence.

## Open questions

- **What GPU is in winpc-5600x?** Model and VRAM decide whether training is local. The Ryzen 5 5600X
  has no integrated graphics, so a discrete card is there — it just isn't recorded in
  `hosts/winpc-5600x`.
- **How many hours of me-only audio exist, and are the originals available?** Decides whether plan A
  works or plan B is needed.
- **Are the cluster nodes 805 G6 Mini or SFF?** Only matters if a low-profile GPU ever becomes a
  question.
- **Does the custom voice need to be better than Piper's best stock voice?** Worth a blind listening
  test before spending days on training.

## Exit Criteria

- [ ] A cleaned dataset of ≥ 1 h of my voice only, with transcripts, in `metadata.csv` form —
      spot-checked by listening to a random 5 %.
- [ ] A fine-tuned Piper voice exported to ONNX, stored privately on hestia.
- [ ] Home Assistant announces through `wyoming-piper` using that voice.
- [ ] Synthesis on the cluster CPU is faster than real time for a 30-second paragraph, measured.
- [ ] Read-aloud works end to end from a golink.
- [ ] A blind A/B with someone who knows my voice prefers the custom voice over the best stock Piper
      voice, or the project records that it didn't.
- [ ] The TTS endpoint is not reachable from outside the LAN — verified, not assumed.

## Plan

Six phases, each ending in something that can be checked. Every phase is a PR (homelab, lab, or the
new private repo) or a recorded measurement; nothing is merged by an agent.

**Where things live.** Code goes in a new **private** repo (working name `gjcourt/voice`): the
dataset pipeline, training configs and the read-aloud service. Audio, datasets, checkpoints and the
ONNX voice live on **hestia only**, in a private dataset George creates (e.g.
`/mnt/main/voice/{raw,dataset,checkpoints,models}`) — never in git, never in an image. The cluster
reads the finished voice the same way Jellyfin reads media: a static NFS PV, read-only. Agents can't
read that dataset (their hestia access is `agent-inbox` and media only), so audio work runs on
George's machine.

### Phase 0 — Decide and inventory (George, ~1 hour)

- [ ] Record the winpc-5600x GPU model and VRAM in `hosts/winpc-5600x`.
- [ ] Inventory published audio; locate the originals; estimate me-only hours.
- [ ] Create the private hestia dataset and its NFS export, readable from the cluster nodes only.

**Gate:** training path chosen — **A** WSL2 + CUDA on winpc (NVIDIA, ≥ 8 GB), **B** WSL2 + ROCm (RX
7800 XT class or newer), or **C** rented GPU. Data path chosen — real recordings if ≥ 1 h of me-only
audio is likely, otherwise plan B (record with `piper-recording-studio`, or synthesize with
Chatterbox).

### Phase 1 — Plumbing with a stock voice (homelab PR, agent can do)

Proves everything except the voice itself, and gives Home Assistant local TTS immediately.

- [ ] `apps/base/wyoming-piper/`: Deployment, Service on 10200 (cluster-internal only, no
      HTTPRoute), NetworkPolicy admitting only the `homeassistant` namespace, the best stock English
      medium voice.
- [ ] George adds the Wyoming integration in Home Assistant's UI (it's a config-flow integration,
      not YAML) and picks the voice as the default TTS.
- [ ] Measure synthesis time for a fixed 30-second paragraph on a cluster node.

**Gate:** HA speaks an automation's announcement; synthesis is faster than real time. This is also
the baseline voice for Phase 3's A/B.

### Phase 2 — Dataset (private repo + George's machine)

- [ ] Pipeline in `gjcourt/voice`: Demucs → pyannote → silence segmentation → Whisper → filter →
      22.05 kHz mono → `metadata.csv`. Pinned dependencies; one command per stage; every stage
      idempotent and resumable.
- [ ] Run one episode end to end and listen to the output before batching.
- [ ] Run the full set; listen to a random 5 % of clips; tighten filters and re-run.
- [ ] Write a dataset card: source list, total minutes kept, rejection counts per filter.

**Gate:** ≥ 1 h of clean me-only clips that survive the listening check. If not, fall back to plan B
and re-enter this phase.

### Phase 3 — Training (winpc or rented GPU)

- [ ] Environment per Phase 0's choice; record versions in the repo.
- [ ] Fine-tune piper1-gpl from the medium English checkpoint, saving checkpoints regularly. Render
      the same fixed test sentences at each checkpoint to hear progress.
- [ ] Export the best checkpoint to ONNX plus its JSON config; copy to `hestia:…/models/`.
- [ ] Blind A/B against the Phase 1 stock voice with someone who knows my voice.

**Gate:** the custom voice wins the A/B. If it doesn't, stop here and record why — the stock voice
already works.

### Phase 4 — Ship the voice (homelab PR)

- [ ] Static NFS PV/PVC (read-only) for the models path; mount it into `wyoming-piper`; select the
      custom voice.
- [ ] Re-measure synthesis speed on the cluster CPU.
- [ ] Verify the endpoint is unreachable from outside the LAN and from namespaces other than Home
      Assistant's.

**Gate:** HA announces in my voice; speed and reachability checks recorded.

### Phase 5 — Read-aloud (private repo + homelab PR)

- [ ] Small HTTP service: URL → readable text → Piper → audio, streamed where piper1-gpl's streaming
      has shipped in a release. Uses the same voice volume.
- [ ] Intranet-only route and a golink `go/read`. Decide its auth first: an endpoint that speaks in
      my voice must not be open to everything on the LAN.

### Phase 6 — Spoken assistant (separate brief)

Speech-to-text (faster-whisper over Wyoming) + Home Assistant's Assist pipeline + a hosted LLM +
this voice. It shares the LLM decision with `03-034`, so it gets its own brief once Phases 1–4 are
done rather than being designed now.

## Related

- `03-034` — the household chat service runs on a hosted LLM API; a spoken assistant would put this
  voice in front of the same backend.
