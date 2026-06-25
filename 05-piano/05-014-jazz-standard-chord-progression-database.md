---
title: 'Jazz Standard Chord Progression Database'
number: '05-014'
category: 'piano'
difficulty: 'Easy'
time_commitment: '1-2 days'
target_skills: 'JSON/YAML Parsing, Simple Web Frontend'
status: 'In Progress'
depends_on: []
---

# Jazz Standard Chord Progression Database

## Description

Create a structured, searchable database (e.g., in JSON format) of the chord progressions for the
top 100 jazz standards. Build a simple frontend to quickly pull up the changes for a song, transpose
them to any key, and display Roman numeral analysis.

## Repo

Built at [`gjcourt/changes`](https://github.com/gjcourt/changes) — a Go web app mirroring the
`vitals` pattern (Go server + embedded JSON corpus + vanilla-JS frontend). The bug-prone music logic
(chord parsing, transposition, Roman-numeral analysis) lives in a pure, unit-tested
`internal/theory` package; `web/` is a dumb renderer over a small JSON API.

## Exit Criteria

- [x] JSON schema for a standard (metadata + sections → bars → chord symbols), validated at load
- [x] Lookup: list standards and pull up a tune's changes as a lead-sheet grid
- [x] Transpose to any of the 12 keys, with key-correct enharmonic spelling
- [x] Roman-numeral analysis toggle (degree + quality; transposition-invariant)
- [x] Runs locally via `make run`; deployable like the other homelab apps
- [ ] Corpus backfilled toward the top ~100 standards (10 encoded so far)
- [ ] Optional: deployed to the homelab at `changes.burntbytes.com`
- [ ] Optional: full functional analysis (secondary-dominant labeling, e.g. `V7/ii`)

## Progress

- [x] Initial research — settled on the vitals stack (Go + vanilla `web/`), engine-in-Go design
- [x] Implementation — theory engine, library + embedded corpus (10 standards), JSON API, frontend;
      gofmt/vet/golangci-lint clean, race tests pass
- [x] Documentation — `README.md` + `AGENTS.md` (how to add a standard, the API, invariants)
- [ ] Backfill corpus + optional homelab deploy
