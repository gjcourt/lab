---
title: 'Audio CD Ripping on macOS (AccurateRip → FLAC → music library)'
number: '03-032'
category: 'homelab-automation'
difficulty: 'Easy'
time_commitment: '1-2 hours'
target_skills:
  'AccurateRip Secure CD Extraction, Drive Read-Offset Calibration, FLAC/MusicBrainz Tagging,
  Library Naming Normalization'
status: 'Not Started'
depends_on: ['03-028 media library', '03-029 sfpl borrow-and-rip pipeline']
---

# Audio CD Ripping on macOS (AccurateRip → FLAC → music library)

## Goal

Turn a borrowed or owned audio CD into correctly-tagged, **AccurateRip-verified FLAC** in the music
library, using the same external USB optical drive already used to rip DVDs/Blu-rays
([03-026](03-026-rip-owned-4k-uhd-blurays-to-nas-jellyfin.md)). This fills the gap in the
[03-029](03-029-sfpl-borrow-and-rip-pipeline.md) pipeline, which specifies _which_ CDs to borrow but
defers the actual CD-rip tool/command to the video pipeline. This is the CD equivalent: the
disc-to-file step for **audio**.

**M-Disc is a red herring.** M-Disc is a write-once archival _burn_ medium for DVD/BD burners;
reading a Red Book audio CD has nothing to do with it. Any drive that reads CDs — including the LG
BH16NS40 used here — rips audio CDs natively.

## Hardware / environment (verified)

- **Drive:** LG HL-DT-ST BD-RE **BH16NS40** (external USB Blu-ray/DVD/CD writer). Reads CD-DA
  natively; shows as `/dev/disk4` (`drutil status`).
- **Host:** Apple Silicon (arm64), macOS.
- **Assumed, confirm at rip time:** the BH16NS40 AccurateRip **read offset is +6 samples** (typical
  for this LG family) — let the ripper confirm it against the AccurateRip DB rather than trusting
  the number.

## Tool: XLD

**Use XLD** (`brew install --cask xld`). It is the macOS gold standard and the only option that
delivers AccurateRip-grade correctness on Apple Silicon with an external USB drive:

- AccurateRip verification against the online DB (the point of ripping-to-keep).
- Correct drive read-offset handling (auto-detect + AccurateRip confirmation).
- Secure/paranoid ripping with C2 error pointers, per-track CRC, rip log + cue sheet.
- FLAC output, MusicBrainz metadata, cover-art embedding — all built in.
- Native arm64; works with the USB BH16NS40.

The catch, stated honestly: **XLD is a GUI.** Its CLI binary is for transcoding files, not driving a
secure AccurateRip extraction — so the rip itself is a GUI action. In practice it is one-time
config, then ~2 clicks per disc (insert → auto MusicBrainz/AccurateRip lookup → Extract), which is
less fragile than the CLI alternatives.

Ruled out: **whipper** (not brew-installable, Linux/Docker-oriented, fragile drive-offset detection
on macOS USB), **cyanrip** (not in Homebrew; no AccurateRip verification), **abcde**
(brew-installable but no AccurateRip DB verification, fiddly `cdparanoia` device wiring on macOS).
Keep `abcde` only as an optional CLI fallback for a disc XLD can't reach.

## One-time XLD configuration

XLD → Preferences:

- **Output format:** FLAC, compression 8; "Embed cue sheet" + "Embed cover art".
- **CD Rip → Ripper mode:** XLD **Secure Ripper** (paranoid). "Query AccurateRip" on; "Verify
  suspicious sectors" on; "Save log" on.
- **Drive offset:** CD Rip → **Configure Drive** → insert an AccurateRip-pressed CD → let XLD
  detect/confirm the offset (should be **+6** for the BH16NS40). This must be right or AccurateRip
  never matches.
- **Filename format:** `%n %t` → `01 Title` (matches the library convention); directory `%A/%T`.
- **Metadata:** MusicBrainz lookup + cover-art fetch on.

Also set macOS **"When you insert a CD" → Ignore** (System Settings / Music.app) so Music.app does
not grab or eject the disc mid-rip.

## Library target + naming (confirmed against the live library)

