#!/usr/bin/env python3
"""
test_mount.py — unit + mock + opt-in live tests for scripts/mount.py.

Three test layers:

1. TestParsers / TestEncoders / TestTargetResolution
       Deterministic. No I/O. Fixture strings captured during the 2026-05-24
       manual verification against the live mount.

2. TestMountConnection
       Mocked socket layer. Verifies TCP send/recv/timeout/error behavior
       without touching a real mount.

3. TestLiveMount
       Opt-in. Gated by MOUNT_TEST_LIVE=1 env var. Requires:
         - mount powered on
         - mount on home WiFi (192.168.178.87 reachable)
         - ASIAIR USB-Serial NOT connected to the mount (single-client invariant)

Run from repo root:
    python3 -m unittest scripts.test_mount               # mock + unit only
    MOUNT_TEST_LIVE=1 python3 -m unittest scripts.test_mount   # + live tests
    python3 scripts/test_mount.py                        # equivalent direct invocation
"""
from __future__ import annotations

import json
import os
import socket
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

# Make `import mount` work whether the test is invoked from repo root
# (`python3 -m unittest scripts.test_mount`) or directly
# (`python3 scripts/test_mount.py`).
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import mount  # noqa: E402


# ============================================================================
# 1. Parsers — deterministic, fixture-driven
# ============================================================================

class TestParseMountInfo(unittest.TestCase):

    def test_cem26(self):
        info = mount.parse_mount_info("0026")
        self.assertEqual(info.code, "0026")
        self.assertEqual(info.name, "CEM26")

    def test_gem28(self):
        info = mount.parse_mount_info("0028")
        self.assertEqual(info.code, "0028")
        self.assertEqual(info.name, "GEM28")

    def test_unknown_code(self):
        info = mount.parse_mount_info("9999")
        self.assertEqual(info.code, "9999")
        self.assertTrue(info.name.startswith("unknown"))

    def test_with_terminator(self):
        info = mount.parse_mount_info("0026#")
        self.assertEqual(info.code, "0026")

    def test_too_short_raises(self):
        with self.assertRaises(mount.MountResponseError):
            mount.parse_mount_info("026")

    def test_non_digits_raises(self):
        with self.assertRaises(mount.MountResponseError):
            mount.parse_mount_info("abcd")


class TestParseFW(unittest.TestCase):

    def test_fw1_v230305_release(self):
        # FW1 returns HC + main board dates.
        # Captured 2026-05-24 from the live mount running V20230305:
        fw = mount.parse_fw("230305230305#")
        self.assertEqual(fw.first, "2023-03-05")    # HC
        self.assertEqual(fw.second, "2023-03-05")   # main board

    def test_fw2_v230305_release(self):
        # FW2 returns RA + DEC motor dates.
        # Captured 2026-05-24 from the live mount running V20230305:
        fw = mount.parse_fw("210420230305#")
        self.assertEqual(fw.first, "2021-04-20")    # RA motor
        self.assertEqual(fw.second, "2023-03-05")   # DEC motor

    def test_fw_latest_v241201(self):
        # Synthetic — what we'd expect after upgrading to V20241201.
        fw = mount.parse_fw("241201240518#")
        self.assertEqual(fw.first, "2024-12-01")
        self.assertEqual(fw.second, "2024-05-18")

    def test_wrong_length_raises(self):
        with self.assertRaises(mount.MountResponseError):
            mount.parse_fw("2303052303#")  # 10 digits, not 12

    def test_non_digits_raises(self):
        with self.assertRaises(mount.MountResponseError):
            mount.parse_fw("23030523030X#")


