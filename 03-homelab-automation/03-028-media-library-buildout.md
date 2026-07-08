---
title: 'Household Media Library Build-Out (Jellyfin + Navidrome)'
number: '03-028'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'Media Curation, Blu-ray Ripping (MakeMKV), Jellyfin/Navidrome Library Management, Inventory
  Reconciliation & Deduplication'
status: 'In Progress'
---

# Household Media Library Build-Out (Jellyfin + Navidrome)

## Description

Build out the household media libraries — **Jellyfin** for video, **Navidrome** for music — from a
mix of **owned**, **library-borrowed**, and **archived** sources, deduplicated against what already
exists on the NAS so nothing is re-acquired. This is the curation-and-acquisition companion to the
ripping-pipeline project [03-026](03-026-rip-owned-4k-uhd-blurays-to-nas-jellyfin.md): 03-026 turns
a disc into a correctly-named file on the NAS; this project decides **which** discs are worth
acquiring, from **where**, and tracks per-title status against a reconciled inventory baseline.

Three efforts kept overlapping — a franchise wishlist, the disc-ripping pipeline (03-026), and an
archive-assimilation effort (tracked separately in a private repo). This ties them into one plan
with an inventory baseline, an acquisition strategy, and per-title status, so the actual build is
one clean batch instead of ad-hoc trips.

## Legal & sourcing note

Consistent with [03-026](03-026-rip-owned-4k-uhd-blurays-to-nas-jellyfin.md)'s legal note, this is
scoped to **personal use**: rip discs I own or legitimately borrow, keep the library at home, never
redistribute the files. Three acquisition sources feed the plan, all matter-of-fact:

- **Own** — discs already on hand; rip and shelve.
- **Library-borrow** — check a disc out from the San Francisco Public Library (SFPL), rip it while
  it's loaned, and return it. Standard-definition and 1080p Blu-ray only; SFPL stocks no 4K UHD (see
  appendix).
- **Buy** — purchase the disc where the library can't supply the format wanted (notably any 4K/HDR
  master).

The DMCA §1201 caveat from 03-026 applies to the 4K UHD path specifically (AACS 2.0); standard
Blu-ray ripping does not need the LibreDrive-flashed drive. Keep it personal, keep the discs, never
redistribute — same posture as 03-026.

## Golden rule: reconcile before acquiring

Never borrow, buy, or re-rip a title without first checking it against **hestia** (the Jellyfin
library + the assimilated archive) **and Mighty Joe** (the legacy movie drive). Mighty Joe (MJ) is
mid-recovery and currently unreadable — treat every "missing" below as "not on hestia," **not**
"confirmed absent." Re-run the reconciliation once MJ mounts cleanly before spending money or making
a library trip.

## Pipelines (the "how")

| Source                                | Pipeline                                                                        |
| ------------------------------------- | ------------------------------------------------------------------------------- |
| Owned / borrowed **4K UHD** disc      | 03-026 — LibreDrive-flashed LG drive → MakeMKV remux → Jellyfin                 |
| Owned / borrowed **standard Blu-ray** | any Blu-ray drive → MakeMKV (no UHD flash needed) → Jellyfin                    |
| **Archive media** (already digital)   | archive-assimilation effort → `family/media/{video,music}` → Jellyfin/Navidrome |
| **CDs**                               | already ripped → Navidrome (complete)                                           |

Standard Blu-ray is the _easy_ path — only 4K UHD needs the flashed drive and AACS 2.0 handling. TV
box sets and every SFPL disc are standard Blu-ray.

## Inventory baseline (reconciled 2026-07-08 vs hestia + MJ)

**On hand: 12 / 104 franchise films** (all on hestia). The archive held only home videos. The
`tv-shows` dataset is empty. **Mighty Joe (~60% recovered) is unreadable — contents UNKNOWN**, so
the 92-film gap below is an upper bound, not a shopping list.

## Track 1 — Movies (6 franchises, 104 films)

