"""Independent local Git/Bash installer fixtures; no network or real credentials.

Only the immutable installer's REPO_URL assignment is replaced in each fixture.
Tiny synthetic gate tests exercise installer ordering, not the real gate logic.
Temporary repositories are retained for review; this test never deletes files.
"""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "ops/install_vps_forcing_functions.sh"
BASH = Path(r"C:\Program Files\Git\bin\bash.exe") if os.name == "nt" else Path("/bin/bash")
GIT = Path(r"C:\Program Files\Git\cmd\git.exe") if os.name == "nt" else Path("/usr/bin/git")
ENTRIES = ("tools/holon_gate.py", "ops/vps_exec_guard.py", "tools/reconcile_kernel.py", "tools/janitor_gate.py", "ops/janitor_exec.py")
GATE_TESTS = ("test_holon_gate.py", "test_reconcile_kernel.py", "test_janitor_gate.py")


def posix(path):
    value = Path(path).resolve().as_posix()
    return "/" + value[0].lower() + value[2:] if re.match(r"^[A-Za-z]:/", value) else value


class InstallerPinTests(unittest.TestCase):
    def setUp(self):
        # A unique owned directory; retained, never chmod'ed or recursively removed.
        self.base = Path(tempfile.mkdtemp(prefix="hfo-installer-pin-"))
        self.source = self.base / "source"
        self.destination = self.base / "installed"
        self.home = self.base / "home"
        self.bin = self.base / "fixture-bin"
        for directory in (self.source, self.home, self.bin):
            directory.mkdir()
        config = self.base / "empty.gitconfig"
        config.write_text("", encoding="utf-8")
        self.env = {k: os.environ[k] for k in ("SystemRoot", "SystemDrive", "COMSPEC", "TEMP", "TMP") if k in os.environ}
        self.env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(config),
                         "GIT_CONFIG_SYSTEM": str(config), "GIT_TERMINAL_PROMPT": "0", "GIT_ALLOW_PROTOCOL": "file",
                         "HOME": posix(self.home), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                         "PATH": str(GIT.parent) + os.pathsep + os.environ.get("PATH", "")})
        self.git("init", "--quiet", "-b", "main", str(self.source))
        for key, value in (("user.name", "Synthetic Installer Reviewer"), ("user.email", "review@example.invalid"),
                           ("core.autocrlf", "false"), ("core.filemode", "false")):
            self.git("-C", str(self.source), "config", key, value)
        candidate = INSTALLER.read_text(encoding="utf-8")
        original = 'REPO_URL="https://github.com/TTaoGaming/hfo-gen-142.git"'
        self.assertEqual(candidate.count(original), 1)
        candidate = candidate.replace(original, "REPO_URL=" + shlex.quote(self.source.as_uri()))
        self.write("ops/install_vps_forcing_functions.sh", candidate)
        for entry in ENTRIES:
            self.write(entry, "#!/usr/bin/env python3\nprint('synthetic original')\n")
        for name in GATE_TESTS:
            self.write("tests/" + name, "import unittest\nclass Gate(unittest.TestCase):\n def test_fixture(self): self.assertTrue(True)\n")
        wrapper = self.bin / "python3"
        wrapper.write_text("#!/usr/bin/env bash\nexec " + shlex.quote(posix(sys.executable)) + ' "$@"\n', encoding="utf-8", newline="\n")
        if os.name != "nt":
            wrapper.chmod(0o700)
        self.pin = self.commit()

    def write(self, relative, text):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def git(self, *args, check=True):
        return subprocess.run([str(GIT), *args], env=self.env, text=True, capture_output=True, timeout=20, check=check)

    def commit(self):
        self.git("-C", str(self.source), "add", "--all")
        for entry in ENTRIES:
            if (self.source / entry).exists():
                self.git("-C", str(self.source), "update-index", "--chmod=+x", "--", entry)
        self.git("-C", str(self.source), "commit", "--quiet", "-m", "Synthetic local installer fixture")
        return self.git("-C", str(self.source), "rev-parse", "HEAD").stdout.strip()

    def install(self, pin):
        env = {**self.env, "HFO_GEN142_ROOT": posix(self.destination), "FIXTURE_BIN": posix(self.bin), "FIXTURE_GIT_DIR": posix(GIT.parent),
               "FIXTURE_INSTALLER": posix(self.source / "ops/install_vps_forcing_functions.sh")}
        if pin is not None:
            env["HFO_GEN142_REF"] = pin
        return subprocess.run([str(BASH), "--noprofile", "--norc", "-c",
                               'export PATH="$FIXTURE_BIN:$FIXTURE_GIT_DIR:/usr/bin:/bin"; exec bash "$FIXTURE_INSTALLER"'],
                              env=env, text=True, capture_output=True, timeout=45)

    def receipt_path(self):
        return self.home / ".local/state/hfo-gen142-forcing/install.json"

    def assert_success(self, result, pin):
        self.assertEqual(result.returncode, 0, result.stderr[-3000:] + result.stdout[-1000:])
        self.assertEqual(self.git("-C", str(self.destination), "rev-parse", "HEAD").stdout.strip(), pin)
        receipt = json.loads(self.receipt_path().read_text(encoding="utf-8"))
        self.assertEqual(receipt["repo_commit"], pin)
        self.assertEqual(receipt["requested_commit"], pin)
        self.assertEqual(receipt["semantic_owner"], "hfo-sigrun-va-r0")

    def test_missing_malformed_moving_and_placeholder_pins_refuse_before_mutation(self):
        for pin in (None, "", "main", "HEAD", "a" * 39, "A" * 40, "0" * 40, "a" * 40 + "\n"):
            with self.subTest(pin=pin):
                out = self.install(pin)
                self.assertEqual(out.returncode, 22, out.stderr)
                self.assertIn("immutable HFO_GEN142_REF required", out.stderr)
                self.assertFalse(self.destination.exists())
                self.assertFalse(self.receipt_path().exists())

    def test_fresh_install_fetches_exact_pin_when_main_has_moved(self):
        self.write("marker.txt", "unrequested later main\n")
        latest = self.commit()
        self.git("-C", str(self.source), "checkout", "--quiet", "--detach", self.pin)
        self.assertEqual(self.git("-C", str(self.source), "rev-parse", "main").stdout.strip(), latest)
        self.assert_success(self.install(self.pin), self.pin)
        self.assertFalse((self.destination / "marker.txt").exists())

    def test_existing_clean_install_updates_to_exact_pin_not_later_main(self):
        self.assert_success(self.install(self.pin), self.pin)
        self.write("marker.txt", "requested second revision\n")
        second = self.commit()
        self.write("marker.txt", "unrequested third main\n")
        self.commit()
        self.git("-C", str(self.source), "checkout", "--quiet", "--detach", second)
        self.assert_success(self.install(second), second)
        self.assertEqual((self.destination / "marker.txt").read_text(), "requested second revision\n")

    def test_dirty_destination_is_preserved_without_reset_or_receipt_replacement(self):
        self.assert_success(self.install(self.pin), self.pin)
        receipt = self.receipt_path().read_bytes()
        dirty = self.destination / ENTRIES[0]
        dirty.write_text("owned uncommitted operator edit\n", encoding="utf-8")
        extra = self.destination / "owned-untracked.txt"
        extra.write_text("owned untracked\n", encoding="utf-8")
        out = self.install(self.pin)
        self.assertEqual(out.returncode, 22, out.stderr)
        self.assertIn("destination dirty", out.stderr)
        self.assertEqual(dirty.read_text(), "owned uncommitted operator edit\n")
        self.assertEqual(extra.read_text(), "owned untracked\n")
        self.assertEqual(self.receipt_path().read_bytes(), receipt)
        self.assertEqual(self.git("-C", str(self.destination), "rev-parse", "HEAD").stdout.strip(), self.pin)

    def test_bad_source_revision_or_dirty_source_never_activates(self):
        out = self.install("a" * 40)
        self.assertEqual(out.returncode, 22, out.stderr)
        self.assertFalse(self.destination.exists())
        self.write("owned-untracked.txt", "synthetic dirty source\n")
        out = self.install(self.pin)
        self.assertEqual(out.returncode, 22, out.stderr)
        self.assertIn("installer source dirty", out.stderr)
        self.assertFalse(self.destination.exists())

    def test_failing_source_test_preserves_existing_checkout_and_receipt(self):
        self.assert_success(self.install(self.pin), self.pin)
        receipt = self.receipt_path().read_bytes()
        self.write("tests/" + GATE_TESTS[0], "import unittest\nclass Gate(unittest.TestCase):\n def test_fixture(self): self.fail('deliberate fixture failure')\n")
        bad = self.commit()
        out = self.install(bad)
        self.assertNotEqual(out.returncode, 0)
        self.assertEqual(self.git("-C", str(self.destination), "rev-parse", "HEAD").stdout.strip(), self.pin)
        self.assertEqual(self.receipt_path().read_bytes(), receipt)

    def test_missing_entrypoint_cannot_switch_existing_live_checkout_before_hold(self):
        self.assert_success(self.install(self.pin), self.pin)
        receipt = self.receipt_path().read_bytes()
        self.git("-C", str(self.source), "rm", "--quiet", ENTRIES[-1])
        bad = self.commit()
        out = self.install(bad)
        self.assertNotEqual(out.returncode, 0)
        self.assertEqual(self.git("-C", str(self.destination), "rev-parse", "HEAD").stdout.strip(), self.pin,
                         "A failing preflight must not switch the checkout already referenced by installed links")
        self.assertTrue((self.destination / ENTRIES[-1]).exists())
        self.assertEqual(self.receipt_path().read_bytes(), receipt)

    def test_installer_has_no_destructive_reset_or_moving_branch_checkout(self):
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"(?m)^\s*(?:git\b[^\n]*\breset\b|rm\s+-[rf]|git\b[^\n]*checkout\b[^\n]*\bmain\b)")


if __name__ == "__main__":
    unittest.main()
