---
title: 'Local Text-to-Speech (stock voice first, my own voice later)'
number: '03-036'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'Wyoming protocol, Home Assistant voice pipeline, TTS evaluation; later, recording a speech
  dataset, Piper/VITS fine-tuning, rented-GPU training (Runpod)'
status: 'In Progress'
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

The constraint that shapes everything: **the cluster has no discrete GPU** (the 2× RTX 4090 were
sold 2026-05-16), so inference has to be fast on CPU. That points at **Piper**, which is built for
CPU — secondary sources report roughly 5× faster than real time on a desktop CPU and real time on a
Raspberry Pi 5 (not stated in Piper's own docs; Phase 1 measures it here) — and which Home Assistant
speaks natively through the Wyoming protocol. Piper moved to
[`OHF-Voice/piper1-gpl`](https://github.com/OHF-Voice/piper1-gpl) (GPL-3.0) in October 2025.

**Start with a voice that already exists, then train my own.** Phase 1 ships a stock, pre-trained
voice chosen by audition. A later phase records my own voice locally, fine-tunes a Piper voice from
it, and plugs it in — so the stock voice carries everything until mine beats it.

## Choosing the voice

| Candidate                                     | Where it runs                         | Notes                                                                                                                                                                                                                                                                                     |
| --------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Piper stock voices**                        | Cluster CPU, Wyoming                  | Many English voices at low/medium/high quality. Each voice carries its own licence in its model card, separate from the engine's — check before settling on one.                                                                                                                          |
| **Kokoro presets** (`Kokoro-82M`, Apache-2.0) | Cluster CPU                           | Preset voices only; often described as more natural than Piper, but slower on CPU (published figures conflict) — both unmeasured here. No native Wyoming server confirmed; an OpenAI-compatible server (`Kokoro-FastAPI`) exists, and the Home Assistant integration path needs checking. |
| **My own voice** (later phase)                | a rented GPU to train, Piper to serve | Fine-tuned from local recordings of me.                                                                                                                                                                                                                                                   |

Cloud "voice design" services (generate a voice from a description) are out of scope — not local —
but are a fair reference point in the audition.

**The audition:** a fixed script (three announcements and one 30-second paragraph), every candidate
rendered from it, ranked blind, and synthesis time measured on a cluster node. The winner is the
default until my own voice wins a blind A/B against it.

## Audition result (2026-10-02)

Thirteen stock voices (9 Piper, 4 Kokoro) rendered the same script, blinded and level-matched, and
were ranked on a listening page. Kokoro took the top three places. The blinded samples, timings and
key are in `hestia:/mnt/main/agent-inbox/tts-audition/2026-10-02/`; the harness is in
`gjcourt/voice` ([voice#1](https://github.com/gjcourt/voice/pull/1)).

| Rank | Voice               | Engine | Paragraph synthesis time (audio length)\* | Licence                                             |
| ---- | ------------------- | ------ | ----------------------------------------- | --------------------------------------------------- |
| 1    | `af_heart`          | Kokoro | 15.4 s (26.0 s)                           | Apache-2.0                                          |
| 2    | `am_michael`        | Kokoro | 13.4 s (27.7 s)                           | Apache-2.0                                          |
| 3    | `af_bella`          | Kokoro | 13.1 s (26.0 s)                           | Apache-2.0                                          |
| 4    | `en_GB-alan-medium` | Piper  | 2.3 s (29.2 s)                            | Unclear — source folder reads "All Rights Reserved" |
| 5    | `en_GB-cori-high`   | Piper  | 10.5 s (24.5 s)                           | Public domain                                       |

\*Median of three runs on a cluster node, under a throttled 4-CPU quota; Kokoro measured with
`kokoro-onnx`.

**Decision:** `af_heart` is the default voice, served by Kokoro-FastAPI on CPU
([homelab#1532](https://github.com/gjcourt/homelab/pull/1532)). Home Assistant's core OpenAI
integration only talks to `api.openai.com`, so it goes through the HACS **OpenAI TTS** integration.
The `wyoming_openai` bridge (Apache-2.0) is the alternative if Wyoming streaming is needed later for
the assistant. Alan was the favourite voice character; improving it is an experiment below. Kokoro
has preset voices only, so any trained voice — alan or mine — is a Piper voice and has to beat
`af_heart` in a blind A/B to replace it.

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

| Option                                                                                                       | Verdict      | Why                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **winpc-5600x discrete GPU** — Radeon RX 580, 8 GB (read from the box 2026-10-02)                            | **No**       | CUDA is NVIDIA-only. ROCm on WSL2 supports only RX 7700 / 7800 XT / 7900-series / 9060 / 9070-class consumer cards ([AMD matrix](https://rocm.docs.amd.com/projects/radeon/en/latest/docs/compatibility/wsl/wsl_compatibility.html)), and Polaris (`gfx803`) is not in current ROCm's supported list on native Linux either — community reports disagree on exactly when it was dropped.                                                                                                                                                                                                                                                                |
| **Talos nodes' integrated GPU** (all four are HP EliteDesk 805 G6 Mini, Ryzen 5 PRO 4650GE, Radeon `gfx90c`) | **No**       | Not officially supported by ROCm; the `HSA_OVERRIDE_GFX_VERSION=9.0.0` spoof has crash reports ([ROCm#5121](https://github.com/ROCm/ROCm/issues/5121)). It shares system DDR4 and already does Immich/Jellyfin VAAPI transcoding on production nodes. Talos _can_ load AMD GPU extensions, so it's possible — just not worth it. The Mini chassis has no PCIe x16 slot, so adding a card to a node isn't an option.                                                                                                                                                                                                                                     |
| **RTX 4060 Ti 16 GB in winpc-5600x** (decided 2026-10-03; replaces the RX 580)                               | Superseded   | Decided 2026-10-03, superseded 2026-10-08 by rented GPUs (below). Ada, so CUDA under WSL2 with the stock Windows driver. Chosen over the faster RTX 4070 Super 12 GB because winpc is for training and inference only: memory caps what can run at all, while speed only changes how long it takes. 16 GB should fit Piper's default batch of 32 (community reports, unmeasured here) and leaves headroom for Chatterbox (~6–10 GB) and larger models. A compact 2-slot model (e.g. Zotac Twin Edge, ~221 mm) fits the NCASE M1 (dual-slot, ≤ 322 mm); ~165 W from one 8-pin is well within the SFX 800 W Gold PSU. Recordings never leave the network. |
| **Rented cloud GPU**                                                                                         | **The plan** | Chosen 2026-10-08. A 24 GB NVIDIA card on Runpod Secure Cloud through the `gjcourt/voice` harness: per-run cost cap, guaranteed teardown, nothing to install or maintain. The data then sits on someone else's box — delete it afterwards.                                                                                                                                                                                                                                                                                                                                                                                                              |

Inference needs none of these: Piper on the existing CPUs is the point.

**Update (2026-10-08): rented GPU is now the working path.** The private `gjcourt/voice` harness
fine-tunes Piper on Runpod Secure Cloud with a per-run cost cap and guaranteed teardown. The first
real fine-tune ran on an RTX A5000 at $0.276/h, about 39 s per epoch on ~70 min of audio, and was
intelligible within ~45 epochs. Community Cloud was dropped after slow image pulls and a host with
no public SSH port. The own-voice phase can use the same harness; the delete-afterwards rule above
still applies.

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

- **How much to record, and does published audio add anything?** Recording time is the main cost of
  the later phase.
- **Software versions for training — answered 2026-10-08.** piper1-gpl's `train` extra allows any
  `torch>=2,<3`, but open issue [#225](https://github.com/OHF-Voice/piper1-gpl/issues/225) breaks
  checkpoint resume (`--ckpt_path`, which fine-tuning needs) on torch ≥ 2.6. The `gjcourt/voice`
  training image pins torch 2.5.1 (CUDA 12.4), and the harness skips Blackwell cards, which need a
  newer torch. Chatterbox pins `torch==2.6.0`, so it still needs its own environment.

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

- [x] `apps/base/wyoming-piper/`: Deployment, Service on 10200 (cluster-internal only, no
      HTTPRoute), NetworkPolicy admitting only the Home Assistant namespace (`homeassistant-prod`,
      or `homeassistant-stage` in the staging overlay), a default English medium voice —
      [homelab#1529](https://github.com/gjcourt/homelab/pull/1529), merged 2026-10-04. Now the home
      for trained Piper voices rather than the default.
- [x] `apps/base/kokoro/`: Kokoro-FastAPI with `af_heart`, same isolation, no internet egress —
      [homelab#1532](https://github.com/gjcourt/homelab/pull/1532), merged 2026-10-04.
- [ ] George installs the HACS OpenAI TTS integration, points it at Kokoro
      (`http://kokoro.kokoro-prod.svc.cluster.local:8880/v1`, model `kokoro`, voice `af_heart`) and
      makes it the default TTS. The Wyoming integration for Piper waits for a trained voice.
- [x] Render the audition script with every candidate; measure synthesis time for the 30-second
      paragraph on a cluster node; rank blind. Done 2026-10-02 — see _Audition result_.

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

- [ ] Training hardware: a rented GPU through `gjcourt/voice` (Runpod Secure Cloud) — nothing to
      install.
- [ ] Create the private hestia dataset and its NFS export, readable from the cluster nodes only.
- [ ] Record with `piper-recording-studio` in sessions, same setup each time; listen to a few takes
      from each session before the next.

**Gate:** ≥ 1 h of clean recordings (or top up from published originals / plan B); training hardware
ready — a rented GPU through `gjcourt/voice`.

**Phase 4 — Train and ship (rented GPU via `gjcourt/voice` + homelab PR).**

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

### Experiment — improve alan (V08)

Alan ranked fourth but was the favourite voice character. The question is whether fine-tuning can
make it sound more natural while keeping its character. Nothing here runs until this plan is agreed.

**What exists to start from:** `rhasspy/piper-checkpoints` has an alan **medium** training
checkpoint (`en/en_GB/alan/medium`, fine-tuned from lessac medium). Its folder includes
`dataset.jsonl.gz`, which is phonemized text with no audio. The original recordings (Mycroft's
`apope` voice) are not public anywhere found, and the source folder's licence reads "All Rights
Reserved". The only en_GB **high** checkpoint is `cori/high`.

**Arm A — re-voice with a stronger model, then fine-tune alan.** Use alan's own renders as reference
audio for Chatterbox (MIT; GPU for the Turbo model, a smaller CPU-capable Nano exists) to synthesize
~1,300–2,000 phrases with more natural prosody in alan's timbre. Whisper-check every clip, then
fine-tune from the alan medium checkpoint. This is the documented hobbyist pattern
([Cal Bryant](https://calbryant.uk/blog/training-a-new-ai-voice-for-piper-tts-with-only-4-words/));
its author fine-tuned from an LJSpeech checkpoint rather than the source voice's own, and reports
that Chatterbox made the voice less robotic and the trained model sounds similar to Chatterbox's
output.

**Arm B — the same dataset, fine-tuned from `cori/high`** for the high-quality architecture. Expect
more natural audio and a larger timbre drift; slower on CPU (cori-high ran at RTF ~0.43). Piper's
[training guide](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/TRAINING.md) says only
medium checkpoints are supported without tweaking other settings, so this arm needs the high-quality
model settings worked out first.

**Not doing:** training a high model on alan's own output alone. No evidence was found that it
improves anything; it would mostly reproduce alan's artifacts.

**How it's judged:** the audition harness renders the original alan, both arms and `af_heart` blind.
Success is beating the original alan on naturalness while still sounding like alan; replacing
`af_heart` as the default is a separate bar.

**Where:** a rented 24 GB GPU through `gjcourt/voice` for the Piper fine-tune, and for Chatterbox
generation in its own environment (see _Open questions_). Measured 2026-10-08: about 39 s per epoch
on an RTX A5000 for ~70 min of audio.

**Use:** private household use only, like every voice here. Alan's licence is unclear and it is a
real person's voice that was released as a TTS model, so the results stay on hestia and are not
published.

## Related

- `03-037` — local speech-to-text; with this brief, the local half of a spoken assistant.
- `03-034` — the household chat service plans a hosted LLM API backend; a spoken assistant would put
  these voices in front of the same backend.
