---
title: 'Pump Pressure Transducer Retrofit'
number: '06-009'
category: 'coffee-espresso'
difficulty: 'Hard'
time_commitment: 'Months'
target_skills: 'Plumbing/Fittings (BSPP/NPT), Analog Sensors, ADC Calibration'
status: 'Not Started'
depends_on:
  - hardware/lucca-a53
  - hardware/esp32
---

# Pump Pressure Transducer Retrofit

## Description

Safely tap into the high-pressure water line of your Lucca A53 Mini (post-pump). Install an
industrial pressure transducer (e.g., 0-15 bar), wire it to an ADC on a microcontroller, and
calibrate the voltage output to accurately read the brew pressure.

> **Largely subsumed by [06-001](06-001-lucca-a53-mini-leva-firmware-integration.md).** The ito +
> `leva!` kit ships a 125 °C-rated brew-pressure sensor with a calibrated readout, and Mini Vivaldi
> II owners simply tee it into the brew line. If you go the leva! route, this standalone retrofit is
> redundant. Keep this project as the **DIY / no-ito alternative** — useful only if you want raw
> pressure logging without buying the EU-only ito module.

## Exit Criteria

- [ ] Define what done looks like for this project

## Progress

- [ ] Initial research
- [ ] Implementation
- [ ] Documentation