| Franchise         | Own (hestia)    | SFPL Blu-ray       | To acquire (pending MJ)                          |
| ----------------- | --------------- | ------------------ | ------------------------------------------------ |
| Star Wars         | **6/6**         | 6/6                | —                                                |
| Indiana Jones     | **5/5**         | 5/5                | —                                                |
| Lord of the Rings | 0/6             | 6/6 (Extended Eds) | 6                                                |
| James Bond        | 0/25            | 24/25              | 25 (24 SFPL + _From Russia with Love_ via LINK+) |
| Pixar             | 0/28            | 27/28              | 28 (27 SFPL + _Luca_ via LINK+)                  |
| Marvel (MCU)      | 1/34 (Iron Man) | 33/34 +1 likely    | 33                                               |
| **Total**         | **12/104**      | **101/104**        | **92 films**                                     |

**Key facts:**

- **SFPL has 101/104 on Blu-ray but ZERO 4K UHD.** 1080p Blu-ray is the ceiling there (still
  lossless audio + high bitrate; LOTR/Hobbit circulate as Extended Editions). For a 4K/HDR master
  you must **buy** the disc — the library can't help.
- 3 to double-check via LINK+ (SFPL regional resource-sharing): _From Russia with Love_, _Luca_,
  _The Marvels_.
- Batch holds for the popular "all copies in use" titles (Toy Story 2/3, Octopussy, Casino Royale,
  Iron Man 3, Civil War, Incredible Hulk).
- **Full per-film availability table** is in the
  [appendix](#appendix--sfpl-blu-ray-availability-104-films) below.

## Track 2 — TV

| Show                | Own?              | Best available       | Acquire via          | Status       |
| ------------------- | ----------------- | -------------------- | -------------------- | ------------ |
| Sex and the City    | **Own (Blu-ray)** | 1080p BR             | —                    | ready to rip |
| Gilmore Girls       | **Own (Blu-ray)** | 1080p BR             | —                    | ready to rip |
| Seinfeld            | no                | DVD (no BR)          | SFPL / buy           | to acquire   |
| Friends             | no                | Blu-ray remaster     | SFPL / buy           | to acquire   |
| The Wire            | no                | Blu-ray HD remaster  | SFPL / buy           | to acquire   |
| Planet Earth (I/II) | no                | **4K UHD reference** | **buy** (SFPL no 4K) | to acquire   |
| Derry Girls         | no                | DVD / UK import      | SFPL / buy           | to acquire   |
| Luther              | no                | Blu-ray              | SFPL / buy           | to acquire   |
| Sherlock            | no                | Blu-ray              | SFPL / buy           | to acquire   |

The two owned box sets rip **now**, independent of MJ. Planet Earth II in 4K is the reference demo
disc — worth buying the UHD for the tuned home-theater setup.

## Track 3 — Music

- **CDs:** all owned CDs are already ripped and in **Navidrome** — done.
- **Archive:** the assimilation dedup found **920 unique tracks / 36 artists** (Sublime, Jack
  Johnson, State Radio…) routing to `family/media/music/`. Task: **fold these into Navidrome,
  deduped against the existing library** — handled by the archive-assimilation effort, not a
  separate ripping run.

### Optional sub-track — music films

SFPL confirmed these concert/music docs on Blu-ray (curation batch): _Stop Making Sense_, _The Last
Waltz_, _Gimme Shelter_, _Buena Vista Social Club_, _Jazz on a Summer's Day_, _Long Strange Trip_.
Fold in if wanted.

## Next actions

**All ripping is gated on the UHD ripper** (03-026: LG WH16NS40 + OWC enclosure, **inbound**) being
flashed to LibreDrive. Once flashed, it's the single drive for everything — standard Blu-ray (TV +
SFPL discs) _and_ 4K UHD (bought reference titles). Timing converges nicely: **ripper-ready ≈ MJ
recovery done**, so kick off one clean batch then.

1. **Flash the ripper** when it lands (03-026: NS40 → NS60 `1.02-MK` on a native SATA port; verify
   `LibreDrive: enabled`) — the gate for all ripping.
2. **Rip the owned TV Blu-rays** (Sex and the City, Gilmore Girls) first — validates the
   standard-Blu-ray path end to end before the bigger runs.
3. **Wait for MJ recovery → re-reconcile** → finalize the movie to-borrow list (MJ likely covers a
   chunk of the 92 "missing").
4. **Batch SFPL holds** for the confirmed gaps: place holds on the in-use titles, grab the available
   ones in one AV Center run, rip, return.
5. **Buy 4K** only for the few reference titles where HDR matters (Planet Earth II).
6. **Fold the archive's 920 tracks into Navidrome** (archive-assimilation effort).

