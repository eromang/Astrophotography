#!/usr/bin/env python3
"""
mount.py — CEM26 mount control via WiFi TCP bridge (iOptron RS-232 V3.10).

Subcommands:
    status [--watch [N]]     Live mount state (RA/Dec, alt/az, tracking, parked/slewing).
    health                   Pre-session readiness check; exits 0 if all pass, 1 if any fail.
    firmware                 Show installed firmware versions + gap vs latest available.
    park                     End-of-session: stop tracking, slew to park position, confirm.
    unpark                   Unpark + start sidereal tracking.
    timesync                 Push host's UTC/DST/offset to mount.
    goto <designation>       Look up target RA/Dec from vault, slew (ASIAIR must be disconnected).
    log [--session FILE]     Periodic state logger; writes NDJSON beside capture-session note.
        [--interval N]

Mount connection: TCP to 192.168.178.87:8899 (CEM26 WiFi APSTA mode, HBX8409 module).
The WiFi module is a TCP-to-Serial bridge — every TCP command is forwarded byte-for-byte
to the Go2Nova 8409 hand controller over its internal 115200 8N1 serial link.

Single-client invariant: do NOT run while ASIAIR is connected via USB-Serial.
Both clients writing to the same hand controller serial interface produces garbled responses.

Requirements:
    python3 -m pip install pyyaml    # only needed for `goto` vault target lookup

Run from the repo root:
    python3 scripts/mount.py status
    python3 scripts/mount.py health
    python3 scripts/mount.py log --interval 30
"""
from __future__ import annotations

import argparse
import json
import math
import os
import signal
import socket
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional


# ============================================================================
# Constants
# ============================================================================

MOUNT_IP = "192.168.178.87"
MOUNT_PORT = 8899
READ_DEADLINE_S = 5.0
CONNECT_TIMEOUT_S = 3.0
RECV_CHUNK = 256
RESPONSE_TERMINATOR = b"#"

# Tuntange balcony reference (for health-check location validation)
EXPECTED_LAT_DEG = 49.71731
EXPECTED_LON_DEG = 6.00823
LOCATION_TOLERANCE_DEG = 0.01  # ~1 km — accommodates mount's encoding rounding

# Firmware reference table — mirrors CEM26_GEM28_FirmwareVersionHistory.pdf cached
# in 01_Equipment/Manuals/CEM26/Firmware/. Each tuple is
# (release_label, hc_date, ra_date, dec_date, notes). Keep in sync with the PDF
# when iOptron publishes a new release.
FIRMWARE_HISTORY: list[tuple[str, str, str, str, str]] = [
    ("V20241201", "241201", "240518", "230305", "Communication overflow fix"),
    ("V20240518", "230305", "240518", "230305", "Go to SUN bug fix"),
    ("V20230305", "230305", "210420", "230305", "GPS display + minor bugs"),
    ("V20210422", "210422", "210420", "210420", "Star alignment recording"),
    ("V20210105", "210105", "210105", "210105", "EAF support, meridian limit +20°"),
    ("V20201030", "201030", "201030", "201030", "Initial release"),
]
LATEST_FIRMWARE = FIRMWARE_HISTORY[0]

# iOptron mount info codes (4 digits returned by :MountInfo#).
MOUNT_MODELS: dict[str, str] = {
    "0026": "CEM26",
    "0028": "GEM28",
    "0040": "CEM40 / CEM40EC",
    "0045": "GEM45 / GEM45EC",
    "0070": "CEM70 / CEM70EC",
    "0120": "CEM120 / CEM120EC / CEM120EC2",
}

# Fallback target catalog — mirrors scripts/fov_atlas.py:CATALOG.
# Keys are normalized designations (uppercase, spaces/hyphens stripped).
# Used when vault target notes don't carry ra_deg/dec_deg in their frontmatter.
# Keep in sync with fov_atlas.py.
TARGET_CATALOG: dict[str, tuple[str, float, float]] = {
    "M16":      ("M16 Eagle",            274.70, -13.78),
    "M17":      ("M17 Omega",            275.20, -16.18),
    "M42":      ("M42 Orion",             83.82,  -5.39),
    "M44":      ("M44 Beehive",          130.10,  19.67),
    "M45":      ("M45 Pleiades",          56.75,  24.12),
    "MEL111":   ("Mel 111 Coma",         186.00,  26.00),
    "M31":      ("M31 Andromeda",         10.68,  41.27),
    "M33":      ("M33 Triangulum",        23.46,  30.66),
    "NGC2244":  ("NGC 2244 Rosette",      97.98,   4.93),
    "NGC2264":  ("NGC 2264 Cone",        100.27,   9.87),
    "NGC1499":  ("NGC 1499 California",   60.38,  36.40),
    "NGC6960":  ("NGC 6960 W Veil",      311.12,  30.72),
    "NGC6992":  ("NGC 6992 E Veil",      313.18,  31.72),
    "NGC7000":  ("NGC 7000 N. America",  314.75,  44.52),
    "IC443":    ("IC 443 Jellyfish",      94.35,  22.57),
    "IC5070":   ("IC 5070 Pelican",      312.68,  44.35),
    "SH2-240":  ("Sh2-240 Simeis 147",    84.50,  28.00),
}

# Decoded enums for :GLS# state digits.
SYSTEM_STATES: dict[int, str] = {
    0: "stopped (non-zero position)",
    1: "tracking (PEC off)",
    2: "slewing",
    3: "auto-guiding",
    4: "meridian flipping",
    5: "tracking (PEC on)",
    6: "parked",
    7: "stopped at zero/home position",
}

