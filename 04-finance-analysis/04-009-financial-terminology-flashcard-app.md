---
title: 'Multi-Deck Flashcard App (financial, NATO, latency, acronyms)'
number: '04-009'
category: 'finance-analysis'
difficulty: 'Easy'
time_commitment: '3-5 days'
target_skills: 'React + TypeScript + Vite, Tailwind, React Router, FSRS Spaced Repetition'
status: 'Not Started'
depends_on: []
---

# Multi-Deck Flashcard App

## Description

A web flashcard app using FSRS-4.5 spaced repetition. Originally scoped as a finance-only deck;
re-scoped to a generic multi-deck app so the same engine drives any knowledge bank — financial
terminology, NATO phonetic alphabet, system-design latency numbers, tech acronyms, etc.

Three usage patterns drive the design:

1. **Study one thing** — open a single deck (`/decks/nato`)
2. **Study everything** — review across all decks merged (`/all`)
3. **Study these N things** — save a named **collection** of decks (e.g.
   `interview-prep = [nato, latency, acronyms]`) and review the merged due queue

Local-first; sync backend optional (see Phase 7 — offline always works). Single-deck mini-deploys
via build-time env flag.

## Stack (locked)

- **Build:** Vite + React 19 + TypeScript
- **Routing:** React Router v7
- **Scheduling:** [`ts-fsrs`](https://github.com/open-spaced-repetition/ts-fsrs) (FSRS-4.5 reference
  implementation — do not reimplement)
- **Styling:** Tailwind CSS v4; dark mode via `prefers-color-scheme`
- **State:** `useReducer` (escalate to Zustand only if prop drilling exceeds 3 levels)
- **Animation:** plain CSS 3D transform for the card flip (no Framer Motion)
- **Tests:** Vitest + @testing-library/react
- **Persistence:** `localStorage`
- **Bundled content:** 4 starter decks shipped as JSON in `public/decks/`
- **Deploy (stretch):** GitHub Pages — multi-deck build + NATO-only locked build

## Concepts

- **Card** — atomic unit. Has FSRS state (D/S/R), `term`, `definition`, `category`, `example`,
  globally unique id (prefixed with deck id, e.g. `nato:a`).
- **Deck** — bundled JSON of cards, immutable content. Loaded from `public/decks/<id>.json`.
- **Collection** — user-saved combo of deck ids: `{ id, name, deckIds, createdAt }`. Persisted in
  localStorage. Reviewing a collection merges due queues across its decks.
- **Pseudo-collections** — `all` (every deck) is hard-coded; not stored as a Collection.

## Data shapes

```ts
type AppCard = FSRSCard & {
  id: string; // e.g. "nato:a"
  deckId: string; // e.g. "nato"
  term: string;
  definition: string;
  category: string;
  example?: string;
};

type Deck = {
  id: string;
  name: string;
  description: string;
  cards: AppCard[];
};

type Collection = {
  id: string; // user-supplied slug
  name: string;
  deckIds: string[];
  createdAt: number;
};
```

localStorage layout:

- `flashcards:cards` — `Record<cardId, FSRSCardState>` — per-card scheduling state, the source of
  truth. Survives deck content edits because card ids are stable.
- `flashcards:collections` — `Collection[]` — user-defined collections.
- `flashcards:reviews` — `Array<{ cardId, ratedAt, rating }>` — review history for streak/stats
  (capped at last 1000 entries).

## Routes

- `/` — home: deck list + saved collections, each with due counts and "review" buttons
- `/decks/:id` — single-deck review session
- `/decks/:id/cards` — deck contents browser (read-only list of all cards in the deck)
- `/collections/:id` — custom-collection review session
- `/all` — review across every bundled deck (pseudo-collection)
- `/manage` — create/edit/delete collections; import deck JSON; reset progress

## Build-time lock

`VITE_LOCKED_DECK=<deckId>` produces a focused single-deck build:

- Router redirects `/` → `/decks/<id>`
- Header chrome (collection picker, manage link) is hidden
- `/manage`, `/collections/*`, `/all` return a 404 component
- Same codebase; deploy multiple instances side-by-side (`flashcards.example.com`,
  `nato.example.com`)

## Exit Criteria

- [ ] FSRS algorithm drives all scheduling: stability (S), difficulty (D), and retrievability (R)
      update correctly on each review; intervals decay realistically when cards are reviewed late
- [ ] App ships with 4 bundled decks: financial (≥50 cards), NATO phonetic (26 cards), latency
      numbers for system design (≥20 cards), tech acronyms (≥50 cards)
- [ ] Card flip UI: tapping a card reveals the back with a CSS 3D flip animation
- [ ] Review session flow: display card front → reveal back on demand → rate with Again / Hard /
      Good / Easy buttons → advance to next card in the merged due queue
