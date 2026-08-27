---
title: 'Multi-DAC Control Plane (Agent at the Metal, Hub in Kubernetes)'
number: '01-022'
category: 'audio-midi'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills:
  'USB HID device lifecycle, agent/hub architecture, outbound service registration, Kubernetes
  deployment of a hardware-adjacent service, capability gating for unverified hardware'
status: 'Not Started'
depends_on:
  - 01-018
---

# Multi-DAC Control Plane

**Objective:** Control several USB DACs from one web UI, regardless of which machine each one is
physically plugged into, without ever letting the UI write an unverified register map to a device.

The existing CLI (`toppingctl`) already speaks the vendor's USB HID protocol and can read full
device state. What it cannot do is answer "which of my DACs is where, and let me drive that one" —
because it assumes it runs on the machine the DAC is attached to.

---

## 1. The constraint that shapes the whole design

**A USB DAC lives where the audio is, not where the servers are.** It sits on a desk driving
headphones, or in a listening room driving speakers. It is not in a rack.

That kills the obvious version of this idea — "deploy the controller to Kubernetes" — because a pod
can only reach a USB HID device if:

1. the device is plugged into a cluster node, **and**
2. the pod is pinned to that node, **and**
3. the pod has `hostPath` access to `/dev/hidraw*`, **and**
4. the node OS exposes `usbhid` at all (a minimal immutable distro may not)

Satisfy all four and the reward is a DAC in a rack, connected to nothing worth listening to.

**The obvious objection is USB/IP** (`usbip` + `vhci-hcd`), which exports a USB device across a
network so a remote host can claim it. It is a real technology and it would technically work. It is
rejected here for the same reason the agent registers outbound: it needs a privileged kernel module
on the receiving side, and it assumes a stable LAN. The machines these DACs plug into are laptops
that sleep, roam between networks, and sit behind NAT. USB/IP moves the _device_ across an
unreliable boundary; the design below moves _messages_ across it instead, which is the thing that
tolerates the boundary being unreliable.

So the controller cannot be the thing in Kubernetes. Only the **coordination** can be.

## 2. Architecture: agent at the metal, hub in the cluster

**Agent** — a small process on each machine that has a DAC attached. It:

- owns the USB HID handle for its local devices (nothing else may hold it)
- enumerates what it can see and reports identity (see §3)
- exposes read and control operations over a local API
- **registers outbound to the hub**, and heartbeats

Outbound registration is deliberate. Agent machines are laptops and small single-board computers:
they sleep, move between networks, and sit behind NAT. A hub that must _reach_ them will spend its
life timing out. A hub that is _reached_ just watches registrations expire.

**Hub** — runs in the cluster. It:

- keeps a registry of live agents and the devices each one reports
- serves the UI
- routes a command to the agent that owns the target device
- **never touches USB**

"Swap devices based on where they're connected" then falls out for free: the hub shows the union of
every agent's devices, you pick one, the hub routes to its owner. Plug a DAC into another machine
running an agent and it appears. Unplug it and it ages out.

## 3. Device identity: serial, never product ID

This is the part that is easy to get wrong and expensive to get wrong.

**The USB product ID does not identify the model.** At least three devices in this vendor's range
ship the _same_ PID, and their register maps **collide** — the same register address means different
things on different models. Writing one model's map to another is exactly how you set an unrelated
setting, or worse.

So identity is layered:

| Field              | Distinguishes    | Notes                                |
| ------------------ | ---------------- | ------------------------------------ |
| USB product string | the **model**    | what the vendor's own app keys on    |
| Serial number      | the **unit**     | two of the same model on one machine |
| Agent ID           | the **location** | which machine it is plugged into     |

Primary key is `(agent, serial)`. Display name is the product string. **PID is never used to select
a register map.**

## 4. The safety property: unverified devices are read-only

The CLI's own guidance is: never claim support for a model you have not driven, because the cost of
being wrong is writing unknown registers to real hardware. The verification sequence is enumerate →
add entry marked unverified → dry-run → observe one benign change on the front panel → run the
hardware smoke test → only then mark confirmed.

A GUI makes violating that _easier_ than a CLI does. A CLI requires typing a flag; a dropdown
requires one click, and the wrong entry looks exactly like the right one.

**Therefore the hub must refuse writes to any device whose model is not `confirmed`.** Read and
dry-run stay available, so an unverified device is still useful for capture and identification. This
has to be enforced in the hub, not left to the operator noticing — a UI that _can_ do the dangerous
thing eventually will.

## 5. Known unknowns

- **A second model's identity is unmeasured.** Whether it shares the colliding PID or reports its
  own is unknown, and it decides whether it needs a separate register map or can share one. This is
  the gating question and it costs one enumerate run to answer.
- **Handle contention.** A resident agent holding the HID handle conflicts with the vendor's own
  application and any other consumer. Behaviour when both are running is untested.
- **Sleep and hot-plug.** What the agent does when the host sleeps mid-session, or the cable is
  pulled during a write, is undesigned. This is the actual engineering content of the project.
- **Whether the UI is worth building at all.** The vendor already ships a working single-device web
  app. The only thing this adds is _multi-device, multi-location_ control. If that stops being
  interesting, the honest move is to stop at the agent and drive it from the CLI.

## 6. Build order

1. **Capture the unmeasured model's identity** — product string, PID, serial. Gating; everything
   else is speculation until this is known.
2. **Agent, read-only** — enumerate + read state, running on one machine.
3. **Hub, read-only** — multi-agent registry, device list, live state. Proves the interesting part
   (routing by location) with zero write risk.
4. **Writes**, gated on `confirmed`, for the one model already verified.
5. **PEQ editing UI** — last, and only if steps 1-4 are actually being used.

Stopping after step 3 is a legitimate outcome. It answers the original question ("which DAC is
where, and what is it set to") without ever taking on write risk.

## Exit Criteria

- Two DACs attached to two different machines both appear in one hub UI, correctly attributed to
  their host, keyed on serial rather than product ID.
- Selecting a device and reading its state returns live values from that device, not a cache.
- A device whose model is not `confirmed` is visibly marked and **cannot** be written to through the
  UI — verified by attempting it.
- Unplugging a DAC removes it from the hub within one heartbeat interval; replugging restores it
  without restarting the agent or the hub.
- The agent survives a host sleep/wake cycle without requiring a manual restart.