class TestParseGLS(unittest.TestCase):

    def test_balcony_at_home(self):
        # Actual response captured 2026-05-24 ~14:25 CEST from the live mount
        # sitting at home position with sidereal tracking enabled, on Tuntange:
        #   +02163000 50298100 070521#
        # i.e. lon +6.0083° E, lat 49.717° N (139.717 - 90), GPS=0, sys=7 (home),
        # track=0 (sidereal), button=5 (64x), time_src=2 (HC), hemisphere=1 (N).
        gls = mount.parse_gls("+0216300050298100070521#")
        self.assertAlmostEqual(gls.longitude_deg, 6.0083, places=4)
        self.assertAlmostEqual(gls.latitude_deg, 49.7170, places=3)
        self.assertEqual(gls.gps_status, 0)
        self.assertEqual(gls.system_state, 7)
        self.assertEqual(gls.system_state_name, "stopped at zero/home position")
        self.assertEqual(gls.tracking_rate, 0)
        self.assertEqual(gls.tracking_rate_name, "sidereal")
        self.assertEqual(gls.button_speed, 5)
        self.assertEqual(gls.time_source, 2)
        self.assertEqual(gls.time_source_name, "hand controller")
        self.assertEqual(gls.hemisphere, "N")
        self.assertTrue(gls.is_at_home)
        self.assertFalse(gls.is_parked)
        self.assertFalse(gls.is_slewing)

    def test_parked_state(self):
        # Construct a parked state (system_state = 6).
        raw = "+0216300050298100" + "0" + "6" + "0" + "5" + "2" + "1" + "#"
        gls = mount.parse_gls(raw)
        self.assertTrue(gls.is_parked)
        self.assertFalse(gls.is_at_home)
        self.assertFalse(gls.is_slewing)

    def test_slewing_state(self):
        raw = "+0216300050298100" + "0" + "2" + "0" + "5" + "2" + "1" + "#"
        gls = mount.parse_gls(raw)
        self.assertTrue(gls.is_slewing)
        self.assertFalse(gls.is_parked)
        self.assertFalse(gls.is_tracking)

    def test_tracking_states(self):
        # State 1 = tracking PEC off, state 5 = tracking PEC on
        for state in (1, 5):
            raw = "+0216300050298100" + "0" + str(state) + "0" + "5" + "2" + "1" + "#"
            gls = mount.parse_gls(raw)
            self.assertTrue(gls.is_tracking, f"state {state} should be tracking")

    def test_southern_hemisphere(self):
        # Hemisphere digit 0 = S
        raw = "+0216300050298100" + "0" + "7" + "0" + "5" + "2" + "0" + "#"
        gls = mount.parse_gls(raw)
        self.assertEqual(gls.hemisphere, "S")

    def test_western_longitude(self):
        # Sign '-' = western longitude
        raw = "-0216300050298100" + "0" + "7" + "0" + "5" + "2" + "1" + "#"
        gls = mount.parse_gls(raw)
        self.assertLess(gls.longitude_deg, 0)
        self.assertAlmostEqual(gls.longitude_deg, -6.0083, places=4)

    def test_wrong_length_raises(self):
        with self.assertRaises(mount.MountResponseError):
            mount.parse_gls("+021630005029810007#")  # truncated

    def test_missing_sign_raises(self):
        with self.assertRaises(mount.MountResponseError):
            mount.parse_gls("0216300050298100070521#")  # no leading sign


class TestParseGEP(unittest.TestCase):

    def test_round_trip_m16(self):
        # M16 is at RA 18h 19m (= 274.7°), Dec -13.78°.
        # Synthetic response with those values, pier east (0), normal pointing (1):
        # sign = -, dec = 13.78 * 3600 * 100 = 4960800 -> 8 digits = 04960800
        # ra  = 274.7 * 3600 * 100 = 98892000 -> 9 digits = 098892000
        raw = "-04960800098892000" + "0" + "1" + "#"
        gep = mount.parse_gep(raw)
        self.assertAlmostEqual(gep.ra_deg, 274.7, places=2)
        self.assertAlmostEqual(gep.dec_deg, -13.78, places=2)
        self.assertEqual(gep.pier_side, "E")
        self.assertEqual(gep.pointing_state, "normal")

    def test_positive_dec_pier_west(self):
        # Dec +30°, RA 0°, pier west, counterweight up
        raw = "+10800000000000000" + "1" + "0" + "#"
        gep = mount.parse_gep(raw)
        self.assertAlmostEqual(gep.dec_deg, 30.0, places=2)
        self.assertAlmostEqual(gep.ra_deg, 0.0, places=2)
        self.assertEqual(gep.pier_side, "W")
        self.assertEqual(gep.pointing_state, "counterweight up")

    def test_indeterminate_pier(self):
        raw = "+10800000000000000" + "2" + "1" + "#"
        gep = mount.parse_gep(raw)
        self.assertEqual(gep.pier_side, "?")