- [ ] Due queue logic: cards scheduled for today surface first; new cards mixed in when queue is
      empty; overdue cards penalised (shorter next interval) via FSRS retrievability decay; merged
      queue across N decks sorts by retrievability regardless of source deck
- [ ] Routes work: `/`, `/decks/:id`, `/decks/:id/cards`, `/collections/:id`, `/all`, `/manage`
- [ ] Collections: `/manage` lets the user create a named collection from any subset of decks;
      collection appears on home with a due-count badge; reviewing it merges queues across its
      decks; collections persist across browser refresh
- [ ] Per-deck and per-collection stats: streak, due-today count, total cards, mastery-level
      breakdown (New / Learning / Review / Mastered)
- [ ] Build-time lock: setting `VITE_LOCKED_DECK=nato` in `.env` and running `npm run build`
      produces a build whose root path goes straight to that deck's review with no chrome
- [ ] Local storage persistence: card state, collections, and review history survive a full browser
      refresh
- [ ] App runs locally with `npm run dev` and opens in a browser without errors
- [ ] (Stretch) Deployed to GitHub Pages: multi-deck instance + NATO-only locked instance, both
      reachable via public URLs in the README

## Progress

Each phase ships as its own PR against `gjcourt/flashcards`.

### Phase 1 — Types, FSRS scheduling, tests

- [ ] Define `AppCard`, `Deck`, `Collection` types in `src/types.ts`
- [ ] Wrap `ts-fsrs` in `src/fsrs.ts`: pure functions `rate(card, rating, now)` →
      `{ card: AppCard, log: ReviewLog }`; default to `ts-fsrs` weight presets
- [ ] Unit tests via Vitest: verify S/D/R updates for each rating (Again/Hard/Good/Easy), confirm
      retrievability decays when `t > S`, confirm Again resets stability
- [ ] No UI yet — tests-only PR

### Phase 2 — Bundled decks, deck loader, per-card storage

- [ ] Author `public/decks/financial.json` (≥50 cards across equities, accounting, valuation, fixed
      income — see card list below)
- [ ] Author `public/decks/nato.json` (26 cards: A=Alfa, B=Bravo, …, Z=Zulu, with example
      transmission strings)
- [ ] Author `public/decks/latency.json` (≥20 cards: L1 cache 0.5ns, L2 7ns, RAM 100ns, SSD 150μs,
      disk 10ms, US→Europe RTT 150ms, etc. — Jeff Dean numbers)
- [ ] Author `public/decks/acronyms.json` (≥50 cards: API, CRUD, REST, gRPC, K8s, CNI, CSI, etc.)
- [ ] `public/decks/manifest.json` — `{ decks: [{ id, name, description, path }] }` so the app can
      enumerate available bundled decks at boot
- [ ] `src/decks/load.ts` — `fetchDeck(id)` and `fetchAllDecks()` with JSON schema validation; ids
      stable across loads (so FSRS state survives deck content edits)
- [ ] `src/storage.ts` — `loadCardState() / saveCardState()` for `flashcards:cards`,
      `loadCollections() / saveCollections()` for `flashcards:collections`, with `Date`
      replacer/reviver
- [ ] Tests: rate a card, persist, reload, verify state restored

### Phase 3 — Routing, home, single-deck review, card flip

- [ ] Install `react-router-dom@7`
- [ ] `src/router.tsx` — routes per the table above; `<Layout>` with header chrome conditionally
      rendered based on `VITE_LOCKED_DECK`
- [ ] `<Home>` — fetches manifest, lists decks with `<DeckTile>` (name, due count, total cards,
      "review" link)
- [ ] `<DeckReview>` (route `/decks/:id`) — loads deck, runs review session
- [ ] `<DeckCards>` (route `/decks/:id/cards`) — read-only table of all cards in the deck
- [ ] `<CardFlip>` — CSS 3D perspective flip; front shows term + category badge; back shows
      definition + optional example
- [ ] `<ReviewSession>` — renders due queue one card at a time; "Show Answer" button triggers flip;
      rating buttons advance to next card and call `rate()` from `fsrs.ts`
- [ ] `useDueQueue(deckIds: string[])` hook — derives sorted queue across the listed decks; overdue
      cards first (FSRS retrievability), then today's new cards; memoised
- [ ] Deck/card state managed via `useReducer` in a small context; rating dispatches `RATE_CARD`
      which calls `rate()` and persists in the same reducer step

### Phase 4 — Collections, /all, /manage

- [ ] `<CollectionReview>` (route `/collections/:id`) — same `<ReviewSession>`, merged queue across
      `collection.deckIds`
- [ ] `<AllReview>` (route `/all`) — same shape, deck ids = every bundled deck
- [ ] `<Manage>` (route `/manage`) — list collections; create new (name + deck checkboxes); delete;
      "reset all progress" button (clears `flashcards:cards`)
