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
---

# Scan the Physical Photo Archive into the Family Library

## Description

Digitise roughly 500–1000 physical prints on an Epson FF-680W and land them in the existing family
photo library so they appear **in chronological order** alongside everything else.

Scanning is the easy half and takes an afternoon. Dating is the project, and it is a records problem
rather than a software one: **the date has to be captured while the print is still in your hand**,
because nothing recoverable from the file itself will tell you later.

## What the pilots established

Two pilot batches ran before this note was finalised. Together they disproved the premise the plan
originally rested on, so the evidence is recorded here rather than re-derived.

### The scans are not dateless — they carry the folder name

The bundled software writes EXIF `CreateDate` derived from **the folder name typed at scan time**. A
folder named `1990s` produced `1990:01:01 12:00:00`; a folder named `1996` produced
`1996:01:01 12:00:00`. Every file in a batch gets the identical value.

The original fear — that scans land among this week's phone photos — was wrong. **The real problem
is granularity**, not absence: name a folder for a decade and 300 photos stack on one January day.
That is not a timeline, just a differently-shaped mess.

Enter the finest interval you can actually justify. The stock flow accepts year _and_ month, so
month-level granularity is free at scan time and unavailable at every later point.

### The folder name is the only date source that exists

The second pilot was designed to check whether the software extracts a date from the image — from a
camera's date burn-in, say — and prefers it over the folder name. It does not, and the reason is
that there was nothing to extract:

- **The backs are blank.** Seven of seven, at 600 dpi with double-sided capture on. Mean luminance
  254.5/255, zero pixels below 100. No lab stamp, no handwriting — only the paper's own watermark.
- **The fronts carry no date burn-in.** Borderless prints, no orange corner stamp.

So the project's founding assumption — _"the prints have lab date stamps on the back"_ — is false
for this batch. **Do not generalise from one envelope in either direction**; see the corpus survey
below. But where it holds, the dating chain is: your memory of the event → the folder name → EXIF.
There is no second opinion available anywhere in the artifact.

### The most precise date source is usually the image content, not the artifact

The pilot batch was dated to a single year not from any stamp but from what is _in_ the frame. Two
kinds of signal did the work, and both generalise:

- **Institutional anchors.** If a subject's school start year is known, apparent grade level
  converts directly to a calendar year, and a childhood archive is largely school events. One
  remembered anchor date prices out a decade of photographs.
- **Curriculum and setting cues.** Standardised school curricula are sequenced by grade, so a
  visible classroom topic pins the grade independently — which either corroborates the estimate or
  exposes it.

This is slow per photo and fast per envelope, since one identified event dates everything shot at
it. It argues for a triage pass that sorts by _recognisable event_ rather than by print appearance,
and for doing that pass with someone who was there.

### A blank back is still evidence — the paper's backprint is datable

