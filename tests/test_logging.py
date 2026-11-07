import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGGER = ROOT / "scripts/run_logged.sh"


class LoggingTests(unittest.TestCase):
    def test_molecules_are_streamed_and_command_errors_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "make.log"
            result = subprocess.run(
                ["sh", str(LOGGER), str(log), "Export", sys.executable, "-c",
                 "import sys; print('[MOLECULE] GABA', flush=True); print('verbose LaTeX output'); sys.exit(7)"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 7)
            self.assertIn("[MOLECULE] GABA\n", result.stdout)
            self.assertIn("[MOLECULE] GABA", log.read_text())
            self.assertNotIn("verbose LaTeX output", result.stdout)
            self.assertIn("verbose LaTeX output", log.read_text())

    def test_failure_preserves_exit_code_and_limits_terminal_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "make.log"
            result = subprocess.run(
                ["sh", str(LOGGER), str(log), "LaTeX", sys.executable, "-c",
                 "import sys; [print('detail', i) for i in range(100)]; sys.exit(7)"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 7)
            self.assertIn("detail 0\n", log.read_text())
            self.assertIn("detail 99\n", result.stderr)
            self.assertNotIn("detail 0\n", result.stderr)
            self.assertLessEqual(len(result.stderr.splitlines()), 16)
            self.assertIn("Exitcode: 7", log.read_text())


if __name__ == "__main__":
    unittest.main()