- [ ] Home page: collections section above decks section; "+ New collection" link → /manage
- [ ] Tests: create a collection, review it, verify merged queue includes cards from each deck

### Phase 5 — Stats, polish, dark mode

- [ ] `<StatsPanel>` shown above review session: streak (consecutive days with ≥1 review across
      anything), due-today count for the current scope (deck or collection), total cards in scope,
      mastery-level breakdown (New / Learning / Review / Mastered) computed from FSRS stability
      thresholds
- [ ] Tailwind dark mode via `prefers-color-scheme`; no theme toggle
- [ ] Empty states: "no cards due — come back tomorrow" with next-due timestamp
- [ ] Keyboard shortcuts: space=flip, 1/2/3/4=rate Again/Hard/Good/Easy
- [ ] Write app `README.md`: project description, quickstart, route map, how FSRS works, deck JSON
      format with a worked example so someone can author a new deck

### Phase 6 — Stretch: build-time lock, GH Pages deploy

- [ ] Wire `VITE_LOCKED_DECK` into `<Layout>` and `<Router>`; redirect / → /decks/$LOCKED; gate
      `/manage`, `/collections/*`, `/all`
- [ ] GitHub Pages deploy via `gh-pages` package + GitHub Actions workflow
- [ ] Two CI workflows: `deploy-multi.yml` (default build) and `deploy-nato.yml`
      (`VITE_LOCKED_DECK=nato`); deploy to `gh-pages` branch under different paths
- [ ] Add public URLs to README

### Phase 7 — Cross-device sync (post-MVP)

App is live at `https://flashcards.burntbytes.com/` with 286 cards across 9 decks. All state still
lives in browser `localStorage` only (`flashcards:cards`, `flashcards:collections`,
`flashcards:reviews`). Phase 7 adds a sync service that mirrors localStorage to a Postgres DB so
state follows the user across devices, while keeping the app local-first and offline-capable.

#### Architecture

- **Same-repo monorepo-ish layout** in `gjcourt/flashcards`: add `server/` subdir with its own
  `package.json` for the sync service. Existing React app stays at the root, untouched.
- **Stack:** Node 22 + Hono (HTTP) + pg + kysely (typed queries) + zod (request validation). Vitest
  for tests.
- **DB:** New CNPG cluster `flashcards-db` in the homelab, mirroring overture's pattern (iSCSI PVC,
  3 replicas, scheduled backup to S3-compatible store).
- **Routing:** Cilium HTTPRoute on `flashcards.burntbytes.com` gains a second path rule: `/api/*` →
  sync service:8080; everything else → existing web service:8080. Single hostname, no DNS changes,
  no CORS.
- **Auth:** default **single-user mode** — env var `SINGLE_USER_ID=george` skips auth and uses that
  ID. Trusts the edge gateway (CF Access) to gate. Multi-user mode (`AUTH_MODE=jwt`) validates
  `CF-Access-Jwt-Assertion` header and derives `user_id` from `email` claim. Documented as a
  follow-up for reusability.

#### Sync protocol

One endpoint: `POST /api/sync`

Request:

```json
{
  "since": 1715000000000,
  "mutations": {
    "cardStates": [{ "id": "nato:a", "fsrs": {...} }],
    "collections": [{ "id": "iv", "name": "...", "deckIds": [...], "updatedAt": 1715..., "deletedAt": null }],
    "reviews":     [{ "cardId": "nato:a", "ratedAt": 1715..., "rating": 3 }]
  }
}
```

Response:

```json
{
  "now": 1715000060000,
  "cardStates": [{ "id": "nato:a", "fsrs": {...}, "updatedAt": 1715... }],
  "collections": [{ "id": "iv", "name": "...", "deckIds": [...], "updatedAt": 1715..., "deletedAt": null }],
  "reviews":     [{ "cardId": "nato:a", "ratedAt": 1715..., "rating": 3 }],
  "truncated": false
}
```