TRACKING_RATES: dict[int, str] = {
    0: "sidereal",
    1: "lunar",
    2: "solar",
    3: "King",
    4: "custom",
}

BUTTON_SPEEDS: dict[int, str] = {
    1: "1x sidereal",
    2: "2x sidereal",
    3: "8x sidereal",
    4: "16x sidereal",
    5: "64x sidereal",
    6: "128x sidereal",
    7: "256x sidereal",
    8: "512x sidereal",
    9: "max",
}

TIME_SOURCES: dict[int, str] = {
    1: "RS-232/Ethernet",
    2: "hand controller",
    3: "GPS module",
}

# J2000 epoch for :SUT# / :GUT# Julian-time encoding.
# JD 2451545.0 = 2000-01-01 12:00:00 UTC
J2000_UNIX_TIMESTAMP = 946728000.0  # seconds


# ============================================================================
# Exceptions
# ============================================================================

class MountError(Exception):
    """Base class for mount communication errors."""


class MountUnreachable(MountError):
    """Couldn't open a TCP connection to the mount."""


class MountTimeout(MountError):
    """Mount didn't return a complete response (terminated by '#') within READ_DEADLINE_S."""


class MountResponseError(MountError):
    """Mount returned a malformed or unexpected response."""


# ============================================================================
# Parsed data types
# ============================================================================

@dataclass
class MountInfo:
    code: str       # 4 chars, e.g. "0026"
    name: str       # human-readable, e.g. "CEM26"


@dataclass
class FirmwareDates:
    """Pair of YYYY-MM-DD firmware dates returned by :FW1# / :FW2#."""
    first: str       # :FW1# -> HC date; :FW2# -> RA motor date
    second: str      # :FW1# -> main board date; :FW2# -> DEC motor date


@dataclass
class MountStatus:
    """Parsed :GLS# response (mount-wide state snapshot)."""
    longitude_deg: float
    latitude_deg: float
    gps_status: int                  # 0=no GPS / malfunction, 1=no data, 2=valid
    system_state: int                # 0-7 (see SYSTEM_STATES)
    system_state_name: str
    tracking_rate: int               # 0-4 (see TRACKING_RATES)
    tracking_rate_name: str
    button_speed: int                # 1-9 (see BUTTON_SPEEDS)
    button_speed_name: str
    time_source: int                 # 1-3 (see TIME_SOURCES)
    time_source_name: str
    hemisphere: str                  # "N" or "S"

    @property
    def is_parked(self) -> bool:
        return self.system_state == 6

    @property
    def is_slewing(self) -> bool:
        return self.system_state == 2

    @property
    def is_tracking(self) -> bool:
        return self.system_state in (1, 3, 5)

    @property
    def is_at_home(self) -> bool:
        return self.system_state == 7


@dataclass
class EquatorialPosition:
    """Parsed :GEP# response."""
    ra_deg: float                    # 0..360
    dec_deg: float                   # -90..+90
    pier_side: str                   # "E", "W", or "?"
    pointing_state: str              # "normal" or "counterweight up"


@dataclass
class AltAzPosition:
    """Parsed :GAC# response."""
    altitude_deg: float
    azimuth_deg: float


@dataclass
class MountTime:
    """Parsed :GUT# response."""
    utc_offset_min: int              # signed, +/- 720
    dst_observed: bool
    utc: datetime                    # decoded from Julian timestamp


@dataclass
class HealthCheckResult:
    name: str
    passed: bool
    detail: str


# ============================================================================
# Parsers
# ============================================================================

def _strip_response(raw: bytes | str) -> str:
    """Decode bytes->str and strip the trailing '#' terminator + any whitespace."""
    if isinstance(raw, bytes):
        raw = raw.decode("ascii", errors="replace")
    return raw.strip().rstrip("#")


def parse_mount_info(raw: bytes | str) -> MountInfo:
    """Parse :MountInfo# response — a 4-digit model code."""
    body = _strip_response(raw)
    if len(body) != 4 or not body.isdigit():
        raise MountResponseError(f"MountInfo response not 4 digits: {raw!r}")
    return MountInfo(code=body, name=MOUNT_MODELS.get(body, f"unknown ({body})"))


def parse_fw(raw: bytes | str) -> FirmwareDates:
    """Parse :FW1# or :FW2# response — two concatenated YYMMDD dates."""
    body = _strip_response(raw)
    if len(body) != 12 or not body.isdigit():
        raise MountResponseError(f"FW response not 12 digits: {raw!r}")
    first = f"20{body[0:2]}-{body[2:4]}-{body[4:6]}"
    second = f"20{body[6:8]}-{body[8:10]}-{body[10:12]}"
    return FirmwareDates(first=first, second=second)


