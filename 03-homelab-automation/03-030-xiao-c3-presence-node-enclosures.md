---
title: 'XIAO ESP32-C3 Wall-Wart Presence-Node Enclosures'
number: '03-030'
category: 'homelab-automation'
difficulty: 'Easy'
time_commitment: '1-2 days'
target_skills: 'Parametric CAD (OpenSCAD), FDM printing, RF/antenna packaging, tolerance/fit'
status: 'In Progress'
depends_on:
  - hardware/esp32
  - homelab/home-assistant
  - homelab/espresense
---

# XIAO ESP32-C3 Wall-Wart Presence-Node Enclosures

## Description

A family of small 3D-printed cases for the **XIAO ESP32-C3 presence nodes** that plug directly into
a USB power brick. Each node sockets to the brick through a **180° USB-C adapter** so the board
rides tight against the brick's room-facing side; the case caps and retains the board, routes the
WiFi antenna lead, and gives the whole thing a clean, wall-wart form factor.

Three variants share one architecture:

1. **Plain C3 + WiFi antenna** — a room presence / ESPresense node. **(rev 4, done)**
2. **mmWave hat** — Seeed 24 GHz radar hat for occupancy. Parametric sibling with a deeper cavity
   and a radar-transparent front. **(pending)**
3. **IR/RF blaster** — reuses the case family around the carrier PCB from
   [03-027](03-027-xiao-c3-ir-rf-blaster-carrier-pcb.md). **(pending)**

## The design problem

The node's antenna is a **Seeed XIAO FPC Antenna A-01** — a 20 × 40 mm flexible PCB antenna,
3M-backed, coax to the center of a short side. It needs a flat 40 mm surface to adhere to and, being
an FPC, wants to lie flat or conform to a _gentle curve_ — a sharp fold detunes it. The brick's
faces are only 32 mm, so no single face gives the antenna its 40 mm.

The **rev 4** answer is an **L** that grips the brick's right corner:

- **Leg 1** caps the board on the room face (open back for the adapter, USB-C throat, retention
  lips).
- **Leg 2** wraps onto the right face — mechanical grip so the case doesn't hang off the plug.
- The outer corner between the legs is a **generous continuous round** (no recess). The FPC antenna
  adheres across leg 1 → curve → leg 2 as one surface (~45 mm of skin), conforming to the curve — no
  crease, no bump.
- A **wire-catch** comb on the back wall strain-relieves the fragile u.FL coax; the lead exits a
  top-center notch to the antenna.

See [`_reference/presence-enclosures/`](_reference/presence-enclosures/README.md) for the OpenSCAD
source, STL, print settings, and the full deployment geometry.

## Why this project

Presence nodes want to disappear — a bare board dangling off a plug looks like a science project and
stresses the antenna lead. A purpose-fit case makes each node solid, repeatable, and tidy, and the
shared L architecture means the mmWave and IR variants are parameter changes, not redesigns.

## Exit Criteria

- [x] rev 4 (plain C3 + WiFi antenna) modeled parametrically and rendered to a manifold STL.
- [ ] rev 4 test-printed and fit-tuned (cavity clearance, USB-C throat, lip snap, antenna wrap).
- [ ] mmWave-hat variant: deeper cavity + radar-transparent front, printed and verified.
- [ ] IR/RF-blaster variant fitted around the 03-027 carrier PCB.
- [ ] All shipped variants deployed on real nodes with the antenna adhered and coax strain-relieved.
