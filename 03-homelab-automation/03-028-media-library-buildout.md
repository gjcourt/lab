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

## Augmented picks — highly-rated films at SFPL (ranked)

The 6-franchise wishlist is a personal target list, not "the best of what SFPL stocks." This is the
**"already at the AV Center, grab these too"** list: 50 highly-rated, rip-worthy films **outside**
the six franchises, all confirmed on **standard Blu-ray** at SFPL (2026-07-08). It folds in the 14
already-confirmed music/art-house discs above and adds acclaimed classics, crowd-pleasers (like _The
Blues Brothers_), reference-quality discs, and modern acclaimed titles.

**Ranking method — multi-signal, highest-first.** Primary key = **Rotten Tomatoes critics %**;
tiebreak = **RT audience %**. AFI Top 100 / Criterion / IMDb Top 250 status is noted in the "why"
column where it adds signal. RT figures are point-in-time public scores (as of 2026-07) and drift a
point or two over time. Every title is **Blu-ray at SFPL — no 4K UHD exists there** (buy the disc if
an HDR master matters).

| #   | Film                              | Year | Director             | RT crit% (aud%) | Why it's rip-worthy                            | SFPL |
| --- | --------------------------------- | ---- | -------------------- | --------------- | ---------------------------------------------- | ---- |
| 1   | Seven Samurai                     | 1954 | Kurosawa             | 100% (97%)      | Criterion; the ur-text of the ensemble epic    | BR   |
| 2   | Stop Making Sense                 | 1984 | Demme                | 100% (97%)      | Greatest concert film ever shot                | BR   |
| 3   | Singin' in the Rain               | 1952 | Kelly / Donen        | 100% (95%)      | AFI-top musical; reference Technicolor         | BR   |
| 4   | Tokyo Story                       | 1953 | Ozu                  | 100% (94%)      | Criterion; perennial "greatest films" pick     | BR   |
| 5   | The Red Shoes                     | 1948 | Powell / Pressburger | 100% (93%)      | Criterion; a Technicolor restoration showpiece | BR   |
| 6   | Long Strange Trip                 | 2017 | Bar-Lev              | 100% (91%)      | Definitive Grateful Dead doc                   | BR   |
| 7   | Casablanca                        | 1942 | Curtiz               | 99% (95%)       | AFI Top 5; the canonical Hollywood romance     | BR   |
| 8   | Chinatown                         | 1974 | Polanski             | 99% (93%)       | AFI Top 100; the perfect screenplay            | BR   |
| 9   | Citizen Kane                      | 1941 | Welles               | 99% (90%)       | Perennial "greatest film"; deep-focus landmark | BR   |
| 10  | Parasite                          | 2019 | Bong Joon-ho         | 99% (90%)       | Best Picture; Criterion                        | BR   |
| 11  | Schindler's List                  | 1993 | Spielberg            | 98% (97%)       | Best Picture; B&W reference transfer           | BR   |
| 12  | Lawrence of Arabia                | 1962 | Lean                 | 98% (94%)       | 70mm epic; a demo disc for scale               | BR   |
| 13  | Apocalypse Now                    | 1979 | Coppola              | 98% (94%)       | Reference 5.1 sound design                     | BR   |
| 14  | Dr. Strangelove                   | 1964 | Kubrick              | 98% (94%)       | Criterion; the definitive satire               | BR   |
| 15  | The Last Waltz                    | 1978 | Scorsese             | 98% (93%)       | The Band's farewell; landmark concert film     | BR   |
| 16  | Get Out                           | 2017 | Peele                | 98% (86%)       | Best Original Screenplay; modern horror pivot  | BR   |
| 17  | Moonlight                         | 2016 | Jenkins              | 98% (79%)       | Best Picture; A24 flagship                     | BR   |
| 18  | The Godfather                     | 1972 | Coppola              | 97% (98%)       | AFI Top 3; restored transfer                   | BR   |
| 19  | Spirited Away                     | 2001 | Miyazaki             | 97% (96%)       | Ghibli's Oscar winner; animation reference     | BR   |
| 20  | Psycho                            | 1960 | Hitchcock            | 97% (95%)       | AFI Top 100; the shower-scene urtext           | BR   |
| 21  | Spider-Man: Into the Spider-Verse | 2018 | Persichetti et al.   | 97% (93%)       | Animation showcase; reference color            | BR   |
| 22  | Jaws                              | 1975 | Spielberg            | 97% (90%)       | The first blockbuster; demo-worthy audio       | BR   |
| 23  | Mad Max: Fury Road                | 2015 | Miller               | 97% (86%)       | Reference action disc; saturated color         | BR   |
| 24  | Jazz on a Summer's Day            | 1959 | Stern                | 97% (82%)       | 1958 Newport Jazz Fest; gorgeous restoration   | BR   |
| 25  | The Godfather Part II             | 1974 | Coppola              | 96% (97%)       | AFI Top 100; the rare superior sequel          | BR   |
| 26  | Goodfellas                        | 1990 | Scorsese             | 96% (97%)       | AFI Top 100; propulsive craft                  | BR   |
| 27  | Ran                               | 1985 | Kurosawa             | 96% (93%)       | Criterion; Kurosawa's color Lear               | BR   |
| 28  | The Silence of the Lambs          | 1991 | Demme                | 95% (95%)       | Best Picture; Criterion                        | BR   |
| 29  | Pan's Labyrinth                   | 2006 | del Toro             | 95% (91%)       | Criterion; a dark-fantasy showcase             | BR   |
| 30  | Die Hard                          | 1988 | McTiernan            | 94% (94%)       | The template action thriller                   | BR   |
| 31  | Whiplash                          | 2014 | Chazelle             | 94% (94%)       | Editing/sound tour de force                    | BR   |
| 32  | Vertigo                           | 1958 | Hitchcock            | 94% (93%)       | Perennial "greatest film"; restored color      | BR   |
| 33  | Alien                             | 1979 | Scott                | 93% (94%)       | Reference production design + sound            | BR   |
| 34  | Back to the Future                | 1985 | Zemeckis             | 93% (94%)       | The crowd-pleaser benchmark                    | BR   |
| 35  | Gimme Shelter                     | 1970 | Maysles / Zwerin     | 93% (91%)       | Altamont; landmark rockumentary                | BR   |
| 36  | Oppenheimer                       | 2023 | Nolan                | 93% (91%)       | Best Picture; large-format photography         | BR   |
| 37  | Everything Everywhere All at Once | 2022 | Daniels              | 93% (88%)       | Best Picture; maximalist editing               | BR   |
| 38  | No Country for Old Men            | 2007 | Coen Bros.           | 93% (86%)       | Best Picture; masterclass in tension           | BR   |
| 39  | Pulp Fiction                      | 1994 | Tarantino            | 92% (96%)       | AFI Top 100; era-defining                      | BR   |
| 40  | Dune: Part Two                    | 2024 | Villeneuve           | 92% (95%)       | Reference-grade image + sound                  | BR   |
| 41  | Jurassic Park                     | 1993 | Spielberg            | 92% (91%)       | VFX landmark; demo audio                       | BR   |
| 42  | Buena Vista Social Club           | 1999 | Wenders              | 92% (90%)       | Cuban-music doc; irresistible soundtrack       | BR   |
| 43  | 2001: A Space Odyssey             | 1968 | Kubrick              | 92% (90%)       | AFI Top 100; the reference restoration         | BR   |
| 44  | In the Mood for Love              | 2000 | Wong Kar-wai         | 92% (89%)       | Criterion; a color-and-mood showpiece          | BR   |
| 45  | Taxi Driver                       | 1976 | Scorsese             | 89% (93%)       | AFI Top 100; restored transfer                 | BR   |
| 46  | The Matrix                        | 1999 | The Wachowskis       | 88% (85%)       | Genre-defining; demo action + sound            | BR   |
| 47  | Blade Runner 2049                 | 2017 | Villeneuve           | 88% (81%)       | Reference cinematography (Deakins)             | BR   |
| 48  | Baraka                            | 1992 | Fricke               | 85% (96%)       | 70mm non-narrative; ultimate demo disc         | BR   |
| 49  | Samsara                           | 2011 | Fricke               | 75% (87%)       | 70mm follow-up to _Baraka_; demo-grade image   | BR   |
| 50  | The Blues Brothers                | 1980 | Landis               | 71% (86%)       | Cult crowd-pleaser; soul/R&B set pieces        | BR   |

