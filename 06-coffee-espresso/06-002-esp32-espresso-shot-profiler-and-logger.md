---
title: 'ESP32 Espresso Shot Profiler and Logger'
number: '06-002'
category: 'coffee-espresso'
difficulty: 'Medium'
time_commitment: '1-4 weeks'
target_skills: 'ESP32, Load Cells, Pressure Transducers, MQTT/Grafana'
status: 'Not Started'
depends_on:
  - hardware/esp32
  - hardware/espresso-machine
  - homelab/mqtt
  - homelab/grafana
---

# ESP32 Espresso Shot Profiler and Logger

## Description

Build a standalone device that sits next to your espresso machine. Use a pressure transducer tapped
into the grouphead and a load cell under the drip tray to log the pressure and weight of every shot
in real-time, sending the data to your homelab for analysis.

> **DIY alternative to [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md).** The ito +
> `leva!` kit already logs pressure, flow, and temperature to the Status Monitor app and supports
> gravimetric dosing with a BLE scale — covering most of this project. Pursue this ESP32 build if
> you want a homelab-native pipeline (MQTT → Grafana) and full control of the data, rather than the
> closed Status Monitor app. The load-cell-under-drip-tray weight logging is the part leva! doesn't
> do on its own.

## Exit Criteria

- [ ] Define what done looks like for this project

## Progress

- [ ] Initial research
- [ ] Implementation
- [ ] Documentation