def parse_gls(raw: bytes | str) -> MountStatus:
    """Parse :GLS# response — unified mount status (location + state).

    Format: sTTTTTTTTTTTTTTTTnnnnnn (23 chars including sign, plus '#').
        sign (1):        longitude sign (+ for East)
        lon (8):         longitude * 100 arcsec (East positive)
        lat (8):         (latitude + 90°) * 100 arcsec (North positive)
        gps (1):         0=malfunction/none, 1=no data, 2=valid
        system (1):      0..7 (see SYSTEM_STATES)
        tracking (1):    0..4 (see TRACKING_RATES)
        speed (1):       1..9 (see BUTTON_SPEEDS)
        time_src (1):    1..3 (see TIME_SOURCES)
        hemisphere (1):  0=S, 1=N
    """
    body = _strip_response(raw)
    if len(body) != 23 or body[0] not in "+-":
        raise MountResponseError(f"GLS response wrong length/format: {raw!r}")
    sign = 1 if body[0] == "+" else -1
    try:
        lon_arcsec = int(body[1:9]) * 0.01
        lat_plus90_arcsec = int(body[9:17]) * 0.01
        gps = int(body[17])
        sys_state = int(body[18])
        track = int(body[19])
        speed = int(body[20])
        time_src = int(body[21])
        hemi_digit = int(body[22])
    except ValueError as e:
        raise MountResponseError(f"GLS response has non-digits: {raw!r}") from e
    longitude_deg = sign * (lon_arcsec / 3600.0)
    latitude_deg = (lat_plus90_arcsec / 3600.0) - 90.0
    return MountStatus(
        longitude_deg=longitude_deg,
        latitude_deg=latitude_deg,
        gps_status=gps,
        system_state=sys_state,
        system_state_name=SYSTEM_STATES.get(sys_state, f"unknown ({sys_state})"),
        tracking_rate=track,
        tracking_rate_name=TRACKING_RATES.get(track, f"unknown ({track})"),
        button_speed=speed,
        button_speed_name=BUTTON_SPEEDS.get(speed, f"unknown ({speed})"),
        time_source=time_src,
        time_source_name=TIME_SOURCES.get(time_src, f"unknown ({time_src})"),
        hemisphere="N" if hemi_digit == 1 else "S",
    )


def parse_gep(raw: bytes | str) -> EquatorialPosition:
    """Parse :GEP# response — current equatorial pointing.

    Format: sTTTTTTTTTTTTTTTTTnn (20 chars + '#').
        sign (1):           declination sign
        dec (8):            |declination| * 100 arcsec
        ra (9):             right ascension * 100 arcsec (0..360°)
        pier (1):           0=east, 1=west, 2=indeterminate
        pointing (1):       0=counterweight up, 1=normal
    """
    body = _strip_response(raw)
    if len(body) != 20 or body[0] not in "+-":
        raise MountResponseError(f"GEP response wrong length/format: {raw!r}")
    sign = 1 if body[0] == "+" else -1
    try:
        dec_arcsec = int(body[1:9]) * 0.01
        ra_arcsec = int(body[9:18]) * 0.01
        pier_digit = int(body[18])
        pointing_digit = int(body[19])
    except ValueError as e:
        raise MountResponseError(f"GEP response has non-digits: {raw!r}") from e
    pier_map = {0: "E", 1: "W", 2: "?"}
    pointing_map = {0: "counterweight up", 1: "normal"}
    return EquatorialPosition(
        ra_deg=ra_arcsec / 3600.0,
        dec_deg=sign * (dec_arcsec / 3600.0),
        pier_side=pier_map.get(pier_digit, "?"),
        pointing_state=pointing_map.get(pointing_digit, "?"),
    )


def parse_gac(raw: bytes | str) -> AltAzPosition:
    """Parse :GAC# response — current alt/az pointing.

    Format: sTTTTTTTTTTTTTTTTT (18 chars + '#').
        sign (1):           altitude sign
        alt (8):            |altitude| * 100 arcsec
        az (9):             azimuth * 100 arcsec
    """
    body = _strip_response(raw)
    if len(body) != 18 or body[0] not in "+-":
        raise MountResponseError(f"GAC response wrong length/format: {raw!r}")
    sign = 1 if body[0] == "+" else -1
    try:
        alt_arcsec = int(body[1:9]) * 0.01
        az_arcsec = int(body[9:18]) * 0.01
    except ValueError as e:
        raise MountResponseError(f"GAC response has non-digits: {raw!r}") from e
    return AltAzPosition(
        altitude_deg=sign * (alt_arcsec / 3600.0),
        azimuth_deg=az_arcsec / 3600.0,
    )


def parse_gut(raw: bytes | str) -> MountTime:
    """Parse :GUT# response — time-related information.

    Format: sMMMnXXXXXXXXXXXXX (18 chars + '#').
        sign (1):           UTC offset sign
        MMM (3):            |UTC offset| in minutes (0..720)
        DST (1):            0=not observing, 1=observing
        time (13):          (JD_now_UTC - J2000) * 86400000 [ms]
    """
    body = _strip_response(raw)
    if len(body) != 18 or body[0] not in "+-":
        raise MountResponseError(f"GUT response wrong length/format: {raw!r}")
    sign = 1 if body[0] == "+" else -1
    try:
        offset_min = sign * int(body[1:4])
        dst = body[4] == "1"
        ms_since_j2000 = int(body[5:18])
    except ValueError as e:
        raise MountResponseError(f"GUT response has non-digits: {raw!r}") from e
    seconds_since_j2000 = ms_since_j2000 / 1000.0
    unix_timestamp = J2000_UNIX_TIMESTAMP + seconds_since_j2000
    utc_dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return MountTime(utc_offset_min=offset_min, dst_observed=dst, utc=utc_dt)


# ============================================================================
# Encoders (for set/slew commands)
# ============================================================================

def encode_longitude(deg: float) -> str:
    """Encode longitude in degrees to ':SLO sTTTTTTTT#' value."""
    sign = "+" if deg >= 0 else "-"
    arcsec_hundredths = int(round(abs(deg) * 3600.0 * 100))
    return f"{sign}{arcsec_hundredths:08d}"


