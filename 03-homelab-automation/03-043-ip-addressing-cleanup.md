---
title: 'IP Addressing Cleanup: DHCP/LB Overlap, Per-VLAN Blocks, Device DNS'
number: '03-043'
category: 'homelab-automation'
difficulty: 'Medium'
time_commitment: '1-2 weeks'
target_skills:
  'IP address planning, UniFi DHCP, Cilium LB-IPAM and BGP, AdGuard DNS rewrites, documentation that
  stays true (generated or CI-checked)'
status: 'Not Started'
depends_on:
  - homelab/cilium
  - homelab/adguard
---

# IP Addressing Cleanup: DHCP/LB Overlap, Per-VLAN Blocks, Device DNS

## Description

The homelab's address map lives in `homelab/docs/architecture/networking/addressing.md`. A review on
2026-10-20, done while placing the office audio Pi, found that the scheme's shape is good. Each VLAN
gets its own `/24`, and the third octet matches the bridge number: `br7` is `10.42.7.x`. But the
scheme has one live hazard and several gaps that make a simple question ("where does this new device
go?") harder than it should be.

This project fixes those findings in order of risk, and leaves the map in a state where it can't
quietly drift again.

## Findings (review 2026-10-20)

1. **Lab DHCP overlaps both cluster LB pools.** Confirmed on the gateway: the Lab DHCP range is
   `10.42.2.6–.254`, while Cilium announces service IPs from `.30–.37` and `.40–.254`.
   - A new wired client on Lab can be handed an IP the cluster later assigns to a service, or one it
     already uses.
   - The addressing doc says Cilium avoids DHCP-reserved IPs. That claim is unverified, and LB-IPAM
     has no view of UniFi's reservations.
   - `kitchen-pi` (`.143`) sits inside the pool.
2. **The real fix has waited since May.** Phase D of
   `2026-05-06-network-resilience-and-bgp-completion` moves LB IPs to a dedicated, BGP-only
   `10.42.5.0/24`. It is still `status: planned`.
3. **The doc is stale but marked Stable.** `last_modified` is 2026-05-06.
   - It lists 6 Talos nodes; the cluster runs 4, and `talos-fpd-h0t` isn't listed.
   - It is missing `mosquitto-lb` (`.46`), the office Pi and every IoT device.
4. **No in-subnet allocation convention.**
   - Lab has blocks in practice (storage in the .10s, nodes in the .20s), but they aren't written
     down.
   - IoT has no reservations and no blocks.
   - DHCP ranges are inconsistent: Core is `.100–.199`, everything else `.6–.254`.
5. **Client devices on the cluster's VLAN.**
   - Apple TV, both HiFiBerries and kitchen-pi sit on Lab. Phase F.1, which moves them to IoT, is
     also only planned.
   - The new office audio Pi went to IoT, so the audio endpoints are now split across two VLANs.
6. **No device DNS names.** The `*.burntbytes.com` wildcard sends every name to the gateway VIP, so
   `office.burntbytes.com` resolves to the cluster, not the office Pi. Devices are reached by raw
   IP.

## Plan

| Step | Change                                                                                                                                       | Where                          |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| 1    | Shrink Lab DHCP to `.6–.29` so it no longer overlaps either LB pool; confirm no dynamic lease sits above `.29` first                         | UniFi (George, or with his OK) |
| 2    | Write a per-VLAN block convention into the addressing doc (proposal below) and reserve the office Pi in IoT under it                         | homelab docs PR + UniFi        |
| 3    | Execute Phase D (LB IPs to `10.42.5.0/24`)                                                                                                   | homelab plan, already written  |
| 4    | Execute Phase F.1 (Apple TV, HiFiBerries, kitchen-pi to IoT); audio endpoints land in the IoT audio block                                    | homelab plan + UniFi           |
| 5    | Refresh the addressing doc against live state, and add a drift check (script comparing gateway reservations and `kubectl` LB IPs to the doc) | homelab PR                     |
| 6    | Device DNS: a device zone in AdGuard (e.g. `office.lan` or `office.dev.burntbytes.com`) for reserved devices                                 | homelab PR (AdGuard config)    |

**Proposed block convention (for review, not decided):**

| Range       | Use                                                         |
| ----------- | ----------------------------------------------------------- |
| `.1`        | Gateway                                                     |
| `.2–.29`    | Static and reserved infrastructure, by role block           |
| `.30–.99`   | DHCP reservations, by role block (e.g. IoT audio `.30–.39`) |
| `.100–.254` | Dynamic DHCP                                                |

Lab keeps its existing `.10s` storage and `.20s` nodes; after Phase D its LB pools leave the subnet.

## Open questions

- Block convention: does the template above suit every VLAN, or should Lab differ until Phase D
  lands?
- Device DNS zone name: `.lan`, `.home.arpa`, or a `dev.burntbytes.com` subdomain?
- Do the HiFiBerries move before or after their DietPi rebuild (`01-016`)?

## Exit Criteria

- [ ] No DHCP range on any VLAN overlaps a Cilium LB pool (verified on the gateway and in the pool
      specs)
- [ ] The per-VLAN block convention is written in the addressing doc, and the office Pi holds a
      reservation under it
- [ ] Phase D is complete: every LoadBalancer IP is in `10.42.5.0/24`
- [ ] Phase F.1 is complete: no client devices remain on the Lab VLAN
- [ ] The addressing doc matches live state, and a check fails CI (or a scheduled job) when it
      drifts
- [ ] Reserved devices resolve by name from the LAN

## Tasks

- [ ] Step 1: list current Lab leases above `.29`, then shrink the Lab DHCP range
- [ ] Step 2: docs PR with the block convention; office Pi reservation in UniFi; update SSH
      known_hosts and homelab host notes
- [ ] Step 3: run Phase D through its GO gates
- [ ] Step 4: run Phase F.1
- [ ] Step 5: refresh the doc and add the drift check
- [ ] Step 6: AdGuard device zone
