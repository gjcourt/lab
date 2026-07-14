#!/usr/bin/env python3
"""
flash_ito.py — flash leva!/caffe! firmware to an ito ATMega1284 over the air.

The ito ATMega bootloader lives in a protected section and only the *application*
region is written, so a failed/garbled transfer is NOT fatal — re-enter the
bootloader and re-flash. XMODEM-CRC checks every 128-byte block, so corruption is
caught and retransmitted. The one real danger (identical for any tool) is flashing
*incompatible* firmware content — verify you're sending the right .hex.

Modes (verify BEFORE the real flash):
  backup   : connect to port 23, run `MCu`, capture the current settings dump.
  check    : NON-DESTRUCTIVE — enter the bootloader, print its menu, quit. No erase.
  loopback : OFFLINE — send the .hex to a local XMODEM receiver and prove it
             round-trips byte-for-byte. Never touches the board.
  flash    : the real thing (enter bootloader, `f`, XMODEM-CRC send .hex, `q`).
             Requires --yes.

Requires: pip install xmodem
"""
import argparse
import io
import socket
import sys
import threading
import time

try:
    from xmodem import XMODEM
except ImportError:
    sys.exit("Missing dependency: pip install xmodem (use the provided venv)")


def _sock(host, port, timeout=10):
    s = socket.create_connection((host, port), timeout=timeout)
    s.settimeout(1.0)
    return s


def _stream_io(sock):
    """getc/putc adapters the xmodem lib drives over a TCP socket."""
    def getc(size, timeout=1):
        sock.settimeout(timeout)
        try:
            data = sock.recv(size)
            return data or None
        except (socket.timeout, TimeoutError):
            return None

    def putc(data, timeout=1):
        sock.settimeout(timeout)
        try:
            sock.sendall(data)
            return len(data)
        except (socket.timeout, TimeoutError):
            return None
    return getc, putc


def _drain(sock, seconds, stop_byte=None):
    """Read+return whatever the board emits for `seconds`; stop early on stop_byte."""
    buf = b""
    end = time.monotonic() + seconds
    sock.settimeout(0.4)
    while time.monotonic() < end:
        try:
            chunk = sock.recv(256)
        except (socket.timeout, TimeoutError):
            continue
        if not chunk:
            break
        buf += chunk
        if stop_byte is not None and stop_byte in chunk:
            break
    return buf


# ---- modes ---------------------------------------------------------------

def cmd_backup(a):
    s = _sock(a.host, 23)
    hello = _drain(s, 2.0)
    print("connected, banner:", hello[:80])
    s.sendall(b"MCu\r")
    dump = _drain(s, 6.0)
    s.close()
    text = dump.decode("latin-1")
    if a.out:
        with open(a.out, "w") as f:
            f.write(text)
        print(f"settings dump -> {a.out} ({len(text)} bytes)")
    else:
        print(text)
    if "leva" not in hello.decode("latin-1", "ignore").lower() and not dump:
        print("WARN: didn't see a leva! banner / dump — check port 23 is reachable")


def cmd_check(a):
    """Non-destructive: enter bootloader, print menu, quit. No erase."""
    s = _sock(a.host, a.port)
    s.sendall(b"\r")               # first byte on 2323 resets ATMega into bootloader
    banner = _drain(s, 3.0)
    txt = banner.decode("latin-1", "ignore")
    print("--- bootloader said ---")
    print(txt.strip() or "(nothing)")
    ok = ("Connected to AVR" in txt) or ("(f)lash" in txt)
    s.sendall(b"q\r")              # exit WITHOUT flashing
    time.sleep(0.5)
    s.close()
    print("--- result:", "PASS — bootloader reachable, exited cleanly (no erase)"
          if ok else "FAIL — no bootloader menu seen")
    return 0 if ok else 1


def cmd_loopback(a):
    """Offline: XMODEM-CRC send the .hex to a local receiver; verify byte-identical."""
    with open(a.hex, "rb") as f:
        original = f.read()
    left, right = socket.socketpair()
    received = io.BytesIO()

    def receiver():
        g, p = _stream_io(right)
        XMODEM(g, p).recv(received, timeout=5, crc_mode=1)  # force CRC like the ito
        right.close()

    t = threading.Thread(target=receiver, daemon=True)
    t.start()
    time.sleep(0.2)
    g, p = _stream_io(left)
    sent = XMODEM(g, p).send(io.BytesIO(original), timeout=5)
    left.close()
    t.join(timeout=10)

    got = received.getvalue().rstrip(b"\x1a")   # XMODEM pads last block with SUB
    ok = sent and got == original
    print(f"sent={sent}  original={len(original)}B  received={len(got)}B  identical={got==original}")
    print("--- result:", "PASS — .hex round-trips byte-for-byte over XMODEM-CRC"
          if ok else "FAIL — transfer mismatch")
    return 0 if ok else 1


def cmd_flash(a):
    if not a.yes:
        sys.exit("Refusing to flash without --yes. Run `check` and `loopback` first, "
                 "and BACK UP settings (`backup`).")
    with open(a.hex, "rb") as f:
        payload = f.read()
    print(f"flashing {a.hex} ({len(payload)} bytes) to {a.host}:{a.port}")
    s = _sock(a.host, a.port)
    s.sendall(b"\r")
    banner = _drain(s, 3.0).decode("latin-1", "ignore")
    if "(f)lash" not in banner and "Connected to AVR" not in banner:
        s.close()
        sys.exit(f"Bootloader menu not seen; got: {banner!r}. Aborting (nothing erased).")
    print("bootloader up; sending 'f' (erase + await XMODEM-CRC)...")
    s.sendall(b"f\r")
    # consume the 'Formatting flash... Waiting for XMODEM-CRC...' text up to the first 'C';
    # the bootloader keeps re-sending 'C', so xmodem.send() will catch the next one.
    _drain(s, 4.0, stop_byte=ord("C"))
    g, p = _stream_io(s)
    ok = XMODEM(g, p).send(io.BytesIO(payload), retry=16, timeout=10)
    if ok:
        s.sendall(b"q\r")
        print("--- result: PASS — firmware sent, exited bootloader. Verify the machine boots.")
    else:
        print("--- result: FAIL — transfer did not complete. Bootloader is intact; just re-run.")
    time.sleep(0.5)
    s.close()
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["backup", "check", "loopback", "flash"])
    ap.add_argument("--host", default="10.42.7.11")
    ap.add_argument("--port", type=int, default=2323, help="flash port (2323)")
    ap.add_argument("--hex", help="path to firmware.hex (loopback/flash)")
    ap.add_argument("--out", help="backup: write settings dump to this file")
    ap.add_argument("--yes", action="store_true", help="flash: confirm the real write")
    a = ap.parse_args()
    if a.mode in ("loopback", "flash") and not a.hex:
        ap.error("--hex is required for loopback/flash")
    sys.exit({"backup": cmd_backup, "check": cmd_check,
              "loopback": cmd_loopback, "flash": cmd_flash}[a.mode](a))


if __name__ == "__main__":
    main()
