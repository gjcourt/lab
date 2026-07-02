---
title: 'Rip Owned 4K UHD Blu-rays to the NAS (TrueNAS → Jellyfin)'
number: '03-026'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'Optical Drive Flashing, MakeMKV/HandBrake, ZFS Dataset Layout, Jellyfin/HDR Direct Play'
status: 'In Progress'
---

# Rip Owned 4K UHD Blu-rays to the NAS (TrueNAS → Jellyfin)

## Description

Build a repeatable pipeline that turns a **legally owned** 4K UHD Blu-ray disc into a lossless file
on the TrueNAS pool, served by Jellyfin, that **Direct Plays** with HDR and lossless audio intact.
The goal is a personal media archive — own the disc, keep the disc, watch the file — not a
distribution operation.

The hard parts aren't the ripping software; they're the three places a naive setup silently degrades
quality: (1) getting a **LibreDrive-capable optical drive** that can read AACS 2.0 UHD discs at all,
(2) storing a **lossless remux** rather than a lossy re-encode as the master, and (3) engineering
Jellyfin + the playback client for **Direct Play** so the server never transcodes HDR down to
washed-out SDR.

## Legal note (read this first)

This project is scoped to **personal backup of discs I own**: rip to TrueNAS, watch on Jellyfin at
home, keep the physical discs. Be honest about the law, though — 4K UHD Blu-rays are protected by
**AACS 2.0**, and ripping them circumvents an access-control measure under **DMCA §1201**. There is
**no explicit space-shifting / personal-backup exemption** for this; the act is technically a §1201
violation even when you own the disc and never share the file. In practice it is not enforced
against individuals making personal backups, but "unenforced" is not "legal." The mitigations are
behavioral: keep it personal, keep the discs, never redistribute the files.

## Hardware

The single biggest gate is the optical drive. Only a narrow set of LG drives can be flashed with
**LibreDrive** firmware to read UHD discs; everything downstream depends on picking the right one.

### Acquired (awaiting shipment)

| Component     | Model                                              | Why                                                                                                                              |
| ------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Optical drive | **LG WH16NS40** (ROM 1.00, mfd Jan 2023)           | Jan-2023 build ships the **MediaTek MT1959** chipset → LibreDrive-flashable. NS40 becomes an NS60 after flashing.                |
| Flash target  | **WH16NS60 firmware `1.02-MK`**                    | Single WRITE step. Flash on a **native motherboard SATA port**, not through the enclosure, then move the drive to the enclosure. |
| Enclosure     | **OWC Mercury Pro 5.25" (OWCMR3UKIT, "NO Drive")** | Externally powered (12 V / 3 A) so no USB bus brown-out; USB 3.2 Gen1; community-confirmed LibreDrive passthrough.               |

The OWC enclosure is externally powered on purpose: bus-powered 5.25" enclosures brown out spinning
a UHD disc, which is exactly when LibreDrive reads fail. A **USB-A → USB-C adapter is fine** —
optical read tops out around **35–70 MB/s**, far below USB 3.x bandwidth, so the bridge is never the
bottleneck.

### Buying checklist (if sourcing again)

**Flashable — look for:**

- MediaTek **MT1959** chipset (service label reads **"SVC code NS50"**).
- Manufactured **after ~Oct 2015**.

**Avoid — these brick or break LibreDrive:**

| Pitfall                                    | Why                                                                            |
| ------------------------------------------ | ------------------------------------------------------------------------------ |
| **MT1939** chipset / pre-Oct-2015 drives   | Wrong/old chipset — flashing bricks them.                                      |
| **Generic no-name enclosures**             | Unverified USB bridge chips break LibreDrive passthrough even on a good drive. |
| **Current Vantec NexStar DX2 (NST-540S3)** | Community read-error reports; not a safe bet for UHD.                          |

Note: **WH16NS40 and WH16NS60 are the same drive post-flash** — pick whichever is cheaper and flash
it to the NS60 `1.02-MK` firmware.

## Software

| Tool                                | Role                                                                                 | Watch out for                                                                                                                       |
| ----------------------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **MakeMKV**                         | Reads the disc via LibreDrive, decrypts AACS 2.0 / BD+, writes a lossless MKV remux. | Uses a free **beta key that rotates ~monthly** (or a paid license). An **expired key silently breaks automated rips** — refresh it. |
| **HandBrake**                       | Optional x265 transcode to a smaller second version.                                 | **Strips Dolby Vision and HDR10+ down to HDR10.** Never let a HandBrake encode be the only copy of a DV title — keep the remux.     |
| **Automatic Ripping Machine (ARM)** | Hands-off automation: insert disc → detect → rip → eject.                            | Optional, layer it on once the manual path works end to end.                                                                        |