def encode_latitude(deg: float) -> str:
    """Encode latitude in degrees to ':SLA sTTTTTTTT#' value (latitude+90)."""
    sign = "+" if deg >= 0 else "-"
    arcsec_hundredths = int(round(abs(deg) * 3600.0 * 100))
    return f"{sign}{arcsec_hundredths:08d}"


def encode_utc_offset(minutes: int) -> str:
    """Encode UTC offset in minutes to ':SG sMMM#' value."""
    sign = "+" if minutes >= 0 else "-"
    return f"{sign}{abs(minutes):03d}"


def encode_utc_time(dt: datetime) -> str:
    """Encode UTC datetime to ':SUT XXXXXXXXXXXXX#' (ms since J2000, 13 digits)."""
    if dt.tzinfo is None:
        raise ValueError("UTC datetime must be timezone-aware")
    unix_ts = dt.astimezone(timezone.utc).timestamp()
    ms_since_j2000 = int(round((unix_ts - J2000_UNIX_TIMESTAMP) * 1000.0))
    return f"{ms_since_j2000:013d}"


def encode_ra(deg: float) -> str:
    """Encode RA in degrees to ':SRA TTTTTTTTT#' (9 digits, 0.01 arcsec)."""
    if not (0.0 <= deg <= 360.0):
        raise ValueError(f"RA out of range: {deg}")
    arcsec_hundredths = int(round(deg * 3600.0 * 100))
    return f"{arcsec_hundredths:09d}"


def encode_dec(deg: float) -> str:
    """Encode Dec in degrees to ':Sds sTTTTTTTT#' (sign + 8 digits, 0.01 arcsec)."""
    if not (-90.0 <= deg <= 90.0):
        raise ValueError(f"Dec out of range: {deg}")
    sign = "+" if deg >= 0 else "-"
    arcsec_hundredths = int(round(abs(deg) * 3600.0 * 100))
    return f"{sign}{arcsec_hundredths:08d}"


# ============================================================================
# TCP I/O
# ============================================================================

class MountConnection:
    """One-shot TCP connection to the mount's WiFi-to-Serial bridge.

    Each command opens a fresh connection, writes the command bytes, reads the
    response until '#' arrives or READ_DEADLINE_S expires, then closes. This
    matches the validated `(printf ':CMD#'; sleep 3) | nc -w 5 IP 8899` pattern
    that works reliably with the HBX8409 module's TCP-to-Serial bridge, and
    sidesteps the documented 300 s TCP idle timeout entirely.
    """

    def __init__(self, ip: str = MOUNT_IP, port: int = MOUNT_PORT,
                 read_deadline_s: float = READ_DEADLINE_S,
                 connect_timeout_s: float = CONNECT_TIMEOUT_S) -> None:
        self.ip = ip
        self.port = port
        self.read_deadline_s = read_deadline_s
        self.connect_timeout_s = connect_timeout_s

    # Settle delay for commands whose responses don't include '#'. Many iOptron
    # commands fall in this category — :MountInfo# returns '0026', set commands
    # like :SG#, :SDS#, :SUT# return just '1' for success, etc. The default
    # send() always uses short-read mode (returns immediately on '#' if present,
    # or after SETTLE_S of quiet if not).
    SETTLE_S = 0.8

    def send(self, command: str) -> str:
        """Send a single iOptron command and return the response.

        Commands must include the ':' prefix and '#' terminator already.
        Returns the raw response as a str, including the trailing '#' when present.

        The read loop returns immediately when '#' arrives (so terminator-included
        commands are fast) or after SETTLE_S of socket quiet for commands that
        don't terminate with '#' (e.g. :MountInfo# returns '0026'; set commands
        return '1' without '#'). EOF with empty buffer raises MountResponseError;
        timeout with empty buffer raises MountTimeout.
        """
        if not command.startswith(":") or not command.endswith("#"):
            raise ValueError(f"command must be of the form ':CMD#', got {command!r}")
        try:
            with socket.create_connection((self.ip, self.port), timeout=self.connect_timeout_s) as sock:
                sock.sendall(command.encode("ascii"))
                sock.settimeout(self.SETTLE_S)
                return self._recv_short(sock)
        except (ConnectionRefusedError, OSError) as e:
            raise MountUnreachable(f"could not connect to {self.ip}:{self.port}: {e}") from e

    @staticmethod
    def _recv_short(sock: socket.socket) -> str:
        """Accumulate recv'd bytes; return on '#', settle-timeout, or EOF.

        Behaviour matrix:
          - '#' seen          → return up to and including '#'
          - timeout, have data → return the partial buffer (assume complete)
          - timeout, no data   → raise MountTimeout
          - EOF, have data     → return the partial buffer
          - EOF, no data       → raise MountResponseError
        """
        buf = bytearray()
        while True:
            try:
                chunk = sock.recv(RECV_CHUNK)
            except (socket.timeout, TimeoutError) as e:
                if not buf:
                    raise MountTimeout("mount did not send any bytes") from e
                break
            if not chunk:
                if not buf:
                    raise MountResponseError("connection closed with no data")
                break
            buf.extend(chunk)
            if RESPONSE_TERMINATOR in buf:
                idx = buf.index(RESPONSE_TERMINATOR)
                return buf[: idx + 1].decode("ascii", errors="replace")
        return buf.decode("ascii", errors="replace")

    def send_fire_and_forget(self, command: str) -> None:
        """Send a command that produces no response (jog, pulse-guide)."""
        if not command.startswith(":") or not command.endswith("#"):
            raise ValueError(f"command must be of the form ':CMD#', got {command!r}")
        try:
            with socket.create_connection((self.ip, self.port), timeout=self.connect_timeout_s) as sock:
                sock.sendall(command.encode("ascii"))
                # tiny grace period so the bridge forwards before we close
                time.sleep(0.2)
        except (ConnectionRefusedError, OSError) as e:
            raise MountUnreachable(f"could not connect to {self.ip}:{self.port}: {e}") from e