class TestParseGAC(unittest.TestCase):

    def test_round_trip(self):
        # alt 45°, az 180°
        # alt = 45 * 3600 * 100 = 16200000 -> 8 digits
        # az  = 180 * 3600 * 100 = 64800000 -> 9 digits
        raw = "+16200000064800000#"
        gac = mount.parse_gac(raw)
        self.assertAlmostEqual(gac.altitude_deg, 45.0, places=3)
        self.assertAlmostEqual(gac.azimuth_deg, 180.0, places=3)

    def test_negative_altitude(self):
        # alt -10° (below horizon)
        raw = "-03600000064800000#"
        gac = mount.parse_gac(raw)
        self.assertAlmostEqual(gac.altitude_deg, -10.0, places=3)


class TestParseGUT(unittest.TestCase):

    def test_round_trip(self):
        # UTC offset +120 min (CEST), DST observed, time = J2000 + 1 day
        # 86400000 ms = 1 day -> 13 digits with leading zeros
        raw = "+1201" + f"{86400000:013d}" + "#"
        gut = mount.parse_gut(raw)
        self.assertEqual(gut.utc_offset_min, 120)
        self.assertTrue(gut.dst_observed)
        # J2000 + 1 day = 2000-01-02 12:00:00 UTC
        expected = datetime(2000, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(gut.utc, expected)

    def test_negative_offset_no_dst(self):
        raw = "-3000" + f"{0:013d}" + "#"
        gut = mount.parse_gut(raw)
        self.assertEqual(gut.utc_offset_min, -300)
        self.assertFalse(gut.dst_observed)


# ============================================================================
# 2. Encoders — round-trip with parsers
# ============================================================================

class TestEncoders(unittest.TestCase):

    def test_ra_round_trip_via_gep(self):
        for ra in (0.0, 90.0, 180.0, 274.70, 359.999):
            encoded = mount.encode_ra(ra)
            self.assertEqual(len(encoded), 9)
            # Build a synthetic :GEP# response with dec=0
            raw = f"+00000000{encoded}01#"
            gep = mount.parse_gep(raw)
            self.assertAlmostEqual(gep.ra_deg, ra, places=3,
                                   msg=f"RA {ra} did not round-trip")

    def test_dec_round_trip_via_gep(self):
        for dec in (-89.5, -13.78, 0.0, 30.0, 89.9):
            encoded = mount.encode_dec(dec)
            self.assertEqual(len(encoded), 9)  # sign + 8 digits
            sign = encoded[0]
            digits = encoded[1:]
            raw = f"{sign}{digits}00000000001#"
            gep = mount.parse_gep(raw)
            self.assertAlmostEqual(gep.dec_deg, dec, places=3,
                                   msg=f"Dec {dec} did not round-trip")

    def test_utc_offset_encoding(self):
        self.assertEqual(mount.encode_utc_offset(120), "+120")
        self.assertEqual(mount.encode_utc_offset(-300), "-300")
        self.assertEqual(mount.encode_utc_offset(0), "+000")

    def test_utc_time_round_trip(self):
        # Pick a known UTC datetime, encode, then re-decode via parse_gut
        for utc_dt in [
            datetime(2026, 5, 24, 14, 30, 0, tzinfo=timezone.utc),
            datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc),  # = J2000
            datetime(2030, 6, 21, 21, 0, 0, tzinfo=timezone.utc),
        ]:
            encoded = mount.encode_utc_time(utc_dt)
            self.assertEqual(len(encoded), 13)
            # Build a synthetic :GUT# response
            raw = f"+0000{encoded}#"
            gut = mount.parse_gut(raw)
            delta_s = abs((gut.utc - utc_dt).total_seconds())
            self.assertLess(delta_s, 0.002, f"UTC drift {delta_s}s for {utc_dt}")

    def test_ra_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            mount.encode_ra(-1.0)
        with self.assertRaises(ValueError):
            mount.encode_ra(361.0)

    def test_dec_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            mount.encode_dec(-91.0)
        with self.assertRaises(ValueError):
            mount.encode_dec(91.0)

    def test_encode_utc_time_naive_raises(self):
        with self.assertRaises(ValueError):
            mount.encode_utc_time(datetime(2026, 5, 24, 14, 30, 0))  # no tzinfo


