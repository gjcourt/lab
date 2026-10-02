<!-- readme-type: content -->

# lab

A curated list of 133 multidisciplinary engineering and skill-building projects

Picking a next project to learn on tends to default to whatever's easiest, not to whatever actually
builds a skill that's missing. `lab` (formerly `brainstorm`) tracks 133 project briefs spanning
software, hardware, woodworking, finance, and music, each one scoped and leveled against existing
skills (Go, Kubernetes, Docker) so the next pick is deliberate rather than convenient. It's a
personal planning catalog, not a set of finished write-ups — most entries are still `Not Started`.

**Status:** active — 133 briefs (1 done, 15 in progress), last content update 2026-09-01; the
espresso profiling build is installed on the machine and its controller app, Vibrato, runs in the
homelab (see [`06-coffee-espresso/AGENTS.md`](06-coffee-espresso/AGENTS.md)).

## Layout

Each directory holds one Markdown file per project plus a `projects.md` index; three also carry a
`_reference/` directory with as-built notes for the work that's actually underway.

```text
01-audio-midi/          22 projects — DSP, custom controllers, and audio hardware
02-woodworking/         15 projects — functional furniture, speaker cabinets, homelab enclosures
03-homelab-automation/  36 projects — eBPF, K8s operators, ESP32 sensors, and infrastructure
04-finance-analysis/    16 projects — EDGAR parsing, DCF modeling, personal finance tracking
05-piano/               15 projects — classical repertoire tools, jazz theory, improvisation
06-coffee-espresso/     19 projects — Lucca A53 profiling, leva! firmware, sensor integration
07-cross-disciplinary/  10 projects — projects blending multiple categories
```

## Conventions

Each project is one file, `NN-NNN-slug.md`, inside its category directory, where `NN` matches the
directory prefix. Every file starts with YAML frontmatter:

```yaml
---
title: 'ESP32 I2S DAC Streamer'
number: '01-001'
category: 'audio-midi'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills: 'C++, ESP-IDF, I2S, Audio Streaming'
status: 'Not Started'
depends_on: # optional
  - hardware/esp32
---
```

`difficulty` is `Easy` (1-2 days, builds on existing skills), `Medium` (1-4 weeks, combines
disciplines or introduces new concepts), or `Hard` (months, stretches into low-level domains such as
C/C++, RTOS, or advanced finance/music theory). `status` moves from `Not Started` through
`In Progress` to `Done`. `depends_on` points at a prerequisite — another project's `NN-NNN`, or a
resource reference like `hardware/esp32`. Every file also needs an `## Exit Criteria` section.

To add a project, create the file with this frontmatter in the right category directory and update
that category's `projects.md` count. To renumber prefixes after reordering, run
`python update_prefixes.py`. See [`AGENTS.md`](AGENTS.md) for the validation commands CI runs on
every change.

## License

No licence file yet.
