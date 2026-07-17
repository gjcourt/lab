# leva! Controller — client analysis + clean-room design (TypeScript, homelab-deployed)

Design record for a **self-owned monitoring/control app** for the ito + `leva!` espresso controller
([06-001](../06-001-lucca-a53-mini-leva-firmware-integration.md)). Two clients exist already; both
are closed-source, so this documents their **mechanism** (to answer "do we need either?") and specs
a **clean-room re-implementation** we own — TypeScript, ports/adapters, deployed in the homelab with
a Home Assistant bridge.

## Why build our own

The 06-001 monitoring requirement wants live pressure/flow/temp in the homelab (HASS), plus profile
authoring. The two existing clients each fall short for that:

- **Status Monitor** (softwareandcircuits, Java) — the vendor app. Apple-Silicon-hostile (Java 7/8),
  read-centric, no HASS path.
- **Leva-Companion** ([github.com/vocian/Leva-Companion](https://github.com/vocian/Leva-Companion),
  Node + browser) — feature-rich, but **all rights reserved** (no redistribution or modification), a
  single-author early project, and a browser app that needs a local Node proxy per client.

Neither is ours to fork. But the **protocol** both speak is the firmware's, not theirs — freely
documented in our own [ito manual summary](ito-manual-summary.md) and
[leva! docs](leva/LEVA-DOCS-SUMMARY.md) — so a clean-room build owes them nothing.

## The two existing clients — same mechanism, different use

Both speak the **identical channel**: TCP **port 23** (port 80 on old firmware), the ito **"MC"
telnet command family**. They differ only in how they use it:

|                   | Status Monitor (Java)                                                              | Leva-Companion (Node)                                                           |
| ----------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Transport         | TCP 23, direct                                                                     | TCP 23 via a Node proxy (browsers can't raw-TCP → WS⇄TCP bridge)                |
| Display model     | **Generic** — firmware sends `XML=<name>`, app renders whatever that XML describes | **Hard-coded** to leva!'s frame layout; reads `XML=` only to identify firmware  |
| Direction         | Read-centric (plots + Virtual-LCD mirror)                                          | Read **and write** (profile upload, dosing, diagnostics, calibration, menu nav) |
| Firmware coupling | Any ito firmware (self-describing)                                                 | leva!-specific                                                                  |
| Platform          | Java (Apple-Silicon pain)                                                          | Node + browser (native on macOS)                                                |
| License           | Proprietary (vendor)                                                               | All rights reserved                                                             |

**The only capability unique to Status Monitor:** generic, XML-driven rendering that adapts to _any_
ito firmware, with a user-editable XML config. That matters only if you flash a non-leva firmware.
For a leva! machine, **Leva-Companion is a functional superset** — nothing the firmware exposes on
port 23 is off-limits to it. So Status Monitor is worth keeping only as the vendor fallback / the
generic-firmware escape hatch; it offers nothing _functionally_ unique on leva!.

## The shared protocol surface (the reusable, clean-room part)

Derived from the [ito manual summary](ito-manual-summary.md) (§ port 23, `MC?`/`MCr`/`MC@`, `{...}`
packets, the 69-char LCD string, button bytes) and the [leva! docs](leva/LEVA-DOCS-SUMMARY.md) (the
`MCc<NAME>` command set + profile model). **Discipline: re-derive and verify every constant against
the ito + leva! manuals and a live capture from the bench ito — do not transcribe another app's
reverse-engineered values as our source of truth.** Facts (the protocol) are not copyrightable; a
specific implementation is.

- **Transport** — TCP 23 (80 on old firmware), telnet-style. Up to **4 simultaneous connections**,
  **5-minute idle timeout**. The menu is a **single shared resource** → serialize operations (never
  interleave an `MCu` read with a mid-navigation profile upload). Model as a named mutex.
- **Handshake** — on connect the firmware emits `XML=leva!-<id>` + status lines. Send `MCr` to start
  **rich telemetry** (~10 Hz frames); `MC@` switches to **LCD-only** mode (for menu navigation);
  `MCr` again resumes telemetry.
- **Command families**
  - `MCc<NAME>` — semantic single-shot commands (flush, warm-up, dose, standby, PID pick, …).
  - Virtual buttons — `MC<byte>` (press) then `MC\x00` (release): `01`=up `02`=down `03`=OK/stop
    `04`=cancel `05`=shortcut-1 `06`=shortcut-2.
  - `MC+` / `MC-` — setpoint ±0.1 °C. `MCu` — dump the full setup tree (streamed indented lines).
- **Frame types**
  - **Rich** `{ … ~ NN }` — position-based fields: state (`OFF`/`IDLE`/`PULLING`/`BREWING`/
    `STEAMING`/`STANDBY`/…), pressure (bar), flow (g/s from scale) + flow (ml/s from meter), volume,
    weight, temp, setpoint, pressure tolerance band, shot timer, shot-running marker. Optional 2-hex
    checksum after `~`.
  - **LCD** `<NNN row1row2row3row4>` — a 3-digit state prefix + 4×16 chars; cursor and progress-fill
    are control bytes.
  - **Alarm** `[TOKEN]` — one-liners overprinted on the LCD title (`[SCALE]`, `[NO SNS]`, `[GAUGE]`,
    `[REFILL]`, …) used for fail-fast on refused operations.

## Domain model (from the leva! firmware)

- **ProfileSlot** (0–3): name, pre-infusion steps, shot steps, flood (enable/pressure/pump-power),
  flow-tracking (ml/s + duration), per-PID overrides, end mode (STOP/SUSTAIN/FULL POWER).
- **Step**: time, bar target (`bar=0` + `time>0` = pause; flow-unit steps sent as `bar=0`).
- **DosePreset**: method (weight/time/volume), quantity, profile slot, flags.
- **Shot / TracePoint**: history snapshot — profile + dose/yield/ratio/time/peak + a per-shot trace
  (t, pressure, flow, temp, weight, volume).

## Architecture — TypeScript ports & adapters

The `core` (domain model + protocol codec) is **pure and isomorphic** — no Node or DOM APIs — so it
runs in a service, a CLI, or a browser unchanged, and unit-tests fully offline. All I/O lives behind
ports.

```text
        ┌──────────────────── @leva/core (pure TS, isomorphic) ───────────────────┐
driving │  model: ProfileSlot, Step, DosePreset, Shot, MachineState                │ driven
 side   │  codec: bytes ⇄ events — rich/LCD/alarm parsers, MCc/button command build │ side
 (API/  │  services: connection FSM (handshake, rich⇄LCD), menu mutex,             │ (ports)
  UI) ─▶│           profile-upload orchestration, diagnostics runner               │─▶
        └──────────────────────────────────────────────────────────────────────────┘
 PORTS (interfaces core owns):
   driven:  MachineTransport(connect/send/onBytes)  ·  ProfileStore  ·  HistoryStore  ·  Clock
   driving: commands (startShot, uploadProfile, runDiag…) + event streams (telemetry, lcd, alarm)

 ADAPTERS (swappable, each its own package):
   transport-tcp   Node net.Socket → port 23            (the only thing that knows TCP)
   transport-sim   replays canned frames                → build/verify with NO machine
   mqtt-bridge     telemetry → mosquitto + HASS discovery (first-class, not a bolt-on)
   store-pg        history/profiles in Postgres (CNPG)   (or store-sqlite on a PVC)
   ui-web          TS SPA: brew chart, profiles, history, LCD mirror
   cli             bring-up: handshake + print decoded telemetry/LCD
```

Package layout (pnpm workspaces): `@leva/core`, `@leva/transport-tcp`, `@leva/transport-sim`,
`@leva/mqtt-bridge`, `@leva/store-*`, `@leva/server` (composition root — Fastify + `ws`, serves the
REST/WS API and static UI), `@leva/ui`. The server is the only place ports get wired to concrete
adapters.

Why this shape fits us: **license-clean** (every line ours; the protocol is the firmware's);
**`transport-sim`** lets us build and tune the whole app — including the brew chart — with no bench
ito and no sensor; **`mqtt-bridge`** satisfies the homelab HASS-monitoring requirement as a proper
adapter rather than a hack; and UI/transport/persistence all swap without touching protocol logic.

## Homelab deployment

- **Image** `ghcr.io/gjcourt/leva-controller` (built with `GITHUB_TOKEN`; amd64 for the cluster).
- **GitOps** — `homelab` `apps/base/leva-controller` (Deployment + Service + HTTPRoute) with
  `staging`/`production` overlays (`leva-controller-stage` / `-prod` ns), reconciled by Flux. Follow
  `homelab/docs/operations/2026-05-02-adding-an-app.md`.
- **Ingress** — `leva.burntbytes.com` via the Cilium Gateway; Authelia SSO like the other apps.
- **IoT-VLAN reachability (design gate).** The pod must reach the ito on the **IoT VLAN** (bench
  `10.42.7.11`; the installed machine's ito joins WiFi/IoT too). Cluster→IoT cross-VLAN egress is
  already exercised (snapcast reaches `10.42.7.x`), but it needs an explicit **Cilium netpol egress
  allow** to the ito IP on port 23. Verify before building the deploy.
- **Persistence** — history + profiles. House pattern is **CNPG Postgres** (`store-pg`); a small
  iSCSI PVC with SQLite (`store-sqlite`) is the lighter alternative.
- **Config/secrets** — ito host/port via ConfigMap/env; any secrets SOPS-encrypted.
- **Probes** — readiness = server up; a distinct liveness (e.g. transport-reconnect loop healthy)
  per the adding-an-app health-probe guidance.

## Suggested phasing

1. **Protocol bring-up** — `@leva/core` codec + `transport-tcp` + `cli`: connect to the bench ito,
   run the handshake, print decoded telemetry + an LCD mirror. Validates the whole protocol layer
   against real hardware with ~no UI. (`transport-sim` in parallel for offline tests.)
2. **HASS bridge** — `mqtt-bridge`: publish pressure/flow/temp to HASS via MQTT discovery. Delivers
   the homelab monitoring goal with minimal surface.
3. **Server + web UI** — brew chart (target curve + live traces), profile editor, history/replay.
4. **GitOps deploy** — image → `homelab` overlays → ingress → netpol egress to the ito → CNPG.

Meanwhile: keep Status Monitor installed as the vendor fallback; run Leva-Companion as-is if a UI is
wanted before ours exists (do not fork it — license).

## License / clean-room

Both existing clients are proprietary / all-rights-reserved — **do not fork or copy their source.**
Our implementation derives solely from the firmware's protocol (the ito + leva! manuals we hold,
verified by live capture) and is licensed as we choose. Facts about the protocol are not
copyrightable; their code is.

## References

- [github.com/vocian/Leva-Companion](https://github.com/vocian/Leva-Companion) — Node/browser client
  (all rights reserved). Announcement:
  [home-barista t61709 #p1075964](https://www.home-barista.com/espresso-machines/ito-leva-controller-q-experience-t61709-360.html#p1075964).
- [ito manual summary](ito-manual-summary.md) — port 23 / MC protocol / Status Monitor XML.
- [leva! docs summary](leva/LEVA-DOCS-SUMMARY.md) — firmware, profiles, tuning.
- [06-001](../06-001-lucca-a53-mini-leva-firmware-integration.md) — the parent project.