# ============================================================================
# 3. Target resolution
# ============================================================================

class TestNormalizeDesignation(unittest.TestCase):

    def test_strips_spaces_and_hyphens(self):
        self.assertEqual(mount.normalize_designation("M 16"), "M16")
        self.assertEqual(mount.normalize_designation("M-16"), "M16")
        self.assertEqual(mount.normalize_designation("ngc 7000"), "NGC7000")
        self.assertEqual(mount.normalize_designation("Sh2-240"), "SH2240")


class TestResolveTarget(unittest.TestCase):

    def setUp(self):
        # Empty repo root → only fallback catalog applies
        self.tmpdir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_resolve_from_catalog(self):
        display, ra, dec = mount.resolve_target("M16", self.repo_root)
        self.assertEqual(display, "M16 Eagle")
        self.assertAlmostEqual(ra, 274.70, places=2)
        self.assertAlmostEqual(dec, -13.78, places=2)

    def test_resolve_normalizes(self):
        display, ra, dec = mount.resolve_target("m 16", self.repo_root)
        self.assertEqual(display, "M16 Eagle")

    def test_unknown_raises(self):
        with self.assertRaises(ValueError) as cm:
            mount.resolve_target("XYZ999", self.repo_root)
        self.assertIn("XYZ999", str(cm.exception))
        self.assertIn("Known:", str(cm.exception))

    def test_vault_wins_over_catalog(self):
        # Write a fake target note with overriding coords
        targets = self.repo_root / "02_Targets" / "Nebulae"
        targets.mkdir(parents=True)
        note = targets / "M16-Eagle.md"
        note.write_text(
            "---\n"
            "title: M16 — Eagle Nebula (from vault)\n"
            "designation: M16\n"
            "ra_deg: 100.0\n"
            "dec_deg: -50.0\n"
            "---\n\nbody\n",
            encoding="utf-8",
        )
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed — vault lookup degrades to fallback (covered separately)")
        display, ra, dec = mount.resolve_target("M16", self.repo_root)
        self.assertEqual(display, "M16 — Eagle Nebula (from vault)")
        self.assertEqual(ra, 100.0)
        self.assertEqual(dec, -50.0)


# ============================================================================
# 4. Mocked TCP layer
# ============================================================================