## Exit Criteria

The household libraries are built out against a reconciled baseline: the two owned TV box sets and
every confirmed-owned franchise film are ripped and correctly named in Jellyfin; the movie gap has
been re-reconciled against a recovered Mighty Joe and closed via a single batched SFPL-borrow run
(plus the handful of buy-only reference 4K titles); the archive's 920 music tracks are deduped into
Navidrome. No title is acquired twice, and per-title status in this doc reflects what is actually on
hestia.

## Related

- Rip pipeline:
  [03-026 — Rip Owned 4K UHD Blu-rays to the NAS](03-026-rip-owned-4k-uhd-blurays-to-nas-jellyfin.md)
- Franchise wishlist + acquisition fallbacks: tracked privately in the homelab repo.
- Media routing / archive assimilation: tracked privately (life repo).

---

## Appendix — SFPL Blu-ray availability (104 films)

_Availability snapshot checked 2026-07-08 against the public SFPL catalog
(`sfpl.bibliocommons.com`). This appendix is **results/data only** — the per-film format and
availability the catalog showed on that date._

### How to read the status column

- **SFPL stocks NO 4K UHD Blu-ray.** Their physical video is DVD + Blu-ray only, so the best disc
  checkoutable for any of these is a **1080p Blu-ray** (still lossless-audio, high-bitrate — well
  worth ripping over a stream). Every "format" cell below is Blu-ray-or-lower by definition.
