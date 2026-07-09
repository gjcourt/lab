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

## Track 3b — Music acquisition (SFPL borrow-and-rip)

**217 albums across a cross-genre Top-50 spine + six genre buckets**, deduped so nothing is listed
twice. **127 are held at SFPL on CD** (the borrowable set — check out, rip losslessly, return) and
**90 must be acquired elsewhere** (LINK+, purchase, or lossless digital). This is the music analogue
of the movie **Augmented picks + genre buckets**: the **Top-50** is the cross-genre elite spine (the
headline), and each genre bucket is **deduped against it** so the Top-50's own entries are never
repeated below. Where an album fit two genres it is listed **once**, in its best-fit bucket (e.g.
LCD Soundsystem's _Sound of Silver_ → Alternative & Indie, not Electronic; the soul records →
Hip-Hop / R&B / Soul, not Rock). Ranked within each list by **album critical acclaim** — spine =
[Acclaimed Music](https://www.acclaimedmusic.net) all-time aggregate; genre buckets blend Acclaimed
Music / Rolling Stone 500 / Pitchfork / RYM / AllMusic; classical by Gramophone Hall of Fame /
Penguin / benchmark-recording consensus (not pop charts). **SFPL CD** = a physical Music-CD holding
verified via BiblioCommons (call number shown where the catalog printed one); `not held` = source
elsewhere. Unlike the movie tracks (SFPL Blu-ray, capped at 1080p), music borrows from SFPL's **CD**
collection — no format ceiling, just rip the disc to FLAC.

> **The SFPL-held subset (127 albums) is the input to a future borrow-and-rip reservation pipeline**
> — batch holds on BiblioCommons, grab them on one AV-Center run, rip into Navidrome, return. The 90
> not-held titles route to LINK+ / purchase / lossless-digital instead. This is the music companion
> to the movie "batch SFPL holds" action.

### Top-50 (all-time, cross-genre) — the headline

_34 held at SFPL / 50 total. Ranked by aggregate all-time critical acclaim (Acclaimed Music all-time
album rank, shown as **AM #**). SFPL = CD holding for borrow-and-rip. This is the elite spine; the
six genre buckets below dedup against it._

| #   | Album                                         | Artist                      | Year | Acclaim                        | SFPL CD                 | Why                                                              |
| --- | --------------------------------------------- | --------------------------- | ---- | ------------------------------ | ----------------------- | ---------------------------------------------------------------- |
| 1   | Pet Sounds                                    | The Beach Boys              | 1966 | AM #1 — #1 all-time            | CD `CD ROCK BEAC`       | Most-acclaimed album ever measured; studio-as-instrument pop.    |
| 2   | Nevermind                                     | Nirvana                     | 1991 | AM #2                          | CD `CD ROCK NIRV`       | Flipped the mainstream to alt-rock overnight; grunge's text.     |
| 3   | Revolver                                      | The Beatles                 | 1966 | AM #3                          | CD `CD ROCK BEAT`       | The Beatles' most top-ranked LP; pop's leap into avant-garde.    |
| 4   | The Velvet Underground & Nico                 | The Velvet Underground      | 1967 | AM #4                          | CD `CD ROCK VELV`       | Foundational art/proto-punk; the ur-text for indie.              |
| 5   | What's Going On                               | Marvin Gaye                 | 1971 | AM #5 — #1 soul all-time       | CD `CD jSONGS GAYE`     | The soul canon's summit; social-conscience song-suite.           |
| 6   | Sgt. Pepper's Lonely Hearts Club Band         | The Beatles                 | 1967 | AM #6                          | CD `CD ROCK BEAT`       | The album-as-statement landmark; psychedelic-pop artifact.       |
| 7   | London Calling                                | The Clash                   | 1979 | AM #7                          | CD `CD ROCK CLAS`       | Punk's genre-devouring double album.                             |
| 8   | OK Computer                                   | Radiohead                   | 1997 | AM #8                          | CD `CD ROCK RADI`       | Defining art-rock album of the '90s; modern acclaim benchmark.   |
| 9   | Blonde on Blonde                              | Bob Dylan                   | 1966 | AM #9                          | CD `CD ROCK DYLA`       | Rock's first great double LP; Dylan's "thin wild mercury" peak.  |
| 10  | Exile on Main St.                             | The Rolling Stones          | 1972 | AM #10                         | not held                | The Stones' ragged double-album masterpiece.                     |
| 11  | Highway 61 Revisited                          | Bob Dylan                   | 1965 | AM #11                         | not held                | The electric-Dylan watershed; the folk-rock big bang.            |
| 12  | Never Mind the Bollocks                       | Sex Pistols                 | 1977 | AM #12                         | not held                | Punk's year-zero manifesto.                                      |
| 13  | The Beatles ("White Album")                   | The Beatles                 | 1968 | AM #13                         | CD `CD ROCK BEAT`       | The sprawling everything-at-once double.                         |
| 14  | Are You Experienced                           | The Jimi Hendrix Experience | 1967 | AM #14                         | CD `CD ROCK HEND`       | The debut that rewrote the electric guitar's vocabulary.         |
| 15  | Astral Weeks                                  | Van Morrison                | 1968 | AM #15                         | not held                | Impressionist chamber-folk touchstone.                           |
| 16  | Born to Run                                   | Bruce Springsteen           | 1975 | AM #16                         | not held                | Heartland rock's grand statement; Spector-scale romanticism.     |
| 17  | To Pimp a Butterfly                           | Kendrick Lamar              | 2015 | AM #17 — top hip-hop all-time  | CD `CD RAP LAMA`        | The modern hip-hop/jazz-rap landmark; top 21st-c. album.         |
| 18  | It Takes a Nation of Millions to Hold Us Back | Public Enemy                | 1988 | AM #18                         | not held                | Hip-hop's dense, incendiary production peak.                     |
| 19  | The Rise and Fall of Ziggy Stardust           | David Bowie                 | 1972 | AM #19                         | CD `CD ROCK BOWI`       | Glam's defining concept album; Bowie's persona-art breakthrough. |
| 20  | Abbey Road                                    | The Beatles                 | 1969 | AM #20                         | CD `CD ROCK BEAT`       | The polished farewell; the side-two medley as a form.            |
| 21  | The Dark Side of the Moon                     | Pink Floyd                  | 1973 | AM #21                         | CD `CD ROCK PINK`       | Prog's crossover colossus; a studio-craft benchmark.             |
| 22  | Blood on the Tracks                           | Bob Dylan                   | 1975 | AM #22                         | CD `CD ROCK DYLA`       | The gold standard of the confessional break-up album.            |
| 23  | Thriller                                      | Michael Jackson             | 1982 | AM #23                         | CD `CD ROCK JACK`       | Best-selling album ever; a pop/R&B production high-water mark.   |
| 24  | Funeral                                       | Arcade Fire                 | 2004 | AM #24                         | not held                | The indie-rock canon's defining 2000s debut.                     |
| 25  | Horses                                        | Patti Smith                 | 1975 | AM #25                         | CD `CD ROCK SMIT`       | Punk-poetry's founding document; where rock met the Beats.       |
| 26  | My Beautiful Dark Twisted Fantasy             | Kanye West                  | 2010 | AM #26                         | not held                | The maximalist hip-hop opus topping decade lists.                |
| 27  | The Queen Is Dead                             | The Smiths                  | 1986 | AM #27                         | CD `CD ROCK SMIT`       | Jangle-pop's crown jewel; the canonical Smiths album.            |
| 28  | Marquee Moon                                  | Television                  | 1977 | AM #28                         | CD `CD ROCK TELE`       | Art-punk's guitar-interplay masterpiece.                         |
| 29  | Kind of Blue                                  | Miles Davis                 | 1959 | AM #29 — best-selling jazz LP  | CD `CD JAZZ DAVI`       | The most famous jazz album ever; modal jazz's statement.         |
| 30  | Sign 'O' the Times                            | Prince                      | 1987 | AM #30                         | not held                | Prince's sprawling double-album peak.                            |
| 31  | Electric Ladyland                             | The Jimi Hendrix Experience | 1968 | AM #31                         | CD `CD ROCK HEND`       | Hendrix's studio-expansive double; psychedelic guitar.           |
| 32  | Rubber Soul                                   | The Beatles                 | 1965 | AM #32                         | CD `CD ROCK BEAT`       | The pivot from pop group to studio artists; folk-rock maturity.  |
| 33  | Led Zeppelin IV                               | Led Zeppelin                | 1971 | AM #33                         | CD `CD ROCK LED`        | Hard rock's most enduring album; "Stairway" and the blueprint.   |
| 34  | Is This It                                    | The Strokes                 | 2001 | AM #34                         | not held                | The garage-rock-revival spark of the 2000s.                      |
| 35  | Kid A                                         | Radiohead                   | 2000 | AM #35                         | CD `CD ROCK RADI`       | Rock's electronic/experimental left turn.                        |
| 36  | The Doors                                     | The Doors                   | 1967 | AM #36                         | CD `CD ROCK DOOR`       | The psychedelic-rock debut fusing blues, theater, menace.        |
| 37  | Remain in Light                               | Talking Heads               | 1980 | AM #37                         | CD `CD ROCK TALK`       | Afrobeat-driven post-punk landmark; Eno-era art-funk peak.       |
| 38  | Who's Next                                    | The Who                     | 1971 | AM #38                         | CD `CD ROCK WHO`        | Synth-and-power-chord hard rock at its most anthemic.            |
| 39  | Beggars Banquet                               | The Rolling Stones          | 1968 | AM #39                         | CD `CD ROCK ROLL`       | The Stones' return-to-roots blues-rock rebirth.                  |
| 40  | The Joshua Tree                               | U2                          | 1987 | AM #40                         | CD `CD ROCK UTWO`       | Stadium rock's most acclaimed album; Americana-tinged and vast.  |
| 41  | Ramones                                       | Ramones                     | 1976 | AM #41                         | not held                | Punk's minimalist blueprint (SFPL holds later LPs, not debut).   |
| 42  | Let It Bleed                                  | The Rolling Stones          | 1969 | AM #42                         | CD `CD ROCK ROLL`       | Dark, apocalyptic blues-rock; "Gimme Shelter" bookends.          |
| 43  | Blue Lines                                    | Massive Attack              | 1991 | AM #43 — trip-hop origin       | not held                | The album that codified trip-hop; downtempo cornerstone.         |
| 44  | 'Live' at the Apollo                          | James Brown                 | 1963 | AM #44                         | not held                | The most celebrated live album in soul/R&B.                      |
| 45  | Songs in the Key of Life                      | Stevie Wonder               | 1976 | AM #45                         | not held                | Wonder's ambitious double-album summit of classic soul.          |
| 46  | Automatic for the People                      | R.E.M.                      | 1992 | AM #46                         | CD `CD ROCK REM`        | Alt-rock's melancholy masterpiece; R.E.M. at their most durable. |
| 47  | Purple Rain                                   | Prince and The Revolution   | 1984 | AM #47                         | CD `CD SOUNDTRACK PRIN` | Prince's synth-funk/rock crossover blockbuster.                  |
| 48  | Innervisions                                  | Stevie Wonder               | 1973 | AM #48                         | not held                | The tight, socially charged peak of Wonder's classic period.     |
| 49  | Blue                                          | Joni Mitchell               | 1971 | AM #49 — top singer-songwriter | not held                | The confessional singer-songwriter benchmark.                    |
| 50  | A Love Supreme                                | John Coltrane               | 1965 | AM #52 — spiritual-jazz apex   | CD `CD JAZZ COLT`       | Jazz's spiritual masterwork; swapped in for genre breadth.       |

### Jazz

_15 held at SFPL / 32 total. Ranked by album critical acclaim (Acclaimed Music / AllMusic / RS500 /
RYM / Penguin). SFPL = CD holding for borrow-and-rip; deduped vs the Top-50 (Kind of Blue and A Love
Supreme live there, not here)._

| #   | Album                               | Artist                            | Year | Acclaim                   | SFPL CD  | Why                                                       |
| --- | ----------------------------------- | --------------------------------- | ---- | ------------------------- | -------- | --------------------------------------------------------- |
| 1   | Mingus Ah Um                        | Charles Mingus                    | 1959 | AllMusic 5★; RYM top-jazz | not held | Gospel/blues big-band writing; "Goodbye Pork Pie Hat."    |
| 2   | The Shape of Jazz to Come           | Ornette Coleman                   | 1959 | RS500 #248                | CD       | The free-jazz manifesto that broke chord-changes open.    |
| 3   | Time Out                            | The Dave Brubeck Quartet          | 1959 | AllMusic 5★; RS500        | CD       | Odd-meter crossover landmark ("Take Five").               |
| 4   | Blue Train                          | John Coltrane                     | 1957 | AllMusic 5★               | CD       | Coltrane's hard-bop Blue Note peak.                       |
| 5   | Giant Steps                         | John Coltrane                     | 1960 | AllMusic 5★               | CD       | "Sheets of sound"; the Coltrane-changes benchmark.        |
| 6   | Saxophone Colossus                  | Sonny Rollins                     | 1956 | AllMusic 5★; Penguin Core | not held | Thematic-improv masterpiece ("St. Thomas").               |
| 7   | Bitches Brew                        | Miles Davis                       | 1970 | RS500 #94                 | CD       | The jazz-fusion big bang; electric, studio-collaged.      |
| 8   | Brilliant Corners                   | Thelonious Monk                   | 1957 | AllMusic 5★               | not held | Monk's angular compositional genius fully realized.       |
| 9   | Birth of the Cool                   | Miles Davis                       | 1957 | AllMusic 5★               | CD       | Nonet sessions that launched cool jazz.                   |
| 10  | My Favorite Things                  | John Coltrane                     | 1961 | AllMusic 5★               | CD       | Soprano-sax modal reinvention of the show tune.           |
| 11  | Sketches of Spain                   | Miles Davis                       | 1960 | RS500; AllMusic 5★        | CD       | Gil Evans orchestral collab; third-stream high point.     |
| 12  | Getz/Gilberto                       | Stan Getz & João Gilberto         | 1964 | RS500 #454; Grammy AOTY   | CD       | Bossa-nova crossover ("Girl from Ipanema").               |
| 13  | Head Hunters                        | Herbie Hancock                    | 1973 | RS500 #248                | not held | Funk-fusion breakthrough ("Chameleon").                   |
| 14  | In a Silent Way                     | Miles Davis                       | 1969 | AllMusic 5★               | CD       | The ambient-electric hinge into Bitches Brew.             |
| 15  | Speak No Evil                       | Wayne Shorter                     | 1966 | AllMusic 5★; Penguin Core | not held | Shorter's finest Blue Note date; harmonically luminous.   |
| 16  | Maiden Voyage                       | Herbie Hancock                    | 1965 | AllMusic 5★               | not held | Oceanic modal suite; a post-bop standard-setter.          |
| 17  | Out to Lunch!                       | Eric Dolphy                       | 1964 | AllMusic 5★; RYM          | not held | Avant-bop apex; jagged, elastic, singular.                |
| 18  | Moanin'                             | Art Blakey & the Jazz Messengers  | 1959 | AllMusic 5★               | not held | Definitive hard bop; the soul-jazz template.              |
| 19  | Somethin' Else                      | Cannonball Adderley               | 1958 | AllMusic 5★; Penguin Core | not held | Adderley date with Miles; blues-drenched hard bop.        |
| 20  | The Black Saint and the Sinner Lady | Charles Mingus                    | 1963 | RYM top-jazz              | not held | Through-composed ballet suite; his most ambitious work.   |
| 21  | Ellington at Newport                | Duke Ellington                    | 1956 | AllMusic 5★               | not held | The career-reviving live set.                             |
| 22  | Money Jungle                        | Ellington / Mingus / Roach        | 1963 | AllMusic 5★; Penguin Core | CD       | Cross-generational trio summit; combustible.              |
| 23  | Song for My Father                  | Horace Silver                     | 1965 | AllMusic 5★               | not held | Latin-tinged hard bop; the riff Steely Dan borrowed.      |
| 24  | Free Jazz                           | Ornette Coleman                   | 1961 | RYM                       | not held | Double-quartet collective improvisation; named the genre. |
| 25  | The Köln Concert                    | Keith Jarrett                     | 1975 | best-selling solo-piano   | not held | The improvised solo-piano touchstone.                     |
| 26  | Sunday at the Village Vanguard      | Bill Evans Trio                   | 1961 | AllMusic 5★; Penguin Core | CD       | Interactive-trio benchmark (held in the Complete box).    |
| 27  | Lady in Satin                       | Billie Holiday                    | 1958 | AllMusic 5★               | not held | Late-voice, string-backed emotional devastation.          |
| 28  | Ella and Louis                      | Ella Fitzgerald & Louis Armstrong | 1956 | AllMusic 5★               | not held | Vocal-duet standard-bearer (comp held, not standalone).   |
| 29  | The Sidewinder                      | Lee Morgan                        | 1964 | AllMusic 5★; Blue Note    | CD       | Boogaloo-groove crossover smash; soul-jazz staple.        |
| 30  | Empyrean Isles                      | Herbie Hancock                    | 1964 | AllMusic 5★; Penguin Core | not held | Lean quartet post-bop ("Cantaloupe Island").              |
| 31  | The Epic                            | Kamasi Washington                 | 2015 | Pitchfork 8.6             | CD       | Sprawling spiritual-jazz revival; modern-canon entry.     |
| 32  | Black Radio                         | Robert Glasper Experiment         | 2012 | Grammy Best R&B           | CD       | Jazz/hip-hop/neo-soul fusion; genre-blurring landmark.    |

### Rock & Classic Rock

_11 held at SFPL / 14 total. Deduped hard against the Top-50 (which is rock-heavy — Beatles, Dylan,
Stones, Zeppelin, Hendrix, Bowie's Ziggy, Floyd's DSOTM all live there), so this bucket is the
canonical rock **not** already showcased above. Ranked by album critical acclaim (Acclaimed Music /
RS500)._

| #   | Album                            | Artist             | Year | Acclaim                 | SFPL CD  | Why                                                       |
| --- | -------------------------------- | ------------------ | ---- | ----------------------- | -------- | --------------------------------------------------------- |
| 1   | Physical Graffiti                | Led Zeppelin       | 1975 | AM top-60; RS500 top-70 | CD       | Sprawling double-LP showing their full range.             |
| 2   | Hunky Dory                       | David Bowie        | 1971 | AM top-40               | CD       | Songwriting high-water mark; "Life on Mars?", "Changes."  |
| 3   | Low                              | David Bowie        | 1977 | AM top-30               | CD       | Berlin-era art-rock; most critically revered Bowie LP.    |
| 4   | After the Gold Rush              | Neil Young         | 1970 | AM top-40; RS500 top-80 | not held | Fragile, essential Neil; a folk-rock benchmark.           |
| 5   | Harvest                          | Neil Young         | 1972 | RS500 top-80            | CD       | His biggest and most beloved; "Heart of Gold."            |
| 6   | Rumours                          | Fleetwood Mac      | 1977 | RS500 top-10            | CD       | Pop-rock craftsmanship; one of the best-sellers ever.     |
| 7   | Sticky Fingers                   | The Rolling Stones | 1971 | AM top-60               | CD       | Loose, bluesy peak; opens the Exile-era run.              |
| 8   | The Wall                         | Pink Floyd         | 1979 | RS500 top-130           | CD       | The rock opera as blockbuster; "Comfortably Numb."        |
| 9   | Wish You Were Here               | Pink Floyd         | 1975 | RS500 top-200           | CD       | Elegiac Floyd; "Shine On You Crazy Diamond."              |
| 10  | Led Zeppelin II                  | Led Zeppelin       | 1969 | RS500 top-80            | CD       | The heavy-riff blueprint; "Whole Lotta Love."             |
| 11  | Darkness on the Edge of Town     | Bruce Springsteen  | 1978 | AM top-100              | not held | Leaner, darker Springsteen; a critics' favorite.          |
| 12  | The Band                         | The Band           | 1969 | RS500 top-50            | CD       | Americana bedrock; "The Night They Drove Old Dixie Down." |
| 13  | A Night at the Opera             | Queen              | 1975 | RS500 top-130           | CD       | Maximalist rock; "Bohemian Rhapsody."                     |
| 14  | In the Court of the Crimson King | King Crimson       | 1969 | RS500 top-300           | not held | The prog-rock founding document.                          |

### Alternative & Indie

_13 held at SFPL / 28 total. Ranked by album critical acclaim (Acclaimed Music / Pitchfork / RYM /
Metacritic). SFPL = CD holding for borrow-and-rip; deduped vs the Top-50 (OK Computer, Kid A, The
Queen Is Dead, Nevermind, Automatic for the People, Funeral, Is This It live there)._

| #   | Album                         | Artist              | Year | Acclaim                       | SFPL CD                | Why                                                          |
| --- | ----------------------------- | ------------------- | ---- | ----------------------------- | ---------------------- | ------------------------------------------------------------ |
| 1   | Doolittle                     | Pixies              | 1989 | Acclaimed top-20              | CD `CD ROCK PIXI`      | The record that taught Nirvana its dynamics.                 |
| 2   | In the Aeroplane Over the Sea | Neutral Milk Hotel  | 1998 | RYM top-10 all-time           | CD `CD ROCK NEUT`      | Lo-fi/folk-punk masterwork; cult devotion.                   |
| 3   | Loveless                      | My Bloody Valentine | 1991 | the shoegaze bible            | not held               | Guitar-texture landmark, endlessly influential.              |
| 4   | Yankee Hotel Foxtrot          | Wilco               | 2002 | Pitchfork/AllMusic; RS500     | CD `CD ROCK WILC`      | Alt-country dissolving into art-rock.                        |
| 5   | Daydream Nation               | Sonic Youth         | 1988 | Library of Congress registry  | not held               | Noise-rock double-LP high-water mark.                        |
| 6   | Surfer Rosa                   | Pixies              | 1988 | Albini production canon       | CD `CD ROCK PIXI`      | Raw, seismic debut.                                          |
| 7   | Sound of Silver               | LCD Soundsystem     | 2007 | Pitchfork 9.2                 | not held               | Dance-punk peak; placed here (best-fit) over Electronic.     |
| 8   | Slanted and Enchanted         | Pavement            | 1992 | lo-fi/slacker touchstone      | CD `CD ROCK PAVE`      | Defined '90s American indie.                                 |
| 9   | Illinois                      | Sufjan Stevens      | 2005 | Metacritic 90; Pitchfork AOTY | not held               | Baroque-folk maximalism.                                     |
| 10  | Boxer                         | The National        | 2007 | critics top-of-decade         | not held               | Slow-burn precision; the band's breakthrough.                |
| 11  | In Rainbows                   | Radiohead           | 2007 | Pitchfork 9.3                 | CD `CD ROCK RADI`      | Warm, human counterweight to Kid A.                          |
| 12  | In Utero                      | Nirvana             | 1993 | Acclaimed top-tier; RS500     | CD `CD ROCK NIRV`      | Abrasive, uncompromised follow-up.                           |
| 13  | Murmur                        | R.E.M.              | 1983 | Acclaimed top-tier; RS500     | CD `CD ROCK REM`       | The jangly birth of American college rock.                   |
| 14  | Odelay                        | Beck                | 1996 | Grammy; Dust Bros. collage    | not held               | Genre-blender that made Beck a star (SFPL holds Sea Change). |
| 15  | Modern Vampires of the City   | Vampire Weekend     | 2013 | Metacritic 87                 | not held               | Ornate, mortality-haunted third act.                         |
| 16  | The Bends                     | Radiohead           | 1995 | Acclaimed top-tier; RS500     | CD `TEEN CD ROCK RADI` | The guitar record before the reinvention.                    |
| 17  | Let England Shake             | PJ Harvey           | 2011 | Mercury Prize; Metacritic 87  | CD `CD ROCK HARV`      | War-poetry song cycle; her critical apex.                    |
| 18  | The Smiths                    | The Smiths          | 1984 | foundational indie debut      | not held               | Where the jangle-pop template starts.                        |
| 19  | Unknown Pleasures             | Joy Division        | 1979 | post-punk cornerstone         | not held               | Cold, cavernous, endlessly imitated.                         |
| 20  | Turn on the Bright Lights     | Interpol            | 2002 | Pitchfork 9.5                 | not held               | Taut, atmospheric NYC debut.                                 |
| 21  | The Moon & Antarctica         | Modest Mouse        | 2000 | critics top-of-decade         | not held               | Cosmic, sprawling indie-rock statement.                      |
| 22  | Either/Or                     | Elliott Smith       | 1997 | singer-songwriter touchstone  | CD `CD ROCK SMIT`      | Intimate, devastating songcraft.                             |
| 23  | If You're Feeling Sinister    | Belle and Sebastian | 1996 | twee/indie-pop canon          | not held               | Wry, literate chamber-pop.                                   |
| 24  | The Suburbs                   | Arcade Fire         | 2010 | Grammy AOTY; Metacritic 87    | not held               | Sprawling concept-album peak.                                |
| 25  | Carrie & Lowell               | Sufjan Stevens      | 2015 | Pitchfork 9.3                 | CD `CD ROCK STEV`      | Hushed, autobiographical devastation.                        |
| 26  | Vampire Weekend               | Vampire Weekend     | 2008 | Metacritic 84; buzz debut     | CD `CD ROCK VAMP`      | Afropop-inflected preppy indie-pop.                          |
| 27  | High Violet                   | The National        | 2010 | Metacritic 85                 | not held               | The band's fullest, most anthemic set.                       |
| 28  | Fleet Foxes                   | Fleet Foxes         | 2008 | Metacritic 87; Pitchfork      | not held               | Harmony-drenched baroque-folk revival.                       |

### Hip-Hop / R&B / Soul

_20 held at SFPL / 31 total. Ranked by album critical acclaim (RS500 2020 / Acclaimed Music /
Pitchfork / RYM). SFPL = CD holding for borrow-and-rip; deduped vs the Top-50 (What's Going On, To
Pimp a Butterfly, Songs in the Key of Life, Innervisions, MBDTF, Nation of Millions live there)._

| #   | Album                                  | Artist                        | Year | Acclaim                   | SFPL CD                 | Why                                                             |
| --- | -------------------------------------- | ----------------------------- | ---- | ------------------------- | ----------------------- | --------------------------------------------------------------- |
| 1   | Illmatic                               | Nas                           | 1994 | RYM #1 hip-hop            | CD `CD RAP NAS`         | The template for lyrical East-Coast rap; near-flawless.         |
| 2   | The Miseducation of Lauryn Hill        | Lauryn Hill                   | 1998 | RS500 #10                 | CD `CD RAP HILL`        | Soul/hip-hop fusion; defining neo-soul statement.               |
| 3   | Enter the Wu-Tang (36 Chambers)        | Wu-Tang Clan                  | 1993 | RS500 #27                 | CD `CD RAP WUTA`        | Raw, gritty blueprint for the NY hardcore era.                  |
| 4   | Ready to Die                           | The Notorious B.I.G.          | 1994 | RS500 #22                 | CD `CD RAP NOTO`        | Street narrative meets pop craft; an East-Coast pillar.         |
| 5   | The Low End Theory                     | A Tribe Called Quest          | 1991 | top jazz-rap              | CD `CD RAP TRIB`        | Jazz-rap high-water mark; bass-and-boom-bap perfection.         |
| 6   | Midnight Marauders                     | A Tribe Called Quest          | 1993 | Acclaimed Music high      | CD `CD RAP TRIB`        | Tighter, hookier companion to Low End Theory.                   |
| 7   | good kid, m.A.A.d city                 | Kendrick Lamar                | 2012 | RS500 #115; Pitchfork     | CD `CD RAP LAMA`        | Cinematic Compton coming-of-age concept album.                  |
| 8   | Voodoo                                 | D'Angelo                      | 2000 | RYM top R&B               | CD `CD R&B DANG`        | Loose, groove-drunk neo-soul landmark.                          |
| 9   | Madvillainy                            | Madvillain (MF DOOM & Madlib) | 2004 | top underground rap       | not held                | Abstract sample-collage cult classic; DOOM at his peak.         |
| 10  | There's a Riot Goin' On                | Sly & the Family Stone        | 1971 | RS500 #82                 | CD `CD R&B SLY`         | Dark, druggy funk that inverted '60s optimism.                  |
| 11  | Let's Get It On                        | Marvin Gaye                   | 1973 | RS500 #165                | not held                | The definitive sensual-soul record (comps only at SFPL).        |
| 12  | The Chronic                            | Dr. Dre                       | 1992 | RS500 #137                | CD `CD RAP DR`          | G-funk blueprint that defined West-Coast rap.                   |
| 13  | I Never Loved a Man the Way I Love You | Aretha Franklin               | 1967 | RS500 top-tier            | not held                | The arrival of the Queen of Soul (comps only at SFPL).          |
| 14  | Blond                                  | Frank Ocean                   | 2016 | Pitchfork #1 of the 2010s | not held (never on CD)  | Fractured, intimate art-R&B; rip from a lossless source.        |
| 15  | Channel Orange                         | Frank Ocean                   | 2012 | RS500 #148; Pitchfork     | CD `TEEN CD R&B OCEA`   | Genre-bending R&B breakthrough.                                 |
| 16  | Super Fly                              | Curtis Mayfield               | 1972 | RS500 #72                 | CD `CD SOUNDTRACK MAYF` | Socially charged funk-soul; a full album, not a score.          |
| 17  | Talking Book                           | Stevie Wonder                 | 1972 | RS500 #59                 | not held                | "Superstition"; the classic run begins (no Wonder LPs at SFPL). |
| 18  | Liquid Swords                          | GZA                           | 1995 | RYM top Wu solo           | CD `CD RAP GENI`        | Chess-dark RZA production; the sharpest Wu solo record.         |
| 19  | Aquemini                               | OutKast                       | 1998 | RS500 #49                 | CD `CD POP OUTK`        | Southern rap's expansive, funk-drenched apex.                   |
| 20  | The Blueprint                          | Jay-Z                         | 2001 | RS500 #50                 | not held                | Soul-sample renaissance; Jay's most cohesive album.             |
| 21  | 3 Feet High and Rising                 | De La Soul                    | 1989 | RS500 #100                | CD `CD RAP DE`          | Playful, sample-dense Daisy-Age counterpoint.                   |
| 22  | The Infamous                           | Mobb Deep                     | 1995 | RYM top hardcore rap      | not held                | Bleak, minimalist Queensbridge classic.                         |
| 23  | Ctrl                                   | SZA                           | 2017 | top modern R&B            | CD `CD R&B SZA`         | Confessional alt-R&B that defined a generation's sound.         |
| 24  | Doggystyle                             | Snoop Doggy Dogg              | 1993 | RS500 #170                | CD `CD RAP SNOO`        | G-funk at its most effortless.                                  |
| 25  | Hot Buttered Soul                      | Isaac Hayes                   | 1969 | top soul                  | not held                | Orchestral, long-form soul that broke the 3-minute mold.        |
| 26  | Otis Blue                              | Otis Redding                  | 1965 | RS500 #78                 | not held                | The definitive Stax soul statement.                             |
| 27  | Baduizm                                | Erykah Badu                   | 1997 | top neo-soul              | not held                | Founding document of neo-soul.                                  |
| 28  | Donuts                                 | J Dilla                       | 2006 | top instrumental hip-hop  | not held                | Beat-tape as art; the producer's-producer touchstone.           |
| 29  | Stankonia                              | OutKast                       | 2000 | RS500 #64                 | CD `CD RAP OUTK`        | Frenetic, futuristic Southern rap; "B.O.B." / "Ms. Jackson."    |
| 30  | DAMN.                                  | Kendrick Lamar                | 2017 | Pulitzer Prize for Music  | CD `CD RAP LAMA`        | The only rap album to win the Pulitzer.                         |
| 31  | Greatest Hits                          | Al Green                      | 1975 | RS500 #135                | CD `CD R&B GREE`        | The canonical Al Green single-disc; Hi Records soul.            |

### Electronic

_8 held at SFPL / 30 total. Ranked by album critical acclaim (Acclaimed Music / RYM / Pitchfork /
Resident Advisor). SFPL = CD holding for borrow-and-rip; deduped vs the Top-50 (Blue Lines lives
there) and vs Alt & Indie (LCD Soundsystem placed there). SFPL's CD collection is thin on electronic
— most of this bucket routes to acquire-elsewhere._

| #   | Album                           | Artist                                 | Year | Acclaim                      | SFPL CD                 | Why                                                     |
| --- | ------------------------------- | -------------------------------------- | ---- | ---------------------------- | ----------------------- | ------------------------------------------------------- |
| 1   | Dummy                           | Portishead                             | 1994 | Mercury Prize winner         | CD `CD ROCK PORT`       | Definitive trip-hop; noir soul over dusty breaks.       |
| 2   | Endtroducing.....               | DJ Shadow                              | 1996 | RYM #1 instrumental hip-hop  | not held                | All-sample masterwork; canonical downtempo/turntablism. |
| 3   | Mezzanine                       | Massive Attack                         | 1998 | RYM top-100                  | CD `CD POP MASS`        | Dark, dubby trip-hop apex.                              |
| 4   | Selected Ambient Works 85–92    | Aphex Twin                             | 1992 | RYM #1 electronic all-time   | not held                | Foundational ambient-techno; the IDM cornerstone.       |
| 5   | Discovery                       | Daft Punk                              | 2001 | Pitchfork best-of-2000s      | CD `CD POP DAFT`        | French-house / filter-disco touchstone.                 |
| 6   | Music Has the Right to Children | Boards of Canada                       | 1998 | RYM top IDM                  | not held                | Warm, hauntological ambient IDM benchmark.              |
| 7   | Trans-Europe Express            | Kraftwerk                              | 1977 | foundational                 | not held                | Ur-text of all electronic pop/techno.                   |
| 8   | Untrue                          | Burial                                 | 2007 | RA / Pitchfork best-of-2000s | not held                | Genre-defining dubstep/2-step; modern canon.            |
| 9   | Another Green World             | Brian Eno                              | 1975 | Acclaimed Music very high    | CD `CD ROCK ENO`        | Bridge from art-rock to ambient/proto-electronic.       |
| 10  | Homework                        | Daft Punk                              | 1997 | Resident Advisor             | CD `CD POP DAFT`        | Raw filter-house debut; "Da Funk."                      |
| 11  | Richard D. James Album          | Aphex Twin                             | 1996 | RYM top IDM                  | not held                | Drill-'n'-bass meets melody; IDM peak.                  |
| 12  | Ambient 1: Music for Airports   | Brian Eno                              | 1978 | coined "ambient"             | not held                | The album that named the genre.                         |
| 13  | Since I Left You                | The Avalanches                         | 2000 | RYM top plunderphonics       | CD `CD POP AVAL`        | Sample-collage magnum opus.                             |
| 14  | Dubnobasswithmyheadman          | Underworld                             | 1994 | NME classic                  | not held                | Progressive-house/techno landmark.                      |
| 15  | Dig Your Own Hole               | The Chemical Brothers                  | 1997 | Pitchfork best-of-90s        | CD `CD POP CHEM`        | Big-beat high-water mark.                               |
| 16  | Orbital 2 (Brown Album)         | Orbital                                | 1993 | critical consensus           | not held                | Melodic UK techno peak.                                 |
| 17  | Moon Safari                     | Air                                    | 1998 | Acclaimed Music; Pitchfork   | not held                | Lush French downtempo/lounge landmark.                  |
| 18  | Rounds                          | Four Tet                               | 2003 | Pitchfork best-of-2000s      | not held                | Folktronica / melodic IDM benchmark.                    |
| 19  | Maxinquaye                      | Tricky                                 | 1995 | NME Album of the Year        | not held                | Paranoid, sensual trip-hop classic.                     |
| 20  | Tri Repetae                     | Autechre                               | 1995 | RYM top IDM                  | not held                | Abstract Warp-era IDM cornerstone.                      |
| 21  | The Fat of the Land             | The Prodigy                            | 1997 | #1 in 25 countries           | not held                | Big-beat/breakbeat crossover monster.                   |
| 22  | You've Come a Long Way, Baby    | Fatboy Slim                            | 1998 | multi-platinum               | not held                | Defining big-beat party record.                         |
| 23  | In Colour                       | Jamie xx                               | 2015 | RA best-of                   | not held                | Modern UK dance/rave-nostalgia standout.                |
| 24  | Swim                            | Caribou                                | 2010 | Pitchfork; RA best-of        | not held                | Organic dance-pop / psych-electronic peak.              |
| 25  | Immunity                        | Jon Hopkins                            | 2013 | Mercury Prize nominee        | not held                | Cinematic techno/ambient arc.                           |
| 26  | Geogaddi                        | Boards of Canada                       | 2002 | Pitchfork best-of-2000s      | not held                | Darker companion to MHTRTC.                             |
| 27  | Cosmogramma                     | Flying Lotus                           | 2010 | Pitchfork best-of; RA        | not held                | Jazz-fusion electronic / beat-scene apex.               |
| 28  | Syro                            | Aphex Twin                             | 2014 | Pitchfork BNM; Grammy        | not held                | Comeback proof the master still leads IDM.              |
| 29  | Third                           | Portishead                             | 2008 | Pitchfork BNM                | not held                | Krautrock-tinged return; a critical darling.            |
| 30  | Promises                        | Floating Points, Pharoah Sanders & LSO | 2021 | Pitchfork BNM; RA best-of    | CD `CD ORCHESTRAL FLOA` | Ambient-jazz-electronic crossover of the decade.        |

### Classical & Piano

_26 held at SFPL / 32 total (2 not held, 4 unverified). Ranked by canonical status +
benchmark-recording acclaim (Gramophone Hall of Fame / Penguin rosettes / reference consensus),
**not** pop-style charts. Rows keep the source's Work | Composer | Recording shape — the named
performer/conductor is the target. SFPL classical cards seldom print the performer, so **CD (alt)**
= the work is on CD but the benchmark artist is unconfirmed (check the disc at pickup), **CD
(benchmark)** = the exact reference disc confirmed held, **unverified** = only compilations/recitals
surfaced. No Top-50 overlap (the spine carries no classical)._

| #   | Work                            | Composer     | Recording (artist / cond.)              | Acclaim                       | SFPL CD        | Why                                                                  |
| --- | ------------------------------- | ------------ | --------------------------------------- | ----------------------------- | -------------- | -------------------------------------------------------------------- |
| 1   | Goldberg Variations, BWV 988    | J.S. Bach    | Glenn Gould (1981, Sony)                | Gramophone Hall of Fame       | CD (alt)       | The desert-island keyboard record; Gould's valedictory re-recording. |
| 2   | Der Ring des Nibelungen         | Wagner       | Solti / Vienna Phil (Decca)             | "Greatest recording" polls    | not held       | The landmark studio Ring; the foundation of the opera shelf.         |
| 3   | Symphonies 5 & 7                | Beethoven    | Carlos Kleiber / Vienna Phil (DG)       | Gramophone Hall of Fame       | CD (alt)       | Electric, propulsive; held only via complete cycles.                 |
| 4   | Tosca                           | Puccini      | Callas / de Sabata / La Scala (1953)    | The canonical opera recording | unverified     | Callas's Tosca; only comps surfaced — buy the de Sabata.             |
| 5   | Cello Concerto in E minor       | Elgar        | du Pré / Barbirolli / LSO (EMI)         | Gramophone Hall of Fame       | CD (alt)       | The definitive account; SFPL holds other soloists.                   |
| 6   | Symphony No. 9 "Choral"         | Beethoven    | Furtwängler / Bayreuth (1951, EMI)      | Perennial "greatest Ninth"    | CD (alt)       | The mythic reopening-of-Bayreuth performance.                        |
| 7   | Symphony No. 9                  | Mahler       | Karajan / Berlin Phil (live, DG)        | Gramophone Hall of Fame       | CD (alt)       | The great modern Mahler 9; the live remake is the one.               |
| 8   | Cello Suites, BWV 1007–1012     | J.S. Bach    | Casals (1936–39) / or Rostropovich      | Historic canon                | CD (alt)       | Casals rescued the Suites; grab Casals or Rostropovich.              |
| 9   | Le nozze di Figaro              | Mozart       | Erich Kleiber / Vienna Phil (Decca)     | Penguin rosette               | not held       | The warm benchmark Figaro; no complete on SFPL CD.                   |
| 10  | Nocturnes (complete)            | Chopin       | Arthur Rubinstein (RCA)                 | Reference Chopin Nocturnes    | unverified     | Aristocratic, definitive; only recital discs surfaced.               |
| 11  | Symphony No. 6 "Pathétique"     | Tchaikovsky  | Mravinsky / Leningrad Phil (DG)         | Canonical reference           | CD (alt)       | Ferocious, idiomatic; the Russian benchmark.                         |
| 12  | Préludes / Images               | Debussy      | Michelangeli (DG)                       | Gramophone Hall of Fame       | unverified     | Tonal-color perfection; only French recitals surfaced.               |
| 13  | Symphony No. 4                  | Brahms       | Carlos Kleiber / Vienna Phil (DG)       | Benchmark Brahms 4            | CD (alt)       | Kleiber's rhythmic fire; held via a Brahms complete set.             |
| 14  | Violin Concerto in D            | Beethoven    | Heifetz / Munch / Boston (RCA)          | Canonical                     | CD (alt)       | Heifetz's aristocratic sweep; SFPL holds other soloists.             |
| 15  | St Matthew Passion              | J.S. Bach    | Karl Richter (Archiv) / or Gardiner     | Canon                         | CD (alt)       | The summit of sacred music; pick your school.                        |
| 16  | Symphony No. 2 "Resurrection"   | Mahler       | Klemperer / Philharmonia (EMI)          | Penguin-lauded                | CD (alt)       | Granitic, overwhelming finale.                                       |
| 17  | Symphony No. 9 "New World"      | Dvořák       | Kertész / Vienna Phil (Decca)           | Penguin reference             | CD (alt)       | Lyrical, glowing benchmark New World.                                |
| 18  | Piano Sonatas (complete / late) | Beethoven    | Wilhelm Kempff (DG stereo)              | Canonical cycle               | CD (benchmark) | Poetic, humane Beethoven; the benchmark disc is confirmed.           |
| 19  | Don Giovanni                    | Mozart       | Giulini / Philharmonia (EMI)            | Penguin / canon benchmark     | CD (alt)       | Star-cast, dramatically taut; a complete set is held.                |
| 20  | Piano Concertos 2 & 3           | Rachmaninoff | Rachmaninoff plays Rachmaninoff (RCA)   | Composer-as-pianist canon     | CD (benchmark) | Definitive by authorial authority; confirmed at SFPL.                |
| 21  | String Quintet in C, D956       | Schubert     | Casals/Stern / or Amadeus Quartet       | Chamber-music canon           | unverified     | The greatest chamber work by many; only a Busch box surfaced.        |
| 22  | Requiem (Messa da Requiem)      | Verdi        | Giulini / Philharmonia (EMI)            | Gramophone benchmark          | CD (alt)       | Operatic power and hush; a reference Verdi Requiem.                  |
| 23  | Ballades / Preludes             | Chopin       | Zimerman / or Pollini (DG)              | Gramophone-lauded             | CD (alt)       | Poised virtuoso Chopin; SFPL holds historic Chopin.                  |
| 24  | Violin Concerto in D            | Brahms       | Oistrakh / Klemperer (EMI) / or Heifetz | Canonical                     | CD (alt)       | Big-boned, noble Brahms; SFPL holds Menuhin.                         |
| 25  | Gymnopédies / Gnossiennes       | Satie        | Pascal Rogé (Decca)                     | Reference Satie piano         | CD (alt)       | Calm, perfectly weighted; SFPL holds a Satie piano-works disc.       |
| 26  | Requiem in D minor, K626        | Mozart       | Karl Böhm / Vienna Phil (DG)            | Canonical                     | CD (alt)       | Weighty, classical Mozart Requiem; Böhm not confirmed.               |
| 27  | Symphonies 2 & 5                | Sibelius     | Karajan (EMI/DG) / or Berglund          | Reference Sibelius            | CD (alt)       | Nordic grandeur and the great Fifth finale.                          |
| 28  | Piano Concerto No. 5 "Emperor"  | Beethoven    | Pollini / Böhm (DG) / or Gilels         | Canonical                     | CD (alt)       | Grand, patrician Emperor; held via concerto sets.                    |
| 29  | The Four Seasons                | Vivaldi      | Il Giardino Armonico / or Carmignola    | Benchmark HIP                 | CD (alt)       | Vivid period-instrument fireworks; performer unconfirmed.            |
| 30  | Winterreise                     | Schubert     | Fischer-Dieskau / Moore (DG)            | Reference song cycle          | CD (alt)       | The summit of Lieder singing; singer unconfirmed.                    |
| 31  | The Well-Tempered Clavier       | J.S. Bach    | Richter / or Gould                      | Canonical keyboard bible      | CD (alt)       | The "Old Testament" of piano; performer unconfirmed.                 |
| 32  | Preludes (op.23 / op.32)        | Rachmaninoff | Vladimir Ashkenazy (Decca)              | Reference Rachmaninoff piano  | CD (alt)       | The great Romantic miniatures; held via a complete set.              |

## Track 3c — Taste-gap buckets (swing · funk/soul · blues · vocal-trad jazz)

**106 albums across four genres the acclaim-based Track 3b under-covered — the owner's top-listening
lanes (swing/big-band, funk/deep-soul, blues, and vocal/trad jazz).** These are the **taste-gap
additions _beyond_ Track 3b**: every album here is deduped against the Top-50 and the six Track 3b
buckets, so nothing already listed above repeats (12 Track 3b cross-overs dropped — see per-section
notes). Where an album fits two of these gap genres it is listed once in its best-fit bucket
(Sinatra's _Songs for Swingin' Lovers!_ and _Sinatra at the Sands_ land in vocal/trad jazz, not
swing). **44 of the 106 are held at SFPL on CD** — the borrow-and-rip subset that feeds the same
reservation pipeline as Track 3b; the other 62 route to LINK+ / purchase / lossless-digital. Ranked
best-first within each genre by canonical/album acclaim (blend of Acclaimed Music, AllMusic, Rolling
Stone 500, Penguin Jazz Guide). **SFPL CD** = a Music-CD holding verified in BiblioCommons
(`f_FORMAT=MUSIC_CD`): `CD` + call # = the album is held; `CD (comp)` = a rip-able compilation or
alternate edition standing in for a pre-CD-era catalog; `not held` = source elsewhere; `unverified`
= catalog inconclusive (only anthologies/errors surfaced). **SFPL's CD shelf is thin on funk/soul**
(only 5 of 21 held — most of that bucket is buy-elsewhere); swing and vocal/trad jazz fare better
via jazz-reissue comps.

### Swing / Big-Band

_27 albums / **10 held at SFPL on CD**. Fills the library's zero-swing/big-band lane despite it
being a top listening lane. Deduped vs Track 3b (Ellington at Newport dropped — it lives in the Jazz
bucket) and vs the vocal/trad bucket below (two Sinatra big-band vocal sets placed there). Ranked by
canonical acclaim (Penguin Jazz Guide / AllMusic / Acclaimed Music). Duke Ellington has 27 CDs on
SFPL under `CD JAZZ ELLI` and Sinatra 30 under `CD POP SINA`, so several "not held"/"unverified"
classics may exist under alternate editions — worth a shelf/LINK+ check before buying._

| #   | Album                                          | Artist                             | Year    | Acclaim                           | SFPL CD                                           | Why                                                                                       |
| --- | ---------------------------------------------- | ---------------------------------- | ------- | --------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | The Atomic Mr. Basie (Complete Atomic Basie)   | Count Basie                        | 1958    | Penguin Crown; AllMusic 5★        | not held (Basie Orch. on CD, `CD JAZZ COUN`)      | The definitive modern big-band statement; Neal Hefti charts, "Whirly-Bird."               |
| 2   | Never No Lament: The Blanton-Webster Band      | Duke Ellington                     | 1940–42 | Penguin Core; AllMusic 5★         | not held (Ellington broadly held, `CD JAZZ ELLI`) | Greatest edition of the greatest band — "Ko-Ko," "Cotton Tail"; his compositional peak.   |
| 3   | The Famous 1938 Carnegie Hall Jazz Concert     | Benny Goodman                      | 1938    | AllMusic 5★; canonical            | CD `CD JAZZ GOOD`                                 | The night swing entered the concert hall; "Sing, Sing, Sing."                             |
| 4   | The Far East Suite                             | Duke Ellington                     | 1966    | Grammy; AllMusic 5★; Penguin Core | unverified                                        | Late-Ellington/Strayhorn suite; mature, exotic big-band writing.                          |
| 5   | The Original American Decca Recordings         | Count Basie                        | 1937–39 | Penguin Core; AllMusic 5★         | not held                                          | The Kansas City engine room — Lester Young, one-take swing, "Jumpin' at the Woodside."    |
| 6   | The Essential Artie Shaw (Begin the Beguine)   | Artie Shaw                         | 1938–45 | AllMusic 4.5★; canonical          | CD `CD JAZZ SHAW`                                 | Goodman's smoother rival; "Begin the Beguine," clarinet elegance.                         |
| 7   | Live on the Air 1938–1942                      | Glenn Miller                       | 1938–42 | genre-defining                    | CD `CD JAZZ MILL`                                 | The best-selling swing sound — "In the Mood," "Moonlight Serenade."                       |
| 8   | Such Sweet Thunder                             | Duke Ellington                     | 1957    | AllMusic 5★; Penguin Core         | CD `CD JAZZ ELLI`                                 | Ellington/Strayhorn Shakespeare suite; sophisticated late-'50s orchestral swing.          |
| 9   | Duke Ellington & John Coltrane                 | Duke Ellington                     | 1962    | AllMusic 4.5★; Acclaimed Music    | CD `CD JAZZ ELLI`                                 | Cross-generation summit; "In a Sentimental Mood."                                         |
| 10  | A Study in Frustration                         | Fletcher Henderson                 | 1923–38 | Penguin Core; foundational        | unverified                                        | The blueprint every swing band copied; Henderson's arrangements built the genre.          |
| 11  | Blowin' Up a Storm! / The Thundering Herds     | Woody Herman                       | 1945–47 | Penguin Core; AllMusic 4.5★       | not held                                          | First & Second Herds — "Caldonia," "Four Brothers"; bebop-informed big band.              |
| 12  | Cab Calloway & His Orchestra, Vol. 1 (1930–34) | Cab Calloway                       | 1930–34 | AllMusic 4.5★; canonical          | CD `CD JAZZ CALL v.1`                             | Harlem hi-de-ho showmanship; the Cotton Club's wildest bandleader.                        |
| 13  | The Wildest!                                   | Louis Prima                        | 1956    | AllMusic 4.5★; genre-defining     | CD `CD WINDS PRIM`                                | Vegas jump-swing with Keely Smith & Sam Butera; "Just a Gigolo."                          |
| 14  | The Best of Louis Jordan                       | Louis Jordan                       | 1942–51 | AllMusic 5★; Acclaimed Music      | not held                                          | The jump-blues king, "father of R&B"; "Caldonia," "Choo Choo Ch'Boogie."                  |
| 15  | Tempo and Swing / Midnight Sun                 | Lionel Hampton                     | 1937–47 | Penguin Core; AllMusic 4.5★       | not held                                          | Vibraphone-driven, hardest-swinging small-big-band; "Flying Home."                        |
| 16  | Spinnin' the Webb / Ella & Chick               | Chick Webb                         | 1935–39 | Penguin Core; canonical           | unverified                                        | The Savoy drum king who launched Ella; dance-floor swing defined.                         |
| 17  | Sings the Duke Ellington Song Book             | Ella Fitzgerald                    | 1957    | AllMusic 5★; Acclaimed Music      | unverified                                        | The band-forward songbook, recorded live-in-studio with Ellington's orchestra.            |
| 18  | 50th Anniversary Collection                    | The Andrews Sisters                | 1937–51 | canonical                         | not held                                          | The definitive close-harmony vocal swing; "Boogie Woogie Bugle Boy."                      |
| 19  | Yes, Indeed! / The Best of Tommy Dorsey        | Tommy Dorsey                       | 1935–45 | AllMusic 4★; canonical            | unverified                                        | "The Sentimental Gentleman of Swing"; smooth trombone, launched Sinatra.                  |
| 20  | Drummin' Man / The Best of Gene Krupa          | Gene Krupa                         | 1938–49 | AllMusic 4★; canonical            | unverified                                        | The showman drummer who made rhythm a solo instrument; "Drum Boogie."                     |
| 21  | The New Classics                               | Scott Bradlee's Postmodern Jukebox | 2017    | genre-crossover                   | CD `CD JAZZ BRAD`                                 | Modern pop reimagined as vintage swing/jazz — the owner's electro-swing gateway.          |
| 22  | Robot (<\|>)                                   | Caravan Palace                     | 2015    | electro-swing landmark            | CD `CD POP CARA`                                  | French electro-swing flagship; gypsy-jazz guitar over house beats.                        |
| 23  | Louie Louie Louie                              | Big Bad Voodoo Daddy               | 2017    | swing-revival staple              | CD `CD JAZZ BIG`                                  | Neo-swing revival mainstays — "Go Daddy-O."                                               |
| 24  | The Dirty Boogie                               | Brian Setzer Orchestra             | 1998    | AllMusic 4★; multi-platinum       | not held (Setzer on CD, `CD ROCK SETZ`)           | The swing-revival smash — "Jump, Jive an' Wail"; a 17-piece band with a rockabilly heart. |
| 25  | Hot                                            | Squirrel Nut Zippers               | 1996    | AllMusic 4.5★; Acclaimed Music    | not held (band otherwise on CD)                   | Hot-jazz/calypso revival; "Hell" — essential to the '90s swing wave.                      |
| 26  | The Birth of Swing / Sing, Sing, Sing          | Benny Goodman                      | 1935–38 | foundational                      | unverified                                        | The studio "King of Swing"; the recordings that ignited the swing era.                    |
| 27  | Rhythm Is Our Business / For Dancers Only      | Jimmie Lunceford                   | 1934–42 | Penguin Core; AllMusic 4.5★       | unverified                                        | The most polished, showmanship-driven '30s band; influenced Basie & Ellington.            |

### Funk / Soul

_21 albums / **only 5 held at SFPL on CD** — the catalog's funk/deep-soul CD shelf is thin, so 16
are buy-elsewhere (LINK+ / purchase / lossless digital). Deduped vs Track 3b's Hip-Hop/R&B/Soul
bucket + Top-50 (**9 overlaps dropped**: There's a Riot Goin' On, Innervisions, Super Fly, I Never
Loved a Man, Talking Book, Otis Blue, Hot Buttered Soul, Let's Get It On, 'Live' at the Apollo).
Owner-favorite artists (Betty Davis, Vulfpeck, Billy Preston) included. Ranked by album acclaim
(Acclaimed Music / RS500 / RYM)._

| #   | Album                                | Artist                 | Year             | Acclaim                       | SFPL CD                   | Why                                                                       |
| --- | ------------------------------------ | ---------------------- | ---------------- | ----------------------------- | ------------------------- | ------------------------------------------------------------------------- |
| 1   | Maggot Brain                         | Funkadelic             | 1971             | Acclaimed Music; RS500 #479   | not held                  | Psychedelic acid-funk apex; Eddie Hazel's ten-minute guitar elegy.        |
| 2   | Mothership Connection                | Parliament             | 1975             | Acclaimed Music; RS500 #274   | not held                  | P-Funk cosmology launched; the horn-and-groove blueprint sampled forever. |
| 3   | Stand!                               | Sly & the Family Stone | 1969             | RS500 #118; AllMusic 5★       | not held (hits comp only) | Utopian, integrated party-funk at its peak — "I Want to Take You Higher." |
| 4   | Let's Stay Together                  | Al Green               | 1972             | RS500 #241; AllMusic 5★       | CD `CD R&B GREE`          | Willie Mitchell's Hi Records sound; the smoothest soul ever cut.          |
| 5   | Live                                 | Donny Hathaway         | 1972             | Acclaimed Music; AllMusic 5★  | not held                  | The gold standard of live soul; audience and singer as one.               |
| 6   | Still Bill                           | Bill Withers           | 1972             | Acclaimed Music; AllMusic 5★  | CD `CD R&B WITH`          | Plainspoken songcraft — "Use Me," "Lean on Me"; understated funk grit.    |
| 7   | Betty Davis                          | Betty Davis            | 1973             | RYM top-funk; reappraisal     | not held                  | Ferocious proto-punk funk; the uncompromising owner-favorite debut.       |
| 8   | Amazing Grace                        | Aretha Franklin        | 1972             | best-selling gospel LP        | CD `CD GOSPEL FRAN`       | Aretha's return to church; the biggest-selling live gospel album ever.    |
| 9   | Call Me                              | Al Green               | 1973             | AllMusic 5★; Acclaimed Music  | not held                  | Often called Green's most complete album; country-soul crossovers.        |
| 10  | Rejuvenation                         | The Meters             | 1974             | Acclaimed Music; RYM top-funk | not held                  | New Orleans syncopation perfected — "Hey Pocky A-Way."                    |
| 11  | Live at the Harlem Square Club, 1963 | Sam Cooke              | 1985 (rec. 1963) | AllMusic 5★; landmark         | not held                  | The raw, sweat-soaked Cooke his label buried; electrifying live soul.     |
| 12  | One Nation Under a Groove            | Funkadelic             | 1978             | RS500 #480; AllMusic 5★       | not held                  | The dancefloor-uniting P-Funk anthem album; tighter, hookier Funkadelic.  |
| 13  | They Say I'm Different               | Betty Davis            | 1974             | RYM top-funk; reappraisal     | not held                  | The second Betty Davis salvo; even wilder — core to the owner's lane.     |
| 14  | Shaft                                | Isaac Hayes            | 1971             | RS500; Oscar/Grammy winner    | CD `CD SOUNDTRACK SHAF`   | The wah-guitar theme that defined an era; symphonic funk-soul.            |
| 15  | Fulfillingness' First Finale         | Stevie Wonder          | 1974             | Grammy AOTY; AllMusic 5★      | CD `CD POP WOND`          | The quieter classic-period gem — "Boogie On Reggae Woman."                |
| 16  | Just as I Am                         | Bill Withers           | 1971             | AllMusic 5★; Acclaimed Music  | not held                  | The debut with "Ain't No Sunshine"; folk-soul intimacy.                   |
| 17  | Thrill of the Arts                   | Vulfpeck               | 2015             | RYM modern-funk; owner pick   | not held                  | The breakout indie-funk statement; the owner's core modern-funk band.     |
| 18  | The Beautiful Game                   | Vulfpeck               | 2016             | RYM; owner pick               | not held                  | Tighter, hookier Vulfpeck — "Dean Town"; a pocket clinic.                 |
| 19  | I Wrote a Simple Song                | Billy Preston          | 1971             | AllMusic 4.5★; owner pick     | not held                  | The keyboardist's A&M funk-gospel breakout — "Outa-Space."                |
| 20  | Good Things                          | Aloe Blacc             | 2010             | neo-soul; owner pick          | not held                  | Stones Throw retro-soul — "I Need a Dollar"; modern deep-soul revival.    |
| 21  | Scary Goldings                       | Scary Goldings         | 2018             | modern-funk cult; owner pick  | not held                  | Larry Goldings + Vulf-orbit organ-funk instrumentals; Vulfpeck-adjacent.  |

### Blues

_30 albums / **14 held at SFPL on CD** (7 as the album itself, 7 via a rip-able artist compilation
standing in for the pre-CD catalog). **No Track 3b overlap** — the buildout carried no blues. Spans
Delta/Chicago, hill-country/juke, blues-rock, and modern blues; The Record Company is an existing
owner favorite, included regardless. Several "not held" rows note that other titles by the same
artist (Buddy Guy, R.L. Burnside, Gary Clark Jr., Joe Bonamassa) are on the shelf — LINK+/ILL
fallbacks. Ranked by album acclaim (Acclaimed Music / AllMusic / RS500)._

| #   | Album                                                 | Artist                      | Year        | Acclaim                                      | SFPL CD                      | Why                                                                                              |
| --- | ----------------------------------------------------- | --------------------------- | ----------- | -------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------ |
| 1   | King of the Delta Blues Singers / Complete Recordings | Robert Johnson              | 1961 / 1990 | RS500; AllMusic 5★; foundational             | CD (comp) `CD BLUES JOHN`    | The Delta wellspring; every later blues traces back here.                                        |
| 2   | Muddy Waters at Newport 1960                          | Muddy Waters                | 1960        | AllMusic 5★; canonical live                  | CD `CD BLUES MUDD`           | The definitive live document of electric Chicago blues — "Got My Mojo Working."                  |
| 3   | Howlin' Wolf ("the rockin' chair album")              | Howlin' Wolf                | 1962        | AllMusic 5★; Acclaimed Music                 | CD (comp) `CD BLUES HOWL`    | Wolf + Willie Dixon songbook — "Spoonful," "Wang Dang Doodle."                                   |
| 4   | Live at the Regal                                     | B.B. King                   | 1965        | AllMusic 5★; canonical                       | CD `CD BLUES KING`           | Widely called the greatest live blues album; B.B. at his peak.                                   |
| 5   | Folk Singer                                           | Muddy Waters                | 1964        | AllMusic 5★; audiophile canon                | not held (comp on CD)        | Muddy unplugged with young Buddy Guy; intimate acoustic landmark.                                |
| 6   | The Ultimate Collection / boogie comp                 | John Lee Hooker             | 1948–62     | AllMusic 5★; foundational                    | CD (comp) `CD BLUES HOOK`    | The hypnotic one-chord Detroit boogie.                                                           |
| 7   | Texas Flood                                           | Stevie Ray Vaughan          | 1983        | RS500; AllMusic 5★                           | CD `CD ROCK VAUG`            | The record that reignited electric blues-rock; SRV's debut firestorm.                            |
| 8   | The Best of Little Walter                             | Little Walter               | 1958        | AllMusic 5★; canonical                       | not held                     | The amplified-harmonica canon; template for every blues harp player since.                       |
| 9   | Born Under a Bad Sign                                 | Albert King                 | 1967        | AllMusic 5★; RS500-adjacent                  | CD (comp) `CD BLUES KING`    | Stax rhythm section + string-bending guitar Clapton/SRV lifted wholesale.                        |
| 10  | Damn Right, I've Got the Blues                        | Buddy Guy                   | 1991        | Grammy; AllMusic 4.5★                        | not held (later Guy on CD)   | The comeback that made Guy an elder statesman.                                                   |
| 11  | Blues Breakers with Eric Clapton ("Beano")            | John Mayall's Bluesbreakers | 1966        | AllMusic 5★; RS500                           | not held                     | The British-blues Rosetta Stone; Clapton's Les Paul + Marshall tone born here.                   |
| 12  | At Last!                                              | Etta James                  | 1960        | AllMusic 5★; Grammy Hall of Fame             | CD `CD BLUES JAME`           | Blues/R&B crossover cornerstone; the title track is standard repertoire.                         |
| 13  | The Sky Is Crying: The History of Elmore James        | Elmore James                | 1959–63     | AllMusic 5★; slide canon                     | CD (comp) `CD BLUES JAME`    | The slide-guitar bloodline — "Dust My Broom."                                                    |
| 14  | Father of the Delta Blues: Complete 1965 Sessions     | Son House                   | 1965        | AllMusic 5★; Delta primary source            | CD `CD BLUES HOUS`           | Raw, preacher-intense country blues from a first-generation Delta master.                        |
| 15  | The Paul Butterfield Blues Band                       | Paul Butterfield Blues Band | 1965        | AllMusic 5★; RS500                           | CD `CD BLUES PAUL`           | Integrated Chicago band that bridged blues to the rock audience.                                 |
| 16  | The Complete Imperial Recordings / comp               | T-Bone Walker               | 1950–54     | AllMusic 5★; origin of electric blues guitar | not held                     | The man who plugged the blues in; the vocabulary B.B. and Chuck Berry inherited.                 |
| 17  | The Anthology / Complete Plantation Recordings        | Muddy Waters                | 1941–72     | AllMusic 5★; canonical                       | CD (comp) `CD BLUES MUDD`    | The full arc from Library-of-Congress field cuts to Chess electric.                              |
| 18  | Mojo Hand                                             | Lightnin' Hopkins           | 1960        | AllMusic; Texas country-blues canon          | CD `CD BLUES HOPK`           | Loose, spontaneous Texas country blues; a giant of the idiom.                                    |
| 19  | Hoodoo Man Blues                                      | Junior Wells                | 1965        | AllMusic 5★; Chicago canon                   | not held (Wells comps on CD) | Landmark working-band Chicago blues with Buddy Guy on guitar.                                    |
| 20  | Getting Ready / Texas guitar comp                     | Freddie King                | 1961–71     | AllMusic 5★; "Three Kings"                   | CD (comp) `CD BLUES KING`    | Instrumental-driven Texas blues guitar — "Hide Away."                                            |
| 21  | The Cobra Recordings / Right Place, Wrong Time        | Otis Rush                   | 1956–71     | AllMusic 5★; West Side Chicago               | not held                     | Minor-key, string-bending "West Side" sound; a guitarist's guitarist.                            |
| 22  | Strong Persuader                                      | Robert Cray                 | 1986        | Grammy; AllMusic 4.5★                        | not held                     | The album that carried polished modern blues onto mainstream radio.                              |
| 23  | A Ass Pocket of Whiskey                               | R.L. Burnside               | 1996        | AllMusic 4★; hill-country landmark           | not held (Burnside on CD)    | North-Mississippi juke-joint grit with Jon Spencer; the Fat Possum sound.                        |
| 24  | All Night Long                                        | Junior Kimbrough            | 1992        | AllMusic 4.5★; hill-country foundational     | not held                     | Droning, trance-like Holly Springs juke blues; the other Fat Possum pillar.                      |
| 25  | Couldn't Stand the Weather                            | Stevie Ray Vaughan          | 1984        | AllMusic 4.5★; RS-listed                     | not held                     | SRV's fully realized follow-up — "Voodoo Chile."                                                 |
| 26  | Then Play On                                          | Fleetwood Mac               | 1969        | AllMusic 5★; Peter Green era                 | not held                     | Peter Green's blues-to-art-rock peak; "Oh Well."                                                 |
| 27  | Give It Back to You                                   | The Record Company          | 2016        | Grammy-nominated (Contemp. Blues)            | not held                     | **Owner favorite.** Stripped-down slide-and-groove blues-rock; the breakout. Acquire regardless. |
| 28  | Blak and Blu                                          | Gary Clark Jr.              | 2012        | Grammy; AllMusic 4★                          | not held (Clark on CD)       | The modern face of blues-rock — fuzz, soul, hip-hop.                                             |
| 29  | Shake Hands with Shorty                               | North Mississippi Allstars  | 2000        | Grammy-nominated; AllMusic 4.5★              | not held (later NMA on CD)   | Hill-country repertoire revved into jam-blues.                                                   |
| 30  | Blues Deluxe                                          | Joe Bonamassa               | 2003        | AllMusic 4★; modern-blues flagship           | not held (Vol. 2 on CD)      | The commercial standard-bearer of 21st-century blues-rock.                                       |

### Vocal & Traditional Jazz

_28 albums / **15 held at SFPL on CD** (4 as the album itself, 11 via a comp/alternate edition). The
vocal/trad complement to Track 3b's modern-instrumental Jazz bucket. Deduped vs Track 3b Jazz
(**Lady in Satin and Ella and Louis dropped** — both live there) and absorbs the two Sinatra
big-band vocal sets that also appeared on the swing list. `CD (comp)` = the album itself isn't on
the shelf but a compilation/strong same-artist substitute is (SFPL's jazz-reissue cataloging is
inconsistent — treat comp as "close-enough on the shelf"). Ranked by canonical acclaim (Penguin Jazz
Guide / AllMusic / Acclaimed Music)._

| #   | Album                                     | Artist                    | Year      | Acclaim                        | SFPL CD                  | Why                                                                                     |
| --- | ----------------------------------------- | ------------------------- | --------- | ------------------------------ | ------------------------ | --------------------------------------------------------------------------------------- |
| 1   | The Hot Fives & Sevens                    | Louis Armstrong           | 1925–28   | Penguin crown; AllMusic 5★     | not held                 | The birth of the jazz solo and of swing phrasing; foundational.                         |
| 2   | In the Wee Small Hours                    | Frank Sinatra             | 1955      | AllMusic 5★; Acclaimed Music   | not held                 | The first true concept album — a 3 a.m. song cycle; Sinatra/Riddle at their peak.       |
| 3   | Sings the Cole Porter Song Book           | Ella Fitzgerald           | 1956      | Penguin core; AllMusic 5★      | CD (comp) `CD JAZZ FITZ` | Launched the Songbook series and the Great American Songbook canon.                     |
| 4   | Songs for Swingin' Lovers!                | Frank Sinatra             | 1956      | AllMusic 5★; Acclaimed Music   | not held                 | The up-tempo Sinatra/Riddle template — "I've Got You Under My Skin." (Also fits swing.) |
| 5   | Sarah Vaughan (w/ Clifford Brown)         | Sarah Vaughan             | 1954      | AllMusic 5★; Penguin core      | CD (comp) `CD JAZZ VAUG` | Vaughan's warmest small-group date, Clifford Brown on trumpet.                          |
| 6   | Chet Baker Sings                          | Chet Baker                | 1954      | Acclaimed Music; benchmark     | CD `CD JAZZ BAKE`        | The fragile, androgynous cool-vocal touchstone — "My Funny Valentine."                  |
| 7   | Love Is the Thing                         | Nat King Cole             | 1957      | #1 LP; AllMusic 4.5★           | CD (comp) `CD JAZZ COLE` | Cole's lush Gordon Jenkins ballad set; his only #1 album.                               |
| 8   | Little Girl Blue                          | Nina Simone               | 1959      | AllMusic 4.5★; debut classic   | CD `CD JAZZ SIMO`        | Her debut — jazz, classical, blues fused; "My Baby Just Cares for Me."                  |
| 9   | Sings the George & Ira Gershwin Song Book | Ella Fitzgerald           | 1959      | Grammy Hall of Fame            | not held                 | The Nelson Riddle summit of the Songbook project; the deepest of the set.               |
| 10  | Birth of the Hot (Red Hot Peppers)        | Jelly Roll Morton         | 1926–27   | Penguin core; canonical        | not held                 | The first great jazz composer-arranger; orchestrated New Orleans jazz.                  |
| 11  | The Quintessential Billie Holiday         | Billie Holiday            | 1930s–40s | Penguin core; canonical        | CD (comp) `CD JAZZ HOLI` | Her peak Columbia small-group sides with Lester Young.                                  |
| 12  | Plays W.C. Handy                          | Louis Armstrong           | 1954      | AllMusic 5★; canonical         | not held                 | The finest Armstrong All-Stars album; trad repertoire reinvented — "St. Louis Blues."   |
| 13  | John Coltrane and Johnny Hartman          | Coltrane / Johnny Hartman | 1963      | AllMusic 5★; Penguin core      | CD (comp) `CD JAZZ HART` | The great baritone-and-tenor ballad album; Hartman's only Coltrane date.                |
| 14  | Sinatra at the Sands                      | Frank Sinatra             | 1966      | canonical live; w/ Basie       | not held                 | Sinatra fronting the Basie band, Quincy Jones conducting. (Also fits swing.)            |
| 15  | Wild Is the Wind                          | Nina Simone               | 1966      | AllMusic 4.5★                  | CD (comp) `CD JAZZ SIMO` | Simone's most emotionally raw Philips set — "Four Women."                               |
| 16  | After Midnight                            | Nat King Cole             | 1957      | AllMusic 4.5★                  | not held                 | Cole back at the piano leading a swinging small combo; his jazziest vocal album.        |
| 17  | The Tony Bennett/Bill Evans Album         | Tony Bennett & Bill Evans | 1975      | AllMusic 5★                    | CD `CD JAZZ BENN`        | Voice-and-piano duets of rare intimacy.                                                 |
| 18  | Anita Sings the Most                      | Anita O'Day               | 1957      | AllMusic 4.5★; Penguin         | CD (comp) `CD JAZZ ODAY` | O'Day's rhythmic daring with the Oscar Peterson trio.                                   |
| 19  | Sassy Swings the Tivoli                   | Sarah Vaughan             | 1963      | Penguin crown                  | not held                 | The best live document of Vaughan's instrument-like control and swing.                  |
| 20  | Carmen Sings Monk                         | Carmen McRae              | 1988      | AllMusic 4.5★                  | not held                 | McRae setting lyrics to Monk's tunes — a late-career triumph of phrasing.               |
| 21  | Dinah Jams                                | Dinah Washington          | 1954      | AllMusic 4.5★; Penguin         | CD `CD JAZZ WASH`        | Washington jamming live with Clifford Brown and Max Roach; blues-drenched.              |
| 22  | Abbey Is Blue                             | Abbey Lincoln             | 1959      | Penguin core                   | not held                 | Lincoln's breakthrough — dramatic, politically charged vocal jazz.                      |
| 23  | The Audience with Betty Carter            | Betty Carter              | 1979      | Penguin crown                  | not held                 | The most adventurous vocalist of her generation, live; radical phrasing freedom.        |
| 24  | Blue Light 'Til Dawn                      | Cassandra Wilson          | 1993      | AllMusic 4.5★; modern landmark | not held                 | Reinvented vocal jazz for the '90s — earthy, blues-and-folk-rooted, atmospheric.        |
| 25  | For One to Love                           | Cécile McLorin Salvant    | 2015      | Grammy Best Jazz Vocal         | CD (comp) `CD JAZZ SALV` | The leading vocalist of the current generation; storytelling and dynamic range.         |
| 26  | Liquid Spirit                             | Gregory Porter            | 2013      | Grammy Best Jazz Vocal         | CD (comp) `CD JAZZ PORT` | Warm gospel-soul-jazz baritone; the modern crossover vocal hit.                         |
| 27  | When I Look in Your Eyes                  | Diana Krall               | 1999      | Grammy; AllMusic 4.5★          | CD (comp) `CD JAZZ KRAL` | The polished piano-and-voice standards album that made Krall a star.                    |
| 28  | My Favorite Things                        | Joey Alexander            | 2015      | 2× Grammy nom; prodigy debut   | CD (comp) `CD JAZZ ALEX` | Modern-trad piano prodigy (in the owner's likes); swinging, standards-forward.          |

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

## Track 1b — Genre expansion (rip-worthy picks beyond the franchises)

**~251 films across 9 genre buckets**, deduped against the 154-film base (the 104 tracked franchise
films + the 50 Augmented picks above). Franchise films and the Augmented-50 are excluded outright;
where a film fit two genres it is listed **once**, in its best-fit bucket (e.g. _Fargo_ → Crime,
_Amélie_ → World Cinema, _Crouching Tiger_ → Epics, the golden-age screwballs → Rom-Com). Ranked
within each bucket by **Rotten Tomatoes** (critics % primary, audience % tiebreak) with
Criterion/AFI/canon weight breaking near-ties. Every title is **Blu-ray at SFPL unless flagged
DVD-only** — no 4K UHD exists there (buy the disc if an HDR master matters). RT figures are
point-in-time public scores (2026-07) and drift a point or two.

### Comedy

_Ranked by RT (crit/aud), canon-weighted; SFPL Blu-ray preferred, no 4K UHD; six franchises
excluded._

| #   | Title                           | Year | RT (crit/aud) | SFPL format | Why                                                            |
| --- | ------------------------------- | ---- | ------------- | ----------- | -------------------------------------------------------------- |
| 1   | His Girl Friday                 | 1940 | 99% (91%)     | BR          | Fastest-talking screwball ever; overlapping-dialogue benchmark |
| 2   | Modern Times                    | 1936 | 98% (95%)     | BR          | Chaplin vs. the machine age; silent-era comic peak             |
| 3   | Airplane!                       | 1980 | 97% (89%)     | BR          | The gag-per-second spoof that defined the form                 |
| 4   | Monty Python and the Holy Grail | 1975 | 97% (95%)     | BR          | Most-quoted absurdist comedy in the language                   |
| 5   | Sideways                        | 2004 | 97% (85%)     | BR          | Wine-country midlife comedy with real ache                     |
| 6   | Life of Brian                   | 1979 | 96% (92%)     | BR          | Python's sharpest satire; endlessly quotable                   |
| 7   | What We Do in the Shadows       | 2014 | 96% (86%)     | BR          | Vampire-flatmate mockumentary, instant cult                    |
| 8   | The Death of Stalin             | 2017 | 96% (79%)     | DVD-only    | Pitch-black politburo farce                                    |
| 9   | Booksmart                       | 2019 | 96% (78%)     | BR          | Whip-smart one-crazy-night teen comedy                         |
| 10  | This Is Spinal Tap              | 1984 | 95% (86%)     | BR          | The mockumentary that goes to eleven                           |
| 11  | Being There                     | 1979 | 95% (93%)     | BR          | Sellers' quiet-genius satire of media America                  |
| 12  | Best in Show                    | 2000 | 95% (91%)     | BR          | Dog-show ensemble improv at its peak                           |
| 13  | Ghostbusters                    | 1984 | 95% (88%)     | BR          | Effects-comedy landmark; wall-to-wall quotable                 |
| 14  | Young Frankenstein              | 1974 | 94% (95%)     | DVD-only    | Brooks' loving Universal-horror parody, flawless               |
| 15  | The Apartment                   | 1960 | 94% (94%)     | BR          | Best Picture bittersweet office comedy                         |
| 16  | A Fish Called Wanda             | 1988 | 94% (89%)     | BR          | Python-meets-heist farce; Kline won an Oscar                   |
| 17  | Being John Malkovich            | 1999 | 94% (91%)     | BR          | Kaufman's surreal comedy of identity                           |
| 18  | Some Like It Hot                | 1959 | 93% (95%)     | BR          | AFI's #1 comedy; "nobody's perfect"                            |
| 19  | Planes, Trains and Automobiles  | 1987 | 93% (87%)     | BR          | Martin/Candy road comedy with a gut-punch finish               |
| 20  | Bringing Up Baby                | 1938 | 93% (91%)     | BR          | The screwball template; Grant, Hepburn, a leopard              |
| 21  | Dazed and Confused              | 1993 | 92% (89%)     | BR          | Last-day-of-school hangout comedy, endlessly rewatchable       |
| 22  | Waiting for Guffman             | 1996 | 92% (91%)     | BR          | Small-town-theater mockumentary, Guest at his driest           |
| 23  | Shaun of the Dead               | 2004 | 92% (86%)     | BR          | Rom-zom-com that launched the Cornetto trilogy                 |
| 24  | The Grand Budapest Hotel        | 2014 | 92% (86%)     | BR          | Anderson's most propulsive, most decorated caper               |
| 25  | Hot Fuzz                        | 2007 | 91% (89%)     | BR          | Buddy-cop parody with real action chops                        |
| 26  | Raising Arizona                 | 1987 | 91% (85%)     | BR          | Manic baby-heist Coen cartoon                                  |
| 27  | The Producers                   | 1967 | 91% (91%)     | BR          | "Springtime for Hitler" — Brooks' original                     |
| 28  | Little Miss Sunshine            | 2006 | 91% (87%)     | BR          | Dysfunctional-family road trip, VW bus and all                 |
| 29  | Duck Soup                       | 1933 | 90% (93%)     | BR          | The Marx Brothers' anarchic war satire                         |
| 30  | The Great Dictator              | 1940 | 90% (90%)     | BR          | Chaplin's fearless anti-fascist comedy                         |

### Rom-Com

_Ranked by RT (crit/aud), canon-weighted; SFPL Blu-ray preferred, no 4K UHD; franchises excluded.
Streaming-only titles with no confirmable SFPL disc dropped._

| #   | Title                                 | Year | RT (crit/aud) | SFPL format | Why                                                              |
| --- | ------------------------------------- | ---- | ------------- | ----------- | ---------------------------------------------------------------- |
| 1   | The Lady Eve                          | 1941 | 100% (93%)    | BR          | Sturges' con-woman screwball; Stanwyck at her sharpest           |
| 2   | The Philadelphia Story                | 1940 | 100% (89%)    | BR          | Hepburn/Grant/Stewart; comedy-of-remarriage peak                 |
| 3   | The Awful Truth                       | 1937 | 100% (89%)    | BR          | The divorce-and-reconcile template; Grant and Dunne              |
| 4   | Ball of Fire                          | 1941 | 100% (85%)    | DVD-only    | Stanwyck vs. a houseful of professors; Wilder-scripted           |
| 5   | The Shop Around the Corner            | 1940 | 99% (93%)     | BR          | Secret-pen-pals romance; the source for _You've Got Mail_        |
| 6   | City Lights                           | 1931 | 98% (98%)     | BR          | The Tramp and the flower girl; silent romantic apex              |
| 7   | It Happened One Night                 | 1934 | 98% (93%)     | BR          | The road-trip romcom that swept the Oscars, set the mold         |
| 8   | Say Anything…                         | 1989 | 98% (91%)     | DVD-only    | Boombox-over-the-head; the definitive teen-romance gesture       |
| 9   | The Big Sick                          | 2017 | 98% (88%)     | BR          | Real-life culture-clash courtship with a coma at its center      |
| 10  | Broadcast News                        | 1987 | 98% (85%)     | BR          | Newsroom triangle where competence is the aphrodisiac            |
| 11  | Roman Holiday                         | 1953 | 97% (93%)     | BR          | Hepburn's runaway princess; the bittersweet benchmark            |
| 12  | Annie Hall                            | 1977 | 97% (91%)     | BR          | Best Picture-winning romantic comedy blueprint                   |
| 13  | Sense and Sensibility                 | 1995 | 97% (88%)     | DVD-only    | Thompson's Austen; wit and heartbreak in balance                 |
| 14  | Bull Durham                           | 1988 | 97% (82%)     | BR          | Minor-league triangle; smartest sports-romance written           |
| 15  | Ninotchka                             | 1939 | 95% (89%)     | DVD-only    | "Garbo laughs!" — icy commissar thawed by Paris                  |
| 16  | The Palm Beach Story                  | 1942 | 94% (81%)     | BR          | Sturges' marriage-and-money farce at breakneck speed             |
| 17  | Moonstruck                            | 1987 | 93% (89%)     | BR          | Cher's Brooklyn-Italian love story; "Snap out of it!"            |
| 18  | Groundhog Day                         | 1993 | 93% (87%)     | BR          | The time-loop romance that became a life metaphor                |
| 19  | About a Boy                           | 2002 | 93% (85%)     | DVD-only    | Grant's cad grows up; the anti-romcom that's still one           |
| 20  | Enchanted                             | 2007 | 93% (80%)     | DVD-only    | Fairy-tale princess loose in cynical NYC; genre-savvy            |
| 21  | Eternal Sunshine of the Spotless Mind | 2004 | 92% (91%)     | BR          | Kaufman's memory-erasure romance; canon despite the ache         |
| 22  | Silver Linings Playbook               | 2012 | 92% (86%)     | BR          | Two damaged people and a dance contest; Lawrence's Oscar         |
| 23  | Four Weddings and a Funeral           | 1994 | 92% (76%)     | BR          | The British ensemble romcom that made Hugh Grant a star          |
| 24  | When Harry Met Sally…                 | 1989 | 91% (92%)     | BR          | The can-they-be-friends benchmark; "I'll have what she's having" |
| 25  | High Fidelity                         | 2000 | 91% (86%)     | BR          | Record-store top-fives and a man cataloguing his heartbreaks     |
| 26  | Crazy Rich Asians                     | 2018 | 91% (76%)     | BR          | Lavish meet-the-family romance; a studio-romcom landmark         |
| 27  | Trouble in Paradise                   | 1932 | 90% (90%)     | BR          | Jewel-thief lovers and "the Lubitsch touch" in full              |
| 28  | Tootsie                               | 1982 | 90% (86%)     | BR          | Hoffman-in-drag comedy that's secretly a great romance           |
| 29  | Roxanne                               | 1987 | 88% (63%)     | DVD-only    | Steve Martin's Cyrano; small-town charmer with a big nose        |
| 30  | As Good as It Gets                    | 1997 | 85% (86%)     | DVD-only    | Nicholson's misanthrope softened; dual acting-Oscar romance      |
| 31  | (500) Days of Summer                  | 2009 | 85% (84%)     | DVD-only    | The anti-romcom romcom; non-linear expectations vs. reality      |
| 32  | Notting Hill                          | 1999 | 84% (82%)     | BR          | Bookshop-meets-movie-star; peak Richard Curtis                   |

### Classics

_Canonical pre-~1970 Hollywood, canon-weighted (Criterion/AFI/Sight & Sound). Noir/thriller overlaps
ceded to Crime, romcom overlaps to Rom-Com. SFPL Blu-ray; no 4K UHD._

| #   | Title                            | Year | RT (crit/aud) | SFPL format | Why                                                        |
| --- | -------------------------------- | ---- | ------------- | ----------- | ---------------------------------------------------------- |
| 1   | Witness for the Prosecution      | 1957 | 100% (94%)    | BR          | Wilder's twist-ending courtroom masterclass                |
| 2   | Cool Hand Luke                   | 1967 | 100% (93%)    | BR          | "Failure to communicate"; peak Newman                      |
| 3   | The Treasure of the Sierra Madre | 1948 | 100% (93%)    | BR          | Greed parable; "badges" line, AFI canon                    |
| 4   | Anatomy of a Murder              | 1959 | 100% (92%)    | BR          | The template for the modern courtroom procedural           |
| 5   | Rebecca                          | 1940 | 100% (91%)    | BR          | Hitchcock's only Best Picture winner; gothic dread         |
| 6   | The Grapes of Wrath              | 1940 | 100% (91%)    | BR          | Ford/Fonda Depression epic; AFI canon                      |
| 7   | All About Eve                    | 1950 | 99% (94%)     | BR          | Record 14 Oscar noms; "fasten your seatbelts"              |
| 8   | On the Waterfront                | 1954 | 99% (92%)     | BR          | Brando's "coulda been a contender"; Method landmark        |
| 9   | The Wizard of Oz                 | 1939 | 98% (89%)     | BR          | The Technicolor touchstone of American cinema              |
| 10  | King Kong                        | 1933 | 98% (86%)     | BR          | The stop-motion spectacle that invented the blockbuster    |
| 11  | The Best Years of Our Lives      | 1946 | 97% (93%)     | BR          | Post-WWII homecoming drama; Best Picture, deep-focus       |
| 12  | A Streetcar Named Desire         | 1951 | 97% (90%)     | BR          | "STELLA!"; Brando rewrites screen acting                   |
| 13  | Mr. Smith Goes to Washington     | 1939 | 96% (94%)     | BR          | The filibuster classic; Stewart's idealism at full voltage |
| 14  | Paths of Glory                   | 1957 | 96% (94%)     | BR          | Kubrick's WWI anti-war indictment; Douglas incandescent    |
| 15  | High Noon                        | 1952 | 96% (91%)     | BR          | Real-time Western allegory; Cooper alone against the clock |
| 16  | In the Heat of the Night         | 1967 | 96% (91%)     | BR          | "They call me Mister Tibbs"; Best Picture, landmark        |
| 17  | The Manchurian Candidate         | 1962 | 96% (90%)     | BR          | The brainwash-conspiracy thriller that still unnerves      |
| 18  | It's a Wonderful Life            | 1946 | 94% (95%)     | BR          | The American Christmas myth; Stewart's Bailey              |
| 19  | The Searchers                    | 1956 | 94% (89%)     | BR          | Ford/Wayne's dark Western; endlessly cited                 |
| 20  | To Kill a Mockingbird            | 1962 | 93% (93%)     | BR          | Atticus Finch; AFI's #1 movie hero                         |
| 21  | Rebel Without a Cause            | 1955 | 89% (86%)     | BR          | James Dean's defining role; the teen-alienation archetype  |
| 22  | The Graduate                     | 1967 | 87% (89%)     | BR          | "Mrs. Robinson"; the generational-drift touchstone         |

### Crime / Thriller / Prestige Drama

_Ranked by RT (crit/aud), canon-weighted; SFPL Blu-ray preferred, no 4K UHD; franchises excluded.
Foreign-language crime ceded to World Cinema._

| #   | Title                    | Year | RT (crit/aud) | SFPL format | Why                                                              |
| --- | ------------------------ | ---- | ------------- | ----------- | ---------------------------------------------------------------- |
| 1   | 12 Angry Men             | 1957 | 100% (97%)    | BR          | The single-room jury drama; a staging masterclass                |
| 2   | The Maltese Falcon       | 1941 | 100% (89%)    | BR          | Foundational American noir; Bogart's Spade defines the PI        |
| 3   | The Third Man            | 1949 | 99% (93%)     | BR          | Zither, Dutch angles, sewers, Welles — peak postwar noir         |
| 4   | High and Low             | 1963 | 99% (95%)     | BR          | Kurosawa's kidnap procedural; moral vertigo in two acts          |
| 5   | L.A. Confidential        | 1997 | 99% (94%)     | BR          | Ellroy's corrupt-LAPD web, immaculately cast and plotted         |
| 6   | Rear Window              | 1954 | 98% (95%)     | BR          | Voyeurism as suspense engine; a thriller from one window         |
| 7   | Sunset Boulevard         | 1950 | 98% (95%)     | BR          | Hollywood as murder scene, narrated by the corpse                |
| 8   | Strangers on a Train     | 1951 | 98% (89%)     | BR          | The swapped-murders premise, carousel-perfect menace             |
| 9   | North by Northwest       | 1959 | 97% (95%)     | BR          | The wrong-man chase; crop-duster and Rushmore set pieces         |
| 10  | Notorious                | 1946 | 97% (91%)     | BR          | Espionage romance with Hitchcock's tightest suspense             |
| 11  | Double Indemnity         | 1944 | 97% (94%)     | BR          | The noir template: insurance, lust, the perfect murder undone    |
| 12  | Spotlight                | 2015 | 97% (93%)     | BR          | Procedural journalism drama; ensemble at its most disciplined    |
| 13  | Dog Day Afternoon        | 1975 | 96% (93%)     | BR          | A botched heist becomes a sweaty media circus; Pacino peak       |
| 14  | The Conversation         | 1974 | 96% (92%)     | BR          | Surveillance paranoia; Hackman's whisper-quiet tour de force     |
| 15  | The French Connection    | 1971 | 96% (86%)     | BR          | Gritty NYC cop chase; the car pursuit that reset the bar         |
| 16  | The Social Network       | 2010 | 96% (87%)     | BR          | Sorkin/Fincher origin drama; betrayal at 100 words a minute      |
| 17  | Anatomy of a Fall        | 2023 | 96% (88%)     | BR          | Courtroom drama as marriage autopsy; ambiguity to the last frame |
| 18  | Touch of Evil            | 1958 | 95% (90%)     | BR          | Border noir opening on the greatest tracking shot                |
| 19  | Infernal Affairs         | 2002 | 95% (90%)     | BR          | The dueling-moles thriller Scorsese remade as _The Departed_     |
| 20  | The Irishman             | 2019 | 95% (86%)     | BR          | Elegiac mob epic; loyalty and mortality over 3.5 hours           |
| 21  | 12 Years a Slave         | 2013 | 95% (90%)     | BR          | Unflinching slavery drama; Best Picture, reference-grade         |
| 22  | Memento                  | 2000 | 94% (94%)     | BR          | Reverse-chronology revenge puzzle; structure as the point        |
| 23  | Fargo                    | 1996 | 94% (93%)     | BR          | Snowbound crime black comedy; "you betcha" and a wood chipper    |
| 24  | Blue Velvet              | 1986 | 94% (89%)     | BR          | Small-town underbelly noir; Lynch's severed-ear plunge           |
| 25  | The Night of the Hunter  | 1955 | 93% (88%)     | BR          | LOVE/HATE knuckles; a one-of-a-kind nightmare fairy-tale         |
| 26  | There Will Be Blood      | 2007 | 91% (86%)     | BR          | Oil, greed, and God; Day-Lewis as capitalism incarnate           |
| 27  | Raging Bull              | 1980 | 92% (93%)     | BR          | Boxing as self-destruction; De Niro and B&W fury                 |
| 28  | Network                  | 1976 | 92% (91%)     | BR          | "Mad as hell" media satire that predicted everything             |
| 29  | The Departed             | 2006 | 90% (94%)     | BR          | Dueling-rats Boston crime drama; Scorsese's Best Picture         |
| 30  | Reservoir Dogs           | 1992 | 90% (93%)     | BR          | Heist-gone-wrong in one warehouse; the debut that lit the fuse   |
| 31  | Heat                     | 1995 | 88% (94%)     | BR          | Cop-vs-thief epic; the diner scene and the LA shootout           |
| 32  | Se7en                    | 1995 | 82% (95%)     | BR          | Seven-deadly-sins serial-killer noir; "What's in the box?"       |
| 33  | The Usual Suspects       | 1995 | 88% (95%)     | BR          | Con-man mystery built entirely around its final reveal           |
| 34  | The Shawshank Redemption | 1994 | 89% (98%)     | BR          | The prison-hope drama; IMDb's perennial #1                       |
| 35  | Zodiac                   | 2007 | 90% (76%)     | BR          | Obsessive unsolved-case procedural; Fincher's coldest, best      |

### Action / Adventure / Sci-Fi / Fantasy

_Ranked by RT (crit/aud); "demo disc" = reference A/V. SFPL Blu-ray preferred, no 4K UHD; franchises
excluded._

| #   | Title                              | Year | RT (crit/aud) | SFPL format | Why                                                        |
| --- | ---------------------------------- | ---- | ------------- | ----------- | ---------------------------------------------------------- |
| 1   | The Terminator                     | 1984 | 100% (90%)    | BR          | Lean, relentless sci-fi chase that launched a franchise    |
| 2   | Mad Max 2: The Road Warrior        | 1981 | 100% (89%)    | BR          | Genre-defining vehicular action; post-apocalypse blueprint |
| 3   | Aliens                             | 1986 | 98% (94%)     | BR          | Peak sci-fi action; "get away from her you bitch"          |
| 4   | Godzilla Minus One                 | 2023 | 98% (98%)     | BR          | Oscar-winning VFX on a shoestring; demo disc               |
| 5   | Brazil                             | 1985 | 98% (89%)     | BR          | Dystopian retro-future masterpiece                         |
| 6   | E.T. the Extra-Terrestrial         | 1982 | 98% (72%)     | BR          | Definitive Spielberg wonder; timeless                      |
| 7   | Mission: Impossible – Fallout      | 2018 | 97% (88%)     | BR          | Best-in-class practical stunt spectacle; demo disc         |
| 8   | The Princess Bride                 | 1987 | 97% (94%)     | BR          | Perfect fantasy-adventure comfort watch                    |
| 9   | Top Gun: Maverick                  | 2022 | 96% (99%)     | BR          | Real-jet IMAX thrill ride; reference demo disc             |
| 10  | Gravity                            | 2013 | 96% (78%)     | BR          | Immersive orbital survival; demo disc                      |
| 11  | Apollo 13                          | 1995 | 96% (87%)     | BR          | Gripping real-stakes space procedural                      |
| 12  | The Fugitive                       | 1993 | 96% (88%)     | BR          | Immaculate chase thriller                                  |
| 13  | Speed                              | 1994 | 95% (85%)     | BR          | Airtight high-concept action                               |
| 14  | The Dark Knight                    | 2008 | 94% (94%)     | BR          | Genre-transcending; IMAX demo disc (non-MCU)               |
| 15  | Arrival                            | 2016 | 94% (82%)     | BR          | Cerebral first-contact sci-fi                              |
| 16  | Close Encounters of the Third Kind | 1977 | 94% (83%)     | BR          | Awe-driven UFO classic                                     |
| 17  | Mission: Impossible – Rogue Nation | 2015 | 94% (89%)     | BR          | Opera + plane stunt; demo disc                             |
| 18  | Logan                              | 2017 | 94% (90%)     | BR          | Grounded, brutal comic-book western (non-MCU)              |
| 19  | Looper                             | 2012 | 93% (83%)     | BR          | Smart time-loop thriller                                   |
| 20  | Terminator 2: Judgment Day         | 1991 | 91% (94%)     | BR          | Sci-fi action / VFX landmark; demo disc                    |
| 21  | RoboCop                            | 1987 | 92% (86%)     | BR          | Satirical ultraviolent sci-fi                              |
| 22  | Ex Machina                         | 2014 | 92% (86%)     | BR          | Sleek AI chamber piece; demo disc                          |
| 23  | The Bourne Ultimatum               | 2007 | 92% (91%)     | BR          | Kinetic spy-action high point                              |
| 24  | Blade Runner                       | 1982 | 89% (91%)     | BR          | Definitive cyberpunk; demo disc                            |
| 25  | District 9                         | 2009 | 91% (81%)     | BR          | Gritty allegorical sci-fi                                  |
| 26  | The Martian                        | 2015 | 91% (91%)     | BR          | Crowd-pleasing space survival; demo disc                   |
| 27  | Predator                           | 1987 | 90% (83%)     | BR          | Muscular jungle sci-fi action                              |
| 28  | Minority Report                    | 2002 | 90% (80%)     | BR          | Stylish pre-crime sci-fi                                   |
| 29  | Inception                          | 2010 | 87% (91%)     | BR          | Blockbuster dream-heist; demo disc                         |
| 30  | John Wick                          | 2014 | 86% (81%)     | BR          | Gun-fu action renaissance; demo disc                       |
| 31  | Dune                               | 2021 | 83% (90%)     | BR          | Monumental scale; reference demo disc (Part One)           |
| 32  | Interstellar                       | 2014 | 73% (86%)     | BR          | IMAX space spectacle; reference demo disc                  |

### Epics

_Grand-scale historical / war / spectacle. Ranked by RT (crit/aud); prefer extended/director's cuts
where noted. SFPL Blu-ray preferred, no 4K UHD; franchises excluded._

| #   | Title                          | Year | RT (crit/aud) | SFPL format | Why                                                                  |
| --- | ------------------------------ | ---- | ------------- | ----------- | -------------------------------------------------------------------- |
| 1   | War and Peace                  | 1966 | 100% (93%)    | BR          | Largest-scale battle spectacle ever filmed; Criterion restoration    |
| 2   | The Battle of Algiers          | 1966 | 99% (95%)     | BR          | Documentary-real insurgency epic; still on military syllabi          |
| 3   | Das Boot                       | 1981 | 98% (91%)     | BR          | Claustrophobic U-boat epic; director's-cut sound is a demo showpiece |
| 4   | Crouching Tiger, Hidden Dragon | 2000 | 97% (86%)     | BR          | Wuxia epic that broke through worldwide; gorgeous scope              |
| 5   | The Bridge on the River Kwai   | 1957 | 96% (95%)     | BR          | Best Picture; the WWII POW epic, immaculate restoration              |
| 6   | Andrei Rublev                  | 1966 | 96% (94%)     | BR          | Medieval-Russia spiritual epic; Criterion                            |
| 7   | The Last of the Mohicans       | 1992 | 96% (90%)     | BR          | Frontier war-romance; the finale + score are pure spectacle          |
| 8   | 13 Assassins                   | 2010 | 96% (85%)     | BR          | Samurai epic building to a 45-minute battle; A/V showpiece           |
| 9   | Once Upon a Time in the West   | 1968 | 95% (97%)     | BR          | The operatic Western; every frame a painting, Morricone peak         |
| 10  | The Deer Hunter                | 1978 | 94% (94%)     | BR          | Best Picture; Vietnam epic of scale and intimacy                     |
| 11  | Saving Private Ryan            | 1998 | 94% (95%)     | BR          | Omaha Beach = the reference war set-piece; demo audio                |
| 12  | Hero                           | 2002 | 94% (89%)     | BR          | Color-coded wuxia epic; one of the great-looking discs               |
| 13  | Glory                          | 1989 | 93% (93%)     | BR          | The 54th Massachusetts; Civil War epic with a perfect ending         |
| 14  | The Great Escape               | 1963 | 93% (94%)     | BR          | The ensemble WWII escape epic; endlessly rewatchable                 |
| 15  | Spartacus                      | 1960 | 93% (91%)     | BR          | The sword-and-sandal benchmark; restored to demo quality             |
| 16  | The Ten Commandments           | 1956 | 93% (89%)     | BR          | The definition of Hollywood biblical spectacle; VistaVision          |
| 17  | Barry Lyndon                   | 1975 | 93% (90%)     | BR          | Candlelit 18th-century epic; the ultimate cinematography demo        |
| 18  | Dunkirk                        | 2017 | 92% (81%)     | BR          | IMAX survival epic; a top-tier home-theater A/V test                 |
| 19  | Red Cliff                      | 2008 | 91% (88%)     | BR          | Three Kingdoms war epic; get the full international cut              |
| 20  | Full Metal Jacket              | 1987 | 91% (94%)     | BR          | Two-act Vietnam epic; the boot-camp half is untouchable              |
| 21  | Letters from Iwo Jima          | 2006 | 91% (89%)     | BR          | The war seen from the other side; near-monochrome epic               |
| 22  | Downfall                       | 2004 | 91% (93%)     | BR          | Hitler's last days; claustrophobic historical epic                   |
| 23  | Gone with the Wind             | 1939 | 90% (91%)     | BR          | The Civil War melodrama epic; Technicolor restoration                |
| 24  | Lincoln                        | 2012 | 90% (82%)     | BR          | Political epic; Day-Lewis + a beautifully lit period disc            |
| 25  | Gandhi                         | 1982 | 89% (92%)     | BR          | Best Picture; cradle-to-grave biographical epic, massive crowds      |
| 26  | 1917                           | 2019 | 89% (88%)     | BR          | One-shot WWII epic; a premier surround + image demo disc             |
| 27  | Amadeus                        | 1984 | 89% (93%)     | BR          | Best Picture; lavish period epic of genius and envy                  |
| 28  | The Last Emperor               | 1987 | 89% (86%)     | BR          | Best Picture; Forbidden City on an overwhelming scale                |
| 29  | Kagemusha                      | 1980 | 88% (89%)     | BR          | Feudal-Japan color epic; Criterion, a visual feast                   |
| 30  | Platoon                        | 1986 | 88% (91%)     | BR          | Best Picture; the grunt's-eye Vietnam epic                           |
| 31  | Ben-Hur                        | 1959 | 86% (91%)     | BR          | 11 Oscars; the chariot race is still a spectacle benchmark           |
| 32  | Gladiator                      | 2000 | 80% (87%)     | BR          | Best Picture; the modern sword-and-sandal revival, demo A/V          |

### Animation & Family

_Non-Pixar (Pixar tracked separately). Ranked by RT (crit/aud). SFPL Blu-ray preferred, no 4K UHD._

| #   | Title                                      | Year | RT (crit/aud) | SFPL format | Why                                                          |
| --- | ------------------------------------------ | ---- | ------------- | ----------- | ------------------------------------------------------------ |
| 1   | Grave of the Fireflies                     | 1988 | 100% (96%)    | BR          | The definitive anti-war film; Ghibli's most devastating work |
| 2   | The Tale of the Princess Kaguya            | 2013 | 100% (88%)    | BR          | Watercolor-line masterpiece, Takahata's final film           |
| 3   | How to Train Your Dragon                   | 2010 | 99% (91%)     | BR          | DreamWorks' peak; flight sequences + Powell score            |
| 4   | Wolfwalkers                                | 2020 | 99% (91%)     | BR          | Cartoon Saloon's hand-drawn Irish folklore triumph           |
| 5   | Song of the Sea                            | 2014 | 99% (87%)     | BR          | Selkie myth rendered in gorgeous 2D                          |
| 6   | Your Name                                  | 2016 | 98% (94%)     | BR          | Body-swap romance, luminous frames, global phenomenon        |
| 7   | Kubo and the Two Strings                   | 2016 | 97% (87%)     | BR          | Laika stop-motion at its most ambitious                      |
| 8   | Ernest & Celestine                         | 2012 | 97% (87%)     | BR (French) | Watercolor charm; a perfect small film                       |
| 9   | The Iron Giant                             | 1999 | 96% (91%)     | BR          | Brad Bird's beloved Cold War fable                           |
| 10  | Persepolis                                 | 2007 | 96% (89%)     | BR (French) | B&W graphic-novel memoir of the Iranian Revolution           |
| 11  | Spider-Man: Across the Spider-Verse        | 2023 | 95% (94%)     | BR          | Even bolder sequel; multi-style animation showcase           |
| 12  | The Nightmare Before Christmas             | 1993 | 95% (91%)     | BR          | Stop-motion holiday perennial; Elfman songs                  |
| 13  | Aladdin                                    | 1992 | 95% (90%)     | BR          | Disney Renaissance peak; Williams as Genie                   |
| 14  | Wallace & Gromit: Curse of the Were-Rabbit | 2005 | 95% (87%)     | BR          | Aardman claymation feature; Oscar winner                     |
| 15  | My Neighbor Totoro                         | 1988 | 94% (93%)     | BR          | Gentle Ghibli touchstone; the studio's mascot                |
| 16  | Beauty and the Beast                       | 1991 | 94% (92%)     | BR          | First animated Best Picture nominee                          |
| 17  | Princess Mononoke                          | 1997 | 93% (93%)     | BR          | Epic eco-fable; Miyazaki's grandest canvas                   |
| 18  | The Lion King                              | 1994 | 93% (93%)     | BR          | Disney's highest-grossing hand-drawn film                    |
| 19  | Fantastic Mr. Fox                          | 2009 | 93% (87%)     | BR          | Anderson's stop-motion Roald Dahl gem                        |
| 20  | Isle of Dogs                               | 2018 | 90% (87%)     | BR          | Meticulous stop-motion; deadpan dystopia                     |
| 21  | Coraline                                   | 2009 | 90% (74%)     | BR          | Laika's debut; genuinely eerie for kids                      |
| 22  | The Wind Rises                             | 2013 | 89% (82%)     | BR          | Miyazaki's elegiac aviation biopic                           |
| 23  | Shrek                                      | 2001 | 88% (90%)     | BR          | Genre-defining CG comedy; first Animated Oscar               |
| 24  | ParaNorman                                 | 2012 | 88% (74%)     | BR          | Laika zombie-comedy with real heart                          |
| 25  | Howl's Moving Castle                       | 2004 | 87% (91%)     | BR          | Sumptuous steampunk fantasy                                  |
| 26  | The Prince of Egypt                        | 1998 | 80% (84%)     | BR          | DreamWorks' grand animated epic; "When You Believe"          |

### Horror

_Ranked by RT (crit/aud). SFPL Blu-ray preferred, no 4K UHD; franchises excluded._

| #   | Title                        | Year | RT (crit/aud) | SFPL format | Why                                                      |
| --- | ---------------------------- | ---- | ------------- | ----------- | -------------------------------------------------------- |
| 1   | Let the Right One In         | 2008 | 98% (86%)     | BR          | Snowbound Swedish vampire romance; genre high-water mark |
| 2   | The Babadook                 | 2014 | 98% (72%)     | BR          | Grief-as-monster; the modern arthouse-horror template    |
| 3   | Nosferatu                    | 1922 | 97% (87%)     | BR          | Foundational silent vampire film; public-domain icon     |
| 4   | Halloween                    | 1978 | 96% (89%)     | DVD-only    | Defined the slasher; Carpenter's synth score             |
| 5   | Rosemary's Baby              | 1968 | 96% (87%)     | BR          | Slow-burn satanic paranoia; Criterion                    |
| 6   | Night of the Living Dead     | 1968 | 96% (87%)     | BR          | Birth of the modern zombie; public domain                |
| 7   | A Quiet Place                | 2018 | 96% (82%)     | BR          | Sound-design horror; taut, inventive                     |
| 8   | It Follows                   | 2014 | 95% (66%)     | DVD-only    | Dread-logic premise; retro synth atmosphere              |
| 9   | A Nightmare on Elm Street    | 1984 | 94% (78%)     | BR          | Dream-slasher that launched a franchise                  |
| 10  | Us                           | 2019 | 93% (59%)     | BR          | Peele's ambitious doppelgänger horror                    |
| 11  | The Fly                      | 1986 | 92% (83%)     | BR          | Body-horror apex; Goldblum's tragic transformation       |
| 12  | The Cabin in the Woods       | 2011 | 92% (72%)     | BR          | Meta-horror deconstruction; Whedon-scripted              |
| 13  | Hereditary                   | 2018 | 90% (71%)     | BR          | Aster's grief-and-cult debut; Collette unhinged          |
| 14  | The Witch                    | 2015 | 90% (59%)     | BR          | Puritan folk-horror; meticulous period dread             |
| 15  | The Shining                  | 1980 | 89% (94%)     | BR          | Kubrick's canonical haunted-hotel masterpiece            |
| 16  | Evil Dead II                 | 1987 | 89% (84%)     | BR          | Splatstick perfection; Raimi's kinetic camera            |
| 17  | The Texas Chain Saw Massacre | 1974 | 89% (82%)     | BR          | Raw, relentless; genre-defining                          |
| 18  | 28 Days Later                | 2002 | 87% (85%)     | DVD-only    | Reinvented the fast zombie; digital dread                |
| 19  | The Thing                    | 1982 | 84% (93%)     | BR          | Practical-FX paranoia masterpiece                        |
| 20  | The Exorcist                 | 1973 | 84% (87%)     | DVD-only    | The most influential possession film ever made           |
| 21  | Nope                         | 2022 | 83% (70%)     | BR          | Peele's spectacle-horror; IMAX-scale                     |
| 22  | Midsommar                    | 2019 | 83% (62%)     | BR          | Daylight folk-horror; a bad-breakup nightmare            |

### World Cinema

_Non-English, acclaimed. Orphan SFPL sub-batch merged in and RT-ranked. SFPL Blu-ray preferred, no
4K UHD; no-disc titles dropped._

| #   | Title                      | Year | RT (crit/aud) | SFPL format     | Why                                                  |
| --- | -------------------------- | ---- | ------------- | --------------- | ---------------------------------------------------- |
| 1   | The 400 Blows              | 1959 | 100% (94%)    | BR              | French New Wave cornerstone; Criterion               |
| 2   | Bicycle Thieves            | 1948 | 99% (95%)     | BR              | Italian neorealism's beating heart; Criterion        |
| 3   | Shoplifters                | 2018 | 99% (91%)     | DVD-only        | Palme d'Or; tender chosen-family drama               |
| 4   | Rashomon                   | 1950 | 98% (93%)     | BR              | Coined "the Rashomon effect"; Criterion              |
| 5   | 8½                         | 1963 | 98% (92%)     | BR              | The definitive film-about-filmmaking; Criterion      |
| 6   | Portrait of a Lady on Fire | 2019 | 98% (91%)     | BR              | Painterly queer romance; Criterion                   |
| 7   | Come and See               | 1985 | 97% (96%)     | BR              | The most harrowing war film ever made; Criterion     |
| 8   | Drive My Car               | 2021 | 97% (87%)     | BR              | Murakami adaptation; Best Intl Feature Oscar         |
| 9   | The Handmaiden             | 2016 | 96% (91%)     | BR              | A triple-cross erotic con; ravishing and ruthless    |
| 10  | Roma                       | 2018 | 96% (72%)     | BR (Criterion)  | B&W memory-piece; Best Director Oscar                |
| 11  | Memories of Murder         | 2003 | 95% (94%)     | BR              | Bong's unsolved-serial-killer procedural masterpiece |
| 12  | Burning                    | 2018 | 95% (89%)     | BR              | Slow-burn Murakami mystery; smoldering ambiguity     |
| 13  | The Lives of Others        | 2006 | 93% (96%)     | BR              | Stasi surveillance drama; Best Foreign Oscar         |
| 14  | The Seventh Seal           | 1957 | 93% (94%)     | BR              | Chess with Death; Criterion cornerstone              |
| 15  | Y Tu Mamá También          | 2001 | 92% (89%)     | BR              | Road-trip coming-of-age; Criterion                   |
| 16  | City of God                | 2002 | 91% (97%)     | BR (Portuguese) | Kinetic Rio favela crime epic                        |
| 17  | Amélie                     | 2001 | 90% (95%)     | BR              | Whimsical Montmartre matchmaker chases her own love  |
| 18  | Cinema Paradiso            | 1988 | 90% (93%)     | BR              | Nostalgic love letter to moviegoing; Morricone       |
| 19  | Oldboy                     | 2003 | 82% (94%)     | DVD-only        | Vengeance shocker; the hallway fight                 |
| 20  | Life Is Beautiful          | 1997 | 80% (96%)     | DVD-only        | Holocaust fable; Benigni's Best Actor Oscar          |

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