class TestMountConnection(unittest.TestCase):

    def _mock_socket_with_response(self, response: bytes) -> MagicMock:
        """Build a socket mock that returns `response` on recv(), then EOF."""
        sock = MagicMock(spec=socket.socket)
        sock.__enter__.return_value = sock
        sock.__exit__.return_value = False
        # recv returns the whole response on first call, then empty (EOF)
        sock.recv.side_effect = [response, b""]
        return sock

    @patch("mount.socket.create_connection")
    def test_send_returns_response(self, mock_create):
        sock = self._mock_socket_with_response(b"0026#")
        mock_create.return_value = sock
        conn = mount.MountConnection()
        resp = conn.send(":MountInfo#")
        self.assertEqual(resp, "0026#")
        sock.sendall.assert_called_once_with(b":MountInfo#")

    @patch("mount.socket.create_connection")
    def test_send_handles_partial_recv(self, mock_create):
        sock = MagicMock(spec=socket.socket)
        sock.__enter__.return_value = sock
        sock.__exit__.return_value = False
        sock.recv.side_effect = [b"0026", b"#"]  # arrives in two chunks
        mock_create.return_value = sock
        conn = mount.MountConnection()
        resp = conn.send(":MountInfo#")
        self.assertEqual(resp, "0026#")

    @patch("mount.socket.create_connection")
    def test_fresh_connection_per_send(self, mock_create):
        sock = self._mock_socket_with_response(b"1#")
        mock_create.return_value = sock
        conn = mount.MountConnection()
        conn.send(":MP0#")
        # reset side_effect for second call
        sock.recv.side_effect = [b"1#", b""]
        conn.send(":RT0#")
        self.assertEqual(mock_create.call_count, 2, "should open a fresh socket per command")

    @patch("mount.socket.create_connection")
    def test_timeout_raises_mount_timeout(self, mock_create):
        sock = MagicMock(spec=socket.socket)
        sock.__enter__.return_value = sock
        sock.__exit__.return_value = False
        sock.recv.side_effect = socket.timeout()
        mock_create.return_value = sock
        conn = mount.MountConnection(read_deadline_s=0.1)
        with self.assertRaises(mount.MountTimeout):
            conn.send(":GLS#")

    @patch("mount.socket.create_connection")
    def test_connection_refused_raises_unreachable(self, mock_create):
        mock_create.side_effect = ConnectionRefusedError()
        conn = mount.MountConnection()
        with self.assertRaises(mount.MountUnreachable):
            conn.send(":GLS#")

    @patch("mount.socket.create_connection")
    def test_eof_with_no_data_raises_response_error(self, mock_create):
        # Empty buffer + immediate EOF is the only "definitely broken" case
        # under the new short-read default. Partial bytes followed by EOF are
        # returned as-is (let the parser decide).
        sock = MagicMock(spec=socket.socket)
        sock.__enter__.return_value = sock
        sock.__exit__.return_value = False
        sock.recv.side_effect = [b""]   # closes with nothing sent
        mock_create.return_value = sock
        conn = mount.MountConnection()
        with self.assertRaises(mount.MountResponseError):
            conn.send(":GLS#")

    @patch("mount.socket.create_connection")
    def test_partial_then_eof_returns_partial(self, mock_create):
        # New behaviour (vs the prior strict mode): if we got some bytes and
        # then EOF, return what we got instead of raising. The parser will
        # surface the error if the partial isn't valid.
        sock = MagicMock(spec=socket.socket)
        sock.__enter__.return_value = sock
        sock.__exit__.return_value = False
        sock.recv.side_effect = [b"+021630", b""]
        mock_create.return_value = sock
        conn = mount.MountConnection()
        resp = conn.send(":GLS#")
        self.assertEqual(resp, "+021630")

    @patch("mount.socket.create_connection")
    def test_no_terminator_command_tolerates_missing_hash(self, mock_create):
        # :MountInfo# returns '0026' without '#' on real firmware — verify our
        # short-read path returns the body cleanly without raising.
        sock = MagicMock(spec=socket.socket)
        sock.__enter__.return_value = sock
        sock.__exit__.return_value = False
        sock.recv.side_effect = [b"0026", socket.timeout()]  # then quiet
        mock_create.return_value = sock
        conn = mount.MountConnection()
        resp = conn.send(":MountInfo#")
        self.assertEqual(resp, "0026")

    def test_send_rejects_unterminated_command(self):
        conn = mount.MountConnection()
        with self.assertRaises(ValueError):
            conn.send("GLS")  # no leading ':', no trailing '#'


# ============================================================================
# 5. Live mount integration tests (opt-in)
# ============================================================================

LIVE = os.environ.get("MOUNT_TEST_LIVE") == "1"


