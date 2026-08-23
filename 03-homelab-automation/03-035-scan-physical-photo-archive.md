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

## The actual problem: a scan has no capture date

The existing photo import sorts on `DateTimeOriginal > CreateDate > FileModifyDate`. A scanned print
has **no `DateTimeOriginal`** — the scanner writes the date of the _scan_. So without intervention
every photo either:

- lands in the current month, burying a 1987 birthday in this week's phone snaps and destroying the
  exact chronology the project exists to build; or
- falls through to the importer's "no readable date — left in place" branch and never arrives.

The second failure is at least loud. The first is silent and corrupts the timeline.

So the deliverable is not "scanned files". It is **scanned files carrying a plausible
`DateTimeOriginal`**.

## Design decisions, and why

### Date by batch, not by photo — and don't build OCR

The tempting design is OCR on the scanned backs, parsing the lab date automatically. Rejected at
this volume.

Lab date codes are typically dot-matrix or thermal on glossy stock: low contrast, odd fonts, often
skewed. OCR will read _most_ of them, which is the worst outcome — every photo still needs checking
to find the failures, and a silently wrong date is worse than an absent one.

The manual path is cheaper than it looks because **prints come in runs**. Lab envelopes are
chronological, so 750 photos is more like 40–70 batches than 750 independent decisions. Typing 60
dates takes minutes. Building and tuning OCR takes an afternoon and still needs review.

Approximate is the correct target. The stamps "may not be accurate but range the photos reasonably"
— and a photo placed in the right season of the right year is worth far more in a timeline than one
placed precisely in the wrong decade.

**Revisit only if** the pilot shows the prints are _not_ grouped in chronological runs, which would
turn 60 decisions back into 750.

### Scan first, date second

Feeding paper through a machine is the irreversible-effort half; assigning dates is software that
can be redone forever. Do not block a scanning session on finished tooling. Get the prints through,
get them back in the box, then take as long as necessary over metadata.

### Keep unenhanced originals

The bundled software offers auto-colour, red-eye and rotation correction. Enhancement is lossy and
taste-dependent, and these prints get scanned once. Keep the untouched scan as the archival master
and treat any enhanced version as derived.

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
- [ ] Back-side images are archived and are **not** indexed as library assets.
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
- [ ] Reconcile counts and spot-check chronology across several decades.

## Related

- `03-028` — the household media library this feeds.
- `03-026` — the same storage layout and library, from the disc side.