- **Canonical path:** `/mnt/main/family/media/music/<artist>/<album>/` on hestia
  (`ssh truenas_admin@10.42.2.10`). This is the modern FLAC library the 03-029 owned-dedup reads
  (~1,200 FLACs).
- **Convention (confirmed by inspecting real albums):** **lowercase-kebab** artist and album
  directory names; track files `NN Title.flac` (2-digit zero-padded, single space, Title-Case title,
  **no dash** — e.g. `01 Fig Tree Bay.flac`). Tags and art are **embedded**; **no** sidecar
  `.cue`/`.log`/`cover.jpg` in album dirs.
- **Do not** target the legacy `/mnt/main/media/music/` (Synology-era Title-Case + `@Syno*`
  sidecars).

## Rip workflow (per disc)

1. Insert CD. XLD reads the TOC and queries **MusicBrainz + AccurateRip**; a track list with tags
   appears.
2. Confirm/fix metadata (artist, album, year, disc-of-set) and cover art.
3. **Extract** to a local staging dir, e.g. `~/src/music-library/rips/`.
4. XLD writes `NN Title.flac` (embedded tags + art) plus an album `.log` and `.cue`.
5. Normalize the `Artist/Album` dir names to lowercase-kebab, then move over SMB (same path the
   video pipeline uses), dropping the `.log`/`.cue` the on-hestia library doesn't carry:

   ```bash
   kebab() { echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g'; }
   rsync -rtv --exclude='*.log' --exclude='*.cue' \
     ~/src/music-library/rips/<artist>/<album>/ \
     /Volumes/family/media/music/<artist>/<album>/
   ```

6. **Refresh the SFPL owned-dedup list** (03-029) so future holds don't re-borrow what you now own —
   re-run the `find … -mindepth 2 -maxdepth 2 -type d` over the music path into
   `~/src/music-library/owned_albums.txt`.
7. Eject: `diskutil eject disk4` (or `drutil eject`).

## Verify a good rip

- Open the album `.log` — every track reads **"Accurately ripped"** (AccurateRip confidence _N_), or
  at minimum "no errors / no suspicious sectors" for a disc not in the AccurateRip DB.
- FLAC integrity: `flac -t ~/src/music-library/rips/**/**.flac` — all tracks `ok`
  (`brew install flac`).
- Spot-check tags: `metaflac --list --block-type=VORBIS_COMMENT "01 Title.flac"`.

**A good rip = AccurateRip "Accurately ripped" on all tracks + `flac -t` all `ok` + correct offset
in the log.**

## Exit Criteria

- [ ] **XLD installed + drive offset calibrated** — `brew install --cask xld`, offset confirmed (+6
      expected) against an AccurateRip-pressed disc.
- [ ] **First CD ripped + verified** — a disc ripped to FLAC with AccurateRip "Accurately ripped" on
      all tracks and `flac -t` all `ok`.
- [ ] **Landed in the library correctly** — files at
      `/mnt/main/family/media/music/<artist>/<album>/`, lowercase-kebab dirs, `NN Title.flac`,
      embedded tags + art, no sidecars; visible in Navidrome.
- [ ] **Owned-dedup refreshed** — `owned_albums.txt` (03-029) re-generated so the borrow queue stops
      re-borrowing the now-owned album.

## Gotchas

- **SMB write path can be TCC-blocked.** `/Volumes/family` may return "Operation not permitted" on
  macOS even while mounted — a Full Disk Access / stale-mount issue, not a hestia one. Grant the
  terminal Full Disk Access, or remount via Finder → Connect to Server `smb://hestia/family`.
  Fallback is the `truenas_admin` staging rsync used by the video pipeline.
- **Enhanced / CD-Extra discs** (audio + data session): XLD rips the audio session and ignores the
  data track — expected.
- **Copy-protected CDs** (Cactus Data Shield etc.): the secure ripper re-reads and reports
  confidence; a few may log "suspicious" sectors with no AccurateRip entry. Re-rip, try a slower
  speed, or accept the logged best effort. Rare in the jazz / classic-rock catalog.
- **Not in AccurateRip** (out-of-print/rare): no match available — rely on the secure-ripper "no
  errors" result instead of a confidence number.
- **SACDs stay separate.** The `.dsf` DSD/SACD rips in the library come from a different workflow;
  this CD path does not produce those.
