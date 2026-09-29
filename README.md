# 132 Multidisciplinary Engineering & Skill-Building Projects

`lab` (formerly `brainstorm`) is a personal catalog of project ideas spanning software, hardware,
woodworking, finance, and music. Each idea is a self-contained Markdown brief, tracked from
`Not Started` through `In Progress` to `Done`. Difficulty is calibrated to existing software skills
(Go, Kubernetes, Docker).

## Categories

1. **[Audio & MIDI](01-audio-midi/projects.md)** (22 projects) — DSP, custom controllers, and audio
   hardware.
2. **[Woodworking](02-woodworking/projects.md)** (15 projects) — functional furniture, speaker
   cabinets, and homelab enclosures.
3. **[Homelab & Automation](03-homelab-automation/projects.md)** (35 projects) — eBPF, K8s
   operators, ESP32 sensors, and infrastructure.
4. **[Finance & Analysis](04-finance-analysis/projects.md)** (16 projects) — EDGAR parsing, DCF
   modeling, and personal finance tracking.
5. **[Piano](05-piano/projects.md)** (15 projects) — advanced classical repertoire tools, jazz
   theory, and improvisation.
6. **[Coffee & Espresso](06-coffee-espresso/projects.md)** (19 projects) — Lucca A53 profiling,
   `leva!` firmware, and sensor integration.
7. **[Cross-Disciplinary](07-cross-disciplinary/projects.md)** (10 projects) — projects that blend
   multiple categories (e.g. wooden ESP32 audio receivers, mechanical keyboards).

Some categories also carry a `_reference/` directory with build notes, teardowns, or as-built state
for the projects that are actually underway (see `06-coffee-espresso/AGENTS.md` for the live state
of the one real espresso build).

## Difficulty scale

- **Easy (1-2 days):** builds on existing skills — Go, basic K8s, simple ESPHome/Home Assistant
  integrations, basic woodworking.
- **Medium (1-4 weeks):** combines multiple disciplines and introduces new concepts — basic PCB
  design, intermediate woodworking, custom sensors, intermediate finance.
- **Hard (months):** ambitious, stretches into low-level domains — C/C++, RTOS, kernel-level
  programming, complex DSP, advanced furniture fabrication, advanced financial modeling, complex
  jazz theory.

## Project file convention

Each project is one file, `NN-NNN-slug.md`, inside its category directory, where `NN` matches the
directory prefix. Every file starts with YAML frontmatter:

```yaml
title: 'ESP32 I2S DAC Streamer'
number: '01-001'
category: 'audio-midi'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills: 'C++, ESP-IDF, I2S, Audio Streaming'
status: 'Not Started'
depends_on: # optional
  - hardware/esp32
```

`depends_on` points at a prerequisite — another project's `NN-NNN`, or a resource reference like
`hardware/esp32`. Every file also needs an `## Exit Criteria` section.

To add a project, create the file with this frontmatter in the right category directory. To renumber
prefixes after reordering, run `python update_prefixes.py`.

## Checks

```text
make format-check     # prettier --check on *.md and *.yml/*.yaml
make lint              # markdownlint-cli2
make check-invariants  # frontmatter, Exit Criteria, per-category and README project counts
make check-brackets    # printed-bracket STL geometry vs. measured inputs
make test              # all of the above
```

`make format` applies prettier's fixes in place. CI (`.github/workflows/ci.yml`) runs the same
targets, plus a YAML lint pass, on every push and PR to `main`.