# ============================================================================
# Vault target lookup (for `goto` subcommand)
# ============================================================================

def normalize_designation(name: str) -> str:
    """Normalize 'M 16', 'm-16', 'NGC 7000' to 'M16' / 'NGC7000' for catalog lookup."""
    return name.replace(" ", "").replace("-", "").upper()


def load_targets_from_vault(targets_dir: Path) -> dict[str, tuple[str, float, float]]:
    """Parse YAML frontmatter from 02_Targets/**/*.md, returning {designation: (display_name, ra_deg, dec_deg)}.

    Mirrors scripts/fov_atlas.py:load_from_vault() — gracefully degrades if PyYAML
    isn't installed (returns empty dict, falls back to TARGET_CATALOG).
    """
    try:
        import yaml
    except ImportError:
        return {}
    out: dict[str, tuple[str, float, float]] = {}
    if not targets_dir.is_dir():
        return out
    for md in targets_dir.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        if not text.startswith("---"):
            continue
        try:
            fm = yaml.safe_load(text.split("---", 2)[1])
        except yaml.YAMLError:
            continue
        if not fm or "ra_deg" not in fm or "dec_deg" not in fm:
            continue
        designation = str(fm.get("designation", "")).strip()
        if not designation:
            continue
        display_name = str(fm.get("title", md.stem))
        try:
            ra = float(fm["ra_deg"])
            dec = float(fm["dec_deg"])
        except (TypeError, ValueError):
            continue
        out[normalize_designation(designation)] = (display_name, ra, dec)
    return out


def resolve_target(designation: str, repo_root: Path) -> tuple[str, float, float]:
    """Look up a target by designation. Vault frontmatter wins over the hardcoded catalog.

    Raises ValueError with the list of known designations if not found.
    """
    key = normalize_designation(designation)
    vault = load_targets_from_vault(repo_root / "02_Targets")
    if key in vault:
        return vault[key]
    if key in TARGET_CATALOG:
        return TARGET_CATALOG[key]
    known = sorted(set(vault.keys()) | set(TARGET_CATALOG.keys()))
    raise ValueError(
        f"unknown target {designation!r} (normalized: {key!r}). "
        f"Known: {', '.join(known)}"
    )


# ============================================================================
# Subcommand implementations
# ============================================================================

def cli_status(mount: MountConnection, watch: Optional[int] = None) -> int:
    """Print parsed mount state. If `watch` is set, repoll every N seconds until Ctrl-C."""
    def _once() -> None:
        gls = parse_gls(mount.send(":GLS#"))
        gep = parse_gep(mount.send(":GEP#"))
        gac = parse_gac(mount.send(":GAC#"))
        gut = parse_gut(mount.send(":GUT#"))
        print(f"--- mount status @ {datetime.now().isoformat(timespec='seconds')} ---")
        print(f"  position    RA  {gep.ra_deg:8.4f}°    Dec {gep.dec_deg:+8.4f}°"
              f"    pier={gep.pier_side}  {gep.pointing_state}")
        print(f"              alt {gac.altitude_deg:+7.3f}°  az  {gac.azimuth_deg:8.3f}°")
        print(f"  state       {gls.system_state_name}  (tracking: {gls.tracking_rate_name})")
        print(f"  location    {gls.latitude_deg:+8.5f}° N    {gls.longitude_deg:+8.5f}° E"
              f"    hemisphere={gls.hemisphere}")
        print(f"  GPS         {gls.gps_status} ({'valid' if gls.gps_status == 2 else 'no data / module absent'})")
        print(f"  time src    {gls.time_source_name}    mount UTC: {gut.utc.isoformat()}"
              f"    offset: {gut.utc_offset_min:+d} min  DST: {'yes' if gut.dst_observed else 'no'}")

    if watch is None:
        _once()
        return 0
    try:
        while True:
            _once()
            print()
            time.sleep(watch)
    except KeyboardInterrupt:
        print("\n(watch stopped)")
        return 0


