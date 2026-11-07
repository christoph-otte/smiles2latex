import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import export_structures as exporter


class ExportTests(unittest.TestCase):
    def test_export_commands_and_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "ethanol.tex").write_text(r"\chemfig{C-C-OH}")

            def run(command: list[str], **kwargs: object) -> None:
                working = Path(str(kwargs["cwd"]))
                self.assertTrue(kwargs["check"])
                if command[0] == "xelatex":
                    self.assertEqual((working / "molecule.tex").read_text(), r"\chemfig{C-C-OH}")
                    self.assertIn("-no-shell-escape", command)
                    if "-no-pdf" in command:
                        self.assertIn(r"\def\svgexport{1}", command[-1])
                        (working / "ethanol-svg.xdv").write_bytes(b"XDV-test")
                    else:
                        (working / "ethanol.pdf").write_bytes(b"%PDF-test")
                else:
                    self.assertEqual(command[:3], ["dvisvgm", "--no-fonts", "--bbox=papersize"])
                    (working / "ethanol.svg").write_text("<svg/>")

            with patch.object(exporter.subprocess, "run", side_effect=run) as runner:
                with contextlib.redirect_stdout(io.StringIO()):
                    exporter.export_structure("ethanol", output)
            self.assertEqual(runner.call_count, 3)
            self.assertEqual((output / "ethanol.pdf").read_bytes(), b"%PDF-test")
            self.assertEqual((output / "ethanol.svg").read_text(), "<svg/>")
            self.assertEqual(len(list(output.iterdir())), 3)

    def test_command_failure_returns_error_and_removes_stale_graphics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for suffix in (".pdf", ".svg"):
                (output / f"ethanol{suffix}").write_text("stale")
            with patch.object(exporter, "PROCESSED_DIR", output):
                with patch.object(exporter, "read_molecules", return_value=[{"id": "ethanol", "name": "Ethanol"}]):
                    with patch.object(exporter.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "xelatex")):
                        (output / "ethanol.tex").write_text(r"\chemfig{C-C-OH}")
                        with patch.object(sys, "argv", ["export_structures.py"]), contextlib.redirect_stderr(io.StringIO()) as errors:
                            self.assertEqual(exporter.main(), 1)
            self.assertIn("ERROR during export:", errors.getvalue())
            self.assertIn("xelatex", errors.getvalue())
            self.assertFalse((output / "ethanol.pdf").exists())
            self.assertFalse((output / "ethanol.svg").exists())


if __name__ == "__main__":
    unittest.main()