**Notes.** All 50 verified against the public SFPL catalog on 2026-07-08 — Blu-ray records surfaced
for every title (SFPL stocks no 4K UHD). "Copies in use" is common on the popular titles (batch
holds as with the franchises). The 14 music/art-house discs from the curation batch above (_Baraka_,
_Samsara_, _Seven Samurai_, _Tokyo Story_, _In the Mood for Love_, _Ran_, _Parasite_, _The Red
Shoes_, and the six concert docs) are folded into the ranking rather than listed twice.

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

**The other Star Wars films (outside the 6-film saga wishlist)** — checked 2026-07-08 for
completeness. Five of six are on Blu-ray at SFPL; only the 2008 animated theatrical film isn't on
disc there.

| Film                                 | Year | Format   | Note                                             |
| ------------------------------------ | ---- | -------- | ------------------------------------------------ |
| The Force Awakens (Ep. VII)          | 2015 | BR       | Blu-ray + DVD                                    |
| The Last Jedi (Ep. VIII)             | 2017 | BR       | Blu-ray + DVD                                    |
| The Rise of Skywalker (Ep. IX)       | 2019 | BR       | Blu-ray + DVD                                    |
| Rogue One: A Star Wars Story         | 2016 | BR       | Blu-ray + DVD                                    |
| Solo: A Star Wars Story              | 2018 | BR       | Blu-ray (copies in use) + DVD                    |
| Star Wars: The Clone Wars (animated) | 2008 | **none** | Not on disc at SFPL; only the TV series is on BR |

So the full live-action saga (Ep. I–IX) plus both anthology films (_Rogue One_, _Solo_) are all
Blu-ray-borrowable at SFPL — the lone gap is the 2008 animated theatrical film, which SFPL never
stocked on disc.

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
