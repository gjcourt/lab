# Mini Vivaldi Pressure-Profiling Build Thread (t56816) — Digest & NAS Pointer

> Original synthesis of the **seminal** home-barista thread
> ["La Spaziale Mini Vivaldi and pressure profiling"](https://www.home-barista.com/espresso-machines/la-spaziale-mini-vivaldi-and-pressure-profiling-t56816.html)
> (t56816, 46 posts, Feb–Apr 2019). This is where `blondica73` did the **first documented US ito +
> `leva!` install on a Mini Vivaldi II** and `sandc` (Dietmar, the firmware author) answered. It
> predates — and is the origin of — the later Q&A thread
> ([t61709](https://www.home-barista.com/espresso-machines/ito-leva-controller-q-experience-t61709.html)).
>
> **The full verbatim index + 20 downloaded photos/graphs are kept out of this public repo** (no
> bulk third-party content) and live on the NAS at
> `/Volumes/family/projects/electronics/espresso/home-barista-mini-vivaldi-t56816/` (`INDEX.md` +
> `images/`). This file is the in-repo synthesis; the parent project
> [06-001](../06-001-lucca-a53-mini-leva-firmware-integration.md) folds the findings into its BOM /
> OPV / Pre-flight / Tuning sections.

## The nine things this thread pins down for 06-001

1. **Sensor tap = a T-fitting into the brew line**, not a factory "pre-tapped port". blondica added
   a tee on the brass brew block with the spare branch capped for a future gauge (post #3). The
   adapter needed filing to fit (#1).
2. **OPV just above max brew pressure** (e.g. slightly over 9 bar): keeps the safety function
   without biasing the flow meter or fighting the profile (#10).
3. **Stock flow meter is a GICAR** — pinout **red = +VCC, white = signal/output, black = GND**,
   behind 3× 3 mm Allen screws (#21/#22). It's an **open-collector output already pulled to 5 V
   internally** (measured: +14.3 V rail, signal 0↔5 V); the 14.8 V meter rail must **never** touch
   ito (5 V + 0.5 V input max) (#13, #26).
4. **Share the stock meter; don't stack a second in series.** A second (kit) meter before the pump
   added a restricting nozzle that cut free flow ~10 % (575→640 mL/min once removed) (#31).
   **Interface — the working circuit runs at 5 V, not 14.8 V.** blondica's _first_ attempt powered a
   NAND + opto on the **14.8 V rail and it interfered/failed** (#25); scoping the meter (#26) showed
   the **output is a 5 V open-collector signal** (14.3 V is only the VCC pin). His **bench-proven**
   build (ITO thread t61709 #26) is **one CD4011B gate as a buffer on ito's 5 V rail** — share the
   meter's `o` (output) + `−` (GND) to both controllers, keep `+`/VCC on the Vivaldi **ONLY**, **no
   opto** (opto is optional, for galvanic isolation only). sandc's simpler, untested variant
   (#28–#29): skip the IC, direct-share `o` + `−`, and desolder ito's R6 (10 K) + C8 (100 N). ⚠️ The
   14.3–14.8 V meter rail must **never** touch an ito input (5 V + 0.5 V max).
5. **The pressure pre-test won't run out of the box:** the stock board drops the SNS signal on
   "inactivity". Fix with a temporary **SNS↔L jumper**, or just **press the shot button first, then
   start the test** (#12–#14). Test data survives firmware upgrades.
6. **The Mini Vivaldi pump is "lazy"** — ~half the bar/s rise rate of a Rancilio Silvia at full
   power; leva! can't exceed the machine's full-power ramp, so characterise that ceiling first
   (#17). blondica later swapped in a **ULKA EX5** pump (#21).
7. **Tuning:** keep **Kc<SP and Kc>SP close** (his 25 vs 90 gave wild swings; ~20 was clean,
   #17–#19). leva! uses **two parameter sets split at 2.5 bar by setpoint** (not actual pressure);
   below 2.5 bar is tuned to avoid overshoot — raise Kc if you undershoot there (#40). If the bias
   plot rides ~5° above the pump-power plot, reduce **Flow Corr by ~5°** (#22).
8. **The flood→profile flow drop is expected, not a bug:** the pump runs full power until ~0.7 bar
   fills the air pockets, then the loop takes over (P, I ≈ 0 at zero error). Start the profile
   higher (e.g. 1.2 bar) to avoid the audible stutter (#45, #46).
9. **Display mount without cutting the face:** sandc's reversible idea is to 3D-print a **La
   Spaziale Dream S1 bezel** (which has a display by design) and swap the Mini Vivaldi's passive LED
   PCB for a custom-shaped one (#30). blondica instead Dremel-cut the opening (#28, #31).

## Image catalog (on NAS — pointers only, not committed here)

Under `.../home-barista-mini-vivaldi-t56816/images/`:

| File                                                                   | Post                | What it shows                                                                                     |
| ---------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------- |
| `p03-pressure-sensor-t-tap-install.jpg`                                | #3                  | The pressure sensor **teed into the brew line** on the brass block — the key tap-point reference. |
| `p03-board-and-cable-install.jpg`, `p03-more-install-1..3.jpg`         | #3                  | ito board / cable routing / display before mounting.                                              |
| `p21-mv-flowmeter-pinout.jpg`                                          | #21                 | **GICAR stock-meter connector pinout** (red/white/black; 3 mm Allen).                             |
| `p26-flowmeter-scope-trace.jpeg`                                       | #26                 | Scope trace of the stock meter's 0↔5 V open-collector output.                                    |
| `p16-...`, `p19-...`, `p21-...`, `p39-...`, `p45-...` (Status Monitor) | #16,#19,#21,#39,#45 | Tuning/profile graphs incl. the 2.5-bar handoff and the flood flow-drop.                          |
| `p28-display-encoder-installed-1..2.jpeg`                              | #28                 | Display + encoder mounted in the face (Dremel-cut).                                               |
| `p23-...`, `p44-denis-install-1..2.jpeg`                               | #23,#44             | Denis's parallel install.                                                                         |

See the NAS `INDEX.md` for the full per-post index and the complete key-findings digest.