The backs carry no stamp, but they carry the manufacturer's repeating backprint, and for Kodak that
text is a dated artifact. A published conservation chronology (Weaver & Keirstead, _Ektacolor Paper
Backprint Chronology_, AIC Photographic Materials Group, 2009; and G. Weaver, "A Study of Kodak
Color Prints, 1942–2008," _Topics in Photographic Preservation_ 13) maps backprint wording to date
ranges, some of them sub-two-year. The pilot batch's backprint is placed by that chronology in a
**21-month window**, which independently corroborated the year reached by content recognition.

Two things follow:

- **It is a falsifier for memory-based dating.** The content-recognition method above has no
  internal error check — a confidently misremembered year looks exactly like a correct one. A
  backprint window that contradicts the guess is the cheapest available way to catch that, and it is
  the only signal here that does not depend on anyone's recall.
- **The paper dates manufacture, not exposure.** Stock sits in a lab's inventory, conventionally up
  to ~18 months, so treat the window as a hard floor and a soft ceiling. It excludes years; it does
  not name one.

Coverage is thin outside Kodak — Agfa is partially documented, Fuji is forum-tier, and Konica has no
published chronology at all.

### Consequence: scan one back per paper stock, not every back

The backprint is identical across a paper batch, so the signal is captured by **one** back per
envelope and the rest are duplicate photographs of blank cardboard. Full double-sided capture spends
a third of the file count and all of the handling time to learn nothing extra.

Scan or photograph a single back per envelope into the archive directory, and leave double-sided off
for the run — enabling it only where a survey shows the backs are actually written on.

### One print emits up to three files, and `_a` is an overloaded suffix

At final settings each print produced `NNNN.jpg`, `NNNN_a.jpg` and `NNNN_b.jpg` — 7/7/7 across the
batch. Measured: `_a` is brighter, higher-contrast and more saturated than the base, so **`_a` is
the auto-enhanced copy and the base file is the untouched scan**. `_b` is the back — ~0.5 MB against
~4.4 MB, consistent with a near-blank sheet.

Note that on the predecessor model `_a`/`_b` meant _front_/_back_. A naive "exclude `*_b`" filter is
therefore not portable, and the reconciliation identity should be written down explicitly:

```text
prints in box = indexed fronts + deliberate exclusions + failed feeds
```

Storage at final settings is roughly 10 MB per print for all three files, ~4.5 MB for fronts alone.

### Resolution defaults to 300 dpi

That yields ~1700×1180 on a 4×6 — thin. 600 dpi gives ~3400×2370 and is the right setting; 1200 is
past the grain limit of consumer prints and is wasted storage.

## Risks

**The feeder can destroy a print.** This is a roller-fed scanner; a jam on a one-of-a-kind photo is
unrecoverable. Sort for condition _before_ feeding and route anything brittle, curled, torn or
irreplaceable to a flatbed or copy stand. This risk is front-loaded and permanent — every other risk
here is recoverable.

**A double-feed is silent.** Two prints stuck together produce N−1 files and no error at all. So
does a skewed or half-captured frame. By the time it would be noticed, the prints are back in the
box.

**Importing before the date is final creates permanent duplicates.** The library's external-library
mode identifies assets by **path**, not by content hash, and its maintainers have explicitly
declined to add move detection. Re-dating changes the `YYYY/MM` path, so the re-dated file is
ingested as a new asset and the original is orphaned — with no dedupe to catch it. This makes
"import now, fix dates later" destructive rather than merely untidy.

> **Invariant: no scan enters an indexed import path until its date is final.** Do all EXIF work in
> a staging directory outside the library.

**`DateTimeOriginal` alone is not sufficient.** The library's date precedence puts
`SubSecDateTimeOriginal` and `SubSecCreateDate` _above_ `DateTimeOriginal`. If the scanner ever
writes a sub-second variant carrying the scan time, it silently outranks whatever was written and
the print lands in the current year. The pilot files carry only `CreateDate` and no sub-second tags,
so this is currently latent rather than active — which is exactly the kind of thing that changes
under a firmware update without announcing itself.

**EXIF cannot express "year known, month unknown."** A month or day of `00` is rejected outright.
Any year-only date therefore has to fabricate a month, and the fabrication is indistinguishable
later from a real one. Pick a policy — unknown month → `YYYY:07:01 12:00:00` — and record the _true_
precision separately, in a keyword or an XMP partial date, so a later pass can tell a guess from a
reading.

**`exiftool` defaults work against this workflow.** Without `-P` it bumps `FileModifyDate` to now;
without `-overwrite_original` it scatters `*_original` copies that the library would index if the
directory were ever inside an import path.

**Back-side and enhanced images will pollute the library** if they reach an import path — the asset
count triples rather than doubles. They belong in a sibling archive directory. Symlinking them in is
not an escape hatch; the library does not follow symlinks in import paths.

**The library indexes per-person paths.** Inherited family photos belong to no current user, so this
needs a third bucket and a configuration change, not just a new folder on disk.

## Open questions

- **Do any envelopes have written backs?** One batch says no. The answer decides whether
  double-sided capture is ever worth enabling, and it is cheap to settle — see the survey task.
- **Which events are still recognisable, and by whom?** The content-dating route depends on someone
  identifying the occasion. That capacity is not permanent, which is the one part of this project
  with a real deadline attached.
- **Are the prints still in chronological runs?** Prints that end up loose in a box are often the
  ones pulled _out_ of envelopes and re-sorted by subject or person. Batch dating is cheap only if
  batch boundaries mean something.
- **Do reprints break the batch?** A reprint or enlargement run carries one date that can postdate
  the photographs by years and typically mixes eras within one envelope.

## Exit Criteria

- [ ] **Zero files lack a date tag.** Counted, as a gate before import — not sampled.
- [ ] **No asset is dated after the scan date**, and the year histogram matches the expected shape
      of the archive.
- [ ] For the years where the archive overlaps the digital library, three named years each show
      scanned prints correctly interleaved with digital photos.
- [ ] Every date is recorded with its true precision, so a year-only guess is later distinguishable
      from a month read off a stamp.
- [ ] Unenhanced archival masters are retained and identifiable as such.
- [ ] Back-side images and enhanced duplicates are archived and **not** indexed. Verified by asset
      count, not by inspecting configuration.
- [ ] Zero prints damaged, against a **count taken before feeding**. A print judged too fragile is
      recorded as a deliberate exclusion, not quietly skipped.
- [ ] `prints in box = indexed fronts + deliberate exclusions + failed feeds` balances.

## Tasks

- [x] **Pilot: scan a batch and inspect the output.** Done twice. Findings above.
- [ ] **Survey the corpus before committing to a workflow.** Sample ten envelopes or album sections
      at random and record, for each: how many prints, how many have written backs, how many
      distinct dates appear within the envelope, and whether it looks like a reprint run. This is
      fifteen minutes and it decides double-sided capture, batch-vs-per-photo dating, and whether
      the chronological-runs assumption holds. A ten-photo scan cannot answer any of those.
- [ ] Triage the physical archive for feeder safety; separate and record the exclusions.
- [ ] Look up each distinct backprint wording in the published chronology once, and keep the
      resulting date windows as a per-paper-stock lookup. It is a fixed cost per _wording_, not per
      print, and it bounds every envelope on that stock.
- [ ] **Do the dating pass on the prints, not on the scans** — sort by recognisable event, with
      someone who was there, and write the year and month on the envelope. Cross-check each result
      against that envelope's backprint window and investigate any contradiction rather than
      averaging it away. This is the step that actually produces the dates; everything downstream is
      mechanical.
- [ ] **Scan at final settings, entering year and month per envelope while the envelope is in your
      hand.** 600 dpi, enhancement on (both copies are kept), double-sided only where the survey
      says the backs are written on. Use the per-batch subfolder option — it namespaces the filename
      counter, so an interrupted session costs one envelope rather than the whole mapping.
- [ ] Write a per-envelope print count on the envelope before feeding, and reconcile against files
      emitted immediately — while the prints are still out.
- [ ] Flip through contact sheets before the prints are put away, to catch skew and half-captures
      while re-feeding is still cheap.
- [ ] **Back up the raw scans.** This is the only irreversible software step against irreplaceable
      data, and it comes before the first `exiftool` run.
- [ ] Derive EXIF dates mechanically from the folder or filename, in a staging directory. Write
      `-AllDates`, clear the higher-precedence scan-time tags explicitly, and use `-P` and
      `-overwrite_original`. Verify on one file with `exiftool -time:all` _and_ by confirming the
      date the library actually displays — not by re-reading the tag that was just written.
- [ ] Increment seconds across each batch in scan order, so intra-batch ordering is defined rather
      than left to tie-breaking.
- [ ] Separate back-side and enhanced images into the archive directory, outside every import path.
- [ ] Add the family bucket to the library's indexed paths and trigger a single scan. Only now.
- [ ] Reconcile counts and spot-check chronology across several decades.

## Related

Nothing here shares storage or tooling with this project — the photo library is separate from the
video and music one, and this note's dependencies live in the homelab repo rather than in lab.

- `03-026` — bulk-ingesting physical media into a self-hosted library, from the disc side. Different
  library and different storage, but the same triage → capture → verify shape, and the same problem
  of reconciling a physical count against an indexed one.