## Workflow

1. **Always make a lossless MKV remux master.** MakeMKV copies the disc's video/audio streams bit
   for bit into an MKV container. Expect **~40–90 GB per UHD film**. This is the reference copy and
   the only one guaranteed to preserve Dolby Vision, HDR10+, and lossless audio.
2. **Optionally transcode a second version** with HandBrake: **x265 10-bit, CRF ~20–22**, landing
   around **15–30 GB**. Add it to Jellyfin as an alternate version for bandwidth-constrained
   clients.
3. **Keep the remux for any Dolby Vision or reference title** — the transcode loses DV/HDR10+, so it
   is a convenience copy, never a replacement.

## Storage (TrueNAS)

Rough capacity math for planning the pool:

| Quantity         | Remux (master) | x265 transcode |
| ---------------- | -------------- | -------------- |
| Per UHD film     | ~40–90 GB      | ~15–30 GB      |
| Films per TB     | ~16–17 remuxes | —              |
| 100-film library | **~6 TB**      | **~2 TB**      |

Keep the **pool below 80%** full — ZFS write performance and fragmentation degrade past that.

**Dataset layout:**

- One **dataset per library** (e.g. `movies-uhd`, `movies-hd`).
- Put Jellyfin's **config/cache and the transcode scratch directory on an SSD** — never on the
  spinning media pool.
- Set **`recordsize=1M`** on media datasets. Large-file sequential media matches a 1 MiB record and
  cuts metadata overhead.

**Jellyfin naming** (get this exactly right or metadata matching and version-stacking break):

- One **folder per movie**.
- Every filename **starts with the exact folder name including the year**.
- Multiple versions of one movie via a **`- Label`** suffix (a hyphen-space label after the base
  name, as in the example below).

```text
Dune Part Two (2024)/
  Dune Part Two (2024) - [2160p Remux].mkv
  Dune Part Two (2024) - [1080p x265].mkv
```

## Playback (design for Direct Play)

The whole storage design is wasted if Jellyfin transcodes on playback. **Jellyfin cannot do HDR →
HDR** — if it transcodes an HDR title, you get **washed-out SDR** and **Atmos/TrueHD stripped**. So
the client must Direct Play.

- **Dolby Vision Profile 7** (the disc's DV format) will **not Direct Play on most clients**. Use a
  client that handles it: **Apple TV 4K + Infuse**, or an **NVIDIA Shield Pro**.
- Set the client's playback bitrate to **"Original"** so it never asks the server to downscale.
- **TrueHD / Atmos passthrough** requires Direct Play **and** a capable client + receiver — same
  requirement as the video.
- Keep an **Intel QuickSync / Arc iGPU** available on the Jellyfin host as a **transcode safety net
  only** (for the odd non-HDR client), not the primary path.

## Progress

- [x] Researched the drive / enclosure / software landscape
- [x] Purchased WH16NS40 + OWC Mercury Pro 5.25" enclosure (awaiting shipment)
- [ ] Flash WH16NS40 → WH16NS60 `1.02-MK` on a native SATA port; verify MakeMKV shows "LibreDrive:
      enabled"
- [ ] Assemble drive in the OWC enclosure; re-verify LibreDrive works through the USB bridge
- [ ] Install MakeMKV + current beta key; complete first lossless remux rip
- [ ] Lay out TrueNAS datasets (per-library, SSD scratch/config, `recordsize=1M`)
- [ ] Build the Jellyfin 4K library with correct naming; verify Direct Play with HDR intact
- [ ] Confirm the playback client + receiver chain with bitrate set to "Original"
- [ ] Optional: ARM automation and a HandBrake x265 transcode profile

## Exit Criteria

One owned UHD disc is ripped to a **lossless remux** on the NAS with **correct Jellyfin naming**,
and it **Direct Plays** on the target client with **HDR (Dolby Vision / HDR10+) and lossless audio
intact** — no server-side transcode, no SDR fallback, no stripped audio.

## Sources

- [MakeMKV LibreDrive flashing guide (forum)](https://forum.makemkv.com/forum/viewtopic.php?t=19634)
- [MakeMKV](https://www.makemkv.com/)
- [Automatic Ripping Machine (ARM)](https://github.com/automatic-ripping-machine/automatic-ripping-machine)
- [Jellyfin documentation](https://jellyfin.org/docs)
- [OWC (Other World Computing)](https://www.owc.com/)
