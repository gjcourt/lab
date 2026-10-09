---
title: 'Personal Search with a Tuned Embedding Model'
number: '03-041'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills:
  'embedding models, retrieval evaluation (recall@k, MRR), contrastive fine-tuning, vector index on
  CPU'
status: 'Not Started'
---

# Personal Search with a Tuned Embedding Model

## Description

"Find the thing I wrote about X" across my notes, plans and project files — semantic search that
understands my vocabulary and abbreviations, running on the cluster CPUs.

Start with a stock embedding model and a small vector index. Fine-tune the embedding model on my own
corpus only if retrieval on my own queries is measurably poor: generic models don't know that
"hestia" is a NAS or that "ito" is an espresso controller.

## Evaluation first

A fixed set of ~50 real queries I've actually wanted to answer, each with the document(s) that
answer it. Every model and index change is scored on recall@5 and MRR against that set. No
fine-tuning without a baseline number to beat.

## Privacy

The corpus includes private material. The index and any tuned model stay on hestia; training pairs
are generated locally; nothing private goes in git. If training needs a rented GPU, delete the data
from it afterwards.

## Exit Criteria

- [ ] A query set with answers, and a baseline score for a stock embedding model.
- [ ] Search running on the cluster over my notes, reachable from a golink.
- [ ] If fine-tuned: a measured gain over the baseline on the same query set.

## Plan

- [ ] Build the query set from real searches.
- [ ] Stock model + index; score it.
- [ ] Generate training pairs from the corpus; fine-tune; re-score; keep the better one.

## Related

- `03-040` — email triage; shares the embedding model choice.
- `03-034` — the household chat service that could use this for retrieval.