- **Result: 101 of 104 confirmed on Blu-ray**, 2 are **DVD-only** (no Blu-ray edition surfaced), and
  1 is **Blu-ray-likely** (Blu-ray discs present in the aggregate result but the film's own record
  couldn't be isolated). Zero films were entirely absent.
- **Availability floats.** The "Available" / "All copies in use" column is a point-in-time snapshot
  from that date and changes constantly — treat it as indicative, not a reservation.
- **DVD-only** means no Blu-ray surfaced for that film — a Blu-ray could exist under an odd edition
  record, unconfirmed. Search each title by name in the public SFPL catalog to land on its record.

Format legend: **BR** = Blu-ray confirmed · **DVD-only** = only a DVD record found · **BR?** =
Blu-ray likely but not isolated. No 4K UHD exists at SFPL.

### Summary by franchise

| Franchise         | On Blu-ray at SFPL           | Notes                                        |
| ----------------- | ---------------------------- | -------------------------------------------- |
| Star Wars         | 6 / 6                        | all confirmed                                |
| Indiana Jones     | 5 / 5                        | all confirmed                                |
| Lord of the Rings | 6 / 6                        | all confirmed (several Extended Edition BRs) |
| James Bond        | 24 / 25                      | _From Russia with Love_ DVD-only             |
| Pixar             | 27 / 28                      | _Luca_ DVD-only                              |
| Marvel (MCU)      | 33 / 34 confirmed + 1 likely | _The Marvels_ Blu-ray-likely                 |
| **Total**         | **101 / 104 confirmed BR**   | +1 likely, 2 DVD-only, 0 not-found, 0 in 4K  |

### Star Wars — 6/6 on Blu-ray

| Film                               | Year | Format | Availability (2026-07-08) |
| ---------------------------------- | ---- | ------ | ------------------------- |
| Episode I: The Phantom Menace      | 1999 | BR     | in collection             |
| Episode II: Attack of the Clones   | 2002 | BR     | in collection             |
| Episode III: Revenge of the Sith   | 2005 | BR     | in collection             |
| Episode IV: A New Hope             | 1977 | BR     | in collection             |
| Episode V: The Empire Strikes Back | 1980 | BR     | in collection             |
| Episode VI: Return of the Jedi     | 1983 | BR     | in collection             |

### Indiana Jones — 5/5 on Blu-ray

| Film                         | Year | Format | Availability               |
| ---------------------------- | ---- | ------ | -------------------------- |
| Raiders of the Lost Ark      | 1981 | BR     | 2 BR copies                |
| Temple of Doom               | 1984 | BR     | Available                  |
| The Last Crusade             | 1989 | BR     | Available                  |
| Kingdom of the Crystal Skull | 2008 | BR     | Available (special ed. HD) |
| Dial of Destiny              | 2023 | BR     | Available                  |

### Lord of the Rings — 6/6 on Blu-ray

| Film                                      | Year | Format | Availability                 |
| ----------------------------------------- | ---- | ------ | ---------------------------- |
| The Fellowship of the Ring                | 2001 | BR     | 3 BR copies                  |
| The Two Towers                            | 2002 | BR     | Extended Ed. + HD, Available |
| The Return of the King                    | 2003 | BR     | 2 BR copies                  |
| The Hobbit: An Unexpected Journey         | 2012 | BR     | Extended Ed., Available      |
| The Hobbit: The Desolation of Smaug       | 2013 | BR     | Extended Ed., Available      |
| The Hobbit: The Battle of the Five Armies | 2014 | BR     | Available                    |

### James Bond — 24/25 on Blu-ray (1 DVD-only)

| Film                            | Year | Format       | Availability               |
| ------------------------------- | ---- | ------------ | -------------------------- |
| Dr. No                          | 1962 | BR           | Available                  |
| From Russia with Love           | 1963 | **DVD-only** | DVD Available; no BR found |
| Goldfinger                      | 1964 | BR           | in collection              |
| Thunderball                     | 1965 | BR           | in collection              |
| You Only Live Twice             | 1967 | BR           | in collection              |
| On Her Majesty's Secret Service | 1969 | BR           | in collection              |
| Diamonds Are Forever            | 1971 | BR           | in collection              |
| Live and Let Die                | 1973 | BR           | in collection              |
| The Man with the Golden Gun     | 1974 | BR           | in collection              |
| The Spy Who Loved Me            | 1977 | BR           | Available                  |
| Moonraker                       | 1979 | BR           | Available                  |
| For Your Eyes Only              | 1981 | BR           | in collection              |
| Octopussy                       | 1983 | BR           | All copies in use (3)      |
| A View to a Kill                | 1985 | BR           | Available                  |
| The Living Daylights            | 1987 | BR           | Available                  |
| Licence to Kill                 | 1989 | BR           | Available                  |
| GoldenEye                       | 1995 | BR           | in collection              |
| Tomorrow Never Dies             | 1997 | BR           | Available                  |
| The World Is Not Enough         | 1999 | BR           | Available                  |
| Die Another Day                 | 2002 | BR           | in collection              |
| Casino Royale                   | 2006 | BR           | 3 BR copies, all in use    |
| Quantum of Solace               | 2008 | BR           | Available                  |
| Skyfall                         | 2012 | BR           | Available                  |
| Spectre                         | 2015 | BR           | 2 BR copies                |
| No Time to Die                  | 2021 | BR           | Available                  |

### Pixar — 27/28 on Blu-ray (1 DVD-only)

| Film                | Year | Format       | Availability                  |
| ------------------- | ---- | ------------ | ----------------------------- |
| Toy Story           | 1995 | BR           | Available                     |
| A Bug's Life        | 1998 | BR           | Available                     |
| Toy Story 2         | 1999 | BR           | All copies in use (holds)     |
| Monsters, Inc.      | 2001 | BR           | 3 BR copies                   |
| Finding Nemo        | 2003 | BR           | Available                     |
| The Incredibles     | 2004 | BR           | Available                     |
| Cars                | 2006 | BR           | Available                     |
| Ratatouille         | 2007 | BR           | 2 BR copies                   |
| WALL-E              | 2008 | BR           | 2 BR copies (no DVD)          |
| Up                  | 2009 | BR           | Available (Eng + Spanish BR)  |
| Toy Story 3         | 2010 | BR           | All copies in use (holds)     |
| Cars 2              | 2011 | BR           | Available                     |
| Brave               | 2012 | BR           | Available                     |
| Monsters University | 2013 | BR           | 2 BR copies, Available        |
| Inside Out          | 2015 | BR           | 2 BR copies                   |
| The Good Dinosaur   | 2015 | BR           | Available                     |
| Finding Dory        | 2016 | BR           | Available                     |
| Cars 3              | 2017 | BR           | Available                     |
| Coco                | 2017 | BR           | in collection (DVD Available) |
| Incredibles 2       | 2018 | BR           | Available                     |
| Toy Story 4         | 2019 | BR           | Available                     |
| Onward              | 2020 | BR           | Available                     |
| Soul                | 2020 | BR           | Available                     |
| Luca                | 2021 | **DVD-only** | DVD Available; no BR found    |
| Turning Red         | 2022 | BR           | Available                     |
| Lightyear           | 2022 | BR           | Available                     |
| Elemental           | 2023 | BR           | in collection                 |
| Inside Out 2        | 2024 | BR           | Available                     |

### Marvel Cinematic Universe — 33/34 confirmed + 1 likely

| Film                                        | Year | Format  | Availability                   |
| ------------------------------------------- | ---- | ------- | ------------------------------ |
| Iron Man                                    | 2008 | BR      | Available                      |
| The Incredible Hulk                         | 2008 | BR      | All copies in use              |
| Iron Man 2                                  | 2010 | BR      | Available                      |
| Thor                                        | 2011 | BR      | Available                      |
| Captain America: The First Avenger          | 2011 | BR      | Available                      |
| The Avengers                                | 2012 | BR      | Available                      |
| Iron Man 3                                  | 2013 | BR      | All copies in use              |
| Thor: The Dark World                        | 2013 | BR      | Available                      |
| Captain America: The Winter Soldier         | 2014 | BR      | Available                      |
| Guardians of the Galaxy                     | 2014 | BR      | Available                      |
| Avengers: Age of Ultron                     | 2015 | BR      | Available                      |
| Ant-Man                                     | 2015 | BR      | Available                      |
| Captain America: Civil War                  | 2016 | BR      | All copies in use (5)          |
| Doctor Strange                              | 2016 | BR      | Available                      |
| Guardians of the Galaxy Vol. 2              | 2017 | BR      | Available                      |
| Spider-Man: Homecoming                      | 2017 | BR      | Available                      |
| Thor: Ragnarok                              | 2017 | BR      | Available                      |
| Black Panther                               | 2018 | BR      | in collection                  |
| Avengers: Infinity War                      | 2018 | BR      | Available                      |
| Ant-Man and the Wasp                        | 2018 | BR      | Available                      |
| Captain Marvel                              | 2019 | BR      | Available                      |
| Avengers: Endgame                           | 2019 | BR      | Available                      |
| Spider-Man: Far From Home                   | 2019 | BR      | Available                      |
| Black Widow                                 | 2021 | BR      | in collection                  |
| Shang-Chi                                   | 2021 | BR      | in collection                  |
| Eternals                                    | 2021 | BR      | in collection                  |
| Spider-Man: No Way Home                     | 2021 | BR      | Available                      |
| Doctor Strange in the Multiverse of Madness | 2022 | BR      | Available                      |
| Thor: Love and Thunder                      | 2022 | BR      | Available                      |
| Black Panther: Wakanda Forever              | 2022 | BR      | Available                      |
| Ant-Man and the Wasp: Quantumania           | 2023 | BR      | Available                      |
| Guardians of the Galaxy Vol. 3              | 2023 | BR      | in collection                  |
| The Marvels                                 | 2023 | **BR?** | BR likely; record not isolated |
| Deadpool & Wolverine                        | 2024 | BR      | Available                      |

### The 3 to double-check in person / via LINK+

1. **From Russia with Love (1963)** — only a DVD record surfaced. For Blu-ray, request via LINK+
   (SFPL's regional resource-sharing network) or check the physical AV Center shelf.
2. **Luca (2021)** — DVD-only in the catalog. Disney's own Luca Blu-ray exists retail; SFPL just may
   not stock it. LINK+ is the fallback.
3. **The Marvels (2023)** — the aggregate result showed Blu-ray discs present but the film's own
   record wasn't isolated; very likely stocked given the rest of the MCU is.

### Practical notes for ripping

- Everything here tops out at **1080p Blu-ray** — there is no 4K UHD at SFPL. For a title where the
  4K/HDR master matters (demo discs, Bond 4K restorations), buy/borrow the UHD elsewhere.
- Many franchise Blu-rays circulate as **Extended Editions** (notably all six LOTR/Hobbit) — a bonus
  for ripping the longer cuts.
- Availability floats hourly. Batch the holds: place holds on the "all copies in use" ones (Toy
  Story 2/3, Octopussy, Casino Royale, Iron Man 3, Civil War, Incredible Hulk) and grab the
  "Available" ones on a single AV Center run.