@unittest.skipUnless(LIVE, "set MOUNT_TEST_LIVE=1 to run live integration tests")
class TestLiveMount(unittest.TestCase):
    """Live tests against the actual mount at MOUNT_IP:MOUNT_PORT.

    Prerequisites (asserted in setUpClass):
      - mount powered on
      - mount on home WiFi (192.168.178.87 reachable)
      - ASIAIR USB-Serial NOT connected (single-client invariant)

    All tests here are READ-ONLY except test_timesync_drift_under_2s
    (which writes :SG#, :SDS#, :SUT# but only restores to host time).
    park / unpark / goto are deliberately NOT covered here — they move the
    mount and need manual safety supervision.
    """

    @classmethod
    def setUpClass(cls):
        cls.mount = mount.MountConnection()
        # sanity ping — fail fast if mount unreachable
        try:
            cls.mount.send(":MountInfo#")
        except mount.MountError as e:
            raise unittest.SkipTest(f"live mount not reachable: {e}")

    def test_status_returns_known_state(self):
        info = mount.parse_mount_info(self.mount.send(":MountInfo#"))
        self.assertEqual(info.code, "0026", "expected CEM26 mount code")
        gls = mount.parse_gls(self.mount.send(":GLS#"))
        # Location should be within 0.01° of Tuntange constants
        self.assertAlmostEqual(gls.latitude_deg, mount.EXPECTED_LAT_DEG, places=2)
        self.assertAlmostEqual(gls.longitude_deg, mount.EXPECTED_LON_DEG, places=2)
        self.assertEqual(gls.hemisphere, "N")

    def test_firmware_matches_documented(self):
        fw1 = mount.parse_fw(self.mount.send(":FW1#"))
        fw2 = mount.parse_fw(self.mount.send(":FW2#"))
        # Documented installed version per 2026-05-24 verification: V20230305
        # If this fails, either the mount was upgraded or the equipment note
        # is out of sync — investigate before pushing.
        self.assertEqual(fw1.first, "2023-03-05", "HC firmware drift detected")
        self.assertEqual(fw2.first, "2021-04-20", "RA firmware drift detected")
        self.assertEqual(fw2.second, "2023-03-05", "DEC firmware drift detected")

    def test_health_runs_without_exception(self):
        # We don't assert exit_code == 0 — that depends on real mount state
        # (e.g., time drift, location set correctly). The test verifies the
        # script runs end-to-end without crashing; a non-zero exit just
        # means the mount has actionable issues for the user to fix.
        from contextlib import redirect_stdout
        import io
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = mount.cli_health(self.mount)
        self.assertIn(exit_code, (0, 1),
                      f"unexpected exit code {exit_code}; output:\n{buf.getvalue()}")
        self.assertIn("Pre-session mount health check", buf.getvalue())
        if exit_code == 1:
            print(f"\n  ℹ️  health check returned 1 — mount has fixable issues:\n{buf.getvalue()}")

    def test_log_writes_valid_ndjson(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "test-mount-log.json"
            # Use a tight interval so the test finishes in a few seconds.
            # cli_log respects SIGINT; we simulate it by spawning a thread.
            import threading
            stop_after_s = 8.0
            interval_s = 2.0

            def _interrupt_after_delay():
                time.sleep(stop_after_s)
                # Use os.kill to send SIGINT to ourselves
                os.kill(os.getpid(), 2)  # SIGINT

            threading.Thread(target=_interrupt_after_delay, daemon=True).start()
            # cli_log catches SIGINT internally and writes a summary line
            exit_code = mount.cli_log(self.mount, out, interval_s)
            self.assertEqual(exit_code, 0)

            self.assertTrue(out.exists())
            lines = out.read_text(encoding="utf-8").strip().split("\n")
            self.assertGreaterEqual(len(lines), 2,
                                    f"expected ≥1 sample + 1 summary, got {len(lines)} lines")
            # Every line must parse as JSON
            records = [json.loads(line) for line in lines]
            kinds = {r["kind"] for r in records}
            self.assertIn("sample", kinds)
            self.assertIn("summary", kinds)
            # Sample records have RA/Dec
            samples = [r for r in records if r["kind"] == "sample"]
            for s in samples:
                self.assertIn("ra_deg", s)
                self.assertIn("dec_deg", s)
                self.assertIn("system_state", s)


if __name__ == "__main__":
    unittest.main()
