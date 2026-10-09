---
title: 'Email Triage Classifier (trained on how I actually handle mail)'
number: '03-040'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills:
  'text classification (small transformer or embeddings + linear head), label extraction from Gmail
  history, precision/recall on imbalanced classes, CPU inference'
status: 'Not Started'
depends_on:
  - repo/valet
---

# Email Triage Classifier (trained on how I actually handle mail)

## Description

A small, private classifier that sorts incoming mail the way I already do — reply, read later,
archive, needs action — trained on my own history of what I did with past mail. It runs on the
cluster CPUs and pre-sorts the valet sweep, so the LLM step only sees what's worth its time.

The labels already exist: what I replied to, archived unread, starred or left in the inbox.

## Design notes

- **Start with the cheapest model that works:** sentence embeddings plus a linear head, before any
  fine-tuned transformer. Fine-tune only if that plateaus.
- **Bias toward "show me":** a missed important email costs more than an extra one in the pile.
  Measure recall on the classes that matter, not overall accuracy.
- **Private by construction:** mail and labels stay on hestia; nothing in git. If training needs a
  rented GPU, the data is deleted from it afterwards.

## Exit Criteria

- [ ] A labelled dataset extracted from my Gmail history, with the label rules written down.
- [ ] Recall on "needs a reply / needs action" measured on held-out recent mail, at a level I
      accept.
- [ ] Wired into the valet sweep as a pre-sort, with its decisions visible and overridable.

## Plan

- [ ] Define the label set and how each label is derived from history.
- [ ] Baseline: embeddings + linear head; measure.
- [ ] Fine-tune only if the baseline misses too much; deploy the winner on CPU.

## Related

- `03-041` — personal search; shares the embedding model choice.
