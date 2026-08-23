---
title: 'Scan the Physical Photo Archive into the Family Library'
number: '03-035'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills:
  'Sheet-fed scanning, EXIF surgery with exiftool, batch metadata workflows, Immich external
  libraries'
status: 'Not Started'
depends_on:
  - '03-028'
---

# Scan the Physical Photo Archive into the Family Library

## Description

Digitise roughly 500–1000 physical prints on an Epson FF-680W and land them in the existing family
photo library so they appear **in chronological order** alongside everything else.

The scanning is the easy half. The prints have lab date stamps on the back and the scanner captures
both sides in a single pass, so the dates exist — they just have to end up in the right EXIF field
before the library ever sees the files.

## What the pilot established

A seven-print pilot ran before this note was finalised, and it disproved the premise the plan
originally rested on. Recorded here so it is not re-derived.

**The scans are not dateless.** The bundled software writes `CreateDate` (EXIF and XMP) derived from
**the folder name you type at scan time**. A folder called `1990s` produced
`CreateDate 1990:01:01 12:00:00` on every file. `DateTimeOriginal` is absent, but the existing
import chain is `FileModifyDate` → `CreateDate` → `DateTimeOriginal` with last-listed winning, so
`CreateDate` beats the file's modification time. These sort to **1990/01, not the current month.**

The original fear — that scans get buried among this week's phone photos — was wrong.

**The real problem is granularity, not absence.** Every print in a decade-named folder receives an
identical timestamp. Scan a whole decade and 300 photos stack on one January day. That is not a
timeline either, it is just a differently-shaped mess.

**Which makes the folder name the dating mechanism.** Naming a folder `1996` instead of `1990s` pins
that batch to 1996. The date is therefore set _at scan time, for free_, by typing a better guess —
no contact sheets, no CSV, no `exiftool` pass for the common case. This replaces most of the tooling
this project was originally going to need.

**Two defaults must be changed before the real run:**

- Resolution defaults to **300 dpi**. A 4×6 at 300 gives ~1700×1180. Use 600.
- Double-sided capture is **off by default** — the pilot produced no back-side images at all. The
  back stamps are the entire reason the dates are recoverable, so this must be enabled.

Both are unrecoverable without re-feeding the print; dates are not. That asymmetry decides what is
worth re-scanning.

**Both an original and an enhanced version are kept automatically.** The pilot produced pairs:
`NNNN.jpg` and `NNNN_a.jpg`, identical in dimensions and EXIF. The `_a` file is measurably brighter,
higher-contrast and more saturated — it is the auto-enhanced version, and the base file is the
untouched scan. Retaining an archival master needs no special handling; it needs a decision about
which of the two the library indexes.

## Risks

**The feeder can destroy a print.** This is a roller-fed scanner. Curled, brittle, torn or oversized
prints can jam, and a jam on a one-of-a-kind photo is unrecoverable. Sort for condition _before_
feeding, and route anything irreplaceable or non-flat to a flatbed or a camera copy stand instead.
This risk is front-loaded and permanent; every other risk here is recoverable.

**Back-side images will pollute the library.** They carry the dates and sometimes handwritten notes,
so they are worth keeping — but if they land in the library's import path they double the asset
count with photographs of blank cardboard. They belong in a sibling archive directory outside the
indexed paths.

**The library indexes specific per-person paths.** Inherited family photos do not belong to any
current user, so this needs a third bucket and a library configuration change, not just a new folder
on disk.

## Exit Criteria

- [ ] Every scanned print carries a `DateTimeOriginal` within the correct year, and where the stamp
      allows it, the correct month.
- [ ] Scrolling the library to any given year shows scanned prints interleaved with digital photos
      from that year, in order.
- [ ] Unenhanced archival masters are retained and identifiable as such.
- [ ] Back-side images and enhanced duplicates are archived and **not** indexed as library assets.
      Verified by asset count, not by inspecting configuration.
- [ ] Zero prints damaged. Any print judged too fragile to feed is recorded as deliberately excluded
      rather than quietly skipped.
- [ ] The count of prints in the box reconciles against the count of assets in the library.

## Tasks

- [ ] **Pilot: scan ten photos and inspect the output.** This is task one and everything else
      depends on it. It answers, for the cost of five minutes: the file-naming convention for front
      versus back, whether the back stamps are legible enough to date from at all, real throughput
      per print, and actual file sizes. Do not plan further until this is done.
- [ ] Decide scan resolution from the pilot. 600 dpi on a 4×6 yields roughly 2400×3600, which is
      past the grain limit of most consumer prints; 1200 dpi is usually wasted storage.
- [ ] Triage the physical archive for feeder safety, and separate the exclusions.
- [ ] Establish the batch convention: one envelope or album section per scan run, preserving order.
- [ ] Scan everything, double-sided, unenhanced. Physical work done in one pass.
- [ ] Build the dating aid: contact sheets of the back images plus a CSV mapping filename ranges to
      dates.
- [ ] Apply dates with `exiftool`, writing `DateTimeOriginal` on fronts only.
- [ ] Separate back-side images into the archive directory.
- [ ] Add the family bucket to the library's indexed paths and trigger a scan.
- [ ] Back up the scans before any `exiftool` run. It writes in place, and a bad mapping applied
      across hundreds of files is only recoverable against a pristine copy.
- [ ] Reconcile counts and spot-check chronology across several decades.

## Related

- `03-028` — the household media library this feeds.
- `03-026` — the same storage layout and library, from the disc side.