Wire format is camelCase per-entity `id` (`id` for cardStates/collections, `cardId` for reviews);
the server maps to the snake_case DB columns below. `Collection.createdAt` is client-only display
metadata and is not synced (it's reconstructable from local creation; `updatedAt` drives LWW).
Client persists `response.now` as the next `since` value; first sync uses `since: 0`.

**Limits.** Per-array cap of 5000 rows in either direction. On response: if any of `cardStates` /
`collections` / `reviews` would exceed 5000 rows, the server truncates that array to the first 5000
sorted by `updatedAt` (or `ratedAt` for reviews) ascending, sets `truncated: true`, and the client
immediately re-syncs with `since = max(updatedAt | ratedAt) of the returned rows` until `truncated`
is `false`. On request: the client batches its outgoing queue into ≤5000 mutations per call.

#### Conflict resolution

Rules are symmetric — applied the same way on both the server (against incoming mutations) and the
client (against response rows). For each `id`, keep the row with the greater comparison key:

- **Card states** — comparison key is `(fsrs.last_review, updated_at)` compared lexicographically,
  with non-null `last_review` always greater than null `last_review` (a rated card never loses to a
  never-rated card). If both sides have null `last_review` (card created but never rated on either
  device), the `updated_at` tiebreaker decides. The server reads `last_review` out of the `fsrs`
  JSONB blob at write time and performs the comparison in app code.
- **Collections** — comparison key is `updatedAt`. Deletions are soft via `deletedAt` tombstones so
  they sync. Tombstones expire server-side after 90 days.
- **Reviews** — append-only log; idempotent insert on `(user_id, card_id, rated_at)` primary key.
  Duplicate inserts are no-ops; no conflict resolution needed because the tuple is content-derived.

#### Client sync model

- New `useSync` hook in `state.tsx`. Runs:
  - on startup
  - every 60s via `setInterval`
  - on `document.visibilitychange` when visible
- Mutation queue persisted in localStorage at `flashcards:sync-queue` so mutations made offline are
  durable. `cardStates` and `collections` entries are coalesced by `id` (latest local write wins
  before sending); `reviews` are append-only (every rating event queued, even repeats on the same
  card).
- Last-sync timestamp persisted at `flashcards:last-sync-at`.
- Reconcile order on response: apply response rows over local state (LWW comparison on the client
  using the same rules below), **then** clear the queue and update `last-sync-at` to `response.now`.
- Failed sync (network error, 5xx) leaves the queue intact for retry.
- A small `<SyncStatus>` indicator in `<Layout>` shows offline/online + "synced 2m ago" / "syncing…"
  / "error".
- The existing local `flashcards:reviews` cap of 1000 entries stays in place (it backs the local
  streak/stats UI only); the server `reviews` table retains the full history.

#### DB schema

```sql
CREATE TABLE card_states  (user_id TEXT, card_id TEXT, fsrs JSONB, updated_at TIMESTAMPTZ DEFAULT now(), PRIMARY KEY (user_id, card_id));
CREATE TABLE collections  (user_id TEXT, collection_id TEXT, data JSONB, updated_at TIMESTAMPTZ DEFAULT now(), deleted_at TIMESTAMPTZ NULL, PRIMARY KEY (user_id, collection_id));
CREATE TABLE reviews      (user_id TEXT, card_id TEXT, rated_at TIMESTAMPTZ, rating SMALLINT, PRIMARY KEY (user_id, card_id, rated_at));

CREATE INDEX card_states_user_updated ON card_states (user_id, updated_at);
CREATE INDEX collections_user_updated ON collections (user_id, updated_at);
CREATE INDEX reviews_user_rated ON reviews (user_id, rated_at);
```

#### Rollout milestones

1. **This PR** (gjcourt/lab) — plan documented.
2. **Sync service skeleton** (gjcourt/flashcards) — `server/` subdir, Hono app, kysely-migrate
   migrations, `Dockerfile.sync`, `image-sync.yml`, unit tests. Image published to
   `ghcr.io/gjcourt/flashcards-sync`.
3. **Client integration** (gjcourt/flashcards) — `useSync` hook, mutation queue, reconcile logic,
   `<SyncStatus>` indicator.
4. **Homelab deploy** (gjcourt/homelab) — `apps/base/flashcards-sync/`, CNPG cluster, second
   HTTPRoute path rule.
5. **Image tag bump** (gjcourt/homelab) — bump `image-sync.yml`-published tag in the homelab
   manifest to roll the service out.

#### Open design questions (call out, don't decide)

- Whether to use logical clocks / vector clocks for stricter cross-device causal ordering (defer;
  LWW is sufficient for single-user).
- Whether to add a "reset device" button that re-pulls from server, blowing away local state
  (probably yes; can add in milestone 3, Client integration).
- Multi-user mode auth specifics — when needed, what claim to trust.

## Card list — financial deck (Phase 2 reference)

- **Equities (~15):** P/E, EPS, market cap, beta, dividend yield, book value, float, short interest,
  alpha, ROE, ROIC, EV, EBITDA, free cash flow, dilution
- **Accounting principles (~12):** accrual basis, matching principle, going concern, materiality,
  conservatism, revenue recognition, depreciation, amortisation, FIFO/LIFO, goodwill, deferred
  revenue, working capital
- **Valuation formulas (~13):** DCF, WACC, terminal value, Gordon Growth Model, comparable company
  analysis, precedent transactions, LBO, NAV, price-to-book, EV/EBITDA, PEG ratio, margin of safety,
  intrinsic value
- **Fixed income basics (~10):** coupon rate, yield to maturity, duration, convexity, credit spread,
  par value, zero-coupon bond, callable bond, inverted yield curve, credit rating
