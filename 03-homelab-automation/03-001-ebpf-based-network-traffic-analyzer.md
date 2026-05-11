---
title: 'eBPF-based Network Traffic Analyzer'
number: '03-001'
category: 'homelab-automation'
difficulty: 'Hard'
time_commitment: 'Months'
target_skills: 'C, eBPF, Go, Linux Kernel (optional: Rust userspace)'
status: 'In Progress'
depends_on:
  - homelab/prometheus
  - homelab/talos
---

# eBPF-based Network Traffic Analyzer

## Final Disposition

> **This section is a draft.** The 48h soak started ~2026-05-10 is still running. The Status and
> Kill-or-Continue verdict below are TODOs that will be filled in once the soak completes.

- **Status**: TODO post-soak (intended: `Complete`)
- **Kill or Continue verdict**: TODO post-soak (intended: `Continue` — rationale: three
  Hubble-distinct panels live (retransmits, SRTT, DNS latency), low steady-state CPU overhead, and a
  healthy 6/6 node deployment.)
- **Soak result**: _Filled in after 48h soak completes (started ~2026-05-10)._

### Links

- Source repo: [`gjcourt/netscope`](https://github.com/gjcourt/netscope)
- Grafana dashboard: `netscope` — TCP retransmit rate, SRTT histogram, DNS latency percentiles
- Operator runbook:
  [`gjcourt/homelab` → `docs/operations/apps/netscope.md`](https://github.com/gjcourt/homelab/blob/main/docs/operations/apps/netscope.md)
  (landed via PR #630)
- Postmortem:
  [`gjcourt/netscope` → `docs/postmortems/2026-05-10-srtt-verifier-iterations.md`](https://github.com/gjcourt/netscope/blob/main/docs/postmortems/2026-05-10-srtt-verifier-iterations.md)
- Alerting rules: [`gjcourt/homelab` PR #631](https://github.com/gjcourt/homelab/pull/631)
- Kernel-load CI smoke gating future BPF changes:
  [`gjcourt/netscope#13`](https://github.com/gjcourt/netscope/issues/13)
- Plan amendments: Phase 0 close-out
  ([brainstorm#12](https://github.com/gjcourt/brainstorm/pull/12)), Phase 2 close-out
  ([brainstorm#14](https://github.com/gjcourt/brainstorm/pull/14)), this Phase 4 finalization PR

### Open follow-ups (deferred, not blockers)

- **Per-domain DNS breakdown (v2)** — QNAME decoding via the ringbuf path; tracked in
  `gjcourt/netscope` (issue / PR link to be added by parallel work)
- **DNS coverage gap for glibc `res_send` / `sendto+msg_name`** — known limitation of the
  connected-UDP-socket hook; captured in the runbook troubleshooting section
- **CI smoke kernel checksum pinning** — the CI smoke job in
  [`netscope#13`](https://github.com/gjcourt/netscope/issues/13) flagged that the kernel image is
  not pinned by sha256; future hardening item
- **Per-4-tuple keying for retransmit / SRTT** — current shipping design aggregates; per-tuple
  keying is deferred to a future PR if signal warrants it

## Description

Build a per-node DaemonSet that attaches eBPF programs (written in C, loaded via libbpf-style CO-RE)
to host network interfaces and key kernel hooks on the Talos cluster, aggregates kernel-level
traffic and TCP-stack signals into per-CPU BPF maps, and exposes them as Prometheus metrics through
a userspace agent (Go via `cilium/ebpf`, optionally Rust via `aya` for the userspace half).

The cluster already runs Cilium, which provides eBPF-based L3/L4/L7 flow observability via Hubble.
This project deliberately does **not** duplicate Hubble. It targets two areas Hubble does not cover
well:

1. **Depth** — kernel-level signals (TCP retransmits, smoothed RTT, congestion events, DNS
   resolver-side latency) that Hubble's flow log does not surface.
2. **Coverage gaps** — host-network traffic, node-to-node management plane (Talos `apid`/`trustd`,
   kubelet), and off-cluster LAN traffic that Hubble does not see.

The project also carries an explicit **learning** goal: hands-on with C + libbpf + the BPF verifier,
CO-RE relocations, and the userspace BPF loader stack.

## Exit Criteria

- [ ] DaemonSet deployed to all 6 Talos nodes (3 control-plane + 3 worker), running ≥7 days
      continuously without OOM, restart, or BPF program load failures
- [ ] eBPF programs cover: TC ingress + TC egress on the primary host NIC, `fentry`/`fexit` on
      `tcp_retransmit_skb`, `fentry`/`fexit` on `tcp_rcv_established` (RTT extraction), and a kprobe
      on `udp_sendmsg` filtered to UDP/53 for DNS query latency
- [ ] At least 10 distinct Prometheus metric series per node exposed by the userspace agent (mix of
      counters, gauges, histograms)
- [ ] Grafana dashboard with at least 3 panels showing signals **not** available from Hubble:
  - TCP retransmit rate by node (counter rate)
  - Smoothed-RTT histogram per peer (on-cluster + off-cluster)
  - DNS query latency p50 / p95 / p99 from the host resolver
- [ ] Steady-state CPU overhead ≤2% of one core per node under typical homelab load
- [ ] Steady-state memory ≤64 MiB resident per agent pod
- [ ] Coexists cleanly with Cilium's TC programs — verified via `bpftool net show dev <iface>` on a
      stage node showing both Cilium and project programs attached, with documented attach order
- [ ] Source repository (`gjcourt/netscope` or equivalent) contains: README, architecture doc, build
      instructions, CO-RE / `vmlinux.h` regeneration steps, and Talos-specific deployment notes
- [ ] Helm chart or Flux Kustomization in `gjcourt/homelab` deploys the DaemonSet via GitOps;
      single-cluster homelab so there is one overlay, not a stage/prod split (see Phase 3)
- [ ] Postmortem document captures: what was learned, what surprised, what would be done
      differently, and an explicit "kill or continue" recommendation for ongoing maintenance

## Non-Goals

- **Reimplementing Hubble.** Standard L3/L4 flow logs and L7 HTTP visibility are Hubble's job; this
  project will not produce a parallel flow log.
- **Replacing node_exporter.** Generic host metrics stay with `node_exporter`; this project ships
  only signals that require eBPF.
- **Per-pod attribution as a v1 requirement.** Cgroup-ID-based pod correlation is real work and
  lives in Phase 5 (stretch). v1 attribution is per-node and per-peer-IP only.
- **L7 protocol parsing.** TLS SNI extraction and HTTP path inspection are stretch territory; the v1
  dataplane is L3/L4 + TCP-stack + DNS only.

## Architecture

```text
┌─────────────────── Talos node ───────────────────────────────┐
│                                                                │
│  Kernel hooks:                                                 │
│    tcx ingress  (eno1) ── packet/byte counters [HEAD anchor]  │
│    tcx egress   (eno1) ── packet/byte counters                │
│    fentry tcp_retransmit_skb  ── retransmit counter           │
│    fentry tcp_rcv_established ── RTT histogram                │
│    kprobe udp_sendmsg :53     ── DNS query timing ringbuf     │
│                                                                │
│  BPF maps:                                                     │
│    per-CPU array  : packet/byte counters                      │
│    per-CPU hash   : retransmit counts keyed by 4-tuple        │
│    per-CPU hist   : RTT buckets (log2)                        │
│    ringbuf        : DNS events for userspace timing match     │
│                                                                │
│  ┌──────── Userspace pod (DaemonSet, hostNetwork) ─────────┐  │
│  │  Go binary using github.com/cilium/ebpf                  │  │
│  │  (or Rust binary using aya, see §"Userspace language")   │  │
│  │                                                           │  │
│  │  - Loads .o produced by clang -target bpf                │  │
│  │  - Attaches programs to hooks                            │  │
│  │  - Scrapes per-CPU maps every N seconds                  │  │
│  │  - Drains DNS ringbuf, computes query→response latency   │  │
│  │  - Exposes /metrics on :9101                             │  │
│  └─────────────────────────┬─────────────────────────────────┘ │
└────────────────────────────┼───────────────────────────────────┘
                             │ scrape
                       ┌─────▼─────┐
                       │ Prometheus│ ──→ Grafana dashboards
                       └───────────┘
```

### Userspace language

Default: **Go + `github.com/cilium/ebpf`**. The brainstorm names Go as a target skill, the library
is mature and used in production by Cilium, and `bpf2go` produces typed bindings from the C `.o`.

Optional swap: **Rust + `aya`** for the userspace half if Go feels limiting after Phase 2. Aya is
pure-Rust (no libbpf dependency) and has a pleasant typed-map API. Kernel-side stays in C either way
— switching kernel-side to Rust is explicitly out of scope (the brainstorm names C as a target
skill, and C + libbpf is the canonical kernel-side BPF path).

### Talos-specific constraints

Talos is an immutable-OS distribution; kernel-side BPF runs in userspace pods, but the deployment
model has more constraints than a generic Linux host. Items to validate in Phase 0:

- **BTF availability** — `/sys/kernel/btf/vmlinux` must exist on every node. Required for CO-RE. ✅
  Confirmed present on all 6 nodes during Phase 0.
- **Kernel version** — Talos v1.12.4 ships kernel **6.18.9-talos** across all 6 nodes (verified
  Phase 0). Comfortably past the floor for `fentry`/`fexit` (5.5+), ringbuf (5.8+), and tcx (6.6+).
- **Capabilities** — pod needs `CAP_BPF`, `CAP_PERFMON`, `CAP_NET_ADMIN`, **and `CAP_SYS_ADMIN`**.
  Phase 0 surfaced that `CAP_SYS_ADMIN` is required for `bpf(BPF_PROG_GET_NEXT_ID)`, which the agent
  uses at startup to discover Cilium's program for tcx anchor placement (see Phase 0 Findings).
  Kernel gates this on `CAP_SYS_ADMIN` regardless of `CAP_BPF`.
- **Seccomp** — pin to `seccompProfile.type: RuntimeDefault`. `CAP_SYS_ADMIN` widens the syscall
  surface; the container runtime's default seccomp profile is essentially free hardening.
- **Pod Security Admission** — namespace must be labeled
  `pod-security.kubernetes.io/enforce=privileged`. PSA `restricted` blocks `hostNetwork` and
  elevated caps.
- **Filesystem** — `/sys/fs/bpf` mounted into the pod (hostPath) for pinned maps; `/sys/kernel/btf`
  read-only for BTF access.
- **`hostNetwork: true`** required to attach to physical interfaces.
- **Cilium coexistence** — Cilium 1.19 uses **tcx** (not classic TC clsact, despite this plan's
  original wording). Multi-program attachment is the design intent of tcx — coexistence is
  structural, not a workaround. **However:** `link.Head()` (sets `BPF_F_BEFORE` without a target)
  did **not** take effect on this kernel/Cilium combination — our program landed at the chain tail
  even with that flag, so a head-anchored counter saw 0 bytes. The working pattern is to enumerate
  loaded programs at startup, find Cilium's by name (`cil_from_netdev`), and attach with
  `link.BeforeProgramByID(id)`. Verify chain order with `bpftool net show dev <iface>` (works via
  the cilium-agent pod's `bpftool`).
- **SOPS / GitOps** — per repo convention, secret-bearing manifests land as draft PRs with
  `.yaml.example` templates and CI is the gate. This project should not need secrets, but if a
  scrape-auth token is added, it follows that flow.

## Progress

### Phase 0 — Feasibility Spike (≈1 week) — ✅ Closed 2026-05-10

Prove the riskiest assumptions on a single staging node before committing.

- [x] Verify `/sys/kernel/btf/vmlinux` exists on a Talos worker node — confirmed on all 6 nodes
- [x] Build a minimal C BPF program (tcx ingress byte counter) with `clang -target bpf`. (Did not
      need `vmlinux.h` for the hello-world — used `<linux/bpf.h>` + `<bpf/bpf_helpers.h>`. CO-RE +
      `vmlinux.h` deferred to Phase 2 where we touch kernel structs.)
- [x] Build a minimal Go loader using `cilium/ebpf` that loads the program, attaches via
      `link.AttachTCX`, reads the map, exposes `/metrics`
- [x] Run the loader as a DaemonSet in a privileged staging namespace; confirm attachment with
      `bpftool net show dev eno1` via the cilium-agent pod's bundled bpftool
- [x] Confirm Cilium does not block the additional tcx attach; document program ordering —
      `count_rx` anchored ahead of `cil_from_netdev` via `link.BeforeProgramByID`
- [x] **Decision gate:** PASSED. `netscope_rx_bytes_total{iface="eno1"}` increments visibly within
      seconds; counter went 2.95 → 4.33 MB over 10s under steady-state load. Project proceeds.

### Phase 1 — DaemonSet Skeleton (≈2 weeks) — In Progress

- [x] Create new repo `gjcourt/netscope` (Apache 2.0, public). Layout: `internal/bpf/src/` (C source
      — outside any Go package so `go vet` doesn't trip on cgo detection), `internal/bpf/embed.go`
      (`go:embed` of the compiled .o), `cmd/agent/` (Go), `deploy/` (raw manifests +
      `helm/netscope/` chart)
- [x] CI on GitHub Actions (amd64-native; QEMU emulation on arm64 Macs hits Go asm segfaults).
      `lint` job: `clang` + `make bpf`, then `gofmt`, `go vet`, `go mod tidy` diff, `helm lint`,
      `helm template`. `image` job: multi-stage Dockerfile, push to
      `ghcr.io/gjcourt/netscope:{branch,sha}`. Public package.
- [x] DaemonSet manifest with correct caps, hostNetwork, hostPath mounts, PSA label, seccomp
- [x] Single packet-counter metric (`netscope_rx_bytes_total{iface}`) exposed at `/metrics`
- [x] Helm chart in `deploy/helm/netscope/` with values for image, iface, nodeSelector,
      capabilities, resources, probes, seccomp
- [ ] Flux Kustomization / HelmRelease PR opened against `gjcourt/homelab` for stage overlay only
- [ ] Stage Prometheus scraping the new agent; one Grafana panel showing per-node packet rate
- [ ] Roll out to all 3 stage nodes (currently pinned to `talos-18u-ski` only); 24-hour soak
- [ ] **Validation:** rollout to all 3 stage nodes succeeds; agent pods stable for 24 hours

### Phase 2 — Core Depth Metrics (≈3 weeks) — ✅ Closed 2026-05-10

- [x] `fentry`/`fexit` on `tcp_retransmit_skb` — per-4-tuple retransmit counter
- [x] `fentry`/`fexit` on `tcp_rcv_established` — extract `tcp_sock->srtt_us`, populate log2
      histogram (three verifier iterations; see Phase 2 Findings)
- [x] kprobe on `udp_sendmsg` filtered to dport 53 — emit DNS query event to ringbuf with timestamp
      and 5-tuple (in-kernel correlation chosen over ringbuf; see Phase 2 Findings)
- [x] kprobe on `udp_recvmsg` (or tracepoint equivalent) for matching DNS response — userspace
      computes RTT (replaced with in-kernel hashmap correlation; userspace just scrapes the latency
      histogram)
- [x] ~~Userspace agent: drain ringbuf, maintain in-flight DNS query table with TTL eviction,
      compute and export latency histogram~~ — superseded by in-kernel hashmap correlation;
      userspace only scrapes the histogram map (see Phase 2 Findings)
- [x] Grafana dashboard: 3 required panels (retransmit rate, SRTT histogram, DNS latency
      percentiles)
- [x] **Validation:** all 5 BPF programs (1 tcx + 4 fentry/fexit) attached cleanly on every one of
      the 6 Talos nodes; observed signal: retransmits ~625/10 min cluster-wide (non-uniform across
      peers), SRTT p50 ~2 ms / p99 ~734 ms, DNS p50 ~816 µs / p95 ~115 ms / p99 ~845 ms

### Phase 3 — Stabilization & Soak (≈1 week)

The original Phase 3 was framed as "Production Rollout" with a stage → prod sequence. For this
single-cluster homelab, that distinction does not exist: the DaemonSet already runs on all 6 nodes
(3 control-plane + 3 worker), the "staging" namespace _is_ the cluster-wide deployment, and there is
no separate prod cluster to promote to. The phase is retitled and re-scoped to the actual remaining
work: observe the deployment under real load, set alert thresholds from observed baselines, and
write the operator-facing runbook.

- [ ] 24–48 hour soak observation on all 6 nodes; track CPU + memory overhead in Grafana against the
      ≤2% CPU / ≤64 MiB RSS budgets
- [ ] Tune scrape interval, map sizes, ringbuf size if soak surfaces pressure
- [ ] Set alert thresholds from observed baselines: retransmit-rate spike alert, DNS p99 SLO,
      SRTT-tail outlier alert, agent-pod CrashLoop / restart alert
- [ ] Operator runbook in `gjcourt/netscope`: how to read each panel, how to interpret threshold
      breaches, how to regenerate `vmlinux.h` across Talos kernel upgrades, how to disable a
      misbehaving program without taking down the agent
- [ ] **Validation:** 7-day rolling window meeting CPU/memory budgets; alerts wired into the
      existing homelab alerting path; runbook checked in and linked from the dashboard

### Phase 4 — Documentation & Postmortem (≈1 week) — Draft close-out (awaiting soak)

- [x] README in `netscope` repo: overview, build, deploy, troubleshoot
- [~] Architecture doc: program-by-program walkthrough, map design, attach ordering with Cilium —
  _partial._ The SRTT verifier postmortem covers the kernel-side iteration story; the operator
  runbook in `gjcourt/homelab` (`docs/operations/apps/netscope.md`) covers the operational
  architecture (attach order, map layout, scrape model). A standalone "architecture doc" in the
  netscope repo is not duplicated.
- [x] ~~CO-RE / `vmlinux.h` regeneration runbook (for Talos kernel upgrades)~~ — **N/A.** The
      shipping design did not need `vmlinux.h` regeneration: CO-RE works via shadowed struct
      definitions (e.g. partial `tcp_sock` with just the fields read) plus `bpf_core_cast` /
      `bpf_skc_to_tcp_sock`. No per-kernel snapshot to regenerate, so the runbook is not required.
- [x] Postmortem with explicit kill-or-continue recommendation for ongoing maintenance burden —
      [SRTT verifier postmortem](https://github.com/gjcourt/netscope/blob/main/docs/postmortems/2026-05-10-srtt-verifier-iterations.md);
      kill-or-continue verdict captured in **Final Disposition** above (pending soak)
- [ ] Update this brainstorm doc: status `Complete`, link to repo and dashboards — links done;
      status flip deferred to post-soak (see **Final Disposition**)

### Phase 5 — Stretch Goals (open-ended; only if Phases 0–4 land cleanly)

- [ ] Per-pod attribution: read cgroup ID from BPF context, correlate to Pod via cgroupv2 hierarchy
      lookup in userspace
- [ ] L7 — TLS SNI extraction at TC egress for outbound HTTPS visibility
- [ ] L7 — HTTP request path / status extraction (cleartext only) at TC egress
- [ ] Userspace rewrite to Rust + aya — direct comparison of ergonomics, build complexity, and
      runtime resource footprint vs the Go implementation
- [ ] XDP variant of the ingress counter for line-rate measurement; CPU comparison vs TC

## Risks & Tradeoffs

| Risk                                                                   | Mitigation                                                                                                                        |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Talos kernel does not expose a needed hook (e.g. `fentry` unavailable) | Phase 0 validates the riskiest hooks first; fall back to tracepoints if `fentry`/`fexit` is unavailable                           |
| BPF verifier rejects programs (loop bounds, complexity limits)         | Keep individual programs small; use bounded loops; prefer per-CPU maps; iterate on stage                                          |
| CPU overhead exceeds budget at LAN line rate                           | XDP at NIC RX is the escape hatch for hot paths; TC tail-calls keep individual programs cheap; tune scrape interval               |
| Talos kernel upgrade breaks verifier-passing programs                  | CO-RE relocations + pinned `vmlinux.h` snapshot per kernel release; CI loads programs against multiple kernel BTFs                |
| Cilium TC ordering causes traffic to bypass project programs           | Validate via `bpftool net show` on stage; document attach order; coordinate with Cilium chain priority                            |
| Project duplicates Hubble and adds no real value                       | Exit criteria explicitly require ≥3 panels Hubble cannot produce; if Phase 2 cannot hit that bar, kill the project                |
| Maintenance burden post-build (kernel upgrades, BPF API churn)         | Postmortem in Phase 4 includes explicit kill-or-continue recommendation; project is allowed to be archived as a learning artifact |
| Userspace memory growth from in-flight DNS query table                 | TTL eviction in agent; bounded map size in BPF; alert if eviction count climbs                                                    |

## Phase 0 Findings

Items surfaced during the spike that materially altered the plan:

1. **Cilium 1.19 uses `tcx`, not classic TC clsact.** The original architecture text was wrong about
   this. Updated above. Multi-program attachment is the explicit design of tcx — coexistence is
   structural, not a workaround.
2. **Physical interface is `eno1`, not `eth0`.** Predictable Network Interface Naming. Configurable
   via `NETSCOPE_IFACE` env (default `eno1`); Phase 1 should switch to default-route discovery so
   the agent works on heterogeneous hardware without per-host config.
3. **`link.Head()` does not actually anchor at head.** cilium/ebpf v0.18's `Head()` sets
   `BPF_F_BEFORE` with no relative target, which the kernel docs say should mean "first" — but
   empirically on Talos kernel 6.18.9 with Cilium present, our program still landed at the tail
   (counter stayed at 0 across hundreds of MB/s of traffic). The working pattern: enumerate programs
   via `BPF_PROG_GET_NEXT_ID`, find `cil_from_netdev` by name, attach with
   `link.BeforeProgramByID(id)`. Resolved fresh at each pod start since program IDs change across
   `cilium-agent` restarts.
4. **`CAP_SYS_ADMIN` is required for program enumeration.** Kernel gates `BPF_PROG_GET_NEXT_ID` on
   `CAP_SYS_ADMIN` regardless of `CAP_BPF`. Added to the cap set; mitigated with
   `seccompProfile: RuntimeDefault`.
5. **Don't build BPF images from arm64 Macs via Docker.** QEMU emulation segfaults Go's asm tool
   when cross-building amd64. GitHub Actions on amd64 runners is the right path.
6. **Talos kernel was the easy part.** 6.18.9 has every BPF feature Phase 0 exercised, and the
   floors for the Phase 2 hooks (`fentry`/`fexit` 5.5+, ringbuf 5.8+, tcx 6.6+) are well behind it.
   The Phase 0 friction was entirely Kubernetes-side (PSA, capabilities, seccomp).

## Phase 2 Findings

Items surfaced during the core-metrics phase that are worth capturing:

1. **SRTT extraction took three verifier iterations.** Reaching `tcp_sock->srtt_us` from an
   `fentry/tcp_rcv_established` program requires the right cast pattern, and CI did not catch the
   verifier traps — they only fired against the live kernel on stage. Postmortem at
   [`gjcourt/netscope` → `docs/postmortems/2026-05-10-srtt-verifier-iterations.md`](https://github.com/gjcourt/netscope/blob/main/docs/postmortems/2026-05-10-srtt-verifier-iterations.md).
2. **Kernel-load CI smoke is overdue.** Three production-caught verifier bugs on a single feature is
   the signal. Tracked at [`gjcourt/netscope#10`](https://github.com/gjcourt/netscope/issues/10);
   the fix is a CI job that loads each program against a real kernel before merge (KIND with a
   matching kernel, or a small qemu-based loader).
3. **`bpf_skc_to_tcp_sock` is the modern path** for reaching kernel sub-types from `fentry`
   programs. The cast-via-`bpf_core_cast` pattern is what unblocked SRTT and is the right reach for
   any future per-flow TCP state work in this project.
4. **DNS coverage is connected-UDP-sockets only.** The `udp_sendmsg` hook captures queries where the
   socket has been `connect()`'d to the resolver, which covers systemd-resolved and Go
   `net.Resolver`. It does **not** cover glibc `res_send`, which uses `sendto()` with an explicit
   `msg_name`. Acceptable for v1 (the homelab's resolver paths are covered), but worth flagging
   before shipping a "DNS latency from this host" claim. Per-domain breakdown via the ringbuf path
   is the future-work knob — userspace can decode the QNAME and emit a label.
5. **In-kernel correlation scales fine for DNS.** The original plan drained query/response events
   through a ringbuf and matched them userspace-side. The shipping design instead keeps an
   8192-entry per-CPU hashmap in BPF (txid → start-ns), looks up the matching entry in the recv
   path, and writes directly into the latency histogram. No userspace state machine, no ringbuf
   drain pressure, confirmed in production on all 6 nodes.

## Open Questions

- **Default-route interface discovery** — Phase 1 should replace the hardcoded `eno1` default with
  runtime discovery (read `/proc/net/route` or netlink). Trivial; just hasn't happened yet.
- **Anchoring against multi-NIC hosts** — `findProgramByName` returns the first match by name; on
  hosts where Cilium has loaded multiple `cil_from_netdev` instances (one per ifindex), we may
  anchor against the wrong one. Single-target stage node makes this moot for now. Phase 1+ should
  filter by ifindex via attach inspection.
- **Stale image cache from `imagePullPolicy: IfNotPresent` + floating `:main` tag** — restarted pods
  cache the old image SHA. Either pin to `:<short-sha>` (Flux can do this from upstream image
  policies) or set `imagePullPolicy: Always` for the floating tag. Flux integration in Phase 1
  should resolve this properly.
- **Phase 5 commitment** — is per-pod attribution a real requirement or a learning curiosity? It is
  the single largest piece of post-v1 work and should be decided before Phase 4 closes.
- **Phase 4 timing** — some of the postmortem work already happened out-of-band via the SRTT
  postmortem PR
  ([`gjcourt/netscope` → `docs/postmortems/2026-05-10-srtt-verifier-iterations.md`](https://github.com/gjcourt/netscope/blob/main/docs/postmortems/2026-05-10-srtt-verifier-iterations.md)).
  Open: does Phase 4 collapse to "write the README + architecture doc + kill-or-continue verdict"
  and reference the existing postmortem, or do we add a second project-wide retrospective doc?
- **Explicit "kill or continue" verdict** — the Exit Criteria call for one. The current answer is
  almost certainly **continue**: three Hubble-distinct panels are live (retransmits, SRTT, DNS
  latency), all 6 nodes are stable, the project is healthy. Worth writing down formally in Phase 4
  rather than leaving implicit.
- **Per-domain DNS latency breakdown** — meaningful v2 work via QNAME decoding in the ringbuf path;
  not urgent and explicitly deferred.

### Resolved during Phase 0

- ~~Repo placement~~ → New top-level `gjcourt/netscope` (public, Apache 2.0).
- ~~Naming~~ → `netscope`.
- ~~Image build~~ → Multi-stage Dockerfile, clang+golang builder,
  `gcr.io/distroless/static-debian12` runtime. Published to `ghcr.io/gjcourt/netscope` (public).
- ~~Metric prefix~~ → `netscope_*`.