def cli_health(mount: MountConnection) -> int:
    """Pre-session readiness check. Returns 0 if all pass, 1 if any fail."""
    results: list[HealthCheckResult] = []

    # 1. Mount model identifiable
    try:
        info = parse_mount_info(mount.send(":MountInfo#"))
        results.append(HealthCheckResult(
            "mount identified",
            info.code == "0026",
            f"{info.name} (code {info.code})",
        ))
    except MountError as e:
        results.append(HealthCheckResult("mount identified", False, f"error: {e}"))

    # 2. Status reachable and parsable
    gls: Optional[MountStatus] = None
    try:
        gls = parse_gls(mount.send(":GLS#"))
        results.append(HealthCheckResult("status reachable", True, "GLS parsed"))
    except MountError as e:
        results.append(HealthCheckResult("status reachable", False, f"error: {e}"))

    if gls is not None:
        # 3. Location matches Tuntange
        lat_off = abs(gls.latitude_deg - EXPECTED_LAT_DEG)
        lon_off = abs(gls.longitude_deg - EXPECTED_LON_DEG)
        location_ok = lat_off <= LOCATION_TOLERANCE_DEG and lon_off <= LOCATION_TOLERANCE_DEG
        results.append(HealthCheckResult(
            "location",
            location_ok,
            f"lat {gls.latitude_deg:.5f}° (Δ {lat_off:.5f}°)"
            f", lon {gls.longitude_deg:.5f}° (Δ {lon_off:.5f}°)"
            f" — expected Tuntange ({EXPECTED_LAT_DEG}, {EXPECTED_LON_DEG})",
        ))

        # 4. Hemisphere correct
        results.append(HealthCheckResult(
            "hemisphere",
            gls.hemisphere == "N",
            f"set to {gls.hemisphere}",
        ))

        # 5. Tracking rate sidereal
        results.append(HealthCheckResult(
            "tracking rate",
            gls.tracking_rate == 0,
            gls.tracking_rate_name,
        ))

        # 6. Not currently slewing (sanity — shouldn't be slewing during a readiness check)
        results.append(HealthCheckResult(
            "not slewing",
            not gls.is_slewing,
            f"state: {gls.system_state_name}",
        ))

    # 7. Time within 60 s of host clock
    try:
        gut = parse_gut(mount.send(":GUT#"))
        host_utc = datetime.now(timezone.utc)
        drift_s = abs((gut.utc - host_utc).total_seconds())
        results.append(HealthCheckResult(
            "time sync",
            drift_s <= 60.0,
            f"mount UTC {gut.utc.isoformat(timespec='seconds')}"
            f", host drift {drift_s:.1f} s",
        ))
    except MountError as e:
        results.append(HealthCheckResult("time sync", False, f"error: {e}"))

    # 8. Firmware reachable + match documented version
    try:
        fw1 = parse_fw(mount.send(":FW1#"))
        fw2 = parse_fw(mount.send(":FW2#"))
        documented_hc = LATEST_FIRMWARE[1]
        installed_hc = fw1.first.replace("-", "")[2:]  # YYYY-MM-DD -> YYMMDD
        gap_label = "current" if installed_hc == documented_hc else f"behind latest (have {fw1.first}, latest {LATEST_FIRMWARE[0]})"
        results.append(HealthCheckResult(
            "firmware",
            True,  # informational only — old firmware isn't a failure
            f"HC {fw1.first}, RA {fw2.first}, DEC {fw2.second} — {gap_label}",
        ))
    except MountError as e:
        results.append(HealthCheckResult("firmware", False, f"error: {e}"))

    # Print results
    print("Pre-session mount health check")
    print("=" * 60)
    overall_pass = True
    for r in results:
        mark = "✓" if r.passed else "✗"
        print(f"  [{mark}] {r.name:20s}  {r.detail}")
        if not r.passed:
            overall_pass = False
    print("=" * 60)
    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    return 0 if overall_pass else 1


def cli_firmware(mount: MountConnection) -> int:
    """Show installed firmware versions + gap analysis."""
    info = parse_mount_info(mount.send(":MountInfo#"))
    fw1 = parse_fw(mount.send(":FW1#"))
    fw2 = parse_fw(mount.send(":FW2#"))

    installed_hc = fw1.first.replace("-", "")[2:]   # YYYY-MM-DD -> YYMMDD
    installed_ra = fw2.first.replace("-", "")[2:]
    installed_dec = fw2.second.replace("-", "")[2:]

    print(f"Mount: {info.name} (code {info.code})")
    print()
    print("Installed firmware:")
    print(f"  Hand Controller: V{installed_hc} ({fw1.first})")
    print(f"  Main board:      V{fw1.second.replace('-', '')[2:]} ({fw1.second})")
    print(f"  RA motor:        V{installed_ra} ({fw2.first})")
    print(f"  DEC motor:       V{installed_dec} ({fw2.second})")
    print()

    # Find matching release
    matching_release = None
    for label, hc, ra, dec, notes in FIRMWARE_HISTORY:
        if (hc, ra, dec) == (installed_hc, installed_ra, installed_dec):
            matching_release = (label, notes)
            break

    latest_label, latest_hc, latest_ra, latest_dec, latest_notes = LATEST_FIRMWARE
    if matching_release:
        print(f"Identified release: {matching_release[0]} ({matching_release[1]})")
    else:
        print("Installed bundle doesn't match any documented release exactly.")
    print(f"Latest available: {latest_label} ({latest_notes})")

    if installed_hc == latest_hc and installed_ra == latest_ra and installed_dec == latest_dec:
        print("  → all components current ✓")
    else:
        gaps = []
        if installed_hc != latest_hc:
            gaps.append(f"HC: {fw1.first} → {latest_hc[:2]}-{latest_hc[2:4]}-{latest_hc[4:6]}")
        if installed_ra != latest_ra:
            gaps.append(f"RA: {fw2.first} → {latest_ra[:2]}-{latest_ra[2:4]}-{latest_ra[4:6]}")
        if installed_dec != latest_dec:
            gaps.append(f"DEC: {fw2.second} → {latest_dec[:2]}-{latest_dec[2:4]}-{latest_dec[4:6]}")
        print("  → update available:")
        for g in gaps:
            print(f"    - {g}")
        print(f"  → upgrade .bin cached at "
              f"01_Equipment/Manuals/CEM26/Firmware/CEM26_GEM28_FW{latest_hc}.bin")
        print(f"  → upgrade procedure requires Windows + iOptronUpgradeUtility223.exe")
    return 0


