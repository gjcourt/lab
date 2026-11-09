#!/usr/bin/env python3
"""06-014 unified ESP32 interposer, rev A: the schematic as data (single source of truth).

Pre-measurement draft 2026-10-28; updated 2026-11-08 with George's bench measurements (bench page
Tests 28-37 = plan M1-M10; cited as "Test n"). Plan of record:
docs/plans/2026-10-27-unified-esp32-interposer-rev-a-plan.md (sections cited as "plan §n").

Everything a future generate_pcb.py needs lives here:

* PARTS   -- every part: ref, value, footprint (KiCad 9 lib:name; the .kicad_mod is vendored
             in ./footprints), MPN, LCSC number, JLC library class, DNP flag, function F0..F9.
* NETS    -- net name -> list of "REF.pad" strings. Pad names are the footprint pad numbers.
* NC      -- pads deliberately left unconnected, with the reason.
* GPIO    -- ESP32-S3 GPIO allocation (GPIO number -> net), cross-checked by check_circuit.py.
* PLACEHOLDERS -- every value/footprint that is a stand-in pending a measurement (M1..M10).

Rules (plan ground rule): nothing here is a guess. A value that is not backed by a cited source
is flagged in PLACEHOLDERS (and in the part's `note`) with the measurement that closes it.

Import it:      from circuit import PARTS, NETS, NC, GPIO, ESP32_PIN_OF_GPIO
Run it:         python3 circuit.py            (prints a part / net summary)
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------------------------
# Library classes as read on the JLCPCB part pages on 2026-10-28 (jlcpcb.com/partdetail/<C#>).
# Stock is NOT shown in the page text we could read, so every stock figure is "unchecked":
# re-check every LCSC number on jlcpcb.com the day of ordering (plan §6).
# ---------------------------------------------------------------------------------------------
BASIC = 'basic'
EXTENDED = 'extended'
UNSTATED = 'unstated'  # page did not show a clear Basic/Extended label
HAND = 'hand-solder'  # THT connector, not in the JLC assembly BoM (06-015 pattern)
NONE = 'none'  # solder jumper / copper only, nothing to buy


@dataclass(frozen=True)
class Part:
    ref: str
    value: str
    footprint: str  # "Library:Footprint" (KiCad 9 standard library)
    func: str  # F0..F9 (plan §1)
    mpn: str = ''
    lcsc: str = ''  # '' = none / hand-solder
    jlc: str = NONE
    dnp: bool = False
    note: str = ''

    @property
    def fp_name(self) -> str:
        return self.footprint.split(':', 1)[1]


# ---------------------------------------------------------------------------------------------
# Footprints (KiCad 9 library names; copies in ./footprints, taken from kicad/kicad:9.0, except the
# lab: EXCON ones, which gen_excon_footprints.py writes)
# ---------------------------------------------------------------------------------------------
FP_R0603 = 'Resistor_SMD:R_0603_1608Metric'
FP_C0603 = 'Capacitor_SMD:C_0603_1608Metric'
FP_C0805 = 'Capacitor_SMD:C_0805_2012Metric'
FP_SOT23 = 'Package_TO_SOT_SMD:SOT-23'
FP_SOT23_5 = 'Package_TO_SOT_SMD:SOT-23-5'
FP_SOT23_6 = 'Package_TO_SOT_SMD:SOT-23-6'
FP_SOT223 = 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'
FP_SOIC14 = 'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm'
FP_SOIC16 = 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm'
FP_VSSOP10 = 'Package_SO:VSSOP-10_3x3mm_P0.5mm'
FP_VSSOP8_DCU = 'Package_SO:VSSOP-8_2.3x2mm_P0.5mm'
FP_SMA = 'Diode_SMD:D_SMA'
FP_ESP = 'RF_Module:ESP32-S3-WROOM-1'
FP_USBC = 'Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12'
FP_TACT = 'Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A'
FP_XH2 = 'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical'
FP_XH3 = 'Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical'
# EXCON 2547 (2.54 mm wafer, latch window): the Mini Vivaldi II control board's sensor + flow headers
# (Test 29, probable, caliper confirm pending). Authored here by gen_excon_footprints.py from EXCON
# drawing C2547WV rev E; not from the KiCad library ("lab" pseudo-library).
FP_EX2 = 'lab:EXCON_2547-02_WV'
FP_EX4 = 'lab:EXCON_2547-04_WV'
FP_SH4 = 'Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal'
FP_KK4 = 'Connector_Molex:Molex_KK-254_AE-6410-04A_1x04_P2.54mm_Vertical'
FP_HDR2 = 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical'
FP_HDR5 = 'Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical'
FP_HDR6 = 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical'
FP_SJ2_OPEN = 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'
FP_DIP4 = 'Package_DIP:DIP-4_W7.62mm'

# Common passives (JLC page read 2026-10-28 for each LCSC number; all 0603 1 % UNI-ROYAL unless
# noted). (lcsc, mpn, jlc class)
R_0 = ('C21189', '0603WAF0000T5E', BASIC)
R_330 = ('C23138', '0603WAF3300T5E', BASIC)
R_1K = ('C21190', '0603WAF1001T5E', BASIC)
R_4K7 = ('C23162', '0603WAF4701T5E', BASIC)
R_5K1 = ('C23186', '0603WAF5101T5E', BASIC)
R_10K = ('C25804', '0603WAF1002T5E', BASIC)
R_100K = ('C25803', '0603WAF1003T5E', BASIC)
R_200K = ('C25811', '0603WAF2003T5E', BASIC)
R_1M = ('C22935', '0603WAF1004T5E', BASIC)
C_100N = ('C14663', 'CC0603KRX7R9BB104', BASIC)  # YAGEO 50 V X7R (the 06-015 part)
C_1U = ('C15849', 'CL10A105KB8NNNC', BASIC)  # Samsung 0603 50 V X5R
C_10U = ('C15850', 'CL21A106KAYNNNE', BASIC)  # Samsung 0805 25 V X5R
C_22U = ('C45783', 'CL21A226MAQNNNE', UNSTATED)  # Samsung 0805 25 V X5R (page label ambiguous)
TBD = ('', '', NONE)  # value not chosen yet: no LCSC number on purpose

LVC1G17 = dict(value='74LVC1G17', footprint=FP_SOT23_5, mpn='SN74LVC1G17DBVR', lcsc='C7836', jlc=EXTENDED)
BAV99 = dict(value='BAV99', footprint=FP_SOT23, mpn='BAV99,215 (Nexperia)', lcsc='C2500', jlc=UNSTATED)
AO3400A = dict(value='AO3400A', footprint=FP_SOT23, mpn='AO3400A (AOS)', lcsc='C20917', jlc=BASIC)


def R(ref, value, spec, func, dnp=False, note=''):
    lcsc, mpn, jlc = spec
    return Part(ref, value, FP_R0603, func, mpn, lcsc, jlc, dnp, note)


def C(ref, value, spec, func, dnp=False, note='', fp=None):
    lcsc, mpn, jlc = spec
    return Part(ref, value, fp or (FP_C0805 if value in ('10uF', '22uF') else FP_C0603), func, mpn, lcsc, jlc, dnp, note)


PARTS: list[Part] = [
    # --- F0 power + ESP32 (plan §3.1, §6) ---------------------------------------------------
    Part('J4', '5V_IN', FP_XH2, 'F0', 'JST B2B-XH-A', '', HAND,
         note='our choice (plan §4): 1 = +5V, 2 = GND, from the off-board isolated 5 V PSU'),
    Part('J5', 'USB-C (bench flash only)', FP_USBC, 'F0', 'TYPE-C-31-M-12 (Korean Hroparts)', 'C165948', EXTENDED,
         note='USB 2.0 only; NEVER plug in while the machine is plugged in (plan §3.1). Board GND is '
              'earth-bonded once installed (Test 30: M3 pin 4 -> boiler body), so flash an installed board '
              'from a grounded or battery-powered laptop'),
    Part('D1', 'SS34', FP_SMA, 'F0', 'SS34 (MDD)', 'C8678', UNSTATED,
         note='VBUS -> +5V OR-ing; stops the 5 V PSU back-feeding a USB host. KiCad pad 1 = K'),
    Part('U3', 'USBLC6-2SC6', FP_SOT23_6, 'F0', 'USBLC6-2SC6 (ST)', 'C7519', EXTENDED,
         note='USB ESD. Pinout from KiCad lib symbol (ST datasheet unreachable 2026-10-28)'),
    R('R1', '5.1k', R_5K1, 'F0', note='CC1 sink (USB-C)'),
    R('R2', '5.1k', R_5K1, 'F0', note='CC2 sink (USB-C)'),
    Part('U4', 'AMS1117-3.3', FP_SOT223, 'F0', 'AMS1117-3.3', 'C6186', BASIC,
         note='1 A LDO (JLC page); dropout 1.3 V max @0.8 A (AMS datasheet)'),
    C('C3', '10uF', C_10U, 'F0', note='LDO input / +5V bulk'),
    C('C4', '22uF', C_22U, 'F0', note='LDO output; AMS datasheet asks 22 uF (tantalum) for all-cases stability'),
    Part('U5', 'ESP32-S3-WROOM-1-N8', FP_ESP, 'F0', 'ESP32-S3-WROOM-1-N8 (Espressif)', 'C2913198', EXTENDED,
         note='8 MB quad flash, no PSRAM, -40..85 C (module datasheet v1.8 Table 1-1)'),
    C('C5', '22uF', C_22U, 'F0', note='module 3V3 bulk (module datasheet v1.8 Fig 9-1: 22 uF + 0.1 uF)'),
    C('C6', '100nF', C_100N, 'F0', note='module 3V3 decoupling'),
    R('R3', '10k', R_10K, 'F0', note='EN pull-up; RC delay R = 10k, C = 1 uF (module datasheet v1.8 §9)'),
    C('C7', '1uF', C_1U, 'F0', note='EN RC delay'),
    Part('SW1', 'EN/RESET', FP_TACT, 'F0', 'TS-1187A-B-A-B (XKB)', 'C318884', UNSTATED),
    Part('SW2', 'BOOT (GPIO0)', FP_TACT, 'F0', 'TS-1187A-B-A-B (XKB)', 'C318884', UNSTATED),
    R('R4', '10k', R_10K, 'F0', note='GPIO0 pull-up (strap default is weak pull-up = SPI boot; this makes it firm)'),

    # --- F1/F2 S1/S2 NTC taps + F3 SB (plan §3.2, §3.3; Tests 29, 30) ---------------------------
    # Board map (Test 29, George 2026-11-08): M2 2-pin = steam NTC (S1): 1 GND, 2 feed.
    # M3 4-pin = 1 GND, 2 group NTC feed (S2), 3 steam-boiler level probe (SB), 4 GND (level return to
    # the boiler body). So S2 and SB share one 4-pin plug, and pin 1 of each probe header is GND
    # (Test 30: 0.2 ohm to M6 pin 3), pin 2 the feed. Each interposer pair is a header for the probe's
    # own plug (_IN) and a header for a 2547HA203-to-2547HA203 jumper to the control board (_OUT).
    # Front end per George's decisions 2026-11-08: "Measure 0-5.5 V, survive 24 V", then, on the
    # follow-up questions, "1 MΩ series" and "Accept 0–5.0 V". So: 1M series R + clamp diodes into
    # a high-impedance follower on +5V (reads 0 to ~5.0 V), then a divider into the ADS1115. Only
    # the feed pin is buffered (the GND pin is known now).
    Part('J6', 'S1_IN (steam probe plug)', FP_EX2, 'F1', 'EXCON 254702WV203', '', HAND,
         note='1 GND, 2 S1 feed (Test 29/30). EXCON 2547 probable: caliper-confirm before ordering'),
    Part('J7', 'S1_OUT (to control board M2)', FP_EX2, 'F1', 'EXCON 254702WV203', '', HAND,
         note='same pin order as J6; jumper = 2 x 254702HA203 + 254700TC351 terminals'),
    Part('J8', 'S2+SB_IN (group probe + steam level plug)', FP_EX4, 'F2', 'EXCON 254704WV203', '', HAND,
         note='1 GND, 2 S2 feed, 3 SB level probe, 4 level return (Test 29). Caliper-confirm (~12.7 mm wide)'),
    Part('J9', 'S2+SB_OUT (to control board M3)', FP_EX4, 'F2', 'EXCON 254704WV203', '', HAND,
         note='same pin order as J8; jumper = 2 x 254704HA203 + 254700TC351 terminals'),
    Part('U6', 'MCP6004', FP_SOIC14, 'F1', 'MCP6004T-I/SL (Microchip)', 'C7378', EXTENDED,
         note='quad CMOS RRIO, IB +-1 pA typ, 1.8-6.0 V (DS20001733L). A = S1, B = S2, C/D unused '
              '(followers with IN+ at VSS: inside the RRIO common-mode range)'),
    C('C8', '100nF', C_100N, 'F1', note='U6 VDD decoupling (U6 on +5V)'),
    R('R5', '1M', R_1M, 'F1', note='S1 series R, George 2026-11-08 "1 MΩ series". 24 V: (24-5.3) V / 1M = 19 uA '
      'into the clamp (MCP6004 input pin +-2 mA). Interposer unpowered: ~0.3 C shift at the control board, '
      'vs ~3 C at 100k (5 V / 15k model, Test 30)'),
    R('R6', '1M', R_1M, 'F2', note='S2 series R (as R5)'),
    Part('D2', **BAV99, func='F1', note='clamp S1_IN to +5V / GND. Leakage <= 25 nA (Diodes ds12007, at 20 V) x 1M '
         '= <= 25 mV worst case at the follower (~0.6 C at 94 C); <= 0.4 mV at the node through the ~15k feed'),
    Part('D3', **BAV99, func='F2', note='clamp S2_IN to +5V / GND'),
    R('R9', '10k', R_10K, 'F1', note='divider top: node x 5.1/15.1 = 0.338. The follower tops out at ~5.0 V '
      '-> 1.69 V, 83 % of the ADS1115 +-2.048 V FSR (SBAS444E PGA table). Kept for "Accept 0–5.0 V": '
      'a closer ratio would need a new resistor value for < 1 bit'),
    R('R10', '10k', R_10K, 'F2', note='divider top'),
    R('R13', '5.1k', R_5K1, 'F1', note='divider bottom; also bounds AIN to 0.338 x 5 V = 1.69 V < VDD + 0.3'),
    R('R14', '5.1k', R_5K1, 'F2', note='divider bottom'),
    C('C9', '100nF', C_100N, 'F1', note='AIN0 filter: 3.4k divider source x 100n = 0.34 ms'),
    C('C10', '100nF', C_100N, 'F2', note='AIN1 filter'),
    Part('U7', 'ADS1115', FP_VSSOP10, 'F1', 'ADS1115IDGSR (TI)', 'C37593', EXTENDED,
         note='VDD = 3V3 so SDA/SCL VIH (0.7 VDD) suits the 3V3 bus; ADDR = GND -> 0x48 (SBAS444E). '
              'AIN0 = S1, AIN1 = S2, AIN2/AIN3 tied to GND (unused; GND is inside the input range)'),
    C('C13', '100nF', C_100N, 'F1', note='ADS1115 VDD decoupling (SBAS444E pin table)'),
    R('R21', '10k', R_10K, 'F1', note='ALERT/RDY open-drain pull-up'),

    # --- F3/F4 SB/SL level taps: pass-through + DNP AC-coupled front-end (plan §3.3) ----------
    # SB rides on J8/J9 pins 3 (probe) and 4 (return). SL = control board M10, 2-pin (Test 29);
    # its method and pin roles are M5 (Test 32, not done).
    Part('J12', 'SL_IN (tank sensor plug)', FP_EX2, 'F4', 'EXCON 254702WV203', '', HAND,
         note='M10 tank level. Which pin is signal vs return: PLACEHOLDER until M5. Pin 2 pass-through only'),
    Part('J13', 'SL_OUT (to control board M10)', FP_EX2, 'F4', 'EXCON 254702WV203', '', HAND, note='mirrors J12'),
    C('C14', '100nF', C_100N, 'F3', dnp=True, note='SB series coupling C: the ONLY thing on the probe line. Value + V rating PLACEHOLDER (M4)'),
    C('C15', '100nF', C_100N, 'F4', dnp=True, note='SL series coupling C. PLACEHOLDER (M5)'),
    R('R22', '100k', R_100K, 'F3', dnp=True, note='series R after the coupling C'),
    R('R23', '100k', R_100K, 'F4', dnp=True),
    R('R24', '1M', R_1M, 'F3', dnp=True, note='mid-rail bias top (bias stays on our side of C14)'),
    R('R25', '1M', R_1M, 'F4', dnp=True),
    R('R26', '1M', R_1M, 'F3', dnp=True, note='mid-rail bias bottom'),
    R('R27', '1M', R_1M, 'F4', dnp=True),
    Part('D6', **BAV99, func='F3', dnp=True, note='clamp SB_FE to 3V3/GND'),
    Part('D7', **BAV99, func='F4', dnp=True, note='clamp SL_FE to 3V3/GND'),

    # --- F5 flow tap: 06-015 circuit (J1/J2/J3/U1/C1) + ESP32 buffer (plan §3.4) ----------------
    # Control board M6 is the same EXCON 2547 family as the sensor headers (Test 29), not JST XH.
    # Test 36 (George 2026-11-08, meter unplugged): P2 (+, red) = 3.3 V, P4 (o, white) = 4.9 V,
    # P3 = GND (black), P1 blank key. Everything on M6 is <= 5 V; the forum's 14.3 V does not apply.
    Part('J1', 'GICAR_meter', FP_EX4, 'F5', 'EXCON 254704WV203', '', HAND,
         note='M6 order (Test 36): 1 key-blank, 2 + supply ~3.3 V (red), 3 GND (black), 4 signal o (white)'),
    Part('J2', 'to_Vivaldi (control board M6)', FP_EX4, 'F5', 'EXCON 254704WV203', '', HAND,
         note='mirrors J1; jumper = 2 x 254704HA203 + 254700TC351 terminals'),
    Part('J3', 'to_ito_IMPULSE', FP_XH3, 'F5', 'JST B3B-XH-A', '', HAND, note='06-015: 1 GND, 2 OUT, 3 +5V (ito)'),
    Part('U1', **LVC1G17, func='F5', note='06-015 buffer on ito 5V (pins 1 NC, 2 A, 3 GND, 4 Y, 5 VCC)'),
    C('C1', '100nF', C_100N, 'F5', note='06-015 U1 decoupling (ito 5V domain)'),
    Part('U2', **LVC1G17, func='F5', note='ESP32 flow buffer on 3V3; A input 5 V OK at VCC 3.3 V (SCES351Y VI 0..5.5 V)'),
    C('C2', '100nF', C_100N, 'F5', note='U2 decoupling'),

    # --- F6 ito ENC interposer (plan §3.5; Tests 33, 34) -----------------------------------------
    # Test 33: the encoder sits on the display board V1.3; its cable carries SW/A/B only (hole 1
    # empty, GND reaches the display board over SPI), each through a 4.7k series R (R1-R3) on the
    # display board. ito ENC pin 1 is GND. Test 34: SW/A/B idle at 5.05 V (ito pull-ups), A/B open
    # at detents, SW pressed = 0 V. So: 3 lines, pull-low only, nothing masked at rest.
    Part('J14', 'ENC_IN (encoder cable plug)', FP_KK4, 'F6', 'Molex 22-27-2041', '', HAND,
         note='Test 33: 1 empty (no wire), 2 SW, 3 A, 4 B'),
    Part('J15', 'ENC_OUT (to ito ENC)', FP_KK4, 'F6', 'Molex 22-27-2041', '', HAND,
         note='ito manual p.63 = Test 33: 1 GND, 2 SW, 3 A, 4 B. Pin 1 carries our GND to ito (the FET return)'),
    Part('Q1', **AO3400A, func='F6', note='open-drain pull-down on ENC_A (G1 S2 D3, AOS DS rev 3.1)'),
    Part('Q2', **AO3400A, func='F6', note='open-drain pull-down on ENC_B'),
    Part('Q3', **AO3400A, func='F6', note='open-drain pull-down on ENC_SW'),
    R('R28', '1k', R_1K, 'F6', note='gate series R'),
    R('R29', '1k', R_1K, 'F6'),
    R('R30', '1k', R_1K, 'F6'),
    R('R31', '100k', R_100K, 'F6', note='gate pull-down: FET stays OFF while the ESP32 is unpowered / booting'),
    R('R32', '100k', R_100K, 'F6'),
    R('R33', '100k', R_100K, 'F6'),
    Part('U8', **LVC1G17, func='F6', note='5V-safe read-back of ENC_A (Ioff: no load when 3V3 is off)'),
    Part('U9', **LVC1G17, func='F6', note='read-back of ENC_B'),
    Part('U10', **LVC1G17, func='F6', note='read-back of ENC_SW'),
    C('C16', '100nF', C_100N, 'F6'),
    C('C17', '100nF', C_100N, 'F6'),
    C('C18', '100nF', C_100N, 'F6'),

    # --- F7 shared I2C (plan §3.6) ---------------------------------------------------------------
    Part('J16', 'Qwiic', FP_SH4, 'F7', 'SM04B-SRSS-TB(LF)(SN) (JST)', 'C160404', EXTENDED,
         note='Qwiic: 1 GND, 2 3V3, 3 SDA, 4 SCL (sparkfun.com/qwiic)'),
    R('R34', '4.7k', R_4K7, 'F7', note='SDA pull-up to 3V3'),
    R('R35', '4.7k', R_4K7, 'F7', note='SCL pull-up to 3V3'),
    Part('U11', 'PCA9306', FP_VSSOP8_DCU, 'F7', 'PCA9306DCUR (TI)', 'C33196', EXTENDED, dnp=True,
         note='3V3 <-> ito 5V I2C translator, isolated by default (SCPS113O). KiCad VSSOP-8 2.3x2 vs TI DCU land: check at layout'),
    R('R36', '200k', R_200K, 'F7', dnp=True, note='EN = VREF2 tied to ito 5V through 200k (SCPS113O §8.1.2)'),
    R('R37', '4.7k', R_4K7, 'F7', dnp=True, note='SDA2 pull-up to ito 5V (fit only if ito has none)'),
    R('R38', '4.7k', R_4K7, 'F7', dnp=True, note='SCL2 pull-up to ito 5V'),
    Part('JP2', 'EXP_SDA link', FP_SJ2_OPEN, 'F7', note='open by default: no multi-master in rev A'),
    Part('JP3', 'EXP_SCL link', FP_SJ2_OPEN, 'F7', note='open by default'),
    Part('J17', 'ito EXPANSION pads', FP_HDR5, 'F7', jlc=HAND, dnp=True,
         note='EXP pads 1..5 (manual p.59): 1 +5V, 2 GND, 3 +3.3V (NC here), 4 SCK, 5 SDA. Pitch/pad form PLACEHOLDER (not measured)'),

    # --- F8 SER stub (plan §3.7) -----------------------------------------------------------------
    Part('J18', 'SER stub', FP_HDR6, 'F8', jlc=HAND, dnp=True, note='1 GND, 2 3V3 (via R39), 3 TX, 4 RX, 5 IO1, 6 IO2'),
    R('R39', '0', R_0, 'F8', dnp=True, note='3V3 to the stub header only when rev B wants it'),
    R('R40', 'TBD', TBD, 'F8', dnp=True, note='TX series R. PLACEHOLDER until M8 / Saleae capture'),
    R('R41', 'TBD', TBD, 'F8', dnp=True, note='RX series R'),
    R('R42', 'TBD', TBD, 'F8', dnp=True, note='IO1 series R'),
    R('R43', 'TBD', TBD, 'F8', dnp=True, note='IO2 series R'),
    R('R44', 'TBD', TBD, 'F8', dnp=True, note='TX divider bottom'),
    R('R45', 'TBD', TBD, 'F8', dnp=True, note='RX divider bottom'),
    R('R46', 'TBD', TBD, 'F8', dnp=True, note='IO1 divider bottom'),
    R('R47', 'TBD', TBD, 'F8', dnp=True, note='IO2 divider bottom'),
    Part('D8', **BAV99, func='F8', dnp=True, note='TX clamp'),
    Part('D9', **BAV99, func='F8', dnp=True, note='RX clamp'),
    Part('D10', **BAV99, func='F8', dnp=True, note='IO1 clamp'),
    Part('D11', **BAV99, func='F8', dnp=True, note='IO2 clamp'),

    # --- F8b M9 "RS232 serial / Seriale 232" tap (Test 29 case sticker) ---------------------------
    # M9 is a 4-pin EXCON header on the control board with nothing plugged in. Its pin roles and
    # levels are unknown: SCOPE BEFORE CONNECTING. J20 breaks every M9 pin out to J21.1-4. Two
    # paths to UART2, both open until M9 is scoped and one is chosen (George 2026-11-08):
    #  * passive (DNP): R49 TX series, R50/R51 RX divider, D12 clamp -> wire links on J21.5/.6
    #  * RS-232 transceiver (FITTED, "Add a DNP transceiver footprint", then "why wouldn't we place
    #    the transceiver if it's cheap?"): U13 MAX3232 + charge-pump caps, line side through DNP 0R
    #    R52/R53 to J22, logic RX through DNP 0R R54.
    # The links stay open because U13's driver swings about +-5.4 V (SLLS410O VOH/VOL at 3 kOhm): into
    # a 5 V logic input on the control board's MCU that could damage the machine. RS-232 is also
    # inverted vs TTL (ESP32 UART can invert in software).
    Part('J20', 'M9 RS232 tap (cable to control board M9)', FP_EX4, 'F8', 'EXCON 254704WV203', '', HAND, dnp=True,
         note='pin roles unknown; EXCON 2547 probable (Test 29)'),
    Part('J21', 'M9 link field', FP_HDR6, 'F8', jlc=HAND, dnp=True,
         note='1-4 = M9 pins 1-4 (via J20); 5 = passive TX side; 6 = passive RX side. Wire-link after scoping'),
    R('R49', 'TBD', TBD, 'F8', dnp=True, note='passive path: M9 TX series R. PLACEHOLDER until M9 is scoped'),
    R('R50', 'TBD', TBD, 'F8', dnp=True, note='passive path: M9 RX series R (divider top)'),
    R('R51', 'TBD', TBD, 'F8', dnp=True, note='passive path: M9 RX divider bottom'),
    Part('D12', **BAV99, func='F8', dnp=True, note='passive path: M9 RX clamp to 3V3 / GND'),
    Part('U13', 'MAX3232', FP_SOIC16, 'F8', 'MAX3232EIDR (TI)', 'C193666', EXTENDED,
         note='2 drivers + 2 receivers, 3-5.5 V, 250 kbit/s, +-15 kV ESD (TI SLLS410O, Jun 2021). VCC = 3V3. '
              'Pins 1 C1+, 2 V+, 3 C1-, 4 C2+, 5 C2-, 6 V-, 7 DOUT2, 8 RIN2, 9 ROUT2, 10 DIN2, 11 DIN1, '
              '12 ROUT1, 13 RIN1, 14 DOUT1, 15 GND, 16 VCC (Table 5-1). Channel 2 unused'),
    C('C19', '100nF', C_100N, 'F8', note='U13 C1 (C1+/C1-): 0.1 uF at VCC 3.3 V (SLLS410O Table 9-1)'),
    C('C20', '100nF', C_100N, 'F8', note='U13 C2 (C2+/C2-)'),
    C('C21', '100nF', C_100N, 'F8', note='U13 C3: V+ to GND (Fig 9-1: C3 to VCC or GND). 50 V part vs V+ <= 7 V'),
    C('C22', '100nF', C_100N, 'F8', note='U13 C4: GND (+) to V- (-), Fig 9-1'),
    C('C23', '100nF', C_100N, 'F8', note='U13 VCC bypass 0.1 uF (Fig 9-1)'),
    R('R55', '10k', R_10K, 'F8', note='M9_TX pull-up: holds U13 DIN1 at a valid level (idle high = UART mark) while '
      'GPIO21 is unconfigured; SLLS410O §8.3.2, §9.2.2: DIN must be valid low or high, and DIN input current is only +-1 uA (§6.6), so no internal pull'),
    R('R52', '0', R_0, 'F8', dnp=True, note='LINK, open until M9 is scoped: U13 DOUT1 -> J22.1'),
    R('R53', '0', R_0, 'F8', dnp=True, note='LINK, open until M9 is scoped: J22.2 -> U13 RIN1 (open RIN = ROUT high, SLLS410O §8.3.3)'),
    R('R54', '0', R_0, 'F8', dnp=True, note='LINK: U13 ROUT1 -> GPIO38. Fit only on the transceiver path '
      '(ROUT1 is push-pull and would fight the passive RX path)'),
    Part('J22', 'M9 RS-232 link pads', FP_HDR2, 'F8', jlc=HAND, dnp=True,
         note='1 = transceiver TX line (via R52), 2 = transceiver RX line (via R53). Wire-link to J21.1-4 after scoping'),

    # --- F9 on/off dry contact (plan §3.8) -------------------------------------------------------
    Part('U12', 'TLP222A', FP_DIP4, 'F9', 'TLP222A(TP1,F) (Toshiba)', 'C2152279', EXTENDED, dnp=True,
         note='photorelay; JLC lists package "DIP-4". Pinout 1 A / 2 K / 3,4 contact: datasheet NOT read, verify'),
    R('R48', '330', R_330, 'F9', dnp=True, note='LED current R. PLACEHOLDER: size from the TLP222A datasheet IFT'),
    Part('J19', 'ON/OFF contact', FP_HDR2, 'F9', jlc=HAND, dnp=True, note='to the panel ON/OFF pin pair, if M8 finds one'),
]

# ---------------------------------------------------------------------------------------------
# ESP32-S3-WROOM-1 module pin <-> GPIO (module datasheet v1.8, Table 3-1 Pin Definitions)
# ---------------------------------------------------------------------------------------------
ESP32_PIN_OF_GPIO = {
    4: 4, 5: 5, 6: 6, 7: 7, 15: 8, 16: 9, 17: 10, 18: 11, 8: 12, 19: 13, 20: 14, 3: 15,
    46: 16, 9: 17, 10: 18, 11: 19, 12: 20, 13: 21, 14: 22, 21: 23, 47: 24, 48: 25, 45: 26,
    0: 27, 35: 28, 36: 29, 37: 30, 38: 31, 39: 32, 40: 33, 41: 34, 42: 35, 44: 36, 43: 37,
    2: 38, 1: 39,
}
ESP32_POWER_PINS = {'GND': (1, 40, 41), '3V3': (2,), 'EN': (3,)}


def esp(gpio: int) -> str:
    """'U5.<module pin>' for a GPIO number."""
    return f'U5.{ESP32_PIN_OF_GPIO[gpio]}'


# GPIO allocation: GPIO number -> (net, direction, note). check_circuit.py verifies each against
# NETS and against the strapping / flash / PSRAM / USB rules.
GPIO = {
    0: ('BOOT', 'strap', 'SW2 + R4 only (strapping pin: boot mode)'),
    1: ('SB_FE', 'analog in', 'ADC1_CH0: SB level front-end (DNP until M4)'),
    2: ('SL_FE', 'analog in', 'ADC1_CH1: SL level front-end (DNP until M5)'),
    4: ('ENC_INJ_A', 'out', 'gate of Q1 (pull ENC_A low)'),
    5: ('ENC_INJ_B', 'out', 'gate of Q2'),
    6: ('ENC_INJ_SW', 'out', 'gate of Q3'),
    7: ('ENC_RD_A', 'in', 'U8 read-back'),
    8: ('I2C_SDA', 'i2c', 'ADS1115 + Qwiic (+ DNP PCA9306)'),
    9: ('I2C_SCL', 'i2c', ''),
    10: ('ADS_ALERT', 'in', 'ADS1115 ALERT/RDY (optional; conversion-ready)'),
    11: ('FLOW_3V3', 'in', 'pulse_counter from U2'),
    12: ('ONOFF_DRV', 'out', 'F9 photorelay LED (DNP)'),
    13: ('SER_IO1', 'io', 'F8 stub spare 1 (DNP)'),
    14: ('SER_IO2', 'io', 'F8 stub spare 2 (DNP)'),
    15: ('ENC_RD_B', 'in', 'U9 read-back'),
    16: ('ENC_RD_SW', 'in', 'U10 read-back'),
    17: ('SER_TX', 'out', 'U1TXD default (F8 stub, DNP)'),
    18: ('SER_RX', 'in', 'U1RXD default (F8 stub, DNP)'),
    19: ('USB_DN', 'usb', 'USB_D- (fixed function)'),
    20: ('USB_DP', 'usb', 'USB_D+ (fixed function)'),
    21: ('M9_TX', 'out', 'UART2 TX via the GPIO matrix: U13 DIN1 + R55 pull-up; passive R49 (DNP)'),
    38: ('M9_RX', 'in', 'UART2 RX via the GPIO matrix: U13 ROUT1 via R54 or passive R50 (both DNP links)'),
}

# Rules the checker enforces (module datasheet v1.8 §3 Table 3-1 notes, §4 Table 4-1):
STRAPPING_GPIO = {0, 3, 45, 46}  # Table 4-1
OCTAL_PSRAM_GPIO = {35, 36, 37}  # Table 3-1 note b: used by octal PSRAM on R8/R16V variants
NOT_LED_OUT_GPIO = {22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34}  # absent from Table 3-1
USB_GPIO = {19: 'USB_DN', 20: 'USB_DP'}  # Table 3-1: IO19 = USB_D-, IO20 = USB_D+
UART0_GPIO = {43, 44}  # TXD0/RXD0: kept free for the ROM console
ADC1_GPIO = set(range(1, 11))  # GPIO1..10 = ADC1_CH0..9 (Table 3-1). ADC2 is unusable with Wi-Fi
ANALOG_NETS = {'SB_FE', 'SL_FE'}

# ---------------------------------------------------------------------------------------------
# Netlist. "REF.pad". Order inside a list carries no meaning.
# ---------------------------------------------------------------------------------------------
NETS: dict[str, list[str]] = {
    # ---- F5 flow (06-015 net names kept) ----
    'N_PLUS': ['J1.2', 'J2.2'],  # meter supply, ~3.3 V on this machine (Test 36): pass-through ONLY
    'N_O': ['J1.4', 'J2.4', 'U1.2', 'U2.2'],
    'V5_ITO': ['J3.3', 'U1.5', 'C1.1'],  # ito's 5 V. Never meets +5V or +3V3
    'N_OUT': ['U1.4', 'J3.2'],
    'FLOW_3V3': ['U2.4', esp(11)],
    # ---- F0 power ----
    '+5V': ['J4.1', 'D1.1', 'U4.3', 'C3.1', 'U6.4', 'C8.1', 'D2.2', 'D3.2'],
    'VBUS': ['J5.A4', 'J5.A9', 'J5.B4', 'J5.B9', 'D1.2', 'U3.5'],
    'CC1': ['J5.A5', 'R1.1'],
    'CC2': ['J5.B5', 'R2.1'],
    # USBLC6 pins 1/6 (I/O1) and 3/4 (I/O2) are one flow-through line each -> one net each
    'USB_DP': ['J5.A6', 'J5.B6', 'U3.1', 'U3.6', esp(20)],
    'USB_DN': ['J5.A7', 'J5.B7', 'U3.3', 'U3.4', esp(19)],
    '+3V3': [
        'U4.2', 'C4.1', 'U5.2', 'C5.1', 'C6.1', 'R3.1', 'R4.1',
        'U2.5', 'C2.1',
        'U7.8', 'C13.1', 'R21.1',
        'U8.5', 'U9.5', 'U10.5', 'C16.1', 'C17.1', 'C18.1',
        'J16.2', 'R34.1', 'R35.1', 'U11.2',
        'R24.1', 'R25.1', 'D6.2', 'D7.2',
        'R39.1', 'D8.2', 'D9.2', 'D10.2', 'D11.2', 'D12.2',
        'U13.16', 'C23.1', 'R55.1',
    ],
    'EN': ['U5.3', 'R3.2', 'C7.1', 'SW1.1'],
    'BOOT': [esp(0), 'R4.2', 'SW2.1'],
    # ---- F1/F2 NTC taps (pin 1 of each probe header is GND, pin 2 the feed: Test 30) ----
    'S1_FEED': ['J6.2', 'J7.2', 'R5.1'],
    'S2_FEED': ['J8.2', 'J9.2', 'R6.1'],
    'S1_IN': ['R5.2', 'U6.3', 'D2.3'],  # op-amp A IN+
    'S2_IN': ['R6.2', 'U6.5', 'D3.3'],  # op-amp B IN+
    'S1_BUF': ['U6.1', 'U6.2', 'R9.1'],  # OUTA tied to INA-
    'S2_BUF': ['U6.7', 'U6.6', 'R10.1'],  # OUTB - INB-
    'S1_ADC': ['R9.2', 'R13.1', 'C9.1', 'U7.4'],  # AIN0
    'S2_ADC': ['R10.2', 'R14.1', 'C10.1', 'U7.5'],  # AIN1
    'U6C_FB': ['U6.8', 'U6.9'],  # unused C: OUTC - INC- (follower)
    'U6D_FB': ['U6.14', 'U6.13'],  # unused D: OUTD - IND-
    'ADS_ALERT': ['U7.2', 'R21.2', esp(10)],
    # ---- F3/F4 levels ----
    'SB_PROBE': ['J8.3', 'J9.3', 'C14.1'],
    'SB_AUX': ['J8.4', 'J9.4'],  # level return to the boiler body (= earth): pure pass-through
    'SB_AC': ['C14.2', 'R22.1'],
    'SB_FE': ['R22.2', 'R24.2', 'R26.1', 'D6.3', esp(1)],
    'SL_PROBE': ['J12.1', 'J13.1', 'C15.1'],
    'SL_AUX': ['J12.2', 'J13.2'],
    'SL_AC': ['C15.2', 'R23.1'],
    'SL_FE': ['R23.2', 'R25.2', 'R27.1', 'D7.3', esp(2)],
    # ---- F6 ENC ----
    'ENC_SW': ['J14.2', 'J15.2', 'Q3.3', 'U10.2'],
    'ENC_A': ['J14.3', 'J15.3', 'Q1.3', 'U8.2'],
    'ENC_B': ['J14.4', 'J15.4', 'Q2.3', 'U9.2'],
    'ENC_INJ_A': [esp(4), 'R28.1'],
    'ENC_INJ_B': [esp(5), 'R29.1'],
    'ENC_INJ_SW': [esp(6), 'R30.1'],
    'ENC_G_A': ['R28.2', 'R31.1', 'Q1.1'],
    'ENC_G_B': ['R29.2', 'R32.1', 'Q2.1'],
    'ENC_G_SW': ['R30.2', 'R33.1', 'Q3.1'],
    'ENC_RD_A': ['U8.4', esp(7)],
    'ENC_RD_B': ['U9.4', esp(15)],
    'ENC_RD_SW': ['U10.4', esp(16)],
    # ---- F7 I2C ----
    'I2C_SDA': [esp(8), 'U7.9', 'R34.2', 'J16.3', 'U11.4'],
    'I2C_SCL': [esp(9), 'U7.10', 'R35.2', 'J16.4', 'U11.3'],
    'EXP_VREF2': ['U11.7', 'U11.8', 'R36.1'],
    'ITO_EXP_5V': ['J17.1', 'R36.2', 'R37.2', 'R38.2'],  # ito's 5 V via EXPANSION. Never meets +3V3
    'EXP_SDA_T': ['U11.5', 'R37.1', 'JP2.1'],
    'EXP_SCL_T': ['U11.6', 'R38.1', 'JP3.1'],
    'EXP_SDA': ['JP2.2', 'J17.5'],
    'EXP_SCL': ['JP3.2', 'J17.4'],
    # ---- F8 SER stub ----
    'SER_3V3_H': ['R39.2', 'J18.2'],
    'SER_TX_H': ['J18.3', 'R40.1'],
    'SER_RX_H': ['J18.4', 'R41.1'],
    'SER_IO1_H': ['J18.5', 'R42.1'],
    'SER_IO2_H': ['J18.6', 'R43.1'],
    'SER_TX': ['R40.2', 'R44.1', 'D8.3', esp(17)],
    'SER_RX': ['R41.2', 'R45.1', 'D9.3', esp(18)],
    'SER_IO1': ['R42.2', 'R46.1', 'D10.3', esp(13)],
    'SER_IO2': ['R43.2', 'R47.1', 'D11.3', esp(14)],
    # ---- F8b M9 RS232 tap (DNP) ----
    'M9_P1': ['J20.1', 'J21.1'],
    'M9_P2': ['J20.2', 'J21.2'],
    'M9_P3': ['J20.3', 'J21.3'],
    'M9_P4': ['J20.4', 'J21.4'],
    'M9_TX_H': ['J21.5', 'R49.2'],
    'M9_TX': ['R49.1', esp(21), 'U13.11', 'R55.2'],
    'M9_RX_H': ['J21.6', 'R50.1'],
    'M9_RX': ['R50.2', 'R51.1', 'D12.3', esp(38), 'R54.2'],
    'RS_DOUT1': ['U13.14', 'R52.1'],
    'RS_TX_H': ['R52.2', 'J22.1'],
    'RS_RX_H': ['J22.2', 'R53.1'],
    'RS_RIN1': ['R53.2', 'U13.13'],
    'RS_ROUT1': ['U13.12', 'R54.1'],
    'MAX_C1P': ['U13.1', 'C19.1'],
    'MAX_C1N': ['U13.3', 'C19.2'],
    'MAX_C2P': ['U13.4', 'C20.1'],
    'MAX_C2N': ['U13.5', 'C20.2'],
    'MAX_VP': ['U13.2', 'C21.1'],
    'MAX_VN': ['U13.6', 'C22.2'],
    # ---- F9 on/off ----
    'ONOFF_DRV': [esp(12), 'R48.1'],
    'ONOFF_LED': ['R48.2', 'U12.1'],
    'ONOFF_C1': ['U12.4', 'J19.1'],
    'ONOFF_C2': ['U12.3', 'J19.2'],
    # ---- the one ground: ESP32 GND = ito GND = control-board LV GND. M1 / Test 28: isolated from
    # mains (PS1 Lauma SMR30.10, Class II); bonded to chassis earth via M3 pin 4 (Test 30) ----
    'GND': [
        'J1.3', 'J2.3', 'J3.1', 'U1.3', 'C1.2', 'U2.3', 'C2.2',
        'J4.2', 'J5.A1', 'J5.A12', 'J5.B1', 'J5.B12', 'J5.S1', 'U3.2', 'R1.2', 'R2.2',
        'U4.1', 'C3.2', 'C4.2', 'U5.1', 'U5.40', 'U5.41', 'C5.2', 'C6.2', 'C7.2', 'SW1.2', 'SW2.2',
        'J6.1', 'J7.1', 'J8.1', 'J9.1',
        'U6.11', 'U6.10', 'U6.12', 'C8.2', 'D2.1', 'D3.1',
        'R13.2', 'R14.2', 'C9.2', 'C10.2',
        'U7.1', 'U7.3', 'U7.6', 'U7.7', 'C13.2',
        'R26.2', 'R27.2', 'D6.1', 'D7.1',
        'J15.1', 'Q1.2', 'Q2.2', 'Q3.2', 'R31.2', 'R32.2', 'R33.2',
        'U8.3', 'U9.3', 'U10.3', 'C16.2', 'C17.2', 'C18.2',
        'J16.1', 'J16.MP', 'U11.1', 'J17.2',
        'J18.1', 'R44.2', 'R45.2', 'R46.2', 'R47.2', 'D8.1', 'D9.1', 'D10.1', 'D11.1',
        'R51.2', 'D12.1',
        'U13.15', 'U13.10', 'C21.2', 'C22.1', 'C23.2',
        'U12.2',
    ],
}

# Pads deliberately unconnected (the checker requires every pad to be in NETS or here).
NC: dict[str, str] = {
    'J1.1': 'GICAR key-blank (Test 36: M6 P1 blank)',
    'J2.1': 'GICAR key-blank',
    'J14.1': 'encoder cable hole 1 is empty: no GND carried (Test 33)',
    'U13.7': 'MAX3232 DOUT2: channel 2 unused',
    'U13.8': 'MAX3232 RIN2: unused; an open receiver input reads high (SLLS410O §8.3.3)',
    'U13.9': 'MAX3232 ROUT2: unused output',
    'U1.1': '74LVC1G17 NC pin',
    'U2.1': '74LVC1G17 NC pin',
    'U8.1': '74LVC1G17 NC pin',
    'U9.1': '74LVC1G17 NC pin',
    'U10.1': '74LVC1G17 NC pin',
    'J5.A8': 'SBU1 unused',
    'J5.B8': 'SBU2 unused',
    'J17.3': 'ito EXPANSION +3.3 V (10 mA max): not used',
    'U5.15': 'GPIO3 strapping (JTAG source): left floating = datasheet default',
    'U5.16': 'GPIO46 strapping (boot mode / ROM print): weak pull-down default',
    'U5.26': 'GPIO45 strapping (VDD_SPI): weak pull-down default',
    'U5.24': 'GPIO47 spare',
    'U5.25': 'GPIO48 spare',
    'U5.28': 'GPIO35: octal-PSRAM pin on R8 variants; unused so a module swap stays safe',
    'U5.29': 'GPIO36: octal-PSRAM pin on R8 variants; unused',
    'U5.30': 'GPIO37: octal-PSRAM pin on R8 variants; unused',
    'U5.32': 'GPIO39 (MTCK) spare: kept for JTAG',
    'U5.33': 'GPIO40 (MTDO) spare: kept for JTAG',
    'U5.34': 'GPIO41 (MTDI) spare: kept for JTAG',
    'U5.35': 'GPIO42 (MTMS) spare: kept for JTAG',
    'U5.36': 'RXD0 (GPIO44): ROM console, free (add a test pad at layout)',
    'U5.37': 'TXD0 (GPIO43): ROM console, free (add a test pad at layout)',
}

# Coupling capacitors that are allowed to touch a level-probe line (plan §3.3).
LEVEL_PROBE_NETS = {'SB_PROBE': {'C14'}, 'SL_PROBE': {'C15'}}
LEVEL_AUX_NETS = {'SB_AUX', 'SL_AUX'}
FLOW_SUPPLY_NET = 'N_PLUS'  # GICAR meter supply: ~3.3 V measured (Test 36), forum said 14.3 V
ITO_5V_NETS = {'V5_ITO', 'ITO_EXP_5V'}
BOARD_RAILS = {'+3V3', '+5V', 'VBUS'}
# NTC feed lines: only the pass-through headers and one series R into a follower (plan §3.2).
NTC_SERIES = {'S1_FEED': 'R5', 'S2_FEED': 'R6'}
NTC_FOLLOWER_IN = {'S1_IN', 'S2_IN'}
# M9 tap: nets where the transceiver meets the machine side or the ESP32 RX pin. Every other part on
# them must be DNP (a link), so nothing reaches M9 until it is scoped (checker C11).
M9_LINK_NETS = {'RS_DOUT1': 'U13', 'RS_RIN1': 'U13', 'RS_ROUT1': 'U13', 'M9_TX_H': 'J21', 'M9_RX_H': 'J21'}

# ---------------------------------------------------------------------------------------------
# Placeholders: what is a stand-in, and which measurement closes it (plan "Open facts").
# ---------------------------------------------------------------------------------------------
PLACEHOLDERS = [
    # Closed 2026-11-08 (kept for the record): M1 Test 28 (GND isolated from mains; earth-bonded via
    # M3 pin 4), M6 Test 33 (KK 254, SW/A/B, hole 1 empty), M7 Test 34 (idle 5.05 V, open at
    # detents), M9 Test 36 (supply ~3.3 V, o 4.9 V). M2 is closed to "EXCON 2547, probable".
    ('M2', 'J1 J2 J6 J7 J8 J9 J12 J13 J20', 'EXCON 2547 is probable, not caliper-confirmed (Test 29): '
     'confirm the 4-pin header is ~12.7 mm wide (2.54 mm pitch) before ordering housings and boards.'),
    ('M3', 'R5 R6 D2 D3 U6 (VDD)', 'Live S1/S2 node voltages not measured (Test 30 live half waits for an '
     'EXCON extension lead). Estimate 1.5-4.7 V (5 V through ~15k). U6 on +5V reads 0 to ~5.0 V: George '
     '"Accept 0–5.0 V"; revisit in rev B if the live node sits near 5 V.'),
    ('M3', 'R5 R6 D2 D3', '1M series R (George "1 MΩ series"). T4 runs with the interposer powered AND '
     'unpowered (~0.3 C estimated unpowered shift). BAV99 leakage x 1M is <= 25 mV worst case at the '
     'follower: if T3 shows it matters, D2/D3 can go DNP (op-amp input diodes + 1M still limit 24 V to 19 uA).'),
    ('M3', 'firmware', 'Steam NTC curve: 201.7k @21 C, 6.8k hot at an unknown temperature; needs a second '
     'known point. Group: beta ~4340 K, R25 ~205k (Test 30).'),
    ('M4', 'C14 R22 R24 R26 D6', 'SB sensing method + excitation (Test 31 not done). SB is on J8/J9 pin 3, '
     'return pin 4 pass-through. Front-end DNP; C14 value/voltage not chosen.'),
    ('M5', 'J12 J13 C15 R23 R25 R27 D7', 'SL (M10) method and which pin is signal vs return (Test 32 not '
     'done). Pin 1 drawn as the tapped line, pin 2 pass-through only. Front-end DNP.'),
    ('M8', 'J18 R39-R47 D8-D11 U12 R48 J19', 'Panel link: 16-way ribbon on M1 seen (Test 35 partial); panel '
     'end and ON/OFF pair not reached. All DNP.'),
    ('M9-RS232', 'J20 J21 J22 R49-R54 D12', 'Control board M9 "RS232 serial" (case sticker, Test 29): pin '
     'roles and levels unknown. Scope before connecting, then fit ONE path: R52/R53/R54 (U13 MAX3232) or '
     'R49-R51/D12 (passive, values TBD) + wire links on J21/J22.'),
    ('M10', 'outline, jumper cables', 'Sites measured (Test 37): box 55x50 mm / 35 mm deep, beside ito '
     '70x50 / 25, opposite tank ~130x120 / 30+. Cable lengths to each connector NOT measured.'),
    ('datasheet', 'U12 R48', 'TLP222A datasheet not read (pinout, IFT); LCSC page says DIP-4.'),
    ('datasheet', 'J17', 'ito EXPANSION pad pitch/form not measured; drawn as a 2.54 mm 1x5 header.'),
]

def part(ref: str) -> Part:
    for p in PARTS:
        if p.ref == ref:
            return p
    raise KeyError(ref)


def pin_to_net() -> dict[str, str]:
    out: dict[str, str] = {}
    for net, pins in NETS.items():
        for pin in pins:
            out.setdefault(pin, net)
    return out


if __name__ == '__main__':
    fit = [p for p in PARTS if not p.dnp]
    print(f'{len(PARTS)} parts ({len(fit)} fitted, {len(PARTS) - len(fit)} DNP), {len(NETS)} nets')
    for f in sorted({p.func for p in PARTS}):
        refs = ' '.join(p.ref + ('*' if p.dnp else '') for p in PARTS if p.func == f)
        print(f'  {f}: {refs}')
    print('  (* = DNP)')
