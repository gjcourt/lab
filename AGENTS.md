# Brainstorm Agent Guidelines

## Repository Overview

Brainstorm is a curated collection of 100 multidisciplinary engineering and skill-building project
ideas, organized by category. Projects span software, hardware, woodworking, finance, and music —
calibrated for someone with strong existing software skills (Go, Kubernetes, Docker).

## Repository Structure

```text
01-audio-midi/         ← audio, MIDI, DSP project ideas
02-woodworking/        ← woodworking and fabrication projects
03-homelab-automation/ ← home lab and automation projects
04-finance-analysis/   ← financial modeling and analysis projects
05-piano/              ← piano and music theory projects
06-coffee-espresso/    ← espresso and coffee projects
07-cross-disciplinary/ ← projects combining multiple domains
README.md              ← overview and difficulty scale
update_prefixes.py     ← script to renumber/reorder project prefixes
Makefile               ← convenience targets
```

## Difficulty Scale

- **Easy (1–2 days)**: Leverages existing skills (Go, basic K8s, simple ESPHome/HA, basic
  woodworking).
- **Medium (1–4 weeks)**: Combines multiple disciplines; introduces new concepts.
- **Hard (months)**: Ambitious; stretches into low-level domains (C/C++, RTOS, DSP, advanced
  finance/music theory).

## Project File Convention

- Each project is one Markdown file named `NN-NNN-slug.md` inside its category directory, where the
  `NN` prefix matches the directory (e.g. `05-006-midi-to-sheet-music-transcriber.md` in
  `05-piano/`).
- Every project file begins with YAML frontmatter. Required keys: `title`, `number`, `category`,
  `difficulty` (`Easy|Medium|Hard`), `time_commitment`, `target_skills`, `status`
  (`Not Started|In Progress|Done`). The `number:` value must match the filename prefix.
- `depends_on:` is an optional list of prerequisite references (e.g. `hardware/midi-keyboard`, or
  another project's `NN-NNN`); use it when a project can't start until another is in place.
- Each file must include an `## Exit Criteria` section.

## Working With This Repo

- To add a new project: create a `NN-NNN-slug.md` file in the appropriate category directory,
  following the frontmatter convention above.
- To renumber project prefixes after reordering: `python update_prefixes.py`
- CI runs on every push/PR to `main` and is mirrored by `make` targets — run these locally before
  pushing:
  - `make format-check` — Prettier formatting check (`make format` to auto-fix).
  - `make lint` — markdownlint.
  - `make check-invariants` — validates frontmatter keys, `number`/filename match, per-category
    counts, and README totals (`scripts/check_invariants.py`).
  - `make test` — runs all three of the above.

## Notes

- This is a personal ideas/planning repo — no application code; content is Markdown project briefs.
- Cross-disciplinary projects (`07-cross-disciplinary/`) intentionally combine concepts from
  multiple categories.