def cli_unpark(mount: MountConnection) -> int:
    """Unpark and start sidereal tracking."""
    resp_unpark = mount.send(":MP0#")
    resp_track = mount.send(":RT0#")
    print(f"unpark: {resp_unpark}   sidereal tracking: {resp_track}")
    return 0 if resp_unpark.startswith("1") and resp_track.startswith("1") else 1


def cli_park(mount: MountConnection, timeout_s: int = 60) -> int:
    """End-of-session park: stop tracking, slew to stored park position, confirm parked."""
    print("stopping tracking…")
    mount.send(":ST0#")
    print("reading park position…")
    try:
        # :GPC# returns alt+az of the stored park position (informational)
        _ = mount.send(":GPC#")
    except MountError as e:
        print(f"warning: couldn't read park position: {e}")
    print("issuing park command…")
    resp = mount.send(":MP1#")
    if not resp.startswith("1"):
        print(f"park rejected by mount: {resp!r}")
        return 1
    print(f"slewing to park (timeout {timeout_s} s)…")
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        gls = parse_gls(mount.send(":GLS#"))
        if gls.is_parked:
            print(f"  parked ✓ (state: {gls.system_state_name})")
            return 0
        print(f"  …{gls.system_state_name}")
        time.sleep(1)
    print(f"timeout: mount did not report 'parked' within {timeout_s} s")
    return 1


def cli_timesync(mount: MountConnection) -> int:
    """Push host's UTC + DST + UTC offset to mount."""
    print("reading mount time before sync…")
    before = parse_gut(mount.send(":GUT#"))
    host_utc = datetime.now(timezone.utc)
    drift_before = (before.utc - host_utc).total_seconds()
    print(f"  mount UTC: {before.utc.isoformat(timespec='seconds')}"
          f"  (drift {drift_before:+.1f} s)")

    # Compute UTC offset from local time
    local_now = datetime.now().astimezone()
    utc_offset_min = int(local_now.utcoffset().total_seconds() // 60)
    # DST flag — approximation: dst() returns nonzero when DST is in effect
    dst_observed = bool(local_now.dst()) and local_now.dst().total_seconds() != 0

    print(f"  pushing UTC offset {utc_offset_min:+d} min  DST {'yes' if dst_observed else 'no'}…")
    mount.send(f":SG{encode_utc_offset(utc_offset_min)}#")
    mount.send(f":SDS{'1' if dst_observed else '0'}#")

    print(f"  pushing UTC time {host_utc.isoformat(timespec='seconds')}…")
    mount.send(f":SUT{encode_utc_time(host_utc)}#")

    # Re-read for drift verification
    time.sleep(0.5)
    after = parse_gut(mount.send(":GUT#"))
    host_after = datetime.now(timezone.utc)
    drift_after = (after.utc - host_after).total_seconds()
    print(f"  mount UTC after sync: {after.utc.isoformat(timespec='seconds')}"
          f"  (drift {drift_after:+.1f} s)")
    if abs(drift_after) <= 2.0:
        print("time sync OK ✓")
        return 0
    print(f"drift still {drift_after:+.1f} s — sync may have failed")
    return 1


def cli_goto(mount: MountConnection, designation: str, repo_root: Path,
             slew_timeout_s: int = 120) -> int:
    """Look up target, set coords, slew. ASIAIR must be disconnected."""
    try:
        display, ra_deg, dec_deg = resolve_target(designation, repo_root)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"target: {display}  RA {ra_deg:.4f}°  Dec {dec_deg:+.4f}°")

    # Check not parked
    gls = parse_gls(mount.send(":GLS#"))
    if gls.is_parked:
        print("mount is parked — run `unpark` first", file=sys.stderr)
        return 1

    print(f"setting target RA…")
    resp = mount.send(f":SRA{encode_ra(ra_deg)}#")
    if not resp.startswith("1"):
        print(f"  SRA rejected: {resp!r}", file=sys.stderr)
        return 1
    print(f"setting target Dec…")
    # NOTE: command is `:Sd` + sign + 8 digits. The protocol spec writes
    # `:SdsTTTTTTTT#` which parses as `:Sd` (literal) + `s` (sign) + 8 digits.
    # Sending `:Sds<sign><digits>#` would inject a redundant 's' literal that
    # firmware silently swallows, leaving Dec target at default 0° — verified
    # 2026-05-24 by attempting M44 and watching the mount slew to Dec 0°.
    resp = mount.send(f":Sd{encode_dec(dec_deg)}#")
    if not resp.startswith("1"):
        print(f"  Sd rejected: {resp!r}", file=sys.stderr)
        return 1
    print("slewing (MS1)…")
    resp = mount.send(":MS1#")
    if not resp.startswith("1"):
        print(f"  MS1 rejected (likely below horizon or limit): {resp!r}", file=sys.stderr)
        return 1

    deadline = time.monotonic() + slew_timeout_s
    while time.monotonic() < deadline:
        gls = parse_gls(mount.send(":GLS#"))
        if not gls.is_slewing:
            gep = parse_gep(mount.send(":GEP#"))
            print(f"  slew complete ✓  RA {gep.ra_deg:.4f}°  Dec {gep.dec_deg:+.4f}°"
                  f"  (state: {gls.system_state_name})")
            return 0
        print(f"  …slewing")
        time.sleep(2)
    print(f"timeout: slew did not complete within {slew_timeout_s} s", file=sys.stderr)
    return 1


