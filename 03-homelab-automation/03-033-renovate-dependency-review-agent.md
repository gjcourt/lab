---
title: 'Renovate Dependency Review Agent (LLM second reader)'
number: '03-033'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills: 'Claude API, Kubernetes CronJobs, Renovate internals, LLM evaluation & backtesting'
status: 'In Progress'
---

# Renovate Dependency Review Agent (LLM second reader)

## Description

An LLM reviewer that reads the **release notes** of a dependency-update PR and comments before a
human approves it. It exists because the existing automation reads _version labels_, and version
labels lie.

The self-hosted Renovate CronJob opens the PRs; a sibling automerge CronJob classifies them by
update type and merges the safe ones. Both operate purely on what Renovate declares — `patch`,
`minor`, `major`, `digest`. Neither can read a changelog. This project adds the layer that can.

## The problem, with receipts

Three cases where the declared update type did not represent the risk:

| Dependency                                        | Declared | Reality                                                                                                                          |
| ------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `viem` 2.55.16 → 2.55.19                          | `patch`  | Author-labelled **Breaking** — a renamed parameter, shipped in a patch release                                                   |
| `python` 3.12 → 3.14 (via `setup-python`)         | `minor`  | A **two-release interpreter jump**. Python's `3.x` _is_ the semver minor field, so Renovate grouped it with routine action bumps |
| `lscr.io/linuxserver/qbittorrent` 5.2.1 → 20.04.1 | `major`  | Not a version bump at all. The `20.04.x` tag is the **Ubuntu base version**, frozen on qbit 4.3.9 — a silent downgrade           |

The third one merged and had to be reverted. Notably the classifier _held it correctly_ — the PR was
labelled `major` and automerge was disabled on it. **A human approved it anyway**, past a warning
Renovate had printed in the PR body: _"Some dependencies could not be looked up."_

That reframes the target. This is not a safety net for automerge, which already fails closed. It is
a **second reader for the PRs a human approves by hand.**

## Evidence — the backtest

Run before writing any code, against 257 historical merged Renovate PRs across ten repositories.

**Method.** Sample 18 PRs from the population that actually needs judgement (majors plus PRs whose
body has no Update column — 57 of 257, about 22%). Seed the one PR with a confirmed post-merge
regression into the sample. Shuffle, withhold the answer key, and give two independent reviewers
nothing but the PR title and body — exactly what a human sees. Reviewers may fetch upstream
changelogs and registry tag lists. Both are barred from searching for reverts, incidents or
post-merge discussion: **reason forward from the evidence, never backward from a known outcome.**

**Result.**

| Metric                  | Value                                            |
| ----------------------- | ------------------------------------------------ |
| Known regression caught | **Both reviewers, confidence 5/5**               |
| Reviewer A held         | 8 of 18 (44%)                                    |
| Reviewer B held         | 5 of 18 (28%)                                    |
| Agreement               | 15 of 18 (83%)                                   |
| Contradictions          | **Zero** — B's flags were a strict subset of A's |

Both reconstructed the tag-scheme root cause from the PR body alone, and both independently noticed
the ignored "could not be looked up" warning.

All three disagreements were the _same dependency_ appearing three times — one reviewer held it, the
other judged it would fail loudly in CI. A substantive engineering disagreement, not instability.

## Design, as the backtest dictates it

- **Veto only, never approval.** It can move a PR from _would-merge_ to _held_. It can never move
  one the other way. A wrong call costs a manual review, never a bad merge — the same fail-closed
  principle the classifier uses.
- **Two-reviewer consensus.** Single-reviewer mode holds 44%; requiring both to agree holds 28% and
  loses nothing that mattered.
- **Deduplicate by root cause, not per PR.** One finding appeared three times in eighteen. At real
  volume that is the same paragraph repeated until nobody reads it — the standard way a useful
  signal becomes wallpaper.
- **Scope to judgement calls.** Skip digests and routine patches; run only on majors and PRs with no
  Update column. That is ~22% of PR volume.
- Runs as a third CronJob beside the existing Renovate and automerge jobs. Renovate is already
  self-hosted in-cluster, so there is no external service in the loop.

## Cost

Roughly $0.125 per review at Opus rates, doubled for consensus, on ~22% of PRs. At current volume
that is **$100–150/year** — real but modest. Worth building because it catches regressions, not as a
way to consume a credit balance.

## Exit Criteria

- [ ] Runs on a schedule against open dependency PRs across all watched repositories.
- [ ] Posts a PR comment only when both reviewers agree the PR warrants scrutiny.
- [ ] Cannot merge, approve, or unblock any PR under any circumstances — verified by the absence of
      write scopes on its token, not by prompt instruction.
- [ ] Findings are deduplicated by root cause across PRs in the same run.
- [ ] Replaying the backtest corpus through the deployed pipeline reproduces the known catch.
- [ ] A measured false-positive rate on a fresh sample, recorded in this file.

## Tasks

- [x] Assemble a corpus of historical dependency PRs with known outcomes
- [x] Identify ground truth — a merged PR with a confirmed post-merge revert
- [x] Run a blind two-reviewer backtest and record agreement and hit rate
- [x] Write the reviewer prompt as a version-controlled artifact, not an inline string
- [x] Build the runner: enumerate open PRs, filter to judgement calls, review, comment
- [x] Replay the corpus through the built filter — selects 58 of 258 (22%), known-bad included
- [x] Mock-run the full pipeline with agents standing in for the API, exercising the JSON contract,
      consensus gate, dedup and comment rendering
- [x] Make the hold binding: a `held-by-review` label the automerge classifier honours
- [x] Write the ConfigMap and CronJob, shipped suspended
- [ ] Buy API credits on a personal account and land the SOPS secret
- [ ] Prove the read-only constraint on the real token — `issues:write`, no `contents:write`
- [ ] Unsuspend and observe one week in shadow mode without commenting
- [ ] Enable commenting; record the false-positive rate here after a month

## Build notes

The only untested leg is the HTTP call itself. Everything either side of it was exercised by
replaying the historical corpus and by a mock run that swapped the API transport for verdict files
on disk.

Two things the mock run settled that were genuinely uncertain beforehand:

**Root-cause slugs agree across independent reviewers.** Dedup groups on exact string match, so a
reviewer writing "node runtime major" for one PR and "major node runtime bump" for another would
defeat it. Both reviewers independently produced byte-identical slugs. Free text is sufficient; a
fixed enum is not needed yet.

**Consensus removes a specific class of false positive.** The three PRs one reviewer held and the
other passed were all the same `actions/checkout` finding — a real breaking change that does not
apply to how these workflows use the action. The reviewer sees the PR body, not the repository, so
it cannot know that. The second reviewer catches it. This is also the clearest known limitation:
giving the reviewer the workflow file would fix it directly, at the cost of tokens and surface area,
and that trade is worth making only once a real false-positive rate has been measured.

**The hold has to be enforced, not requested.** The reviewer comments; the classifier does not read
comments. Without the label the reviewer would flag a PR at 01:00 and the classifier would merge it
at 06:00 anyway. The label is the enforcement, and the token lacking `contents:write` is what keeps
the reviewer incapable of doing it any other way.