def cli_log(mount: MountConnection, output_path: Path, interval_s: float) -> int:
    """Periodic mount-state logger. Appends NDJSON until Ctrl-C, then writes a summary line."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_count = 0
    start_ts = datetime.now(timezone.utc)
    print(f"logging to {output_path} every {interval_s} s — Ctrl-C to stop")

    def _write(record: dict) -> None:
        nonlocal sample_count
        with output_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")
        sample_count += 1

    stop = {"flag": False}

    def _on_sigint(signum, frame):
        stop["flag"] = True

    signal.signal(signal.SIGINT, _on_sigint)

    try:
        while not stop["flag"]:
            now = datetime.now(timezone.utc)
            try:
                gls = parse_gls(mount.send(":GLS#"))
                gep = parse_gep(mount.send(":GEP#"))
                rec = {
                    "ts": now.isoformat(),
                    "kind": "sample",
                    "ra_deg": round(gep.ra_deg, 5),
                    "dec_deg": round(gep.dec_deg, 5),
                    "pier_side": gep.pier_side,
                    "pointing_state": gep.pointing_state,
                    "system_state": gls.system_state,
                    "system_state_name": gls.system_state_name,
                    "tracking_rate": gls.tracking_rate,
                    "tracking_rate_name": gls.tracking_rate_name,
                    "is_parked": gls.is_parked,
                    "is_slewing": gls.is_slewing,
                    "is_tracking": gls.is_tracking,
                }
                _write(rec)
                print(f"  {now.isoformat(timespec='seconds')}"
                      f"  RA {gep.ra_deg:7.3f}°  Dec {gep.dec_deg:+7.3f}°"
                      f"  {gls.system_state_name}")
            except MountError as e:
                _write({"ts": now.isoformat(), "kind": "error", "error": str(e)})
                print(f"  {now.isoformat(timespec='seconds')}  ERROR: {e}")
            # interruptible sleep
            slept = 0.0
            while slept < interval_s and not stop["flag"]:
                time.sleep(min(0.5, interval_s - slept))
                slept += 0.5
    finally:
        end_ts = datetime.now(timezone.utc)
        summary = {
            "ts": end_ts.isoformat(),
            "kind": "summary",
            "started": start_ts.isoformat(),
            "ended": end_ts.isoformat(),
            "duration_s": (end_ts - start_ts).total_seconds(),
            "samples_written": sample_count,
            "interval_s": interval_s,
        }
        _write(summary)
        print(f"\nwrote {sample_count} samples + summary to {output_path}")
    return 0


def default_log_path(repo_root: Path) -> Path:
    """Path beside the capture-session note for today: 05_Sessions/{year}/Capture/{date}-mount-log.json."""
    today = datetime.now().date()
    return repo_root / "05_Sessions" / f"{today.year}" / "Capture" / f"{today.isoformat()}-mount-log.json"


# ============================================================================
# CLI entry point
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mount.py",
        description="CEM26 mount control via WiFi TCP bridge (iOptron RS-232 V3.10).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See scripts/README.md and 03_Techniques/Mount-Diagnostics.md for workflow guides.",
    )
    p.add_argument("--ip", default=MOUNT_IP, help=f"mount IP (default: {MOUNT_IP})")
    p.add_argument("--port", type=int, default=MOUNT_PORT, help=f"mount TCP port (default: {MOUNT_PORT})")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="COMMAND")

    s_status = sub.add_parser("status", help="print parsed mount state")
    s_status.add_argument("--watch", type=int, nargs="?", const=5, default=None,
                          metavar="N", help="repoll every N seconds (default 5) until Ctrl-C")

    sub.add_parser("health", help="pre-session readiness check (exit 0=pass, 1=fail)")
    sub.add_parser("firmware", help="show installed firmware versions + gap analysis")
    sub.add_parser("park", help="end-of-session: stop tracking, slew to park, confirm")
    sub.add_parser("unpark", help="unpark + start sidereal tracking")
    sub.add_parser("timesync", help="push host UTC/DST/offset to mount")

    s_goto = sub.add_parser("goto", help="slew to a target by designation (ASIAIR must be disconnected)")
    s_goto.add_argument("designation", help="e.g. M16, NGC7000, MEL111")

    s_log = sub.add_parser("log", help="periodic state logger; writes NDJSON beside capture-session note")
    s_log.add_argument("--session", type=Path, default=None,
                       help="override output path (default: 05_Sessions/{year}/Capture/{date}-mount-log.json)")
    s_log.add_argument("--interval", type=float, default=30.0,
                       help="seconds between samples (default 30)")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    mount = MountConnection(ip=args.ip, port=args.port)
    repo_root = Path(__file__).resolve().parent.parent

    try:
        if args.cmd == "status":
            return cli_status(mount, watch=args.watch)
        if args.cmd == "health":
            return cli_health(mount)
        if args.cmd == "firmware":
            return cli_firmware(mount)
        if args.cmd == "park":
            return cli_park(mount)
        if args.cmd == "unpark":
            return cli_unpark(mount)
        if args.cmd == "timesync":
            return cli_timesync(mount)
        if args.cmd == "goto":
            return cli_goto(mount, args.designation, repo_root)
        if args.cmd == "log":
            output = args.session if args.session else default_log_path(repo_root)
            return cli_log(mount, output, args.interval)
    except MountUnreachable as e:
        print(f"mount unreachable: {e}", file=sys.stderr)
        print(f"  → check the mount is powered on and on home WiFi (BleiftDoheem)", file=sys.stderr)
        print(f"  → verify with: ping {args.ip}", file=sys.stderr)
        return 2
    except MountError as e:
        print(f"mount error: {e}", file=sys.stderr)
        return 2

    return 1  # unreachable


if __name__ == "__main__":
    sys.exit(main())
